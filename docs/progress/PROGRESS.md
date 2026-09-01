# Project Progress Tracking - NYC Taxi Data Engineering

> Updated: 2026-09-02. Reflects actual codebase after ETLT refactor.

## Current Status

| Attribute | Value |
| --- | --- |
| Current phase | Phase 5 - Production & Orchestration |
| Overall progress | 92% |
| Last updated | 2026-09-02 |
| Last completed | ETLT refactor + BQ pipeline optimization |

## Completed Milestones

| # | Milestone | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Data ingestion | Done | spark/etl/fetch_taxi_data.py |
| 2 | Spark ETL T1 pipeline | Done | transform.py -- clean & standardize only |
| 3 | BigQuery staging load | Done | load_bigquery.py -- yellow_taxi_raw |
| 4 | dbt T2 staging models | Done | stg_trip (outliers+metrics), stg_vendor/payment/rate (hardcoded VALUES), stg_location, stg_time |
| 5 | dbt intermediate & marts | Done | int_trips_with_dimensions, fct_trip_summary, fct_vendor_daily_metrics, mart_revenue_by_zone_hour |
| 6 | Docker Compose Spark + dbt | Done | infrastructure/docker/docker-compose.yml |
| 7 | ETLT architecture refactor | Done | filter_outliers + derived metrics moved from Spark to dbt |
| 8 | BQ upload optimization | Done | coalesce(1) -- 1 file/batch, 1 BQ job (~10s vs ~4min before) |
| 9 | Metadata-driven pipeline | Done | fetched -> processed -> bq_loaded state per file |
| 10 | Utility scripts | Done | scripts/clean_bigquery.py, scripts/reset_metadata_status.py |

## Current Work

| # | Task | Status | Notes |
| --- | --- | --- | --- |
| 1 | Load all 13 months into BQ | In progress | 2025-05 done, running through 2026-05 |
| 2 | dbt full run after BQ load complete | Pending | Blocked on full BQ load |
| 3 | Power BI dashboards | In progress | Planning phase |

## Remaining Work

| # | Task | Priority | Depends on |
| --- | --- | --- | --- |
| 1 | Complete BQ load for all 13 months | High | Docker pipeline |
| 2 | dbt full run + test on complete dataset | High | Full BQ load |
| 3 | Build Power BI dashboards | High | dbt marts in BQ |
| 4 | Document dashboard metrics | Medium | Power BI dashboards |
| 5 | Add Airflow orchestration | Medium | Stable end-to-end workflow |
| 6 | Add CI for Python and dbt tests | Medium | -- |

## Phase Roadmap

```
Phase 1: Data ingestion                    Done
Phase 2: Spark ETL (T1 - clean only)       Done  <- refactored from full ETL
Phase 3: BigQuery staging                  Done  <- replaced PostgreSQL
Phase 4: dbt T2 transform & analytics      Done
  - staging / intermediate / marts         Done
  - ETLT architecture separation           Done
  - BQ upload optimization coalesce(1)     Done
Phase 5: Production orchestration          In progress
  - Complete 13-month BQ load              In progress
  - Power BI dashboards                    In progress
  - Apache Airflow                         Planned
```

## Architecture Notes

### ETLT Pattern
```
Spark T1:   standardize types, fill nulls, dedup, add pickup_date
BQ staging: yellow_taxi_raw -- raw cleaned data, no business logic
dbt T2:     filter outliers, derive trip_duration_min/tip_ratio,
            surrogate keys, generate dim/fact tables
```

### Key Design Decisions
- T1 vs T2 boundary: filter_outliers and derived metrics belong in dbt (business logic, not cleaning)
- Dim tables in dbt: stg_vendor/payment/rate use UNNEST(VALUES) -- no ETL dependency for static data
- coalesce(1): 1 Parquet/batch -> 1 BQ load job. Previous partitionBy pickup_date caused 31 files -> 4 min upload
- Metadata state machine: fetched -> processed -> bq_loaded -> completed, resumes on failure
- Processing order: ascending by filename (oldest first) for chronological BQ APPEND
