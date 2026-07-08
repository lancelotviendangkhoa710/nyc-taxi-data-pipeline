# Architectural Decisions — NYC Taxi Project

> Record các quyết định thiết kế đã được thống nhất.
> AI KHÔNG được tự thay đổi những quyết định này mà không hỏi user.

---

## ADR-001: Dùng PySpark Local Mode (Không Cluster)

**Trạng thái:** ✅ Confirmed

**Quyết định:** Chạy Spark ở `local[*]` mode trên máy dev Windows.

**Lý do:**
- Dự án học tập, không cần distributed cluster thật
- Tiết kiệm chi phí (free)
- Phát triển và debug dễ hơn

**Hệ quả:** Khi scale lên production, cần đổi `SPARK_MASTER` trong config.

---

## ADR-002: Google BigQuery Sandbox Làm Warehouse

**Trạng thái:** ✅ Confirmed

**Quyết định:** Dùng BigQuery Sandbox (miễn phí, không cần billing) thay vì PostgreSQL local.

**Lý do:**
- Portfolio value cao hơn (cloud-native)
- BigQuery là industry standard cho analytics
- Sandbox mode hoàn toàn miễn phí

**Trade-offs:**
- Cần GCP account và setup Service Account
- Spark cần BigQuery connector JAR
- Không dùng được offline

**Credentials:** Service Account JSON key → `warehouse/credentials/` (gitignored)

---

## ADR-003: ETL State Control — Metadata Table (Phase 3+)

**Trạng thái:** ⏳ Planned (triển khai sau Phase 3)

**Quyết định:** Dùng metadata table trong database để track trạng thái xử lý file.

**Schema metadata table:**
```sql
CREATE TABLE etl_file_log (
    id          SERIAL PRIMARY KEY,
    filename    TEXT NOT NULL,
    status      TEXT CHECK (status IN ('processing', 'done', 'failed')),
    processed_at TIMESTAMP,
    row_count   INTEGER,
    error_msg   TEXT
);
```

**Hiện tại (Phase 2):** Chưa implement, ETL chạy full reprocess mỗi lần.

---

## ADR-004: Star Schema Cho Data Warehouse

**Trạng thái:** ✅ Confirmed

**Quyết định:** Dùng Star Schema với 1 bảng Fact và nhiều bảng Dimension.

**Lý do:**
- Tối ưu cho analytics queries
- Dễ hiểu, phù hợp business questions
- Standard trong industry

**Schema:** Xem `docs/data_model.md`

---

## ADR-005: dbt Layers — 3 Tầng

**Trạng thái:** ✅ Confirmed (implement ở Phase 4)

```
staging/        → 1-1 với source tables, rename, cast types
intermediate/   → Business logic, joins
mart/           → Final tables cho dashboard
```

**Naming convention dbt:**
- Staging: `stg_<source>_<table>` (e.g., `stg_bigquery_yellow_trips`)
- Intermediate: `int_<description>` (e.g., `int_trips_enriched`)
- Mart: `mart_<subject>` (e.g., `mart_revenue`, `mart_trips`)

---

## ADR-006: Derived Columns — Tính Trong ETL, Không Trong dbt

**Trạng thái:** ✅ Confirmed

**Quyết định:** `trip_duration_min`, `tip_ratio`, `pickup_date` được tính trong Spark ETL (transform.py), không phải trong dbt.

**Lý do:**
- Giảm compute trong warehouse
- Data vào BigQuery đã clean và enriched
- dbt tập trung vào business aggregations

---

## ADR-007: Partitioning Strategy

**Trạng thái:** ✅ Confirmed

**Quyết định:** Partition processed parquet theo `pickup_date`.

**Lý do:**
- Phần lớn queries filter theo ngày/tháng
- Partition pruning giảm scan data
- Nhất quán với time-based analytics

---

## Quy Trình Thêm Decision Mới

Khi cần quyết định kiến trúc mới:
1. Thảo luận với user
2. Ghi vào file này với format `ADR-NNN`
3. Commit: `docs(agent): add ADR-NNN <decision title>`
