# Kiến trúc — NYC Taxi Data Engineering Platform

## Tổng quan

Nền tảng xử lý batch hàng tháng theo mô hình **Lakehouse-lite**. Metadata manifest là source of truth duy nhất. Raw và processed là staging tạm có thể dọn sau khi BigQuery và dbt xác nhận thành công.

---

## Luồng dữ liệu

```
NYC TLC (Parquet hàng tháng, trễ 2-3 tháng)
  │  fetch_taxi_data.py — bỏ qua month đã completed theo manifest
  ▼
data/raw/yellow/yellow_tripdata_YYYY-MM.parquet
  │  metadata: fetched
  │  Spark: validate + transform + thêm cột source_month
  ▼
data/processed/yellow_taxi/source_month=YYYY-MM/   [staging tạm]
  │  metadata: processed
  │  BigQueryLoader.load_batch(source_month)
  │    DELETE yellow_taxi_raw WHERE source_month = YYYY-MM
  │    WRITE_APPEND parquet batch
  ▼
BigQuery: nyc_taxi_raw.yellow_taxi_raw
  │  metadata: bq_loaded
  │  dbt run
  │  dbt test
  ▼
BigQuery: staging / intermediate / marts
  │  metadata: dbt_tested
  │  finalize.py — chỉ chạy sau dbt test pass
  │    xóa raw file + processed/source_month=YYYY-MM khi hết retention
  │  metadata: completed
  ▼
data/metadata/etl_metadata.json   [manifest — KHÔNG xóa]
  │
  ▼
Power BI kết nối BigQuery marts
```

---

## Vòng đời status batch

| Status | Ý nghĩa | Raw | Processed | Retry lần tiếp |
|---|---|---|---|---|
| `fetched` | Raw đã tải về | Có | Chưa | Spark process |
| `processed` | Parquet batch đã ghi | Có | Có | BQ load, không Spark lại |
| `bq_loaded` | BQ load thành công | Có | Có | Chờ dbt run + test |
| `dbt_tested` | dbt test pass | Có | Có | Cleanup sau retention |
| `completed` | Artifact đã dọn | Đã xóa | Đã xóa | Skip toàn bộ |
| `failed` | Bước gần nhất lỗi | Tùy bước | Tùy bước | Retry từ bước đó |

Manifest giữ record kể cả sau cleanup. Record `completed` tránh fetch/process lại khi raw đã bị xóa.

---

## Điều phối Docker

```
docker compose -f infrastructure/docker/docker-compose.yml up --build

[spark-etl]
  entrypoint-spark.sh
    python spark/etl/main.py
      fetch_data()        → data/raw/
      ETL pipeline        → data/processed/source_month=YYYY-MM/
      load_batch() → BQ  → yellow_taxi_raw

[dbt]  depends_on: spark-etl completed_successfully
  entrypoint-dbt.sh
    dbt debug
    dbt deps
    dbt run              → staging / intermediate / marts
    dbt test             → data quality checks
    python finalize.py   → mark dbt_tested, cleanup retention
```

`set -e` đảm bảo: dbt test fail thì finalize không chạy, raw/processed giữ nguyên để retry.

---

## Cấu hình môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `ETL_LOCAL_RETENTION_DAYS` | `7` | Ngày giữ raw/processed sau `dbt_tested` |
| `ETL_TEST_ROW_LIMIT` | unset | Giới hạn row test thủ công; batch này không cleanup |
| `GCP_PROJECT_ID` | `nyc-taxi-data-pipeline-507015` | GCP project |
| `GCP_DATASET_RAW` | `nyc_taxi_raw` | BigQuery dataset |
| `GCP_KEYFILE_PATH` | `gcp_service_account.json` | Service account key |
| `ETL_PARTITION_PROFILE` | `standard` | `heavy` tăng target file size lên 512 MiB |

---

## Thư mục

| Vai trò | Đường dẫn |
|---|---|
| Manifest vĩnh viễn | `data/metadata/etl_metadata.json` |
| Raw staging | `data/raw/yellow/yellow_tripdata_YYYY-MM.parquet` |
| Processed staging | `data/processed/yellow_taxi/source_month=YYYY-MM/` |
| Spark ETL modules | `spark/etl/` |
| Config tập trung | `spark/config.py` |
| dbt models | `dbt/models/` |
| Docker | `infrastructure/docker/` |
| Tests | `tests/` |

Chi tiết vòng đời, retention, backfill: [`docs/etl_lifecycle.md`](etl_lifecycle.md)