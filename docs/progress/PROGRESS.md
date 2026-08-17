# Project Progress Tracking — NYC Taxi Data Engineering

> Updated: 2026-08-17. This status reflects the source code and repository artefacts currently present; it does not replace an end-to-end deployment validation.

## Current Status

| Attribute | Value |
|---|---|
| Current phase | Phase 4 — dbt & analytics |
| Overall progress | 80% |
| Last updated | 2026-08-17 |
| Last completed | Adaptive Spark write partition sizing |

## Completed Milestones

| # | Milestone | Status | Evidence |
|---|---|---|---|
| 1 | Data ingestion and Spark configuration | Done | `spark/config.py`, `spark/etl/fetch_taxi_data.py` |
| 2 | Spark ETL pipeline | Done | Extract, validate, transform, load, and orchestration modules in `spark/etl/` |
| 3 | Processed Parquet output | Done | Date-partitioned output under `data/processed/yellow_taxi/` |
| 4 | PostgreSQL star schema and warehouse loader | Done | DDL in `infrastructure/warehouse/ddl/` and `spark/etl/load_warehouse.py` |
| 5 | Docker development environment | Done | Compose files, PostgreSQL initialization, Spark and dbt entrypoints in `infrastructure/docker/` |
| 6 | dbt transformation layers | Done | Staging, intermediate, and mart models in `dbt/models/` |
| 7 | Python pipeline tests | Done | `tests/test_pipeline.py` |
| 8 | Adaptive Spark write partition sizing | Done | `spark/etl/load.py`, `docs/partitioning_strategy.md` |

## Current Work

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | Validate complete pipeline in Docker | Pending | Run Spark ETL, PostgreSQL load, dbt run, and dbt test as one reproducible workflow. |
| 2 | Verify dbt data-quality results | Pending | Existing dbt artefacts indicate prior runs; record a fresh successful run. |

## Remaining Work

| # | Task | Priority | Depends on |
|---|---|---|---|
| 1 | Build Metabase dashboards | High | Validated warehouse and dbt marts |
| 2 | Document dashboard metrics and refresh process | Medium | Metabase dashboards |
| 3 | Add production scheduling/orchestration (for example Airflow) | Medium | Stable end-to-end workflow |
| 4 | Add CI for Python and dbt tests | Medium | Repeatable test commands |

## Phase Roadmap

```text
Phase 1: Data ingestion                 Done
Phase 2: Spark ETL                      Done
Phase 3: PostgreSQL warehouse           Done
Phase 4: dbt & analytics                In progress
  ├─ dbt staging/intermediate/marts     Done
  ├─ End-to-end validation              Pending
  └─ Metabase dashboards                Pending
Phase 5: Production orchestration       Planned
```

## Notes

- The full pipeline writes processed Parquet locally and loads the warehouse through PostgreSQL JDBC.
- Docker entrypoints validate dependencies before running the Spark ETL or dbt workflow.
- `load_warehouse.py` contains PostgreSQL loading logic, although one pipeline log label still refers to BigQuery and should be corrected in a later cleanup.
