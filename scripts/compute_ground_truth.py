#!/usr/bin/env python3
"""Calculate or verify Oakwell ground-truth answers from DuckDB."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ground_truth_cases import CASES  # noqa: E402

WAREHOUSE = ROOT / "data" / "oakwell.duckdb"
JSON_PATH = ROOT / "validation" / "ground_truth.json"
MD_PATH = ROOT / "validation" / "ground_truth.md"


def jsonable(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def run_case(con, case: dict):
    rows = con.execute(case["sql"]).fetchall()
    columns = [d[0] for d in con.description]
    if case["result_type"] == "scalar":
        value = jsonable(rows[0][0]) if rows else None
        if isinstance(value, float):
            value = round(value, 4 if abs(value) < 10 else 2)
        return {"value": value}
    table = []
    for row in rows:
        table.append({col: jsonable(val) for col, val in zip(columns, row)})
    return {"rows": table}


def values_close(expected, actual, tolerance: float) -> bool:
    if expected is None or actual is None:
        return expected == actual
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(expected) - float(actual)) <= tolerance
    return expected == actual


def tables_close(expected_rows, actual_rows, tolerance: float) -> bool:
    if len(expected_rows) != len(actual_rows):
        return False
    for exp, act in zip(expected_rows, actual_rows):
        if set(exp) != set(act):
            return False
        for key in exp:
            if not values_close(exp[key], act[key], tolerance):
                return False
    return True


def compute_all(con) -> list[dict]:
    results = []
    for case in CASES:
        computed = run_case(con, case)
        results.append(
            {
                "id": case["id"],
                "question": case["question"],
                "concept": case["concept"],
                "time_period": case["time_period"],
                "dimensions": case["dimensions"],
                "filters": case["filters"],
                "result_type": case["result_type"],
                "tolerance": case["tolerance"],
                "method": "Independent DuckDB SQL against the built marts.",
                "sql": " ".join(case["sql"].split()),
                "mf": case.get("mf"),
                "expected": computed,
            }
        )
    return results


def write_markdown(results: list[dict]) -> str:
    lines = [
        "# Oakwell ground truth",
        "",
        "Expected answers calculated from the DuckDB warehouse after `dbt build`.",
        "Do not edit numbers by hand — regenerate with "
        "`python scripts/compute_ground_truth.py --write`.",
        "",
        f"Cases: **{len(results)}**. As-of date: **2026-08-31**.",
        "",
    ]
    for row in results:
        lines.append(f"## {row['id']} — {row['question']}")
        lines.append("")
        lines.append(f"- Concept: `{row['concept']}`")
        period = row["time_period"]
        lines.append(
            f"- Time period: {period['start']} to {period['end']} ({period['grain']})"
        )
        if row["dimensions"]:
            lines.append("- Dimensions: " + ", ".join(f"`{d}`" for d in row["dimensions"]))
        if row["filters"]:
            filt = "; ".join(
                f"{f['dimension']} {f['op']} {f['value']}" for f in row["filters"]
            )
            lines.append(f"- Filters: {filt}")
        lines.append(f"- Method: {row['method']}")
        expected = row["expected"]
        if "value" in expected:
            lines.append(f"- Expected result: `{expected['value']}`")
        else:
            lines.append("- Expected result:")
            lines.append("")
            if expected["rows"]:
                headers = list(expected["rows"][0].keys())
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join("---" for _ in headers) + " |")
                for rec in expected["rows"]:
                    lines.append("| " + " | ".join(str(rec[h]) for h in headers) + " |")
            lines.append("")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write JSON and Markdown artifacts")
    parser.add_argument("--check", action="store_true", help="Compare warehouse to stored JSON")
    parser.add_argument("--warehouse", type=Path, default=WAREHOUSE)
    args = parser.parse_args()

    if not args.warehouse.exists():
        print(f"Warehouse not found: {args.warehouse}. Run dbt build first.", file=sys.stderr)
        return 2

    import duckdb

    con = duckdb.connect(str(args.warehouse), read_only=True)
    computed = compute_all(con)
    con.close()

    if args.write:
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        JSON_PATH.write_text(json.dumps(computed, indent=2, sort_keys=False) + "\n")
        MD_PATH.write_text(write_markdown(computed))
        print(f"Wrote {len(computed)} cases to {JSON_PATH} and {MD_PATH}")
        return 0

    if args.check:
        if not JSON_PATH.exists():
            print(f"Missing {JSON_PATH}. Run with --write first.", file=sys.stderr)
            return 2
        stored = json.loads(JSON_PATH.read_text())
        stored_by_id = {c["id"]: c for c in stored}
        failures = []
        for case, current in zip(CASES, computed):
            previous = stored_by_id.get(case["id"])
            if previous is None:
                failures.append(f"{case['id']} missing from stored ground truth")
                continue
            exp = previous["expected"]
            got = current["expected"]
            tol = case["tolerance"]
            ok = (
                values_close(exp.get("value"), got.get("value"), tol)
                if case["result_type"] == "scalar"
                else tables_close(exp.get("rows", []), got.get("rows", []), tol)
            )
            if not ok:
                failures.append(f"{case['id']}: expected {exp} got {got}")
        if failures:
            print("Ground truth check failed:")
            for f in failures:
                print("  -", f)
            return 1
        print(f"Ground truth check passed for {len(computed)} cases.")
        return 0

    for row in computed:
        print(f"{row['id']}: {row['expected']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
