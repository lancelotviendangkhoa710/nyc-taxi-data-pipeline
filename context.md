# NYC Taxi — Project Context

> **Mục đích file này:** Context tập trung cho toàn bộ dự án. Đọc file này trước khi bắt đầu bất kỳ tác vụ nào.
> Các sub-context chi tiết nằm trong thư mục `docs/`.

---

## 1. Mục Tiêu Dự Án

Xây dựng nền tảng Data Engineering end-to-end sử dụng NYC Taxi Trip Record Data.

| Mục tiêu | Mô tả |
|---|---|
| Học thực tế | Áp dụng quy trình DE thực tế |
| Portfolio | Dự án nổi bật cho CV |
| Kỹ năng | ETL + Warehouse + Analytics |
| Định hướng | Chuẩn bị cho internship/job Data Engineer |

**KHÔNG thuộc phạm vi:**
- Machine Learning / Deep Learning
- Prediction models

---

## 2. Business Scenario

Một công ty taxi muốn xây dựng nền tảng dữ liệu để:

- Theo dõi hiệu suất chuyến đi
- Phân tích doanh thu
- Hiểu hành vi tiền tip
- Đo lường hiệu quả vận hành
- Hỗ trợ ra quyết định kinh doanh

---

## 3. Dataset

| Thuộc tính | Thông tin |
|---|---|
| Nguồn | NYC Taxi & Limousine Commission (TLC) |
| Format | Parquet |
| Dung lượng | Tối thiểu 10GB |
| Phạm vi | Nhiều tháng (historical) |
| Bảng chính | Yellow Taxi Trip Records |

**Nhóm dữ liệu:**
- **Trip:** pickup, dropoff, distance
- **Payment:** fare, tip, tax, surcharge
- **Location:** pickup zone, dropoff zone

---

## 4. Kiến Trúc Hệ Thống

```
RAW Parquet Files
      ↓
  PySpark ETL
      ↓
Google BigQuery Warehouse (Sandbox)
      ↓
  dbt Transform
      ↓
Metabase Dashboard
```

Chi tiết: [`docs/architecture.md`](docs/architecture.md)

---

## 5. Technology Stack

| Layer | Tool | Lý do |
|---|---|---|
| Language | Python | Standard DE, Spark ecosystem |
| Processing | PySpark | Big data, distributed, industry standard |
| Storage | Parquet | Columnar, compressed, fast analytics |
| Warehouse | Google BigQuery | Cloud Data Warehouse, Sandbox mode (Free), industry standard |
| Transform | dbt | SQL-first, lineage, testing |
| Orchestration | Airflow | DAG scheduling, monitoring |
| Visualization | Metabase | Free, easy setup, SQL support |

**PySpark Mode:** Local `local[*]` → Future: Docker cluster

---

## 6. Data Model

Schema: **Star Schema**

| Bảng | Loại | Mô tả |
|---|---|---|
| `FACT_TRIP` | Fact | Bảng sự kiện chuyến đi |
| `DIM_TIME` | Dimension | Chiều thời gian |
| `DIM_LOCATION` | Dimension | Chiều địa điểm |
| `DIM_VENDOR` | Dimension | Chiều nhà cung cấp |
| `DIM_PAYMENT` | Dimension | Chiều phương thức thanh toán |
| `DIM_RATE` | Dimension | Chiều loại giá |

Chi tiết: [`docs/data_model.md`](docs/data_model.md)

---

## 7. Cấu Trúc Repository

```
NYC_Taxi_Prj/
├── data/
│   ├── raw/                 # File parquet gốc
│   └── processed/           # File đã xử lý
├── spark/
│   ├── config.py            # Cấu hình tập trung (không hardcode)
│   ├── etl/                 # ETL jobs
│   └── utils/
│       └── logger.py        # Logging module
├── notebooks/               # Jupyter notebooks (EDA, research)
├── warehouse/               # DDL scripts PostgreSQL
├── dbt/                     # dbt models (staging, intermediate, mart)
├── airflow/
│   └── dags/                # Airflow DAGs
├── docker/                  # Docker Compose configs
└── docs/
    ├── architecture.md      # Kiến trúc chi tiết
    ├── data_model.md        # Data model & schema
    ├── phases.md            # Roadmap & milestones
    ├── schema_report.md     # [Phase 1 Deliverable]
    ├── data_dictionary.md   # [Phase 1 Deliverable]
    └── profiling_report.md  # [Phase 1 Deliverable]
```

---

## 8. Coding Principles

| # | Nguyên tắc | BAD ❌ | GOOD ✅ |
|---|---|---|---|
| 1 | Không hardcode paths | `"C:/data/..."` | `config.py → BASE_DIR` |
| 2 | Đặt tên snake_case | `tripData` | `trip_data` |
| 3 | Code modular | Logic trong notebook | Functions trong `utils/` |
| 4 | Thêm logging | `print("done")` | `logger.info("done")` |
| 5 | Tránh notebook-only logic | Xử lý chỉ trong `.ipynb` | Import từ `.py` modules |
| 6 | Functions tái sử dụng | Code lặp lại | Hàm nhận params |

---

## 9. ETL Philosophy

```
Extract → Validate → Transform → Load → Test → Document
```

**Quyết định Thiết kế về Trạng thái ETL (State Control):**
- Dự án sẽ hướng tới áp dụng **Cách 1: Quản lý bằng Bảng Metadata trong Database (PostgreSQL)** để ghi log/audit trạng thái xử lý file (`status`, `processed_at`, `row_count`).
- *Lưu ý:* Sẽ triển khai cơ chế này sau khi đã dựng xong hạ tầng Database ở Phase 3. Hiện tại ở Phase 2, ta tập trung xử lý luồng ETL chính trước.

---

## 10. Phase Hiện Tại & Roadmap

| Phase | Tên | Trạng thái |
|---|---|---|
| **1** | Data Understanding | ✅ Completed |
| 2 | Spark ETL | ⏳ Planned |
| 3 | Warehouse | ⏳ Planned |
| 4 | dbt | ⏳ Planned |
| 5 | Dashboard | ⏳ Planned |
| 6 | Portfolio | ⏳ Planned |

**Phase 1 Goals:**
- [x] Đọc parquet files
- [x] Khám phá schema
- [x] Data profiling
- [x] Xác định dimensions & facts

**Phase 1 Deliverables:** `schema_report.md`, `data_dictionary.md`, `profiling_report.md`

Chi tiết: [`docs/phases.md`](docs/phases.md)

---

## 11. Definition of Done

Dự án hoàn thành khi:

- [ ] ETL được tự động hóa bằng Airflow
- [ ] Warehouse (PostgreSQL) đã được build
- [ ] Dashboard (Metabase) hoạt động
- [ ] README.md đã được document đầy đủ
- [ ] Toàn bộ hệ thống có thể reproduce bằng Docker
- [ ] Portfolio-ready
