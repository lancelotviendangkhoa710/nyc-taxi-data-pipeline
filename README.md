# NYC Yellow Taxi Data Engineering Platform

A production-grade data engineering platform for analyzing NYC Yellow Taxi trip data using Apache Spark, dbt, and Google BigQuery. This project demonstrates modern data lakehouse architecture with batch processing, data transformations, and business intelligence dashboards.

## 🎯 Project Overview

This platform ingests, processes, and analyzes millions of NYC taxi trip records to provide actionable insights on:
- Revenue trends and taxi demand patterns
- Trip duration and distance analytics
- Payment method distribution
- Geographic hotspot analysis by pickup/dropoff zones
- Driver performance metrics

**Tech Stack:**
- **Data Ingestion**: NYC TLC Parquet Files
- **Processing**: Apache Spark (PySpark) with local execution
- **Storage**: Google BigQuery (Sandbox)
- **Transformation**: dbt (data build tool)
- **Orchestration**: Apache Airflow
- **Visualization**: Metabase
- **Infrastructure**: Docker (containerized deployment)

---

## 📊 Architecture

### Data Flow Pipeline

```
NYC TLC Data (Parquet)
    ↓
[Raw Layer] - data/raw/*.parquet
    ↓ (PySpark ETL)
[Processed Layer] - data/processed/*.parquet
    ↓ (GCS/BigQuery API)
[Warehouse Layer] - BigQuery (Star Schema)
    ↓ (dbt transformations)
[Transform Layer] - Staging → Intermediate → Mart
    ↓
[Presentation Layer] - Metabase Dashboards
```

### Execution Flow (Airflow DAG)

```
download_data
    ↓
run_spark_etl (cleaning, validation, enrichment)
    ↓
load_to_postgres (or BigQuery)
    ↓
run_dbt_models (dimensional modeling)
    ↓
refresh_dashboard (analytics dashboards)
```

### Directory Structure

```
.
├── data/
│   ├── raw/                 # Unprocessed NYC TLC Parquet files
│   └── processed/           # Cleaned and validated parquet files
├── spark/
│   ├── config.py           # Spark configuration
│   ├── utils/              # Helper functions
│   └── etl/
│       ├── main.py         # ETL orchestration entry point
│       ├── pipeline.py     # Core transformation logic
│       ├── load.py         # Data loading utilities
│       └── load_warehouse.py  # BigQuery/PostgreSQL loading
├── warehouse/
│   └── ddl/                # Data warehouse schema definitions
│       ├── fact_trip.sql   # Trip fact table
│       ├── dim_vendor.sql  # Vendor dimension
│       ├── dim_time.sql    # Time dimension
│       ├── dim_location.sql # Location dimension
│       ├── dim_payment.sql # Payment dimension
│       └── dim_rate.sql    # Rate code dimension
├── dbt/                     # dbt models, tests, documentation
├── airflow/
│   └── dags/               # Airflow DAG definitions
├── docker/                 # Docker Compose configuration
├── docs/                   # Project documentation
└── .gitnexus/             # GitNexus code intelligence index
```

---

## 📋 Dataset

**Source:** NYC Taxi and Limousine Commission (TLC) Yellow Taxi Trip Records

**Key Fields:**
- `VendorID`: Taxi service provider (1 = Creative Mobile, 2 = VeriFone)
- `tpep_pickup_datetime / tpep_dropoff_datetime`: Trip timestamps
- `passenger_count`: Number of passengers
- `trip_distance`: Distance in miles
- `RatecodeID`: Fare type (Standard, JFK, Newark, etc.)
- `PULocationID / DOLocationID`: Pickup/dropoff zone identifiers
- `payment_type`: Payment method (Credit card, Cash, etc.)
- `fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, congestion_surcharge`: Fare components
- `total_amount`: Total trip cost

**Derived Columns (ETL Phase):**
- `trip_duration_min`: Trip duration in minutes
- `tip_ratio`: Tip as percentage of base fare
- `pickup_date`: Date partition key (YYYY-MM-DD)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Apache Spark 3.x
- Google Cloud SDK (for BigQuery access)
- Docker & Docker Compose (for containerized deployment)
- dbt 1.5+
- Apache Airflow 2.x

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lancelotviendangkhoa710/nyc-taxi-de-project.git
   cd nyc-taxi-de-project
   ```

2. **Install Python dependencies:**
   ```bash
   pip install pyspark pandas numpy dbt-bigquery apache-airflow
   ```

3. **Configure Google Cloud credentials:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

4. **Run the ETL pipeline locally:**
   ```bash
   python spark/etl/main.py
   ```

5. **Load data to warehouse:**
   ```bash
   python spark/etl/load_warehouse.py
   ```

6. **Execute dbt transformations:**
   ```bash
   cd dbt
   dbt run
   dbt test
   ```

### Docker Deployment

```bash
docker-compose -f docker/docker-compose.yml up -d
```

This starts:
- Apache Airflow (localhost:8080)
- Metabase (localhost:3000)
- dbt transformation container
- BigQuery connector

---

## 🔧 Configuration

### Spark Configuration (`spark/config.py`)

```python
SPARK_MASTER = "local[*]"  # Local execution using all cores
WAREHOUSE_PATH = "data/processed/"
WAREHOUSE_FORMAT = "parquet"
```

### Environment Variables

Create `.env` file in project root:

```env
GCP_PROJECT_ID=your-gcp-project
BIGQUERY_DATASET=taxi_data
AIRFLOW_HOME=./airflow
DBT_PROFILES_DIR=./dbt
```

### Warehouse Schema

**Star Schema Design:**
- **fact_trip**: Central fact table with trip metrics
- **dim_vendor**: Taxi service providers
- **dim_time**: Time dimension (hour, date, month, quarter, year)
- **dim_location**: NYC taxi zones with geography
- **dim_payment**: Payment methods
- **dim_rate**: Fare code categories

---

## 📈 Pipeline Execution

### ETL Phase 1: Data Ingestion & Cleaning

**Input:** Raw NYC TLC Parquet files
**Processing:**
- Schema validation
- Null value handling
- Data type casting
- Outlier detection and handling
- Timestamp normalization

**Output:** Cleaned parquet files in `data/processed/`

### ETL Phase 2: Warehouse Loading

**Input:** Processed parquet files
**Processing:**
- Fact table aggregations
- Dimension table lookups
- Surrogate key generation
- SCD Type 1 updates

**Output:** BigQuery star schema tables

### Transform Phase 3: dbt Models

**Staging Layer:** Raw table aliasing and basic cleaning
**Intermediate Layer:** Business logic and calculations
**Mart Layer:** Final analytical tables and aggregations

```sql
-- Example: Revenue by zone
SELECT 
    dl.zone_name,
    DATE(ft.pickup_date) as trip_date,
    COUNT(*) as total_trips,
    SUM(ft.total_amount) as total_revenue,
    AVG(ft.tip_amount) as avg_tip
