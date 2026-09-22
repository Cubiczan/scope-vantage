#!/usr/bin/env python3
"""Evidence check: README tracked-commodity HS codes exist in the source maps.

Backs evidence/matrix.yaml row C015. Stdlib-only, no network, no git.
The five codes come from the README Tracked Commodities table; each must be
tracked in both ComtradeService's HS_CODE_NAMES and the Commodity model's
CRITICAL_MINERALS registry.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

README_HS_CODES = ["2836.90", "8105.20", "7504.00", "7403.11", "2846.90"]

SERVICE_MAP = REPO_ROOT / "src" / "services" / "comtrade_service.py"
MODEL_MAP = REPO_ROOT / "src" / "models" / "commodity.py"


def main() -> int:
    service_text = SERVICE_MAP.read_text(encoding="utf-8")
    model_text = MODEL_MAP.read_text(encoding="utf-8")

    failed = False
    for code in README_HS_CODES:
        in_service = f'"{code}"' in service_text
        in_model = f'"{code}"' in model_text
        print(
            f"{'PASS' if in_service and in_model else 'FAIL'}  HS {code}: "
            f"service map={'yes' if in_service else 'NO'} "
            f"model registry={'yes' if in_model else 'NO'}"
        )
        failed = failed or not (in_service and in_model)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
