# 🎨 PHASE 3A: Visual Architecture Guide

---

## 📊 3-Layer Architecture

```
┌────────────────────────────────┐
│  PostgreSQL WAREHOUSE          │
│  fact_trip (100M) | dim_*      │
└────────────┬───────────────────┘
             ↓ source()
┌────────────────────────────────┐
│  STAGING (VIEW) ✅ Đã Có      │
│  stg_trip, stg_vendor, ...     │
│  Purpose: Làm sạch, lọc        │
└────────────┬───────────────────┘
             ↓ ref()
┌────────────────────────────────┐
│  INTERMEDIATE (VIEW) ❌ Phase 3A│
│  int_trips_with_dimensions     │
│  Purpose: JOIN + aggregate     │
└────────────┬───────────────────┘
             ↓ ref()
┌────────────────────────────────┐
│  MARTS (TABLE) ❌ Phase 3A     │
│  fct_trip_summary (indexed)    │
│  Purpose: BI-ready tables      │
└────────────┬───────────────────┘
             ↓
┌────────────────────────────────┐
│  BI TOOLS (Metabase)           │
│  Dashboards & Reports          │
└────────────────────────────────┘
```

---

## 📈 Data Transformation Flow

```
Raw Parquet (100M rows)
    ↓ (Spark ETL)
PostgreSQL (90M rows, 24 cols)
    ↓ (dbt staging - filter)
Staging Views (90M rows)
    ↓ (dbt intermediate - JOIN)
Enriched Views (90M rows, 30+ cols)
    ↓ (dbt marts - materialize)
Analytics Tables (indexed, fast)
    ↓ (BI Tools)
Dashboards & Insights 📊
```

---

## 🔄 Dependencies (Lineage)

```
fact_trip → stg_trip
              ↓
dim_vendor → stg_vendor
              ↓
         int_trips_with_dimensions
              ↓
         fct_trip_summary (TABLE)
              ↓
         Metabase Dashboard

dbt tracks this automatically!
dbt run executes in correct order
dbt test validates at each layer
```

---

## ⏱️ Query Performance

```
BEFORE Phase 3A:
SELECT vendor_name, COUNT(*)
FROM fact_trip f (90M rows)
LEFT JOIN dim_vendor v ON ...
LEFT JOIN dim_location l ON ...
LEFT JOIN dim_time t ON ...
GROUP BY vendor_name

Time: 5-10 seconds ❌


AFTER Phase 3A:
SELECT vendor_name, trip_count
FROM fct_vendor_daily_metrics (730 rows)

Time: 100ms ✅
Improvement: 50-100x faster!
```

---

## 🏗️ Phase 3A Checklist

**Intermediate Layer (4-6 hours):**
- [ ] int_trips_with_dimensions.sql (JOIN tables)
- [ ] int_trip_metrics_by_vendor.sql (GROUP BY)
- [ ] _int_models.yml (tests + docs)

**Marts Layer (4-6 hours):**
- [ ] fct_trip_summary.sql (TABLE, indexed)
- [ ] fct_vendor_daily_metrics.sql (TABLE)
- [ ] _mart_models.yml (tests + docs)

**Testing (2-3 hours):**
- [ ] dbt run
- [ ] dbt test
- [ ] Verify PostgreSQL tables

**Result:**
- ✅ 3 intermediate views
- ✅ 3 marts tables
- ✅ ~20 tests
- ✅ Full docs

---

## 📋 File Structure After Phase 3A

```
dbt/models/
├─ staging/ (✅ exists)
│  └─ stg_trip.sql, stg_vendor.sql, ...
├─ intermediate/ (❌ NEW)
│  ├─ int_trips_with_dimensions.sql
│  ├─ int_trip_metrics_by_vendor.sql
│  └─ _int_models.yml
└─ marts/ (❌ NEW)
   ├─ fct_trip_summary.sql
   ├─ fct_vendor_daily_metrics.sql
   └─ _mart_models.yml

New files: 8
New lines: ~500
```

---

## 🎯 Why Phase 3A Matters

| Problem | Solution |
|---------|----------|
| Analysts write complex JOIN queries | Intermediate does JOINs |
| Queries are slow (100M rows) | Marts tables are indexed |
| Logic scattered | Centralized in dbt layers |
| No data quality checks | 20+ tests validate |

---

## 💡 Simple Analogy

```
STAGING    = Rửa rau, cắt thịt ✨
INTERMEDIATE = Nấu ăn, kết hợp ingredients 👨‍🍳
MARTS      = Bộ phận bán lẻ, bày biện 🛒
BI TOOLS   = Nhà hàng, phục vụ khách 🍽️
```

---

## ✅ After Phase 3A Complete

You will have:
- ✅ Complete dbt transformation layers
- ✅ Tested & documented models
- ✅ BI-ready tables
- ✅ Performance optimized (indexed)
- ✅ Analysts can query marts directly

---

**Ready to start Phase 3A?** 🚀
