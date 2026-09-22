#!/usr/bin/env python3
"""Evidence check: Bedrock Converse API client for Claude 3 Haiku.

Backs evidence/matrix.yaml row C006. Stdlib-only, no network, no git.
Statically asserts the client wraps the Bedrock Runtime Converse API with a
Claude 3 Haiku default model and that IntelligenceService uses it.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BEDROCK_CLIENT = REPO_ROOT / "bedrock_client.py"
INTELLIGENCE_SERVICE = REPO_ROOT / "src" / "services" / "intelligence_service.py"


def main() -> int:
    client_text = BEDROCK_CLIENT.read_text(encoding="utf-8")
    service_text = INTELLIGENCE_SERVICE.read_text(encoding="utf-8")

    checks: list[tuple[str, bool]] = [
        ("bedrock_client.py defines converse()", "def converse(" in client_text),
        ("default model is Claude 3 Haiku", "claude-3-haiku" in client_text),
        ("client targets the Bedrock Runtime", "bedrock-runtime" in client_text),
        (
            "IntelligenceService imports BedrockClient",
            "from bedrock_client import BedrockClient" in service_text,
        ),
    ]

    failed = False
    for label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
