"""Bedrock client defaults to Amazon Nova Lite and rejects Anthropic overrides."""
import importlib

import pytest

from bedrock_client import (
    DEFAULT_MODEL_ID,
    DEFAULT_REGION,
    AnthropicModelRejected,
    BedrockClient,
    resolve_model_id,
)


NOVA_LITE = "us.amazon.nova-lite-v1:0"
ANTHROPIC_IDS = [
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "us.anthropic.claude-3-haiku-20240307-v1:0",
    "eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "  ANTHROPIC.CLAUDE-3-HAIKU-20240307-V1:0  ",
]


def test_default_constants():
    assert DEFAULT_MODEL_ID == NOVA_LITE
    assert DEFAULT_REGION == "us-east-1"


def test_resolve_model_id_defaults_to_nova_lite(monkeypatch):
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    assert resolve_model_id() == NOVA_LITE
    assert resolve_model_id("") == NOVA_LITE
    assert resolve_model_id("   ") == NOVA_LITE


def test_resolve_model_id_honors_nova_override(monkeypatch):
    monkeypatch.setenv("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")
    assert resolve_model_id() == "amazon.nova-micro-v1:0"
    assert resolve_model_id("us.amazon.nova-pro-v1:0") == "us.amazon.nova-pro-v1:0"


@pytest.mark.parametrize("model_id", ANTHROPIC_IDS)
def test_rejects_anthropic_model_ids(model_id):
    with pytest.raises(AnthropicModelRejected, match="Amazon Nova"):
        resolve_model_id(model_id)


def test_client_defaults_to_nova_lite(monkeypatch):
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.setattr("bedrock_client.boto3.client", lambda *args, **kwargs: object())
    client = BedrockClient()
    assert client.model_id == NOVA_LITE
    assert client.region == "us-east-1"


def test_client_rejects_anthropic_override():
    with pytest.raises(AnthropicModelRejected, match="not allowed"):
        BedrockClient(model_id="anthropic.claude-3-haiku-20240307-v1:0")


def test_client_rejects_anthropic_env(monkeypatch):
    monkeypatch.setenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-haiku-20240307-v1:0")
    with pytest.raises(AnthropicModelRejected):
        BedrockClient()


def test_converse_sends_nova_model_id(monkeypatch):
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    calls = {}

    class FakeRuntime:
        def converse(self, **kwargs):
            calls["kwargs"] = kwargs
            return {
                "output": {"message": {"content": [{"text": "briefing"}]}},
                "usage": {"inputTokens": 4, "outputTokens": 2},
                "stopReason": "end_turn",
            }

    monkeypatch.setattr("bedrock_client.boto3.client", lambda *a, **k: FakeRuntime())
    client = BedrockClient()
    text = client.chat("Summarize lithium risk", system="Be concise")

    assert text == "briefing"
    sent = calls["kwargs"]
    assert sent["modelId"] == NOVA_LITE
    assert sent["messages"] == [{"role": "user", "content": [{"text": "Summarize lithium risk"}]}]
    assert sent["system"] == [{"text": "Be concise"}]
    assert sent["inferenceConfig"]["temperature"] == 0.3


def test_lambda_uses_nova_lite_and_rejects_anthropic(monkeypatch):
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    handler = importlib.import_module("src.lambda.intelligence_handler")
    calls = {}

    class FakeRuntime:
        def converse(self, **kwargs):
            calls["kwargs"] = kwargs
            return {"output": {"message": {"content": [{"text": "nova analysis"}]}}}

    monkeypatch.setattr(handler.boto3, "client", lambda *a, **k: FakeRuntime())
    analysis = handler.invoke_bedrock_analysis("Lithium", {"hhi_index": 4200})
    assert analysis == "nova analysis"
    assert calls["kwargs"]["modelId"] == NOVA_LITE

    monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    with pytest.raises(AnthropicModelRejected, match="not allowed"):
        handler.invoke_bedrock_analysis("Lithium", {})


def test_lambda_handler_surfaces_anthropic_rejection(monkeypatch):
    monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0")
    handler = importlib.import_module("src.lambda.intelligence_handler")
    with pytest.raises(AnthropicModelRejected):
        handler.handler(
            {"step": "bedrock_analysis", "scores": [{"commodity": "Cobalt"}]},
            None,
        )
