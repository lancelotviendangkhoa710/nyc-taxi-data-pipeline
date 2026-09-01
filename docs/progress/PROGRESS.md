# Project Progress Tracking - NYC Taxi Data Engineering

> Updated: 2026-08-24. This status reflects the source code and repository artefacts currently present; it does not replace an end-to-end deployment validation.

## Current Status

| Attribute | Value |
| --- | --- |
| Current phase | Phase 4 - dbt & analytics |
| Overall progress | 90% |
| Last updated | 2026-08-24 |
| Last completed | End-to-end validation and dbt test verification |

## Completed Milestones

| # | Milestone | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Data ingestion and Spark configuration | Done | `spark/config.py`, `spark/etl/fetch_taxi_data.py` |
| 2 | Spark ETL pipeline | Done | Extract, validate, transform, load, and orchestration modules in `spark/etl/` |
| 3 | Processed Parquet output | Done | Date-partitioned output under `data/processed/yellow_taxi/` |
| 4 | PostgreSQL star schema and warehouse loader | Done | DDL in `infrastructure/warehouse/ddl/` and `spark/etl/load_warehouse.py` |
| 5 | Docker development environment | Done | Compose files, PostgreSQL initialization, Spark and dbt entrypoints in `infrastructure/docker/` |
| 6 | dbt transformation layers | Done | Staging, intermediate, and mart models in `dbt/models/` |
| 7 | Python pipeline tests | Done | `tests/test_pipeline.py` |
| 8 | Adaptive Spark write partition sizing | Done | `spark/etl/load.py`, `docs/partitioning_strategy.md` |
| 9 | Spark ETL benchmark harness and regression tests | Done | `spark/benchmark/etl_benchmark.py`, `tests/test_etl_benchmark.py`, `benchmarks/README.md`, `benchmarks/results/etl_benchmark.csv` |
| 10 | End-to-end validation and dbt test verification | Done | `scripts/validate_end_to_end.ps1`, `scripts/validate_end_to_end.py`, Docker compose validation run |

## Current Work

| # | Task | Status | Notes |
| --- | --- | --- | --- |
| 1 | Validate complete pipeline in Docker | Done | Spark ETL, PostgreSQL load, dbt run, and dbt test now run successfully through the validation script. |
| 2 | Verify dbt data-quality results | Done | Fresh `dbt test` run completed successfully as part of end-to-end validation. |
| 3 | Bootstrap Power BI analytics layer | In progress | Power BI dashboard planning doc is in place; next step is to create the actual report collection. |

## Remaining Work

| # | Task | Priority | Depends on |
| --- | --- | --- | --- |
| 1 | Build Power BI dashboards | High | Validated warehouse and dbt marts |
| 2 | Document dashboard metrics and refresh process | Medium | Power BI dashboards |
| 3 | Add production scheduling/orchestration (for example Airflow) | Medium | Stable end-to-end workflow |
| 4 | Add CI for Python and dbt tests | Medium | Repeatable test commands |

## Phase Roadmap

```text
Phase 1: Data ingestion                 Done
Phase 2: Spark ETL                      Done
Phase 3: PostgreSQL warehouse           Done
Phase 4: dbt & analytics                Done
  - dbt staging/intermediate/marts      Done
  - Spark benchmark harness             Done
  - End-to-end validation                Done
  - Power BI dashboards                 In progress
Phase 5: Production orchestration       Planned
```

## Notes

- The full pipeline writes processed Parquet locally and loads the warehouse through PostgreSQL JDBC.
- Docker entrypoints validate dependencies before running the Spark ETL or dbt workflow.
- `load_warehouse.py` contains PostgreSQL loading logic, although one pipeline log label still refers to BigQuery and should be corrected in a later cleanup.
