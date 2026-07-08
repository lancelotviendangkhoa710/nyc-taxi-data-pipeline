# Architecture — NYC Taxi Data Engineering Platform

## Overview

Nền tảng được thiết kế theo mô hình **Batch Processing** với các lớp tách biệt rõ ràng (Lakehouse-lite pattern).

---

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                         │
│         NYC TLC Parquet Files (Yellow Taxi)             │
└─────────────────┬───────────────────────────────────────┘
                  │  Download / Extract
                  ▼
┌─────────────────────────────────────────────────────────┐
│                   RAW LAYER                             │
│              data/raw/*.parquet                         │
│         (Không chỉnh sửa, giữ nguyên gốc)              │
└─────────────────┬───────────────────────────────────────┘
                  │  PySpark ETL (spark/etl/)
                  ▼
┌─────────────────────────────────────────────────────────┐
│                PROCESSED LAYER                          │
│           data/processed/*.parquet                      │
│     (Cleaned, validated, enriched với new columns)      │
└─────────────────┬───────────────────────────────────────┘
                  │  PySpark Write (GCS / BigQuery API)
                  ▼
┌─────────────────────────────────────────────────────────┐
│              WAREHOUSE LAYER                            │
│           Google BigQuery (Sandbox)                     │
│    FACT_TRIP + DIM_* (Star Schema)                      │
└─────────────────┬───────────────────────────────────────┘
                  │  dbt run / dbt test
                  ▼
┌─────────────────────────────────────────────────────────┐
│              TRANSFORM LAYER                            │
│                    dbt                                  │
│   staging → intermediate → mart                        │
└─────────────────┬───────────────────────────────────────┘
                  │  Google BigQuery Connection
                  ▼
┌─────────────────────────────────────────────────────────┐
│             PRESENTATION LAYER                          │
│                  Metabase                               │
│    Revenue / Trips / Tips / Zone Analysis Dashboards    │
└─────────────────────────────────────────────────────────┘
```

---

## Orchestration (Airflow DAG)

```
download_data
     ↓
run_spark_etl
     ↓
load_to_postgres
     ↓
run_dbt_models
     ↓
refresh_dashboard
```

Tất cả các bước trên được schedule và monitor bởi **Apache Airflow**.

---

## Deployment

| Môi trường | Mô tả |
|---|---|
| **Hybrid (hiện tại)** | PySpark `local[*]`, BigQuery Sandbox (Cloud), dbt local |
| **Future: Docker** | Toàn bộ local stack (Airflow, Metabase, dbt) chạy bằng `docker compose up` kết nối tới BigQuery |

---

## Thư mục liên quan

| Layer | Path |
|---|---|
| Raw Data | `data/raw/` |
| Processed Data | `data/processed/` |
| Spark ETL | `spark/etl/` |
| Warehouse Schema | `warehouse/` |
| dbt Models | `dbt/` |
| Airflow DAGs | `airflow/dags/` |
| Docker Config | `docker/` |
