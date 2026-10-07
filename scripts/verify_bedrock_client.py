#!/usr/bin/env python3
"""Evidence check: Bedrock Converse API client for Amazon Nova Lite.

Backs evidence/matrix.yaml row C006. Stdlib-only, no network, no git.
Statically asserts the client wraps the Bedrock Runtime Converse API with
the Amazon Nova Lite inference profile as the default, that Anthropic
Claude overrides are rejected, and that Terraform IAM allows Nova only.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BEDROCK_CLIENT = REPO_ROOT / "bedrock_client.py"
INTELLIGENCE_SERVICE = REPO_ROOT / "src" / "services" / "intelligence_service.py"
INTELLIGENCE_HANDLER = REPO_ROOT / "src" / "lambda" / "intelligence_handler.py"
VARIABLES_TF = REPO_ROOT / "terraform" / "variables.tf"
MAIN_TF = REPO_ROOT / "terraform" / "main.tf"
ENV_EXAMPLE = REPO_ROOT / ".env.example"

NOVA_LITE = "us.amazon.nova-lite-v1:0"
# The previous default. It must not remain as a configured model id.
RETIRED_CLAUDE_ID = "anthropic.claude-3-haiku-20240307-v1:0"

PRODUCTION_FILES = (
    BEDROCK_CLIENT,
    INTELLIGENCE_SERVICE,
    INTELLIGENCE_HANDLER,
    VARIABLES_TF,
    MAIN_TF,
    ENV_EXAMPLE,
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "GREAT_EXPECTATIONS_INTEGRATION.md",
)


def main() -> int:
    client_text = BEDROCK_CLIENT.read_text(encoding="utf-8")
    service_text = INTELLIGENCE_SERVICE.read_text(encoding="utf-8")
    handler_text = INTELLIGENCE_HANDLER.read_text(encoding="utf-8")
    variables_text = VARIABLES_TF.read_text(encoding="utf-8")
    main_text = MAIN_TF.read_text(encoding="utf-8")
    env_text = ENV_EXAMPLE.read_text(encoding="utf-8")

    retired_hits = [
        str(path.relative_to(REPO_ROOT))
        for path in PRODUCTION_FILES
        if RETIRED_CLAUDE_ID in path.read_text(encoding="utf-8")
    ]

    checks: list[tuple[str, bool]] = [
        ("bedrock_client.py defines converse()", "def converse(" in client_text),
        (
            "default model is Amazon Nova Lite",
            f'DEFAULT_MODEL_ID = "{NOVA_LITE}"' in client_text,
        ),
        ("default region is us-east-1", 'DEFAULT_REGION = "us-east-1"' in client_text),
        ("client targets the Bedrock Runtime", "bedrock-runtime" in client_text),
        ("client calls the Converse API", "self._client.converse(" in client_text),
        (
            "Anthropic model overrides are rejected",
            "class AnthropicModelRejected" in client_text and "def resolve_model_id(" in client_text,
        ),
        (
            "IntelligenceService imports BedrockClient",
            "from bedrock_client import BedrockClient" in service_text,
        ),
        (
            "Lambda resolves the model id before calling Bedrock",
            "resolve_model_id()" in handler_text and "bedrock.converse(" in handler_text,
        ),
        (
            "Terraform defaults to Amazon Nova Lite",
            f'default     = "{NOVA_LITE}"' in variables_text,
        ),
        (
            "Terraform rejects anthropic model ids",
            'strcontains(lower(var.bedrock_model_id), "anthropic.")' in variables_text,
        ),
        (
            "IAM allows Nova foundation models",
            "foundation-model/amazon.nova-*" in main_text,
        ),
        (
            "IAM allows Nova inference profiles",
            "inference-profile/us.amazon.nova-*" in main_text,
        ),
        (
            "IAM Converse action is scoped to the Nova statement",
            "bedrock:" not in main_text[
                main_text.find("Statement = ["):main_text.find('Resource = "*"')
            ]
            and "bedrock:Converse" in main_text.split("AllowAmazonNovaConverse", 1)[1],
        ),
        (".env.example defaults to Amazon Nova Lite", f"BEDROCK_MODEL_ID={NOVA_LITE}" in env_text),
        ("retired Claude model id is not a default", not retired_hits),
    ]

    failed = False
    for label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
        failed = failed or not ok
    if retired_hits:
        print("retired Claude model id still present in: " + ", ".join(retired_hits))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
