# Coding Conventions — NYC Taxi Project

> Mọi AI agent PHẢI tuân thủ các quy tắc này khi viết hoặc sửa code.

---

## 1. Language & Style

| Rule | BAD ❌ | GOOD ✅ |
|---|---|---|
| snake_case cho biến, hàm | `tripData`, `vendorID` | `trip_data`, `vendor_id` |
| snake_case cho file | `extractData.py` | `extract.py` |
| UPPER_CASE cho constants | `max_rows = 100` | `MAX_ROWS = 100` |
| PascalCase cho class | `sparkSession` | `SparkSession` |
| Docstrings bắt buộc | Hàm không có doc | Mọi function/class có docstring |
| Type hints | `def fn(x):` | `def fn(x: str) -> int:` |

---

## 2. File Organization Rules

### Không Được Làm
- ❌ Hardcode đường dẫn tuyệt đối (`"C:/data/..."`)
- ❌ Đặt business logic vào notebook (`.ipynb`)
- ❌ Lặp code — nếu dùng 2+ lần, tạo hàm trong `utils/`
- ❌ Import `*` (`from pyspark.sql.functions import *`)
- ❌ Dùng `print()` thay `logger` trong production code
- ❌ Commit file `.env` hoặc credentials JSON

### Phải Làm
- ✅ Tất cả paths → import từ `spark/config.py`
- ✅ Logging → dùng `spark/utils/logger.py`
- ✅ Explicit imports (`from pyspark.sql import functions as F`)
- ✅ Modular code — mỗi file một responsibility
- ✅ Xử lý exception với meaningful messages

---

## 3. Python File Template

```python
"""
spark/etl/<module_name>.py
--------------------------
<Mô tả ngắn mục đích file này>.

Author: NYC Taxi Project
Phase: <Phase số>
"""

import logging
from pathlib import Path
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from spark.config import RAW_DIR, PROCESSED_DIR  # Luôn import từ config

logger = logging.getLogger(__name__)


def function_name(param: type) -> return_type:
    """
    Mô tả ngắn hàm.

    Args:
        param: Mô tả tham số.

    Returns:
        Mô tả return value.

    Raises:
        ValueError: Khi nào raise error.
    """
    ...
```

---

## 4. PySpark Conventions

```python
# ✅ GOOD — Explicit import alias
from pyspark.sql import functions as F
from pyspark.sql import types as T

# Tên biến DataFrame
df_raw       = ...   # raw input
df_validated = ...   # sau validate
df_cleaned   = ...   # sau clean/filter
df_enriched  = ...   # sau thêm derived columns
df_final     = ...   # ready to write

# Method chaining — line break sau mỗi transformation
df_result = (
    df_raw
    .filter(F.col("trip_distance") > 0)
    .withColumn("trip_duration_min",
        (F.unix_timestamp("tpep_dropoff_datetime")
         - F.unix_timestamp("tpep_pickup_datetime")) / 60)
    .dropna(subset=["VendorID", "tpep_pickup_datetime"])
)
```

---

## 5. Configuration Rules

```python
# spark/config.py là SINGLE SOURCE OF TRUTH
# ⛔ NEVER DO THIS in etl/*.py:
DATA_PATH = "C:/Users/user/data/raw/"

# ✅ ALWAYS DO THIS:
from spark.config import RAW_DIR, PROCESSED_DIR, SPARK_APP_NAME
```

**Sensitive values — dùng os.getenv:**
```python
import os
PG_PASSWORD = os.getenv("PG_PASSWORD", "")  # Default rỗng, không default password
GCP_KEY_PATH = os.getenv("GCP_SERVICE_ACCOUNT_PATH", "")
```

---

## 6. Logging Standards

```python
from spark.utils.logger import get_logger
logger = get_logger(__name__)

# Levels:
logger.info("ETL started: reading %d files", file_count)  # Progress
logger.warning("Null values found in column: %s", col_name)  # Soft issue
logger.error("Failed to read file: %s", filepath)  # Hard error
logger.debug("Schema: %s", df.schema.json())  # Dev only

# ⛔ KHÔNG dùng print() trong module code
# ✅ print() chỉ OK trong notebooks
```

---

## 7. Error Handling

```python
# ✅ Meaningful errors với context
try:
    df = spark.read.parquet(str(RAW_DIR))
except Exception as e:
    logger.error("Failed to read parquet from %s: %s", RAW_DIR, e)
    raise RuntimeError(f"ETL Extract failed: {e}") from e

# ✅ Validate early, fail fast
def validate_columns(df: DataFrame, required: list[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
```

---

## 8. Testing & Quality

- Unit tests: `tests/` thư mục (tạo nếu chưa có)
- Mỗi ETL function nên có test cơ bản
- Dùng `pytest` và `pyspark` local session cho tests
- Data quality checks nằm trong `spark/etl/validate.py`

---

## 9. Notebooks vs Modules

| Notebook (`.ipynb`) | Module (`.py`) |
|---|---|
| EDA, exploration, research | Production logic |
| Một lần dùng | Reusable |
| `print()`, quick plots | `logger`, structured output |
| `notebooks/` directory | `spark/`, `airflow/`, `dbt/` |
