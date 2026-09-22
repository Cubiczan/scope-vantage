#!/usr/bin/env python3
"""Evidence check: the test suite carries 50 or more pytest test functions.

Backs evidence/matrix.yaml row C014. Stdlib-only, no network, no git.
Static inventory only — CI's test job is what executes the suite.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = REPO_ROOT / "tests"

MIN_TEST_FUNCTIONS = 50
TEST_DEF = re.compile(r"^\s*def (test_\w+)\s*\(", re.M)


def main() -> int:
    count = 0
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        found = TEST_DEF.findall(path.read_text(encoding="utf-8"))
        count += len(found)
        print(f"PASS  {path.relative_to(REPO_ROOT)}: {len(found)} test functions")
    print(f"total test functions: {count} (minimum {MIN_TEST_FUNCTIONS})")
    return 0 if count >= MIN_TEST_FUNCTIONS else 1


if __name__ == "__main__":
    raise SystemExit(main())
