# Git Commit Standards — NYC Taxi Project

> Mọi commit PHẢI tuân theo **Conventional Commits** specification.
> Reference: https://www.conventionalcommits.org/

---

## Cấu Trúc Commit Message

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### Ví Dụ Đầy Đủ

```
feat(spark/etl): add transform.py with derived columns

Implement add_derived_columns() function:
- trip_duration_min: calculated from pickup/dropoff timestamps
- tip_ratio: tip_amount / fare_amount (0 when fare = 0)
- pickup_date: date-only column for partitioning

Refs #12
```

---

## 1. Type (Bắt Buộc)

| Type | Khi Dùng | Ví Dụ |
|---|---|---|
| `feat` | Thêm tính năng mới | `feat(etl): add load.py to write processed parquet` |
| `fix` | Sửa bug | `fix(transform): handle zero fare_amount in tip_ratio calc` |
| `refactor` | Refactor code, không thêm feature | `refactor(config): centralize spark settings` |
| `docs` | Chỉ thay đổi documentation | `docs(phases): update phase 2 task status` |
| `test` | Thêm hoặc sửa tests | `test(validate): add null check unit tests` |
| `chore` | Maintenance tasks | `chore(deps): add pyspark 3.5 to requirements` |
| `style` | Format, whitespace (không đổi logic) | `style(extract): reorder imports` |
| `perf` | Cải thiện performance | `perf(etl): reduce partitions from 200 to 8` |
| `ci` | CI/CD changes | `ci: add github actions workflow` |
| `build` | Build system, dependencies | `build: add Dockerfile for spark environment` |
| `revert` | Revert commit trước | `revert: revert "feat(etl): add load.py"` |

---

## 2. Scope (Nên Có)

Scope chỉ rõ phần nào của dự án bị ảnh hưởng:

| Scope | Dùng cho |
|---|---|
| `spark/etl` | Files trong `spark/etl/` |
| `spark/config` | `spark/config.py` |
| `spark/utils` | `spark/utils/` |
| `airflow` | Airflow DAGs |
| `dbt` | dbt models |
| `warehouse` | BigQuery schemas/DDL |
| `docs` | Documentation files |
| `docker` | Docker configs |
| `notebooks` | Jupyter notebooks |
| `data` | Data scripts, không phải data files |
| `deps` | Dependencies (requirements.txt) |
| `agent` | Files trong `.agent/` |

---

## 3. Subject (Bắt Buộc)

**Quy tắc:**
- ✅ Viết thường (lowercase) — `add transform logic`
- ✅ Động từ nguyên thể (imperative mood) — `add`, `fix`, `update`, `remove`
- ✅ Ngắn gọn, rõ ràng — tối đa **72 ký tự**
- ✅ Không kết thúc bằng dấu chấm `.`
- ❌ Không viết hoa chữ đầu — `Add transform logic` ❌
- ❌ Không dùng quá khứ — `added transform logic` ❌
- ❌ Không dùng `-ing` — `adding transform logic` ❌

**Imperative mood examples:**
```
add / fix / update / remove / refactor / implement / create
extract / transform / load / validate / configure / enable
```

---

## 4. Body (Tùy Chọn — Nên Dùng cho feat/fix/refactor)

Giải thích **tại sao** (why) và **như thế nào** (how), không phải **cái gì** (what) — cái gì đã thấy trong subject:

```
feat(spark/etl): implement validate.py data quality checks

Add row-level validation before transform stage:
- Filter out trips with trip_distance <= 0 (invalid)
- Filter out trips with fare_amount <= 0 (invalid)
- Drop rows where VendorID or pickup_datetime is null
- Log count of rows dropped at each step

Business rule: trips with distance=0 are test/cancelled trips
and should not appear in revenue analysis.
```

**Body rules:**
- Cách subject bằng 1 dòng trống
- Mỗi dòng tối đa **72 ký tự**
- Dùng bullet points cho danh sách thay đổi
- Giải thích business reasoning nếu cần

---

## 5. Footer (Tùy Chọn)

