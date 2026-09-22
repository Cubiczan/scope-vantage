#!/usr/bin/env python3
"""Evidence check: PolarsDataProcessor operations used by the GX doc exist.

Backs evidence/matrix.yaml row C017. Stdlib-only, no network, no git.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSOR = REPO_ROOT / "src" / "polars_utils.py"

METHODS = [
    "filter_by_commodity",
    "filter_by_country",
    "filter_by_date_range",
    "aggregate_by_region",
    "compute_volatility",
    "hhi_index",
]


def main() -> int:
    text = PROCESSOR.read_text(encoding="utf-8")
    checks: list[tuple[str, bool]] = [
        ("PolarsDataProcessor class is defined", "class PolarsDataProcessor" in text),
    ]
    checks += [
        (f"method defined: {method}", f"def {method}(" in text) for method in METHODS
    ]

    failed = False
    for label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
