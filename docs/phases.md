# Phases & Roadmap — NYC Taxi Data Engineering Project

## Overview

| Phase | Tên | Trạng thái | Deliverables |
|---|---|---|---|
| **1** | Data Understanding | ✅ Completed | schema, profiling, dictionary |
| **2** | Spark ETL | ⏳ Planned | etl scripts, processed data |
| **3** | Warehouse | ⏳ Planned | PostgreSQL schema, loaded data |
| **4** | dbt Transform | ⏳ Planned | dbt models, tests, docs |
| **5** | Dashboard | ⏳ Planned | Metabase dashboards |
| **6** | Portfolio | ⏳ Planned | README, Docker, demo |

---

## Phase 1: Data Understanding ✅

**Mục tiêu:** Hiểu toàn bộ dataset trước khi xây dựng pipeline.

### Tasks

- [x] Setup môi trường (PySpark, Java, Hadoop winutils)
- [x] Đọc file parquet bằng PySpark
- [x] Explore schema (`printSchema()`)
- [x] Xem sample data (`show()`)
- [x] Thống kê cơ bản (`describe()`)
- [x] Phân tích data quality (null, outlier, duplicate)
- [x] Xác định dimensions và facts
- [x] Viết `schema_report.md`
- [x] Viết `data_dictionary.md`
- [x] Viết `profiling_report.md`

### Deliverables

| File | Mô tả |
|---|---|
| `docs/schema_report.md` | Schema của dataset, kiểu dữ liệu từng cột |
| `docs/data_dictionary.md` | Giải thích ý nghĩa từng cột |
| `docs/profiling_report.md` | Thống kê, null%, outliers, phân phối |

### Notebook

`notebooks/01_data_understanding.ipynb`

---

## Phase 2: Spark ETL ⏳

**Mục tiêu:** Xây dựng ETL pipeline để clean và transform data.

### Tasks

- [ ] Tạo `spark/config.py`
- [ ] Tạo `spark/utils/logger.py`
- [ ] Tạo `spark/etl/extract.py` — đọc parquet
- [ ] Tạo `spark/etl/validate.py` — kiểm tra chất lượng
- [ ] Tạo `spark/etl/transform.py` — clean + derive columns
- [ ] Tạo `spark/etl/load.py` — ghi ra processed parquet
- [ ] Tạo `spark/etl/main.py` — orchestrate ETL job
- [ ] Xử lý null values
- [ ] Lọc outlier (trip_distance, fare_amount)
- [ ] Thêm derived columns (duration, tip_ratio, pickup_date)
- [ ] Viết processed parquet vào `data/processed/`

### Deliverables

| File | Mô tả |
|---|---|
| `spark/etl/main.py` | Entry point ETL job |
| `spark/etl/transform.py` | Transform logic |
| `data/processed/` | Parquet đã clean |

---

## Phase 3: Warehouse ⏳

**Mục tiêu:** Setup Google BigQuery Sandbox và load dữ liệu từ Spark lên BigQuery theo Star Schema.

### Tasks

- [ ] Tạo GCP Account và kích hoạt BigQuery Sandbox (miễn phí)
- [ ] Tạo GCP Project `nyc-taxi-dw` và Dataset tương ứng
- [ ] Cấu hình GCP Service Account & tải file JSON key để xác thực
- [ ] Viết Schema/DDL cho FACT_TRIP và các bảng chiều (DIM_*) trên BigQuery
- [ ] Cấu hình Spark BigQuery Connector trong PySpark job
- [ ] Viết `spark/etl/load_warehouse.py` — ghi dữ liệu từ processed parquet lên BigQuery tables
- [ ] Populate dimension tables và load Fact table

### Deliverables

| File | Mô tả |
|---|---|
| `warehouse/schemas/` | DDL schema và định nghĩa các bảng trên BigQuery |
| `warehouse/credentials/` | Hướng dẫn cấu hình Service Account JSON key (được ignore trên git) |

---

## Phase 4: dbt Transform ⏳

**Mục tiêu:** Transform dữ liệu trong BigQuery bằng dbt với 3 layers.

### dbt Layers

```
staging/        # 1-1 với source tables, rename, cast types
intermediate/   # Business logic, joins
mart/           # Final tables (Marts) cho dashboard
```

### Tasks

- [ ] Cài đặt dbt với adapter `dbt-bigquery`
- [ ] Init dbt project và cấu hình `profiles.yml` kết nối với BigQuery Sandbox qua JSON key
- [ ] Viết staging models tương ứng các bảng nguồn trong BigQuery
- [ ] Viết intermediate models thực hiện kết hợp dữ liệu (joins, business logic)
- [ ] Viết mart models (mart_revenue, mart_trips, mart_tips, mart_zones)
- [ ] Viết dbt tests (not_null, unique, relationships)
- [ ] Generate dbt docs để theo dõi lineage chart trên BigQuery

---

## Phase 5: Dashboard ⏳

**Mục tiêu:** Trực quan hóa dữ liệu bằng Metabase.

### Dashboards

| Dashboard | Metrics |
|---|---|
| Revenue | Total revenue theo ngày/tháng/zone |
| Trips | Số chuyến đi, peak hours, distance |
| Tips | Tip ratio, payment type distribution |
| Zone Analysis | Pickup/dropoff hotspots |

---

## Phase 6: Portfolio ⏳

**Mục tiêu:** Đóng gói dự án thành portfolio hoàn chỉnh.

### Tasks

- [ ] Viết `README.md` đầy đủ (architecture diagram, setup guide)
- [ ] Tạo `docker/docker-compose.yml` cho toàn bộ stack
- [ ] Test chạy toàn bộ bằng Docker từ đầu
- [ ] Chụp screenshots dashboard
- [ ] Upload lên GitHub với tags phù hợp
- [ ] Viết blog post / LinkedIn post (optional)
