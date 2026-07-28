# ETL Workflow & Current Phase — NYC Taxi Project

> File này mô tả workflow hiện tại, trạng thái các task, và hướng dẫn cho AI về next steps.

---

## Phase Hiện Tại: Phase 2 — Spark ETL ⏳

### Tổng Quan ETL Flow

```
data/raw/*.parquet
       ↓
   extract.py          ← Đọc file parquet bằng PySpark
       ↓
   validate.py         ← Lọc dữ liệu sai/null/outlier
       ↓
   transform.py        ← Clean + thêm derived columns
       ↓
   load.py             ← Ghi ra data/processed/ (TODO)
       ↓
data/processed/*.parquet
```

**Orchestration entry point:** `spark/etl/main.py` (TODO)

---

## Task Status — Phase 2

### Đã Hoàn Thành ✅

| Task | File | Ghi Chú |
|---|---|---|
| Setup config | `spark/config.py` | Paths, Spark settings, PG/BQ config |
| Setup logger | `spark/utils/logger.py` | Logger factory |
| ETL Extract | `spark/etl/extract.py` | Đọc parquet, filter columns |
| ETL Validate | `spark/etl/validate.py` | Null checks, outlier filters |
| ETL Transform | `spark/etl/transform.py` | `trip_duration_min`, `tip_ratio`, `pickup_date` |

### Còn Lại ⏳

| Task | File Cần Tạo | Ưu Tiên |
|---|---|---|
| ETL Load | `spark/etl/load.py` | HIGH |
| ETL Main | `spark/etl/main.py` | HIGH |
| ETL Test | `tests/test_transform.py` | MEDIUM |

---

## Cách ETL Hoạt Động Chi Tiết

### Extract (`spark/etl/extract.py`)
```python
# Input: data/raw/yellow_tripdata_YYYY-MM.parquet
# Output: DataFrame với SELECTED_COLUMNS từ config.py
```
- Đọc tất cả parquet files matching `YELLOW_TAXI_PATTERN`
- Chỉ giữ lại columns trong `SELECTED_COLUMNS` (config.py)
- Log số records đọc được

### Validate (`spark/etl/validate.py`)
```python
# Input: raw DataFrame
# Output: DataFrame đã lọc, log số rows dropped
```
Các business rules:
- `trip_distance > 0` — loại bỏ chuyến đi không di chuyển
- `fare_amount > 0` — loại bỏ fare không hợp lệ
- Không null: `VendorID`, `tpep_pickup_datetime`, `tpep_dropoff_datetime`
- `tpep_dropoff_datetime > tpep_pickup_datetime` — time phải hợp lệ

### Transform (`spark/etl/transform.py`)
```python
# Input: validated DataFrame
# Output: enriched DataFrame với derived columns
```
Derived columns:
- `trip_duration_min = (unix(dropoff) - unix(pickup)) / 60`
- `tip_ratio = tip_amount / fare_amount` (0 nếu fare = 0)
- `pickup_date = to_date(tpep_pickup_datetime)`

### Load (`spark/etl/load.py`) — TODO
```python
# Input: transformed DataFrame
# Output: parquet files tại data/processed/
```
Requirements:
- Partition by `pickup_date` để query nhanh
- Dùng `WRITE_PARTITIONS` từ config
- Overwrite mode (idempotent)
- Log số rows ghi ra

### Main (`spark/etl/main.py`) — TODO
```python
# Entry point chạy toàn bộ ETL pipeline
# python -m spark.etl.main
```
Flow:
1. `setup_java_env()` — setup env vars
2. Tạo SparkSession với settings từ config
3. `extract()` → `validate()` → `transform()` → `load()`
4. Log summary (rows in, rows out, thời gian)

---

## Khi AI Được Yêu Cầu Tạo Code

### Checklist Trước Khi Viết Code

1. **Import config** — Không hardcode paths
   ```python
   from spark.config import RAW_DIR, PROCESSED_DIR, SPARK_APP_NAME
   ```

2. **Import logger** — Không dùng print()
   ```python
   from spark.utils.logger import get_logger
   logger = get_logger(__name__)
   ```

3. **Type hints** — Tất cả functions có type hints

4. **Docstrings** — Tất cả functions/classes có docstring

5. **Error handling** — Wrap risky operations trong try/except

### Pattern Cho ETL Functions

```python
def function_name(df: DataFrame, ...) -> DataFrame:
    """
    Mô tả mục đích.

    Args:
        df: Input DataFrame.
        ...: Mô tả params.

    Returns:
        DataFrame đã xử lý.
    """
    logger.info("Starting <function_name>, rows=%d", df.count())

    result = (
        df
        .withColumn(...)
        .filter(...)
    )

    logger.info("Completed <function_name>, rows=%d", result.count())
    return result
```

---

## Next Phase Preview

**Phase 3: Warehouse (BigQuery)**
- Tạo GCP Project và BigQuery Sandbox
- Viết DDL schema cho FACT_TRIP và DIM_* tables
- Viết `spark/etl/load_warehouse.py` — load lên BigQuery
- Config: GCP credentials, BigQuery connector JAR

**Phase 4: dbt**
- Init dbt project với `dbt-bigquery` adapter
- 3 layers: staging → intermediate → mart

Xem roadmap đầy đủ: `docs/phases.md`
