<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=32&pause=1000&color=F7C948&center=true&vCenter=true&width=800&lines=NYC+Taxi+Data+Engineering;End-to-End+Batch+Pipeline;Spark+%7C+PostgreSQL+%7C+dbt+%7C+Power+BI" alt="Typing SVG" />

<br/>

<img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Apache%20Spark-3.x-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/dbt-1.x-FF694B?style=for-the-badge&logo=dbt&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-Latest-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/Power%20BI-Latest-F2C811?style=for-the-badge&logo=powerbi&logoColor=black"/>
<img src="https://img.shields.io/badge/Parquet-Columnar-50AF95?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-In%20Progress-orange?style=for-the-badge"/>

<br/><br/>
<img src="docs/WorkFlow.png" alt="Architecture Workflow" width="85%"/>
</div>

---

## Overview

An **end-to-end batch data engineering pipeline** for NYC Yellow Taxi trip data (TLC).

Downloads raw Parquet files from the NYC TLC public dataset, processes them through a **Spark ETL** pipeline, loads data into a **PostgreSQL star-schema** data warehouse, applies **dbt** transformations, and produces analytics-ready tables for **Power BI** visualization.

---

## Architecture

```
NYC TLC (Parquet)
        |
Spark ETL  --  Extract -> Transform -> Validate -> Load
        |
PostgreSQL  --  Star Schema Data Warehouse
        |
dbt  --  Staging -> Intermediate -> Marts
        |
Power BI  --  Interactive Analytics Dashboard
```

---

## Tech Stack

