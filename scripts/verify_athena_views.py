#!/usr/bin/env python3
"""Evidence check: the three pre-built Athena SQL views exist and declare views.

Backs evidence/matrix.yaml row C012. Stdlib-only, no network, no git.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VIEWS_DIR = REPO_ROOT / "src" / "aws" / "athena_views"

EXPECTED = {
    "critical_mineral_flows.sql": "scope_vantage.critical_mineral_flows_v",
    "tariff_impact.sql": "scope_vantage.tariff_impact_v",
    "supply_chain_risk.sql": "scope_vantage.supply_chain_risk_v",
}


def main() -> int:
    failed = False
    for filename, view_name in EXPECTED.items():
        path = VIEWS_DIR / filename
        if not path.is_file():
            print(f"FAIL  missing view file: src/aws/athena_views/{filename}")
            failed = True
            continue
        text = path.read_text(encoding="utf-8")
        declares = "CREATE OR REPLACE VIEW" in text and view_name in text
        print(
            f"{'PASS' if declares else 'FAIL'}  {filename} declares {view_name}"
        )
        failed = failed or not declares
    extra = sorted(p.name for p in VIEWS_DIR.glob("*.sql") if p.name not in EXPECTED)
    if extra:
        print(f"FAIL  unexpected extra SQL views present: {', '.join(extra)}")
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
