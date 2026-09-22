#!/usr/bin/env python3
"""Evidence check: README project-structure inventory matches the tree.

Backs evidence/matrix.yaml row C013. Stdlib-only, no network, no git.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED = {
    "src/models": [
        "trade_flow.py",
        "commodity.py",
        "supply_chain_node.py",
        "logistics_event.py",
        "tariff_regulation.py",
        "intelligence_briefing.py",
    ],
    "src/services": [
        "comtrade_service.py",
        "pricing_service.py",
        "supply_chain_service.py",
        "tariff_service.py",
        "intelligence_service.py",
    ],
    "src/aws/glue_scripts": [
        "trade_flow_etl.py",
        "supply_chain_etl.py",
        "logistics_event_etl.py",
    ],
    "src/aws/athena_views": [
        "critical_mineral_flows.sql",
        "tariff_impact.sql",
        "supply_chain_risk.sql",
    ],
    "src/lambda": [
        "comtrade_ingestion_handler.py",
        "intelligence_handler.py",
    ],
}

ROOT_FILES = ["bedrock_client.py", "requirements.txt"]


def main() -> int:
    failed = False
    for rel_dir, names in EXPECTED.items():
        for name in names:
            ok = (REPO_ROOT / rel_dir / name).is_file()
            print(f"{'PASS' if ok else 'FAIL'}  {rel_dir}/{name}")
            failed = failed or not ok
    for name in ROOT_FILES:
        ok = (REPO_ROOT / name).is_file()
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
