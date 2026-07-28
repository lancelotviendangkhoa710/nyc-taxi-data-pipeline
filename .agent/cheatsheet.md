# Quick Reference — AI Agent Cheat Sheet

> Copy-paste guide cho các tác vụ thường gặp nhất.

---

## Commit Nhanh

```bash
# Thêm tính năng
git commit -m "feat(<scope>): <subject>"

# Sửa bug
git commit -m "fix(<scope>): <subject>"

# Cập nhật docs
git commit -m "docs(<scope>): <subject>"

# Refactor
git commit -m "refactor(<scope>): <subject>"
```

**Scopes phổ biến:** `spark/etl`, `spark/config`, `spark/utils`, `airflow`, `dbt`, `warehouse`, `docs`, `agent`

---

## Import Pattern (Bắt Buộc)

```python
# Config — LUÔN LUÔN
from spark.config import RAW_DIR, PROCESSED_DIR, SPARK_APP_NAME
from spark.config import SPARK_CONFIGS, SPARK_MASTER

# Logger
from spark.utils.logger import get_logger
logger = get_
ogger(__name__)

# PySpark
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T
```

---

## Tạo SparkSession

```python
from spark.config import setup_java_env, SPARK_APP_NAME, SPARK_MASTER, SPARK_CONFIGS

setup_java_env()  # PHẢI gọi trước khi import SparkSession

from pyspark.sql import SparkSession

builder = SparkSession.builder.appName(SPARK_APP_NAME).master(SPARK_MASTER)
for key, val in SPARK_CONFIGS.items():
    builder = builder.config(key, val)
spark = builder.getOrCreate()
spark.sparkContext.setLogLevel("WARN")
```

---

## ETL Function Template

```python
def transform_step(df: DataFrame) -> DataFrame:
    """One-liner description."""
    logger.info("Starting transform_step, input rows=%d", df.count())
    result = (
        df
        .withColumn("new_col", F.lit("value"))
    )
    logger.info("Completed transform_step, output rows=%d", result.count())
    return result
```

---

## Derived Columns (Đã Implement)

```python
# trip_duration_min
.withColumn("trip_duration_min",
    (F.unix_timestamp("tpep_dropoff_datetime")
     - F.unix_timestamp("tpep_pickup_datetime")) / 60.0)

# tip_ratio
.withColumn("tip_ratio",
    F.when(F.col("fare_amount") > 0,
        F.col("tip_amount") / F.col("fare_amount"))
    .otherwise(F.lit(0.0)))

# pickup_date
.withColumn("pickup_date",
    F.to_date(F.col("tpep_pickup_datetime")))
```

---

## Validate Filters (Business Rules)

```python
df_validated = (
    df_raw
    .filter(F.col("trip_distance") > 0)
    .filter(F.col("fare_amount") > 0)
    .filter(F.col("tpep_dropoff_datetime") > F.col("tpep_pickup_datetime"))
    .dropna(subset=["VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime"])
)
```

---

## Write Parquet (Pattern Load)

```python
from spark.config import PROCESSED_DIR, WRITE_PARTITIONS

(df_final
 .repartition(WRITE_PARTITIONS)
 .write
 .mode("overwrite")
 .partitionBy("pickup_date")
 .parquet(str(PROCESSED_DIR)))
```

---

## Key Files Map

| Mục đích | File |
|---|---|
| Tất cả config | `spark/config.py` |
| Logging | `spark/utils/logger.py` |
| Đọc data | `spark/etl/extract.py` |
| Kiểm tra quality | `spark/etl/validate.py` |
| Transform | `spark/etl/transform.py` |
| Ghi output | `spark/etl/load.py` (TODO) |
| Run pipeline | `spark/etl/main.py` (TODO) |
| Phases roadmap | `docs/phases.md` |
| Data model | `docs/data_model.md` |
| Architecture | `docs/architecture.md` |
| AI context | `.agent/README.md` |
