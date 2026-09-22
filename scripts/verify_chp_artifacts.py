#!/usr/bin/env python3
"""Evidence check: the four CHP compliance artifacts are present and non-empty.

Backs evidence/matrix.yaml row C022. Stdlib-only, no network, no git.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHP_DIR = REPO_ROOT / ".chp"

ARTIFACTS = [
    "STATE_MACHINE.md",
    "R0_CONFIG.yaml",
    "ADVERSARIAL_PROMPTS.md",
    "CHP_COMPLIANCE.md",
]


def main() -> int:
    failed = False
    for name in ARTIFACTS:
        path = CHP_DIR / name
        ok = path.is_file() and path.stat().st_size > 0
        print(f"{'PASS' if ok else 'FAIL'}  .chp/{name} present and non-empty")
        failed = failed or not ok

    config = (CHP_DIR / "R0_CONFIG.yaml").read_text(encoding="utf-8")
    for section in ("r0_gate:", "foundation:", "adversary:"):
        ok = section in config
        print(f"{'PASS' if ok else 'FAIL'}  R0_CONFIG.yaml declares {section}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
