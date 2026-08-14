# NYC Taxi End-to-End Data Engineering Project

> [🇻🇳 Tiếng Việt](#-tiếng-việt) | [🇬🇧 English](#-english)

---

## 🇬🇧 English

### Overview

An end-to-end batch data engineering pipeline for **NYC Yellow Taxi** trip data (TLC). The project downloads raw Parquet files from the NYC TLC public dataset, processes them through a Spark ETL pipeline, loads into a PostgreSQL star-schema data warehouse, applies dbt transformations, and produces analytics-ready tables for visualization.

### Architecture

```
NYC TLC (Parquet) 
    ↓
Spark ETL (Extract → Transform → Validate → Load)
    ↓
PostgreSQL Data Warehouse (Star Schema)
    ↓
dbt (Staging → Intermediate → Marts)
    ↓
Metabase (Analytics Dashboard)
```

![Workflow](docs/WorkFlow.png)

### Tech Stack

| Technology | Version | Purpose |
| --- | --- | --- |
| **Python** | 3.12+ | Core language for ETL |
| **Apache Spark** | 3.x | Distributed data processing (local mode) |
| **PostgreSQL** | 16 | Data warehouse (star schema) |
| **dbt** | 1.x | SQL-based data transformation layer |
| **Metabase** | Latest | Business analytics & visualization |
| **Docker** | Latest | PostgreSQL containerization |
| **Parquet** | N/A | Columnar storage format |
| **JDBC** | N/A | Spark ↔ PostgreSQL connectivity |

### Project Structure

```
NYC_Taxi_Project/
├── spark/                      # PySpark ETL source code
│   ├── config.py               # Centralized configuration
│   ├── etl/                    # ETL pipeline modules
│   │   ├── extract.py          # Data extraction from Parquet
│   │   ├── transform.py        # Data cleaning & enrichment
│   │   ├── validate.py         # Data quality validation
│   │   ├── load.py             # Write processed Parquet
│   │   ├── load_warehouse.py   # Load into PostgreSQL via JDBC
│   │   ├── fetch_taxi_data.py  # Download from NYC TLC API
│   │   ├── pipeline.py         # Full pipeline orchestration
│   │   ├── main.py             # CLI entry point
│   │   ├── run_pipeline.py     # Pipeline runner
│   │   └── __init__.py
│   └── utils/                  # Shared utilities
│       ├── logger.py           # Logging configuration
│       ├── spark_session.py    # Spark session factory
│       └── __init__.py
│
├── dbt/                        # dbt transformation layer
│   ├── dbt_project.yml         # dbt project configuration
│   ├── profiles.yml            # PostgreSQL connection config
│   ├── models/
│   │   ├── staging/            # Layer 1: Extract & standardize
│   │   ├── intermediate/       # Layer 2: Business logic & joins
│   │   └── marts/              # Layer 3: Analytics-ready tables
│   ├── tests/                  # Data quality tests
│   ├── macros/                 # Jinja2 reusable functions
│   └── logs/                   # dbt execution logs
│
├── infrastructure/             # Infrastructure & deployment
│   ├── docker/                 # Docker Compose for PostgreSQL
│   ├── hadoop/                 # Hadoop binaries (Windows)
│   └── warehouse/              # SQL DDL scripts (star schema)
│
├── data/                       # Data storage (git-ignored)
│   ├── raw/yellow/             # Raw Parquet files from NYC TLC
│   └── processed/              # Transformed Parquet (date-partitioned)
│
├── docs/                       # Documentation

### ETL & Transformation Pipeline

```
1. EXTRACT (PySpark)
   └─ Download Yellow Taxi Parquet files from NYC TLC website
   └─ Store in data/raw/yellow/

2. TRANSFORM (PySpark)
   └─ Clean data, remove outliers
   └─ Add derived columns (trip_duration_min, tip_ratio, pickup_date)
   └─ Validate schema consistency

3. VALIDATE (PySpark)
   └─ Data quality checks (nulls, value ranges, referential integrity)
   └─ Generate quality reports

4. LOAD (PySpark + JDBC)
   └─ Write partitioned Parquet files to data/processed/
   └─ Load into PostgreSQL star schema tables

5. TRANSFORM (dbt)
   └─ staging: Standardize and document sources
   └─ intermediate: Apply business logic, create enriched views
   └─ marts: Generate analytics-ready fact/dimension tables

6. VISUALIZE (Metabase)
   └─ Connect to PostgreSQL mart tables
   └─ Create interactive dashboards
```

### Quick Start

#### Prerequisites

- Python 3.12+
- Java 21 (Eclipse Adoptium)
- Docker & Docker Compose
- ~2GB free disk space (for raw data)
- Git 2.36+ (for worktree support)

#### 1. Clone & Setup Environment

```bash
# Clone repository
git clone https://github.com/lancelotviendangkhoa710/nyc-taxi-de-project.git
cd nyc-taxi-de-project

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# OR
source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -e .
pip install dbt-postgres      # For dbt transformations
```

#### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your PostgreSQL credentials
# Example:
# PG_HOST=localhost
# PG_PORT=5432
# PG_USER=postgres
# PG_PASSWORD=postgres
# PG_DATABASE=postgres
```

#### 3. Start PostgreSQL

```bash
cd infrastructure/docker
docker compose up -d

# Verify PostgreSQL is running
docker compose logs postgres
```

#### 4. Run Spark ETL Pipeline

```bash
cd /path/to/project

# Run full pipeline (extract → transform → validate → load)
python -m spark.etl.main

# Or run specific stages
python -m spark.etl.extract
python -m spark.etl.transform
python -m spark.etl.validate
python -m spark.etl.load_warehouse
```

#### 5. Run dbt Transformations

```bash
cd dbt

# Verify dbt connection to PostgreSQL
dbt debug

# Run all dbt models (staging → intermediate → marts)
dbt run


---

## Git Worktree Workflow

### What is Git Worktree?

Git worktree allows you to work on multiple branches simultaneously without switching branches constantly. Each worktree has its own working directory, so you can test features independently.

### Setting Up Worktrees

#### Create a worktree for feature development

```bash
# Navigate to project root
cd d:\NYC_Taxi_Project

# Create a new worktree linked to a new branch
git worktree add -b feature/dbt-transformations ./worktrees/dbt-feature

# List all worktrees
git worktree list

# Output:
# D:/NYC_Taxi_Project                 d837498 [main]
# D:/NYC_Taxi_Project/worktrees/dbt-feature  (new commit) [feature/dbt-transformations]
```

#### Switch to the worktree

```bash
# Navigate into worktree
cd ./worktrees/dbt-feature

# You're now on feature/dbt-transformations branch
git status

# Install dependencies in this worktree
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install dbt-postgres
```

#### Work on your feature

```bash
# Make changes
# ... edit files ...

# Stage and commit
git add .
git commit -m "feat: add new dbt models for revenue analysis"

# Push to remote
git push -u origin feature/dbt-transformations
```

#### Create Pull Request

```bash
# Using GitHub CLI (gh)
gh pr create \
  --title "Add dbt transformation models" \
  --body "This PR adds staging, intermediate, and mart models for revenue analysis" \
  --base main \
  --head feature/dbt-transformations
```

#### Cleanup Worktree

```bash
# After PR is merged, remove worktree
cd d:\NYC_Taxi_Project  # Back to main worktree

# Delete the worktree
git worktree remove ./worktrees/dbt-feature

# Verify it's gone
git worktree list
```

### Worktree Best Practices

1. **One worktree per feature/branch** — Prevents confusion about which directory is which branch
2. **Always switch back to main worktree before cleaning up** — Don't be in the worktree you're removing
3. **Use consistent naming** — `./worktrees/<branch-name>` makes it clear what each directory contains
4. **Keep worktrees organized** — Remove old worktrees after PR merges to avoid clutter
5. **Test in isolation** — Each worktree can have independent data/logs without interfering

### Example Workflow: Multiple Features in Parallel

```bash
# Main worktree (main branch)
cd d:\NYC_Taxi_Project

# Create feature 1 worktree
git worktree add -b feature/metabase-dashboards ./worktrees/metabase
cd ./worktrees/metabase
# ... work on feature 1 ...

# Back to main, create feature 2 worktree
cd d:\NYC_Taxi_Project
git worktree add -b feature/airflow-dag ./worktrees/airflow
cd ./worktrees/airflow
# ... work on feature 2 ...

# List all active worktrees
git worktree list
# Output:
# D:/NYC_Taxi_Project                          d837498 [main]
# D:/NYC_Taxi_Project/worktrees/metabase       abcd123 [feature/metabase-dashboards]
# D:/NYC_Taxi_Project/worktrees/airflow        efgh456 [feature/airflow-dag]
```

---

## Development Workflow

### Local Development Setup

```bash
# 1. Start PostgreSQL
cd infrastructure/docker
docker compose up -d

# 2. Activate Python environment
cd /path/to/project
.venv\Scripts\activate

# 3. Run Spark ETL (first time only or when data updates needed)
python -m spark.etl.main

# 4. Run dbt transformations
cd dbt
dbt run && dbt test

# 5. View dbt documentation
dbt docs serve
```

### Running Tests

```bash
# Python unit tests
pytest tests/

# dbt data quality tests
cd dbt
dbt test

# Specific dbt model tests
dbt test --select staging
```

### Troubleshooting

#### PostgreSQL Connection Issues
```bash
# Check if container is running
docker compose ps

# View logs
docker compose logs postgres

# Restart
docker compose restart postgres
```

#### Spark ETL Errors
```bash
# Check logs
cat logs/spark_etl.log

# Run with verbose logging
python -m spark.etl.main --verbose
```

#### dbt Issues
```bash
# Verify connection
cd dbt && dbt debug

# Check profiles.yml path
echo %DBT_PROFILES_DIR%

# Regenerate lock file
dbt deps
```

---

---

## 🇻🇳 Tiếng Việt

### Tổng Quan

Một pipeline dữ liệu batch end-to-end cho dữ liệu chuyến xe Taxi vàng NYC (TLC). Dự án tải các file Parquet thô từ dataset công khai NYC TLC, xử lý thông qua pipeline Spark ETL, nạp vào PostgreSQL với star-schema data warehouse, áp dụng các phép biến đổi dbt, và tạo ra các bảng sẵn sàng phân tích cho visualization.

### Kiến Trúc

```
NYC TLC (Parquet) 
    ↓
Spark ETL (Extract → Transform → Validate → Load)
    ↓
PostgreSQL Data Warehouse (Star Schema)
    ↓
dbt (Staging → Intermediate → Marts)
    ↓
Metabase (Analytics Dashboard)
```

### Tech Stack

| Công Nghệ | Phiên Bản | Mục Đích |
| --- | --- | --- |
| **Python** | 3.12+ | Ngôn ngữ chính cho ETL |
| **Apache Spark** | 3.x | Xử lý dữ liệu phân tán (local mode) |
| **PostgreSQL** | 16 | Data warehouse (star schema) |
| **dbt** | 1.x | Lớp biến đổi dữ liệu dựa trên SQL |
| **Metabase** | Latest | Business analytics & visualization |


### Cấu Trúc Dự Án

```
NYC_Taxi_Project/
├── spark/                      # Mã nguồn PySpark ETL
│   ├── config.py               # Cấu hình tập trung
│   ├── etl/                    # Các module pipeline ETL
│   │   ├── extract.py          # Trích xuất từ Parquet
│   │   ├── transform.py        # Làm sạch & làm giàu dữ liệu
│   │   ├── validate.py         # Xác thực chất lượng dữ liệu
│   │   ├── load.py             # Ghi Parquet đã xử lý
│   │   ├── load_warehouse.py   # Nạp vào PostgreSQL qua JDBC
│   │   ├── fetch_taxi_data.py  # Tải từ NYC TLC API
│   │   ├── pipeline.py         # Điều phối pipeline
│   │   └── main.py             # Điểm vào CLI
│   └── utils/                  # Tiện ích dùng chung
│       ├── logger.py           # Cấu hình logging
│       └── spark_session.py    # Tạo Spark session
│
├── dbt/                        # Lớp biến đổi dbt
│   ├── dbt_project.yml         # Cấu hình dbt project
│   ├── profiles.yml            # Cấu hình kết nối PostgreSQL
│   ├── models/
│   │   ├── staging/            # Lớp 1: Trích xuất & chuẩn hóa
│   │   ├── intermediate/       # Lớp 2: Business logic & join
│   │   └── marts/              # Lớp 3: Bảng sẵn sàng phân tích
│   ├── tests/                  # Kiểm tra chất lượng dữ liệu
│   ├── macros/                 # Hàm Jinja2 tái sử dụng
│   └── logs/                   # Log thực thi dbt
│
├── infrastructure/             # Hạ tầng & triển khai
│   ├── docker/                 # Docker Compose cho PostgreSQL
│   ├── hadoop/                 # Hadoop binaries (Windows)
│   └── warehouse/              # DDL scripts (star schema)
│
├── data/                       # Lưu trữ dữ liệu (git-ignored)
│   ├── raw/yellow/             # File Parquet thô từ NYC TLC
│   └── processed/              # Parquet đã xử lý (phân vùng theo ngày)
│
├── docs/                       # Tài liệu
│   ├── architecture.md         # Kiến trúc hệ thống & luồng dữ liệu
│   ├── data_model.md           # Thiết kế star schema
│   ├── data_dictionary.md      # Định nghĩa cột & metric
│   ├── dbt_learning_guide.md   # Hướng dẫn dbt & best practices
│   ├── IMPLEMENT_PLAN.md       # Lộ trình triển khai
│   └── specs/                  # Đặc tả nguồn dữ liệu
│
├── tests/                      # Kiểm tra đơn vị Python
├── logs/                       # Log ứng dụng
├── pyproject.toml              # Cấu hình project Python
├── .env.example                # Mẫu biến môi trường
└── README.md                   # File này
```

### Mô Hình Dữ Liệu (Star Schema)

| Bảng | Loại | Mô Tả |
| --- | --- | --- |
| `fact_trip` | Fact | Bản ghi chuyến đi với measures (giá, khoảng cách, thời gian) |
| `dim_vendor` | Dimension | Thông tin nhà cung cấp taxi |
| `dim_payment` | Dimension | Bảng tra cứu loại thanh toán |
| `dim_rate` | Dimension | Bảng tra cứu mã giá |
| `dim_location` | Dimension | Ánh xạ khu vực đón/trả khách |
| `dim_time` | Dimension | Chiều thời gian cho phân tích theo thời gian |

| **Docker** | Latest | Container hóa PostgreSQL |
| **Parquet** | N/A | Định dạng lưu trữ dạng cột |
| **JDBC** | N/A | Kết nối Spark ↔ PostgreSQL |


## Contributing

1. Create a feature branch using worktree: `git worktree add -b feature/xyz ./worktrees/xyz`
2. Make changes and test thoroughly
3. Commit with clear messages
4. Push and create a PR
5. After merge, remove worktree: `git worktree remove ./worktrees/xyz`

---

## Project Status

✅ Spark ETL Pipeline — Complete  
✅ PostgreSQL Star Schema — Complete  
✅ dbt Transformation Layer — In Progress  
⏳ Metabase Dashboards — Planned  
⏳ Apache Airflow Orchestration — Planned  

---

## Resources

- [NYC TLC Taxi Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [dbt Documentation](https://docs.getdbt.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Metabase Documentation](https://www.metabase.com/docs/)

# Run data quality tests
dbt test

# Generate and view documentation
dbt docs generate
dbt docs serve  # Opens http://localhost:8000 with DAG visualization
```

#### 6. Verify Data in PostgreSQL

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d postgres

# Check tables
\dt public.*

# Quick query
SELECT COUNT(*) FROM fact_trip;
SELECT COUNT(*) FROM dim_vendor;
```

│   ├── architecture.md         # System architecture & data flow
│   ├── data_model.md           # Star schema design
│   ├── data_dictionary.md      # Column definitions & metrics
│   ├── dbt_learning_guide.md   # dbt tutorial & best practices
│   ├── IMPLEMENT_PLAN.md       # Implementation roadmap
│   └── specs/                  # Data source specifications
│
├── tests/                      # Python unit tests
├── logs/                       # Application logs
├── pyproject.toml              # Python project configuration
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

### Data Model (Star Schema)

| Table | Type | Description |
| --- | --- | --- |
| `fact_trip` | Fact | Trip records with measures (fare, distance, duration) |
| `dim_vendor` | Dimension | Taxi vendor information |
| `dim_payment` | Dimension | Payment type lookup |
| `dim_rate` | Dimension | Rate code lookup |
| `dim_location` | Dimension | Pickup/dropoff zone mapping |
| `dim_time` | Dimension | Time dimension for temporal analysis |
