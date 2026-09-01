# NYC Taxi Data Engineering Pipeline

End-to-end batch ETLT pipeline for NYC TLC Yellow Taxi trip data --
raw Parquet -> Spark T1 (clean & standardize) -> BigQuery staging -> dbt T2 (transform) -> Power BI.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Spark](https://img.shields.io/badge/Apache%20Spark-3.5.0-E25A1C?logo=apachespark&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-GCP-4285F4?logo=googlecloud&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-1.8.0-FF694B?logo=dbt&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-26.x-2496ED?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## Overview

Processes NYC TLC Yellow Taxi trip records (2025-05 to present) through a multi-stage ETLT batch pipeline.

**ETLT pattern:**
- **T1 (Spark)** -- type casting, null fill, dedup, add `pickup_date`. No business logic.
- **T2 (dbt/BigQuery)** -- filter outliers, derive metrics (`trip_duration_min`, `tip_ratio`), build dim/fact star schema.

---

## Architecture

```
[NYC TLC - Public HTTP]
        |
[fetch_taxi_data.py]  ->  data/raw/yellow/
        |
[Apache Spark 3.5.0 -- T1 Transform]
  standardize_data_types()
  handle_null_values()
  remove_duplicates()
  add_pickup_date()
        |  coalesce(1) -> 1 Parquet per source_month
        |
[BigQuery -- nyc_taxi_raw.yellow_taxi_raw]
        |
[dbt -- T2 Transform]
  staging -> intermediate -> marts
        |
[Power BI]
```

---

## Key Highlights

- Processes **13 months** of data (2025-05 to 2026-05)
- **ETLT architecture** -- clean separation between Spark T1 and dbt T2
- `coalesce(1)` write strategy -- 1 file/batch -> 1 BQ load job (~10s vs ~4min before)
- Dim tables (`dim_vendor`, `dim_payment`, `dim_rate`) hardcoded in dbt via `UNNEST(VALUES)` -- no ETL dependency
- `dim_location` from `taxi_zone_lookup` dbt seed
- `dim_time` generated entirely in warehouse from timestamps
- Metadata-driven pipeline with per-file status tracking and retry logic

---

## Tech Stack

| Technology | Version | Purpose |
| :--- | :---: | :--- |
| Python | `3.12` | Core ETL language |
| Apache Spark (PySpark) | `3.5.0` | T1: distributed data cleaning |
| Google BigQuery | GCP | Cloud data warehouse |
| dbt-bigquery | `1.8.x` | T2: SQL transformation layer |
| Docker Compose | `26.x` | Spark & dbt containerization |
| Power BI Desktop | `2.x` | Analytics & reporting |

---

## Project Structure

```
NYC_Taxi_Project/
+-- spark/
|   +-- config.py                  # Paths, Spark/BQ config, SELECTED_COLUMNS
|   +-- etl/
|       +-- fetch_taxi_data.py     # Download raw Parquet from NYC TLC
|       +-- extract.py             # Spark read + column pruning
|       +-- validate.py            # Schema & empty-frame checks
|       +-- transform.py           # T1: standardize, null-fill, dedup, pickup_date
|       +-- load.py                # coalesce(1) -> local Parquet
|       +-- load_bigquery.py       # Upload Parquet -> BigQuery
|       +-- metadata.py            # Per-file status tracking
|       +-- pipeline.py            # Orchestrates full ETLT flow
|       +-- main.py
+-- dbt/
|   +-- seeds/taxi_zone_lookup.csv
|   +-- models/
|       +-- staging/               # stg_trip, stg_vendor, stg_payment, stg_rate, stg_location, stg_time
|       +-- intermediate/          # int_trips_with_dimensions, int_trip_metrics_*
|       +-- marts/                 # fct_trip_summary, fct_vendor_daily_metrics, mart_revenue_by_zone_hour
+-- infrastructure/docker/         # Dockerfile.spark, Dockerfile.dbt, docker-compose.yml
+-- scripts/
|   +-- clean_bigquery.py          # Drop all BQ tables
|   +-- reset_metadata_status.py   # Reset ETL metadata for re-run
+-- data/
|   +-- raw/yellow/                # Source Parquet files
|   +-- processed/yellow_taxi/     # source_month=YYYY-MM/ (1 file each)
|   +-- metadata/etl_metadata.json # Pipeline state
+-- tests/
+-- docs/
+-- README.md
```

---

## Quick Start

### Prerequisites

- Python 3.12+, Java 21, Docker 26+
- GCP Service Account with BigQuery write permission
- Place `gcp_service_account.json` in project root

### 1. Clone & Setup

```bash
git clone https://github.com/lancelotviendangkhoa710/nyc-taxi-de-project.git
cd nyc-taxi-de-project
python -m venv .venv && .venv\Scripts\activate
pip install -e .
```

### 2. Configure Environment

```bash
cp .env.example .env
# Set: GCP_PROJECT_ID, GCP_DATASET_RAW, GCP_KEYFILE_PATH
```

### 3. Fetch Raw Data

```bash
python -m spark.etl.fetch_taxi_data
```

### 4. Run ETL Pipeline (Docker)

```bash
cd infrastructure/docker
docker compose -f docker-compose.yml build spark-etl

# One batch at a time (picks next unprocessed file)
docker compose -f docker-compose.yml run --rm spark-etl
```

### 5. Run dbt

```bash
docker compose -f docker-compose.yml run --rm dbt
# or locally:
cd dbt && dbt run && dbt test
```

### 6. Utility Scripts

```bash
# Full BQ reset
python scripts/clean_bigquery.py

# Reset metadata to re-process all files
python scripts/reset_metadata_status.py
```

---

## Performance

| Batch size | Spark T1 | BQ upload | Total/file |
| :--- | :---: | :---: | :---: |
| ~70 MB/month | ~30s | ~10-15s | **~1.5 min** |

coalesce(1): 1 file/batch -> 1 BQ load job. Previous partitionBy approach: 31 files -> ~4 min upload.

---

## Project Status

| Component | Status |
| :--- | :---: |
| Data fetch (2025-05 to 2026-05) | Done |
| Spark ETL T1 (clean & standardize) | Done |
| BigQuery staging load | Done |
| dbt T2 staging / intermediate / marts | Done |
| Docker Compose (Spark + dbt) | Done |
| Power BI Dashboards | Planned |
| Apache Airflow Orchestration | Planned |

---

## References

- [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Google BigQuery Documentation](https://cloud.google.com/bigquery/docs)
