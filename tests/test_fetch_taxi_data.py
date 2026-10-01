from datetime import datetime

from spark.etl.fetch_taxi_data import _latest_completed_month


def test_latest_completed_month_returns_previous_month() -> None:
    assert _latest_completed_month(datetime(2026, 10, 1)) == "2026-09"
    assert _latest_completed_month(datetime(2026, 1, 1)) == "2025-12"