```
Refs #<issue_number>      ← Liên kết issue
Closes #<issue_number>    ← Đóng issue
BREAKING CHANGE: <desc>   ← Breaking changes (dùng ! sau type)
Co-authored-by: Name <email>
```

---

## 6. Breaking Changes

Thêm `!` sau type hoặc dùng `BREAKING CHANGE:` trong footer:

```
refactor!(spark/config)!: rename DATA_PATH to RAW_DIR

BREAKING CHANGE: DATA_PATH variable renamed to RAW_DIR in config.py.
All ETL files must update their imports from:
  from spark.config import DATA_PATH
to:
  from spark.config import RAW_DIR
```

---

## 7. Ví Dụ Thực Tế Cho Dự Án Này

```bash
# Phase 2 — Spark ETL
feat(spark/etl): add extract.py to read yellow taxi parquet files
feat(spark/etl): implement validate.py with data quality filters
feat(spark/etl): add transform.py with derived column calculations
feat(spark/etl): create load.py to write processed parquet output
feat(spark/etl): add main.py as etl orchestration entry point

# Fixes
fix(transform): handle division by zero in tip_ratio calculation
fix(extract): use glob pattern instead of hardcoded filename

# Config & Utils
feat(spark/config): add bigquery connection settings
feat(spark/utils): add get_logger factory function

# Documentation
docs(agent): add commit standards and workflow guides
docs(phases): mark phase 2 extract task as completed
docs(architecture): add bigquery layer to pipeline diagram

# Phase 3 — Warehouse
feat(warehouse): add bigquery star schema DDL scripts
feat(spark/etl): add load_warehouse.py for bigquery ingestion

# Phase 4 — dbt
feat(dbt): init dbt project with bigquery adapter
feat(dbt/staging): add stg_yellow_trips staging model
feat(dbt/mart): add mart_revenue analytics model
test(dbt): add not_null tests for fact_trip key columns

# Maintenance
chore(deps): add dbt-bigquery and google-cloud-bigquery deps
chore(.gitignore): add credentials and .env to ignored files
refactor(spark/etl): extract common validation logic to utils
```

---

## 8. Multi-line Commit (Git Command)

```bash
# Cách 1: Dùng editor mặc định (khuyến nghị)
git commit

# Cách 2: -m với escape cho multi-line (PowerShell)
git commit -m "feat(spark/etl): add transform.py with derived columns`n`nImplement add_derived_columns() function:`n- trip_duration_min`n- tip_ratio`n- pickup_date"

# Cách 3: Viết vào file rồi dùng -F
git commit -F commit_message.txt
```

---

## 9. Commit Checklist

Trước khi commit, kiểm tra:

- [ ] Type đúng không? (`feat`, `fix`, `docs`, ...)
- [ ] Scope có không? (`spark/etl`, `docs`, ...)
- [ ] Subject lowercase, imperative, ≤72 ký tự?
- [ ] Không kết thúc bằng dấu chấm?
- [ ] Body giải thích **tại sao** (nếu cần)?
- [ ] Không commit file `.env`, credentials, `data/raw/*.parquet`?
- [ ] Code đã pass basic check/lint?

---

## 10. Commit Antipatterns (Tuyệt Đối Tránh)

```bash
# ❌ BAD — Quá chung chung
git commit -m "update files"
git commit -m "fix bug"
git commit -m "changes"
git commit -m "wip"
git commit -m "asdf"

# ❌ BAD — Quá khứ, viết hoa
git commit -m "Fixed the transform bug"
git commit -m "Added new feature"

# ❌ BAD — Không có type
git commit -m "add transform.py"

# ❌ BAD — Commit quá nhiều thứ một lúc
git commit -m "add extract, transform, load, fix bugs, update docs"

# ✅ GOOD — Mỗi commit một mục đích rõ ràng
git commit -m "feat(spark/etl): add extract.py to read parquet files"
git commit -m "feat(spark/etl): add transform.py with derived columns"
git commit -m "docs(phases): update phase 2 extract task status"
```
