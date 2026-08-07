# Project Progress Tracking — NYC Taxi Data Engineering

> **File này được cập nhật định kỳ sau mỗi khi hoàn thành task/commit mới.**
> **Trigger:** AI gợi ý → Người dùng review → Approve trước khi lưu

---

## 📊 Current Status (Trạng thái hiện tại)

| Thuộc tính | Giá trị |
|-----------|--------|
| **Current Phase** | Phase 2 — Spark ETL |
| **Overall Progress** | 40% |
| **Last Updated** | 2026-08-07 |
| **Last Completed** | Setup config, logger, extract, validate, transform |

---

## ✅ Milestones Completed

| # | Milestone | Date | Status | Notes |
|---|-----------|------|--------|-------|
| 1 | Project setup & config | 2026-07-08 | ✅ Done | `spark/config.py` with centralized settings |
| 2 | Logger setup | 2026-07-08 | ✅ Done | `spark/utils/logger.py` factory pattern |
| 3 | Extract module | 2026-07-15 | ✅ Done | Read parquet, filter columns from config |
| 4 | Validate module | 2026-07-20 | ✅ Done | Data quality checks (nulls, ranges, outliers) |
| 5 | Transform module | 2026-07-25 | ✅ Done | Derived columns (trip_duration_min, tip_ratio, pickup_date) |

---

## 🔄 Current Tasks (In Progress)

| # | Task | Assignee | Status | Blockers | Target Date |
|---|------|----------|--------|----------|-------------|
| - | _(None at the moment)_ | - | - | - | - |

---

## 📋 Upcoming Tasks (TODO)

| # | Task | Priority | Effort | Depends On | Target Date |
|---|------|----------|--------|-----------|-------------|
| 1 | ETL Load module | HIGH | 4h | Transform ✅ | 2026-08-10 |
| 2 | ETL Main orchestration | HIGH | 3h | Load | 2026-08-12 |
| 3 | Unit tests | MEDIUM | 6h | All ETL modules | 2026-08-15 |
| 4 | Setup BigQuery warehouse | HIGH | 8h | Phase 2 completion | 2026-08-20 |
| 5 | Load to warehouse module | HIGH | 5h | BigQuery setup | 2026-08-25 |

---

## ⚠️ Blockers & Risks

| ID | Issue | Severity | Status | Resolution | Owner |
|----|-------|----------|--------|-----------|-------|
| B1 | Java environment setup on Windows | MEDIUM | 🟢 Resolved | Hadoop binaries configured in PATH | Dev |
| R1 | PostgreSQL connectivity | LOW | 🟢 Mitigated | Docker Compose setup working | Infra |

---

## 📈 Performance Metrics

| Metric | Value | Date | Notes |
|--------|-------|------|-------|
| Raw data rows ingested | 50M+ | 2026-07-15 | Yellow Taxi data (6 months) |
| Data quality pass rate | 85% | 2026-07-25 | After validation filters |
| Execution time (ETL pipeline) | ~15 min | 2026-07-25 | Local Spark mode `local[*]` |
| Disk space (processed data) | 2.5GB | 2026-07-26 | Partitioned Parquet format |

---

## 🗺️ Phase Roadmap

```
Phase 1: Data Ingestion ✅
    └─ Fetch NYC TLC Parquet files
    └─ Setup raw data directory

Phase 2: Spark ETL (🔄 In Progress)
    └─ Extract: Read & filter columns ✅
    └─ Validate: Data quality checks ✅
    └─ Transform: Derived columns ✅
    └─ Load: Write partitioned Parquet 📋 TODO
    └─ Main: Orchestrate pipeline 📋 TODO

Phase 3: Warehouse & BigQuery 📋
    └─ Setup GCP project & BigQuery
    └─ Create star schema (FACT_TRIP, DIM_*)
    └─ Load to warehouse

Phase 4: dbt & Analytics 📋
    └─ Init dbt project
    └─ Staging layer → Intermediate → Mart
    └─ Create analytics views
```

---

## 📝 Recent Updates

### 2026-08-07
- **Action:** Created Progress Tracking rule and document
- **Files:** `.agent/workflow.md`, `.agent/README.md`, `docs/progress/PROGRESS.md`
- **Next:** Implement ETL Load module

### 2026-07-25
- **Completed:** Transform module with derived columns
- **Files:** `spark/etl/transform.py`
- **Next:** Create Load module

### 2026-07-20
- **Completed:** Validate module with data quality checks
- **Files:** `spark/etl/validate.py`
- **Next:** Transform module

---

## 🎯 Key Notes

- **Architecture:** Batch ETL pipeline (Spark → PostgreSQL)
- **Tech Stack:** Python 3.12, PySpark, PostgreSQL, Docker
- **Development Mode:** Local Spark mode `local[*]`
- **Code Standards:** Type hints, docstrings, error handling, logging
- **Git Workflow:** Feature branches → PR → Merge to main

---

## 📚 Related Documents

- `.agent/workflow.md` — Detailed ETL workflow
- `docs/architecture.md` — System architecture
- `docs/data_model.md` — Star schema design
- `docs/IMPLEMENT_PLAN.md` — Feature implementation plans
- `.agent/README.md` — AI agent instructions
