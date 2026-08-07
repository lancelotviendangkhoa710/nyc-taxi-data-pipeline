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

## Progress Tracking Rule 📊

> **Rule này định nghĩa khi nào AI sẽ gợi ý cập nhật document tiến độ công việc.**

### Khi Nào Gợi Ý Cập Nhật?

AI sẽ tự động gợi ý cập nhật `docs/progress/PROGRESS.md` trong các tình huống sau:

1. **Hoàn thành một task từ TODO → Done**
   - Ví dụ: `spark/etl/load.py` hoàn thành
   - Gợi ý: Thêm vào mục "Milestones Completed" với date & notes

2. **Hoàn thành một Phase**
   - Ví dụ: Phase 2 hoàn thành 100%
   - Gợi ý: Cập nhật "Current Status" → Overall Progress, Current Phase

3. **Phát hiện Blocker hoặc Risk mới**
   - Ví dụ: Java config issue, PostgreSQL connection failure
   - Gợi ý: Thêm vào "Blockers & Risks" table

4. **Có thay đổi lớn trong Performance Metrics**
   - Ví dụ: Execution time giảm từ 15m → 8m do optimization
   - Gợi ý: Cập nhật "Performance Metrics" table

### Format Cập Nhật

AI sẽ gợi ý theo format này:

```markdown
### [Date - HH:MM]
- **Action:** Mô tả ngắn gọn
- **Files:** Files bị ảnh hưởng (nếu có)
- **Next:** Next step là gì
```

### Quy Trình Approval

**Hybrid Model: AI Suggest → Human Review → Approve**

1. **AI Suggest** (bước 1)
   - AI tạo draft update cho `docs/progress/PROGRESS.md`
   - Hiển thị cho người dùng (không tự động commit)
   - Format: Markdown snippet ready to copy-paste

2. **Human Review** (bước 2)
   - Người dùng đọc gợi ý
   - Sửa/chỉnh lại nếu cần (thêm chi tiết, sửa date, v.v.)
   - Hoặc từ chối nếu không phù hợp

3. **Approve & Save** (bước 3)
   - Nếu đồng ý: Người dùng cho phép AI save vào file
   - Nếu từ chối: AI bỏ qua, không update

### Ví Dụ

**Tình huống:** Vừa hoàn thành `spark/etl/load.py`

**AI Gợi Ý:**
```markdown
Tôi phát hiện bạn vừa hoàn thành spark/etl/load.py. 
Đây là gợi ý cập nhật PROGRESS.md:

### 2026-08-10 14:30
- **Action:** Completed ETL Load module — write partitioned Parquet
- **Files:** spark/etl/load.py (NEW)
- **Next:** Create main.py orchestration

[Table Update]
| 6 | Load module | 2026-08-10 | ✅ Done | Partition by pickup_date, overwrite mode |
```

**Bạn có muốn save update này không? (Yes/No)**

### Khi Nào KHÔNG Gợi Ý

- Sửa lỗi nhỏ trong code (typo, formatting) — không cần update
- Thay đổi comments/docstrings — không cần update
- Test run không được lưu — không cần update
- Chỉ read file, không thay đổi — không cần update

### File Tham Khảo

- **Template:** `docs/progress/PROGRESS.md`
- **Current Status:** Xem mục "Current Status" trong PROGRESS.md
- **Related:** `.agent/CURRENT_STATE.md` (workflow state)

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
