#!/usr/bin/env python3
"""Evidence check: Terraform provisions the Iceberg warehouse and AWS stack.

Backs evidence/matrix.yaml row C003. Stdlib-only, no network, no git.
Reads terraform/main.tf and asserts the declared resources exist.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAIN_TF = REPO_ROOT / "terraform" / "main.tf"


def resource_count(text: str, resource_type: str) -> int:
    return len(re.findall(rf'^resource\s+"{re.escape(resource_type)}"', text, re.M))


def main() -> int:
    text = MAIN_TF.read_text(encoding="utf-8")
    iceberg_tables = text.count('table_type = "ICEBERG"')
    checks: list[tuple[str, bool, str]] = [
        (
            "iceberg warehouse S3 bucket declared",
            'resource "aws_s3_bucket" "iceberg_warehouse"' in text,
            'resource "aws_s3_bucket" "iceberg_warehouse"',
        ),
        (
            "Glue catalog database declared",
            resource_count(text, "aws_glue_catalog_database") == 1,
            'resource "aws_glue_catalog_database"',
        ),
        (
            "at least 5 Glue catalog tables declared",
            resource_count(text, "aws_glue_catalog_table") >= 5,
            f'found {resource_count(text, "aws_glue_catalog_table")}',
        ),
        (
            'at least 5 Glue tables are table_type "ICEBERG"',
            iceberg_tables >= 5,
            f"found {iceberg_tables}",
        ),
        (
            "Athena workgroup declared",
            resource_count(text, "aws_athena_workgroup") == 1,
            'resource "aws_athena_workgroup"',
        ),
        (
            "exactly 2 Lambda functions declared",
            resource_count(text, "aws_lambda_function") == 2,
            f'found {resource_count(text, "aws_lambda_function")}',
        ),
        (
            "EventBridge schedule rules declared",
            resource_count(text, "aws_cloudwatch_event_rule") >= 2,
            f'found {resource_count(text, "aws_cloudwatch_event_rule")}',
        ),
        (
            "Step Functions state machine declared",
            resource_count(text, "aws_sfn_state_machine") == 1,
            'resource "aws_sfn_state_machine"',
        ),
    ]

    failed = False
    for label, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {label}  ({detail})")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
