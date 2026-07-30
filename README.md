# NYC Taxi End-to-End Data Engineering Project

> [🇻🇳 Tiếng Việt](#-tiếng-việt) | [🇬🇧 English](#-english)

---

## 🇬🇧 English

### Overview

An end-to-end batch data engineering pipeline for **NYC Yellow Taxi** trip data (TLC). The project downloads raw Parquet files from the NYC TLC public dataset, processes them through a Spark ETL pipeline, loads into a PostgreSQL star-schema data warehouse, and produces analytics-ready tables.

### Architecture

```
NYC TLC (Parquet) → Spark ETL (Extract → Transform → Validate → Load) → PostgreSQL Data Warehouse
```

![Workflow](docs/WorkFlow.png)

### Tech Stack

| Technology | Purpose |
| --- | --- |
| **Python 3.12** | Core language |
| **Apache Spark** | Distributed data processing (local mode) |
| **PostgreSQL 16** | Data warehouse |
| **Docker** | PostgreSQL containerization |
| **Parquet** | Columnar storage format |
| **JDBC** | Spark ↔ PostgreSQL connectivity |

### Project Structure

```
├── spark/                  # ETL source code
│   ├── config.py           # Central configuration
│   ├── etl/                # ETL modules
│   │   ├── extract.py      # Data extraction from Parquet
│   │   ├── transform.py    # Data cleaning & enrichment
│   │   ├── validate.py     # Data quality checks
│   │   ├── load.py         # Write processed Parquet
│   │   ├── load_warehouse.py  # Load into PostgreSQL
│   │   ├── fetch_taxi_data.py # Download from NYC TLC
│   │   ├── pipeline.py     # Full pipeline orchestration
│   │   ├── main.py         # CLI entry point
│   │   └── run_pipeline.py # Pipeline runner
│   └── utils/              # Shared utilities
│       ├── logger.py       # Logging config
│       └── spark_session.py # Spark session factory
├── infrastructure/         # Infrastructure & deployment
│   ├── docker/             # Docker Compose for PostgreSQL
│   ├── hadoop/             # Hadoop binaries (Windows)
│   └── warehouse/          # DDL scripts (star schema)
│       └── ddl/            # Dimension & fact table definitions
├── data/                   # Data storage (git-ignored)
│   ├── raw/yellow/         # Raw Parquet files
│   └── processed/          # Transformed Parquet (partitioned by date)
├── docs/                   # Documentation
│   ├── architecture.md     # System architecture
│   ├── data_model.md       # Data model design
│   ├── data_dictionary.md  # Column definitions
│   ├── IMPLEMENT_PLAN.md   # Implementation roadmap
│   └── specs/              # Data source specifications
├── tests/                  # Test suite
├── logs/                   # Application logs
├── pyproject.toml          # Python project config
└── .env.example            # Environment variable template
```

### Data Model (Star Schema)

| Table | Type | Description |
| --- | --- | --- |
| `fact_trip` | Fact | Trip records with measures (fare, distance, duration) |
| `dim_vendor` | Dimension | Taxi vendor information |
| `dim_payment` | Dimension | Payment type lookup |
| `dim_rate` | Dimension | Rate code lookup |
| `dim_location` | Dimension | Pickup/dropoff zone mapping |
| `dim_time` | Dimension | Time dimension |

### ETL Pipeline

1. **Extract** — Download Yellow Taxi Parquet files from NYC TLC website
2. **Transform** — Clean data, remove outliers, add derived columns (`trip_duration_min`, `tip_ratio`, `pickup_date`)
3. **Validate** — Data quality checks (nulls, ranges, referential integrity)
4. **Load** — Write partitioned Parquet files + load into PostgreSQL via JDBC

### Quick Start

```bash
# 1. Clone
git clone https://github.com/lancelotviendangkhoa710/nyc-taxi-de-project.git
cd nyc-taxi-de-project

# 2. Set up environment
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .

# 3. Configure
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 4. Start PostgreSQL
cd infrastructure/docker
docker compose up -d

# 5. Run pipeline
python -m spark.etl.main
```

### Requirements

- Python 3.12+
- Java 21 (Eclipse Adoptium)
- Docker (for PostgreSQL)
- ~2GB disk space for raw data

---

## 🇻🇳 Tiếng Việt

### Tổng Quan

Pipeline xử lý dữ liệu batch end-to-end cho dữ liệu **NYC Yellow Taxi** (TLC). Dự án tải file Parquet thô từ bộ dữ liệu công khai NYC TLC, xử lý qua pipeline Spark ETL, nạp vào data warehouse PostgreSQL theo mô hình star schema, và tạo ra các bảng sẵn sàng cho phân tích.

### Kiến Trúc

```
NYC TLC (Parquet) → Spark ETL (Extract → Transform → Validate → Load) → PostgreSQL Data Warehouse
```

![Workflow](docs/WorkFlow.png)

### Công Nghệ Sử Dụng

| Công nghệ | Mục đích |
| --- | --- |
| **Python 3.12** | Ngôn ngữ chính |
| **Apache Spark** | Xử lý dữ liệu phân tán (local mode) |
| **PostgreSQL 16** | Data warehouse |
| **Docker** | Container hóa PostgreSQL |
| **Parquet** | Định dạng lưu trữ dạng cột |
| **JDBC** | Kết nối Spark ↔ PostgreSQL |

### Cấu Trúc Dự Án

```
├── spark/                  # Mã nguồn ETL
│   ├── config.py           # Cấu hình trung tâm
│   ├── etl/                # Các module ETL
│   │   ├── extract.py      # Trích xuất dữ liệu từ Parquet
│   │   ├── transform.py    # Làm sạch & làm giàu dữ liệu
│   │   ├── validate.py     # Kiểm tra chất lượng dữ liệu
│   │   ├── load.py         # Ghi Parquet đã xử lý
│   │   ├── load_warehouse.py  # Nạp vào PostgreSQL
│   │   ├── fetch_taxi_data.py # Tải từ NYC TLC
│   │   ├── pipeline.py     # Điều phối pipeline
│   │   ├── main.py         # Điểm vào CLI
│   │   └── run_pipeline.py # Chạy pipeline
│   └── utils/              # Tiện ích dùng chung
│       ├── logger.py       # Cấu hình logging
│       └── spark_session.py # Tạo Spark session
├── infrastructure/         # Hạ tầng & triển khai
│   ├── docker/             # Docker Compose cho PostgreSQL
│   ├── hadoop/             # Hadoop binaries (Windows)
│   └── warehouse/          # DDL scripts (star schema)
│       └── ddl/            # Định nghĩa bảng dimension & fact
├── data/                   # Dữ liệu (không theo dõi bởi git)
│   ├── raw/yellow/         # File Parquet thô
│   └── processed/          # Parquet đã xử lý (phân vùng theo ngày)
├── docs/                   # Tài liệu
│   ├── architecture.md     # Kiến trúc hệ thống
│   ├── data_model.md       # Thiết kế mô hình dữ liệu
│   ├── data_dictionary.md  # Định nghĩa các cột
│   ├── IMPLEMENT_PLAN.md   # Lộ trình triển khai
│   └── specs/              # Đặc tả nguồn dữ liệu
├── tests/                  # Bộ test
├── logs/                   # Log ứng dụng
├── pyproject.toml          # Cấu hình project Python
└── .env.example            # Mẫu biến môi trường
```

### Mô Hình Dữ Liệu (Star Schema)

| Bảng | Loại | Mô tả |
| --- | --- | --- |
| `fact_trip` | Fact | Bản ghi chuyến đi với các measure (giá, khoảng cách, thời gian) |
| `dim_vendor` | Dimension | Thông tin nhà cung cấp taxi |
| `dim_payment` | Dimension | Bảng tra cứu loại thanh toán |
| `dim_rate` | Dimension | Bảng tra cứu mã giá |
| `dim_location` | Dimension | Ánh xạ khu vực đón/trả khách |
| `dim_time` | Dimension | Chiều thời gian |

### Pipeline ETL

1. **Extract** — Tải file Parquet Yellow Taxi từ website NYC TLC
2. **Transform** — Làm sạch dữ liệu, loại bỏ outlier, thêm cột phái sinh (`trip_duration_min`, `tip_ratio`, `pickup_date`)
3. **Validate** — Kiểm tra chất lượng dữ liệu (null, khoảng giá trị, tham chiếu)
4. **Load** — Ghi file Parquet phân vùng + nạp vào PostgreSQL qua JDBC

### Bắt Đầu Nhanh

```bash
# 1. Clone
git clone https://github.com/lancelotviendangkhoa710/nyc-taxi-de-project.git
cd nyc-taxi-de-project

# 2. Thiết lập môi trường
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .

# 3. Cấu hình
cp .env.example .env
# Chỉnh sửa .env với thông tin PostgreSQL của bạn

# 4. Khởi động PostgreSQL
cd infrastructure/docker
docker compose up -d

# 5. Chạy pipeline
python -m spark.etl.main
```

### Yêu Cầu

- Python 3.12+
- Java 21 (Eclipse Adoptium)
- Docker (cho PostgreSQL)
- ~2GB dung lượng đĩa cho dữ liệu thô
