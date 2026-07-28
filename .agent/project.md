# Project Context — NYC Taxi Data Engineering

## 1. Business Context

Một công ty taxi muốn xây dựng nền tảng dữ liệu để:
- Theo dõi hiệu suất chuyến đi (trip performance)
- Phân tích doanh thu (revenue analysis)
- Hiểu hành vi tiền tip (tip behavior)
- Đo lường hiệu quả vận hành (operational efficiency)
- Hỗ trợ ra quyết định kinh doanh (data-driven decisions)

**Ngoài phạm vi:** Machine Learning, Prediction models, Real-time streaming.

---

## 2. Dataset

| Thuộc tính | Thông tin |
|---|---|
| Nguồn | NYC Taxi & Limousine Commission (TLC) |
| Format | Parquet |
| Dung lượng | Tối thiểu 10GB |
| Bảng chính | Yellow Taxi Trip Records |
| Pattern | `yellow_tripdata_YYYY-MM.parquet` |

**Nhóm dữ liệu:**
- **Trip:** pickup_datetime, dropoff_datetime, distance
- **Payment:** fare_amount, tip_amount, tax, surcharge, total_amount
- **Location:** PULocationID, DOLocationID (taxi zone IDs)

**Derived columns (ETL thêm vào):**
- `trip_duration_min` — thời gian chuyến đi (phút)
- `tip_ratio` — tỉ lệ tip / fare_amount
- `pickup_date` — ngày pickup (date only, dùng cho partitioning)

---

## 3. Kiến Trúc Pipeline

```
RAW Parquet (data/raw/)
      ↓
  PySpark ETL (spark/etl/)
  ├── extract.py   → đọc parquet files
  ├── validate.py  → data quality checks
  └── transform.py → clean + derive columns
      ↓
Processed Parquet (data/processed/)
      ↓
Google BigQuery Sandbox
  └── FACT_TRIP, DIM_TIME, DIM_LOCATION, ...
      ↓
  dbt Transform
  ├── staging/      → 1-1 với source tables
  ├── intermediate/ → business logic & joins
  └── mart/         → final tables cho dashboard
      ↓
Metabase Dashboard
```

**Orchestration:** Apache Airflow DAGs (airflow/dags/)

---

## 4. Technology Stack

| Layer | Tool | Version | Notes |
|---|---|---|---|
| Language | Python | 3.10+ | snake_case everywhere |
| Processing | PySpark | 3.x | Local `local[*]` mode trên dev |
| Storage | Parquet | — | Columnar, compressed |
| Warehouse | Google BigQuery | Sandbox | Free tier, không cần billing |
| Transform | dbt | dbt-bigquery | 3 layers: staging/intermediate/mart |
| Orchestration | Airflow | 2.x | DAGs trong `airflow/dags/` |
| Visualization | Metabase | — | Free, SQL support |
| Container | Docker | — | Phase 6 — production setup |

---

## 5. Data Model — Star Schema

```
         DIM_TIME
            |
DIM_VENDOR — FACT_TRIP — DIM_LOCATION
            |
       DIM_PAYMENT
            |
         DIM_RATE
```

| Bảng | Loại | Mô tả |
|---|---|---|
| `FACT_TRIP` | Fact | Bảng sự kiện chính |
| `DIM_TIME` | Dimension | Chiều thời gian (giờ, ngày, tháng) |
| `DIM_LOCATION` | Dimension | Taxi zones (pickup/dropoff) |
| `DIM_VENDOR` | Dimension | Vendor taxi (VendorID) |
| `DIM_PAYMENT` | Dimension | Phương thức thanh toán |
| `DIM_RATE` | Dimension | Loại giá (RatecodeID) |

Chi tiết: `docs/data_model.md`

---

## 6. Environment — Windows Dev Setup

```python
# spark/config.py — LUÔN import từ đây
JAVA_HOME   = r"C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot"
HADOOP_HOME = str(ROOT_DIR / "hadoop")  # winutils.exe ở đây
SPARK_MASTER = "local[*]"
```

**Sensitive configs** (dùng `.env` hoặc environment variables):
- `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD`
- GCP Service Account JSON key → `warehouse/credentials/` (gitignored)

---

## 7. Phase Hiện Tại

**Phase 2: Spark ETL — ⏳ In Progress**

Xem chi tiết roadmap: `docs/phases.md`
Xem workflow hiện tại: `.agent/workflow.md`
