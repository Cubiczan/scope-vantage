"""Bedrock Client — Amazon Bedrock Runtime Converse API for Amazon Nova.

Uses boto3 (no OpenAI SDK) to call Amazon Nova via the Bedrock Converse API.
The default model is the Nova Lite cross-region inference profile in us-east-1
(``us.amazon.nova-lite-v1:0``). Anthropic Claude model IDs are rejected:
Claude on Bedrock is an AWS Marketplace product and is not covered by promo credits.

https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html
https://docs.aws.amazon.com/nova/latest/userguide/using-converse-api.html
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Amazon Nova Lite cross-region inference profile. Invoke from us-east-1.
DEFAULT_MODEL_ID = "us.amazon.nova-lite-v1:0"
DEFAULT_REGION = "us-east-1"


class AnthropicModelRejected(ValueError):
    """Raised when an Anthropic Claude model id is configured.

    Claude on Amazon Bedrock is billed through AWS Marketplace and is
    IAM-denied on this account. Amazon Nova is the supported model family.
    """


def _is_anthropic_model(model_id: str) -> bool:
    """True for on-demand ``anthropic.*`` ids and geo profiles such as ``us.anthropic.*``."""
    lowered = model_id.strip().lower()
    return lowered.startswith("anthropic.") or ".anthropic." in lowered


def resolve_model_id(model_id: Optional[str] = None) -> str:
    """Return the Bedrock model id to call, rejecting Anthropic overrides.

    ``None`` reads ``BEDROCK_MODEL_ID`` and otherwise uses Amazon Nova Lite.
    A blank value also falls back to Nova Lite. Any ``anthropic.*`` id,
    including cross-region profiles (``us.anthropic.*``), raises
    ``AnthropicModelRejected``.
    """
    if model_id is None:
        model_id = os.environ.get("BEDROCK_MODEL_ID")
    candidate = model_id.strip() if isinstance(model_id, str) else ""
    if not candidate:
        candidate = DEFAULT_MODEL_ID
    if _is_anthropic_model(candidate):
        raise AnthropicModelRejected(
            f"Anthropic model '{candidate}' is not allowed. "
            "Claude on Amazon Bedrock is billed through AWS Marketplace and is "
            "not covered by promo credits (anthropic.* is IAM-denied on this account). "
            f"Use an Amazon Nova model such as {DEFAULT_MODEL_ID}."
        )
    return candidate


@dataclass
class BedrockClient:
    """Thin wrapper around boto3 Bedrock Runtime Converse API."""

    model_id: str = field(
        default_factory=lambda: os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)
    )
    region: str = field(default_factory=lambda: os.environ.get("AWS_REGION", DEFAULT_REGION))
    max_tokens: int = 1500
    temperature: float = 0.3
    max_retries: int = 3
    base_delay: float = 1.0
    _client: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.model_id = resolve_model_id(self.model_id)
        if not (self.region or "").strip():
            self.region = DEFAULT_REGION
        self._client = boto3.client("bedrock-runtime", region_name=self.region)

    def converse(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        inference_config = {
            "maxTokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
        }
        for attempt in range(self.max_retries):
            try:
                kwargs: Dict[str, Any] = {
                    "modelId": self.model_id,
                    "messages": messages,
                    "inferenceConfig": inference_config,
                }
                if system:
                    kwargs["system"] = [{"text": system}]
                response = self._client.converse(**kwargs)
                output = response.get("output", {})
                message = output.get("message", {})
                text = "".join(cb.get("text", "") for cb in message.get("content", []))
                usage = response.get("usage", {})
                return {
                    "content": text,
                    "input_tokens": usage.get("inputTokens", 0),
                    "output_tokens": usage.get("outputTokens", 0),
                    "model": self.model_id,
                    "stop_reason": response.get("stopReason", message.get("stopReason")),
                }
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code", "")
                if code in ("ThrottlingException", "ServiceUnavailable") and attempt < self.max_retries - 1:
                    time.sleep(self.base_delay * (2 ** attempt))
                    continue
                raise
        raise RuntimeError(f"Bedrock converse failed after {self.max_retries} retries")

    def chat(self, prompt: str, system: Optional[str] = None, **kw) -> str:
        return self.converse(
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            system=system,
            **kw,
        )["content"]

    def multi_turn(self, messages: List[Dict[str, str]], system: Optional[str] = None, **kw) -> str:
        return self.converse(
            messages=[{"role": m["role"], "content": [{"text": m["content"]}]} for m in messages],
            system=system,
            **kw,
        )["content"]
