# Kiến trúc — Nền tảng Kỹ thuật Dữ liệu Taxi NYC

## Tổng quan

Nền tảng được thiết kế theo mô hình **Batch Processing** với các lớp tách biệt rõ ràng (mô hình Lakehouse-lite).

---

## Luồng dữ liệu

```
┌─────────────────────────────────────────────────────────┐
│                    NGUỒN DỮ LIỆU                        │
│         Tệp Parquet NYC TLC (Taxi Vàng)                 │
└─────────────────┬───────────────────────────────────────┘
                  │  Tải xuống / Trích xuất
                  ▼
┌─────────────────────────────────────────────────────────┐
│                   LỚP THÔ (RAW)                         │
│              data/raw/*.parquet                         │
│         (Không chỉnh sửa, giữ nguyên gốc)              │
└─────────────────┬───────────────────────────────────────┘
                  │  PySpark ETL (spark/etl/)
                  ▼
┌─────────────────────────────────────────────────────────┐
│                LỚP ĐÃ XỬ LÝ (PROCESSED)                 │
│           data/processed/*.parquet                      │
│     (Đã làm sạch, xác thực, làm giàu với cột mới)      │
└─────────────────┬───────────────────────────────────────┘
                  │  PySpark Write (JDBC)
                  ▼
┌─────────────────────────────────────────────────────────┐
│              LỚP KHO DỮ LIỆU (WAREHOUSE)                │
│           PostgreSQL                                    │
│    FACT_TRIP + DIM_* (Star Schema)                      │
└─────────────────┬───────────────────────────────────────┘
                  │  dbt run / dbt test
                  ▼
┌─────────────────────────────────────────────────────────┐
│              LỚP CHUYỂN ĐỔI (TRANSFORM)                 │
│                    dbt                                  │
│   staging → intermediate → mart                        │
└─────────────────┬───────────────────────────────────────┘
                  │  Kết nối PostgreSQL
                  ▼
┌─────────────────────────────────────────────────────────┐
│             LỚP TRÌNH BÀY (PRESENTATION)                │
│                  Metabase                               │
│    Bảng điều khiển Doanh thu / Chuyến đi / Tiền boa     │
└─────────────────────────────────────────────────────────┘
```

---

## Điều phối (Airflow DAG)

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

Tất cả các bước trên được lập lịch và giám sát bởi **Apache Airflow**.

---

## Triển khai

| Môi trường | Mô tả |
| --- | --- |
| **Hybrid (hiện tại)** | PySpark `local[*]`, PostgreSQL, dbt local |
| **Future: Docker** | Toàn bộ local stack (Airflow, Metabase, dbt) chạy bằng `docker compose up` |

---

## Thư mục liên quan

| Lớp | Đường dẫn |
| --- | --- |
| Dữ liệu thô | `data/raw/` |
| Dữ liệu đã xử lý | `data/processed/` |
| Spark ETL | `spark/etl/` |
| Lược đồ kho dữ liệu | `warehouse/` |
| Mô hình dbt | `dbt/` |
| Airflow DAGs | `airflow/dags/` |
| Cấu hình Docker | `docker/` |