FROM fact_trip ft
JOIN dim_location dl ON ft.pu_location_id = dl.location_id
GROUP BY dl.zone_name, trip_date
```

---

## 📊 Key Analytics

### Business Metrics Dashboard (Metabase)

1. **Revenue Analysis**
   - Total revenue by day/month/zone
   - Revenue by payment type
   - Revenue per taxi zone

2. **Trip Analytics**
   - Trip count and frequency
   - Average trip distance
   - Average trip duration
   - Peak hours and zones

3. **Driver Performance**
   - Trips per vendor
   - Tip percentage distribution
   - Passenger count statistics

4. **Geographic Insights**
   - Heatmaps of pickup/dropoff zones
   - Popular routes
   - Zone-to-zone trip patterns

---

## 🧪 Testing & Validation

### dbt Tests

```bash
cd dbt
dbt test  # Run all tests
dbt test --select model_name  # Test specific model
```

Built-in tests:
- **unique**: No duplicate primary keys
- **not_null**: Required fields populated
- **relationships**: Foreign key constraints
- **accepted_values**: Enum validation

### Data Quality Checks

Spark ETL includes:
- Row count validation
- Schema mismatch detection
- Null percentage thresholds
- Duplicate detection

```python
# Example: Validate trip duration
valid_trips = df.filter((col("trip_duration_min") > 0) & 
                        (col("trip_duration_min") <= 1440))
invalid_count = df.count() - valid_trips.count()
```

---

## 📚 Documentation

- **[Architecture Guide](docs/architecture.md)** - System design and data flow
- **[Data Dictionary](docs/data_dictionary.md)** - Field definitions and transformations
- **[Data Model](docs/data_model.md)** - Star schema and dimensional design
- **[Project Phases](docs/phases.md)** - Development roadmap

---

## 🛠️ Development Workflow

### Local Changes

1. Modify Spark ETL code in `spark/etl/`
2. Test locally: `python spark/etl/main.py`
3. Update dbt models in `dbt/models/`
4. Run dbt tests: `cd dbt && dbt test`

### Code Quality

This project uses GitNexus for code intelligence:
- Run impact analysis before changes: `gitnexus impact`
- Detect what changes affect: `gitnexus detect_changes`
- Explore code relationships: `gitnexus query`

### Deployment

```bash
git add .
git commit -m "feat: description of changes"
git push origin main
```

Airflow will automatically pick up DAG changes.

---

## 🐛 Troubleshooting

### Spark Memory Issues

```bash
export SPARK_LOCAL_IP=127.0.0.1
export SPARK_DRIVER_MEMORY=4g
export SPARK_EXECUTOR_MEMORY=4g
python spark/etl/main.py
```

### BigQuery Authentication

```bash
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT
```

### dbt Connection Errors

Verify `~/.dbt/profiles.yml`:
```yaml
nyc_taxi:
  target: dev
  outputs:
    dev:
      type: bigquery
      project: YOUR_GCP_PROJECT
      dataset: taxi_data
      location: US
      method: service-account
      keyfile: /path/to/service-account-key.json
```

---

## 📋 Roadmap

- [ ] Real-time streaming pipeline (Kafka → Spark Streaming)
- [ ] Machine learning models (trip demand forecasting)
- [ ] Advanced monitoring (Great Expectations, Soda)
- [ ] Multi-cloud support (AWS Redshift, Azure Synapse)
- [ ] API layer (FastAPI for analytics queries)

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👤 Author

**Khoa Lance** - [GitHub](https://github.com/lancelotviendangkhoa710)

## 🤝 Contributing

Contributions are welcome! Please follow the development workflow and ensure all tests pass before submitting pull requests.

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub Issues](https://github.com/lancelotviendangkhoa710/nyc-taxi-de-project/issues)
- Check existing documentation in `docs/`
- Review project code intelligence with GitNexus

---

**Last Updated:** July 2026