| Technology | Version | Purpose |
| :---: | :---: | :--- |
| ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) | `3.12+` | Core language for ETL |
| ![Spark](https://img.shields.io/badge/-Apache%20Spark-E25A1C?logo=apachespark&logoColor=white) | `3.x` | Distributed data processing |
| ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?logo=postgresql&logoColor=white) | `16` | Data warehouse — star schema |
| ![dbt](https://img.shields.io/badge/-dbt-FF694B?logo=dbt&logoColor=white) | `1.x` | SQL transformation layer |
| ![Power BI](https://img.shields.io/badge/-Power%20BI-F2C811?logo=powerbi&logoColor=black) | `Latest` | Business analytics |
| ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white) | `Latest` | PostgreSQL containerization |
| **Parquet** | `N/A` | Columnar storage format |
| **JDBC** | `N/A` | Spark to PostgreSQL connectivity |

---

## Project Structure

```
NYC_Taxi_Project/
├── spark/
│   ├── config.py
│   ├── etl/
│   │   ├── extract.py
│   │   ├── transform.py
│   │   ├── validate.py
│   │   ├── load.py
│   │   ├── load_warehouse.py
│   │   ├── fetch_taxi_data.py
│   │   ├── pipeline.py
│   │   ├── main.py
│   │   └── run_pipeline.py
│   └── utils/
│       ├── logger.py
│       └── spark_session.py
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── tests/
│   └── macros/
├── infrastructure/
│   ├── docker/
│   ├── hadoop/
│   └── warehouse/
├── data/
│   ├── raw/yellow/
│   └── processed/
├── docs/
│   ├── architecture.md
│   ├── data_model.md
│   ├── data_dictionary.md
│   ├── dbt_learning_guide.md
│   └── IMPLEMENT_PLAN.md
├── tests/
├── logs/
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

---

## ETL Pipeline

```
1. EXTRACT  (PySpark)
   -- Download Yellow Taxi Parquet from NYC TLC
   -- Store in data/raw/yellow/

2. TRANSFORM  (PySpark)
   -- Clean data, remove outliers
   -- Add derived columns: trip_duration_min | tip_ratio | pickup_date
   -- Validate schema consistency

3. VALIDATE  (PySpark)
   -- Data quality checks (nulls, ranges, referential integrity)
   -- Generate quality reports

4. LOAD  (PySpark + JDBC)
   -- Write partitioned Parquet to data/processed/
   -- Load into PostgreSQL star schema tables

5. TRANSFORM  (dbt)
   -- staging      : Standardize & document sources
   -- intermediate : Business logic, enriched views
   -- marts        : Analytics-ready fact/dim tables

6. VISUALIZE  (Power BI)
   -- Connect to PostgreSQL mart tables
   -- Interactive dashboards & reports
```

---

## Data Model — Star Schema

| Table | Type | Description |
| :--- | :---: | :--- |
| `fact_trip` | Fact | Trip records with measures (fare, distance, duration) |
| `dim_vendor` | Dimension | Taxi vendor information |
| `dim_payment` | Dimension | Payment type lookup |
| `dim_rate` | Dimension | Rate code lookup |
| `dim_location` | Dimension | Pickup / dropoff zone mapping |
| `dim_time` | Dimension | Time dimension for temporal analysis |

---

## Quick Start

### Prerequisites

| Requirement | Version |
| :--- | :---: |
| Python | `3.12+` |
| Java (Eclipse Adoptium) | `21` |
| Docker & Docker Compose | `Latest` |
| Git | `2.36+` |
| Free disk space | `~2 GB` |

### 1. Clone & Setup

```bash
git clone https://github.com/lancelotviendangkhoa710/nyc-taxi-de-project.git
cd nyc-taxi-de-project

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

pip install -e .
pip install dbt-postgres
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env:
# PG_HOST=localhost
# PG_PORT=5432
# PG_USER=postgres
# PG_PASSWORD=postgres
# PG_DATABASE=postgres
```

### 3. Start PostgreSQL

```bash
cd infrastructure/docker
docker compose up -d
docker compose logs postgres
```

### 4. Run Spark ETL

```bash
python -m spark.etl.main

# Or individual stages:
python -m spark.etl.extract
python -m spark.etl.transform
python -m spark.etl.validate
python -m spark.etl.load_warehouse
```

### 5. Run dbt

```bash
cd dbt
dbt debug
dbt run
dbt test
dbt docs generate
dbt docs serve
```

### 6. Verify Data

```bash
psql -h localhost -U postgres -d postgres
\dt public.*
SELECT COUNT(*) FROM fact_trip;
SELECT COUNT(*) FROM dim_vendor;
```

---

## Git Worktree Workflow

Git worktree lets you work on **multiple branches simultaneously** without constant branch switching.

```bash
# Create worktree
git worktree add -b feature/dbt-transformations ./worktrees/dbt-feature

# List worktrees
git worktree list

# Navigate & setup
cd ./worktrees/dbt-feature
python -m venv .venv
.venv\Scripts\activate
pip install -e . && pip install dbt-postgres

# Commit & push
git add .
git commit -m "feat: add dbt models for revenue analysis"
git push -u origin feature/dbt-transformations

# Open PR
gh pr create --title "Add dbt transformation models" --base main --head feature/dbt-transformations

# Cleanup after merge
git worktree remove ./worktrees/dbt-feature
git branch -d feature/dbt-transformations
```

---

## Contributing

1. `git worktree add -b feature/xyz ./worktrees/xyz`
2. Make changes and test thoroughly
3. Commit with clear messages
4. Push and open a Pull Request
5. After merge: `git worktree remove ./worktrees/xyz`

---

## Project Status

| Component | Status |
| :--- | :---: |
| Spark ETL Pipeline | Completed |
| PostgreSQL Star Schema | Completed |
| dbt Transformation Layer | Completed |
| Power BI Dashboards | Planned |
| Apache Airflow Orchestration | Planned |

---

## Resources

[![NYC TLC](https://img.shields.io/badge/NYC%20TLC%20Taxi%20Data-Dataset-yellow?style=for-the-badge)](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
[![Spark](https://img.shields.io/badge/Apache%20Spark-Docs-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/docs/latest/)
[![dbt](https://img.shields.io/badge/dbt-Docs-FF694B?style=for-the-badge&logo=dbt&logoColor=white)](https://docs.getdbt.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Docs-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/docs/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Docs-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://learn.microsoft.com/power-bi/)

---

<div align="center">
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=14&pause=1000&color=888888&center=true&vCenter=true&width=500&lines=Built+with+love+for+Data+Engineering;NYC+Yellow+Taxi+2024" alt="footer"/>
</div>
