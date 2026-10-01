"""Measure read-only Redshift fact-versus-mart query performance."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

import redshift_connector

from spark.config import DATA_DIR

FACT_QUERY = """
select pickup_zone, pickup_hour, count(*) as trip_count, sum(fare_amount) as total_revenue
from public_marts.fct_trip_summary
where trip_date >= dateadd(month, -12, current_date)
  and pickup_zone is not null
group by pickup_zone, pickup_hour
"""
MART_QUERY = """
select zone_name, pickup_hour, sum(trip_count) as trip_count, sum(total_revenue) as total_revenue
from public_marts.mart_revenue_by_zone_hour
where trip_date >= dateadd(month, -12, current_date)
group by zone_name, pickup_hour
"""
ROW_COUNT_QUERY = """
select 'fct_trip_summary' as relation_name, count(*) as row_count
from public_marts.fct_trip_summary
where trip_date >= dateadd(month, -12, current_date)
  and pickup_zone is not null
union all
select 'mart_revenue_by_zone_hour' as relation_name, count(*) as row_count
from public_marts.mart_revenue_by_zone_hour
where trip_date >= dateadd(month, -12, current_date)
"""


def _required_env(name: str) -> str:
    """Return a required connection environment variable without logging its value."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _execute(cursor: object, query: str) -> tuple[float, int]:
    """Execute one read-only query and return elapsed seconds plus row count."""
    started = time.perf_counter()
    cursor.execute(query)
    rows = cursor.fetchall()
    return round(time.perf_counter() - started, 3), len(rows)


def benchmark(output_path: Path) -> dict[str, object]:
    """Measure result size and elapsed time for equivalent fact and mart aggregations."""
    connection = redshift_connector.connect(
        host=_required_env("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT", "5439")),
        database=_required_env("REDSHIFT_DB"),
        user=_required_env("REDSHIFT_USER"),
        password=_required_env("REDSHIFT_PASSWORD"),
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(ROW_COUNT_QUERY)
            relation_rows = {name: row_count for name, row_count in cursor.fetchall()}
            fact_seconds, fact_result_rows = _execute(cursor, FACT_QUERY)
            mart_seconds, mart_result_rows = _execute(cursor, MART_QUERY)
    finally:
        connection.close()

    result = {
        "measured_at_utc": datetime.now(UTC).isoformat(),
        "scope": "Last 12 months; non-null pickup zones; trip-zone-hour aggregation.",
        "queries": {
            "fact_aggregation": {
                "source_relation": "public_marts.fct_trip_summary",
                "source_rows": relation_rows["fct_trip_summary"],
                "result_rows": fact_result_rows,
                "elapsed_seconds": fact_seconds,
            },
            "mart_aggregation": {
                "source_relation": "public_marts.mart_revenue_by_zone_hour",
                "source_rows": relation_rows["mart_revenue_by_zone_hour"],
                "result_rows": mart_result_rows,
                "elapsed_seconds": mart_seconds,
            },
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    """Run the benchmark and print the sanitized evidence JSON."""
    parser = argparse.ArgumentParser(
        description="Benchmark equivalent Redshift fact and mart queries."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DATA_DIR / "evidence" / "redshift-query-benchmark.json",
    )
    args = parser.parse_args()
    print(json.dumps(benchmark(args.output), indent=2))


if __name__ == "__main__":
    main()
