import json

from spark.benchmark import redshift_query_benchmark as benchmark_module


class FakeCursor:
    def __init__(self) -> None:
        self.query = ""

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def execute(self, query: str) -> None:
        self.query = query

    def fetchall(self) -> list[tuple[str, int]] | list[tuple[str, int, int, int]]:
        if "union all" in self.query.lower():
            return [("fct_trip_summary", 100), ("mart_revenue_by_zone_hour", 24)]
        return [("zone", 10, 20, 30)]


class FakeConnection:
    def cursor(self) -> FakeCursor:
        return FakeCursor()

    def close(self) -> None:
        return None


def test_benchmark_writes_sanitized_result(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("REDSHIFT_HOST", "warehouse.example")
    monkeypatch.setenv("REDSHIFT_DB", "dev")
    monkeypatch.setenv("REDSHIFT_USER", "tester")
    monkeypatch.setenv("REDSHIFT_PASSWORD", "not-published")
    monkeypatch.setattr(
        benchmark_module.redshift_connector, "connect", lambda **_kwargs: FakeConnection()
    )

    output_path = tmp_path / "evidence" / "redshift-query-benchmark.json"
    result = benchmark_module.benchmark(output_path)

    assert result["queries"]["fact_aggregation"]["source_rows"] == 100
    assert result["queries"]["mart_aggregation"]["source_rows"] == 24
    assert "Last 12 months" in result["scope"]
    assert json.loads(output_path.read_text(encoding="utf-8")) == result
