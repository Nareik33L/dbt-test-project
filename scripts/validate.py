#!/usr/bin/env python3
"""Validate the Oakwell dbt + MetricFlow project end to end."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], heading: str) -> None:
    print(f"\n==> {heading}")
    print(" ".join(cmd))
    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = str(ROOT)
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def main() -> int:
    dbt = shutil.which("dbt")
    mf = shutil.which("mf")
    python = sys.executable

    if not dbt or not mf:
        print(
            "dbt and mf must be on PATH. Create a virtualenv and install "
            "requirements.txt first.",
            file=sys.stderr,
        )
        return 2

    run([dbt, "build"], "dbt build (models + tests)")
    run([dbt, "parse"], "dbt parse (semantic manifest)")
    run([mf, "validate-configs"], "MetricFlow semantic validation")

    queries = [
        [
            mf,
            "query",
            "--metrics",
            "revenue",
            "--start-time",
            "2026-07-01",
            "--end-time",
            "2026-07-31",
            "--decimals",
            "2",
        ],
        [
            mf,
            "query",
            "--metrics",
            "ending_mrr,active_customers",
            "--start-time",
            "2026-08-01",
            "--end-time",
            "2026-08-31",
            "--decimals",
            "2",
        ],
        [
            mf,
            "query",
            "--metrics",
            "ending_mrr",
            "--group-by",
            "customer_month__customer_segment",
            "--start-time",
            "2026-08-01",
            "--end-time",
            "2026-08-31",
            "--decimals",
            "2",
        ],
        [
            mf,
            "query",
            "--metrics",
            "support_tickets",
            "--group-by",
            "ticket__ticket_category",
            "--start-time",
            "2026-04-01",
            "--end-time",
            "2026-06-30",
        ],
        [
            mf,
            "query",
            "--metrics",
            "ending_mrr,new_mrr,churned_mrr,expansion_mrr",
            "--group-by",
            "metric_time",
            "--start-time",
            "2026-03-01",
            "--end-time",
            "2026-08-31",
            "--order",
            "metric_time",
            "--decimals",
            "2",
        ],
    ]
    for i, cmd in enumerate(queries, start=1):
        run(cmd, f"MetricFlow query {i}/{len(queries)}")

    run(
        [python, str(ROOT / "scripts" / "compute_ground_truth.py"), "--check"],
        "Recompute ground truth against stored expected results",
    )
    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
