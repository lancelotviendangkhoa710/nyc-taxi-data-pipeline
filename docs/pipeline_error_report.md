# NYC Taxi ETL Pipeline — Error Report & Fix Documentation

**Date:** 2026-07-29  
**Pipeline:** `spark/etl/run_pipeline.py`  
**Target:** Supabase PostgreSQL

---

## Error 1: `AnalysisException` — Column `trip_id` not found

### Symptom

```
pyspark.errors.exceptions.captured.AnalysisException: 
Cannot resolve column name "trip_id" among (VendorID, tpep_pickup_datetime, 
tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, 
store_and_fwd_flag, PULocationID, DOLocationID, payment_type, fare_amount, 
extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, 
congestion_surcharge, Airport_fee, cbd_congestion_fee, trip_duration_min, 
tip_ratio, pickup_date)
```

### Root Cause

`remove_duplicates()` in `spark/etl/transform.py` called `df.dropDuplicates(["trip_id"])`, but column `trip_id` does not exist at the transform stage. The `trip_id` column is only created later during the LOAD phase (in `load_fact_trip()`) via an MD5 hash of key fields.

### Fix

Changed `remove_duplicates()` to use all raw columns for deduplication instead of the non-existent `trip_id`:

```python
# Before (broken)
df_cleaned = df.dropDuplicates(["trip_id"])

# After (fixed)
df_cleaned = df.dropDuplicates()
```

**File:** `spark/etl/transform.py`, line 58

---

## Error 2: `BatchUpdateException` — Duplicate key on `dim_location`

### Symptom

```
java.sql.BatchUpdateException: Batch entry 0 INSERT INTO dim_location 
("location_key","zone","borough","service_zone") VALUES (1,'Newark Airport','EWR','EWR') 
was aborted: ERROR: duplicate key value violates unique constraint "dim_location_pkey"
  Detail: Key (location_key)=(1) already exists.
```

### Root Cause

`load_dim_location()` used `mode="append"` when writing to PostgreSQL. On re-runs, it attempted to INSERT rows that already existed, violating the primary key constraint. The same issue also affected `load_dim_time()` and potentially `load_fact_trip()`.

### Fix

Changed all dimension table and fact table writes to use `mode="overwrite"`, which performs a `TRUNCATE TABLE ... RESTART IDENTITY CASCADE` before inserting:

```python
# Before (broken)
self._write_to_postgres(df_location, "dim_location", mode="append")
self._write_to_postgres(df_time, "dim_time", mode="append")
self.load_fact_trip(df_processed, mode="append")

# After (fixed)
self._write_to_postgres(df_location, "dim_location", mode="overwrite")
self._write_to_postgres(df_time, "dim_time", mode="overwrite")
self.load_fact_trip(df_processed, mode="overwrite")
```

**File:** `spark/etl/load_warehouse.py`, lines 145, 207, 262

### Why `overwrite` is safe here

The `_write_to_postgres()` method implements manual overwrite: it connects via `psycopg2`, runs `TRUNCATE TABLE ... CASCADE`, then uses Spark JDBC in `append` mode. This ensures:

1. Foreign key constraints are properly cascaded
2. No orphaned dimension references
3. Pipeline is idempotent (safe to re-run)

---

## Summary of Changes

| File | Change | Reason |
| ------ | -------- | -------- |
| `spark/etl/transform.py` | `dropDuplicates(["trip_id"])` → `dropDuplicates()` | `trip_id` column doesn't exist at transform stage |
| `spark/etl/load_warehouse.py` | `dim_location` mode `append` → `overwrite` | Duplicate PK on re-run |
| `spark/etl/load_warehouse.py` | `dim_time` mode `append` → `overwrite` | Duplicate PK on re-run |
| `spark/etl/load_warehouse.py` | `fact_trip` mode `append` → `overwrite` | Duplicate data on re-run |

---

## Pipeline Result (after fixes)

- **Extract:** 55,847,357 raw records from 14 parquet files (2025-01 to 2026-02)
- **Transform:** 39,740,462 records after cleaning (removed 16,106,895 outliers)
- **Load:** All dimension tables (dim_vendor, dim_payment, dim_rate, dim_location, dim_time) and fact_trip loaded to Supabase PostgreSQL
