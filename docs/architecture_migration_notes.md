# Tài liệu kỹ thuật: Migration PostgreSQL → BigQuery + dbt

---

## 1. Tại sao PostgreSQL tự sinh được `dim_time`

### Luồng cũ

```
Raw Parquet → Spark ETL → df_transformed (còn sống trong memory JVM)
                                │
                    YellowTaxiWarehouseLoader
                        ├── load_dim_vendor()    ← static list
                        ├── load_dim_time(df)    ← NHẬN df ← chìa khóa
                        └── load_fact_trip(df)   ← NHẬN df
```

### Cơ chế `load_dim_time`

```python
def load_dim_time(self, df_processed: DataFrame) -> None:
    pickup  = df_processed.select(F.col("tpep_pickup_datetime").alias("ts"))
    dropoff = df_processed.select(F.col("tpep_dropoff_datetime").alias("ts"))
    df_time = pickup.union(dropoff).distinct()
    df_time = df_time.withColumn("time_key",
        F.date_format("ts", "yyyyMMddHH").cast("long"))
    self._write_to_postgres(df_time, "dim_time")
```

**Tại sao hoạt động:** DataFrame `df_transformed` vẫn sống trong memory JVM.
`load_dim_time` nhận chính cái đó → không đọc lại từ disk → toàn bộ là một
Spark job liên tục → ghi thẳng vào PostgreSQL qua JDBC.

**Bản chất:** PostgreSQL là điểm đến cuối duy nhất. Spark tính xong ghi thẳng.
Không có tầng trung gian nào.

---

## 2. Tại sao BigQuery không làm được như vậy

### Kiến trúc thay đổi căn bản

```
Cũ (PostgreSQL):
Spark ──────────────────────────────▶ PostgreSQL
      df còn trong memory → dùng luôn  (JDBC direct write)

Mới (BigQuery):
Spark ──▶ local Parquet ──▶ BQ Python client ──▶ BigQuery
          (ghi xuống disk)   (upload HTTP)
```

**Vấn đề cốt lõi:** BigQuery không có JDBC connector. `google-cloud-bigquery`
Python client chỉ nhận file từ local disk hoặc GCS URI — không biết Spark
DataFrame là gì.

Pipeline phải chia 2 bước tách biệt:
1. Spark ghi Parquet xuống disk → `data/processed/yellow_taxi/`
2. BQ client đọc Parquet từ disk → upload lên BigQuery

Đến bước 2, **Spark đã bị tắt (`.stop()`)**, DataFrame không còn tồn tại.
`BigQueryLoader.load_all()` không nhận DataFrame → không có gì để generate
`dim_time`.

### Tại sao không giữ Spark sống để truyền df vào BigQueryLoader

**Resource lãng phí:** Spark phải giữ RAM/CPU trong 10–30 phút upload BQ trong
khi không làm gì hữu ích.

**Coupling sai tầng:** BQ client là HTTP I/O, Spark là distributed compute.
Trộn lẫn vi phạm single responsibility và làm cả 2 khó test độc lập.

### Hệ quả: `dim_time` bị bỏ lại trong BigQueryLoader

```python
def load_all(self):
    self._load_parquet_files(...)           # yellow_taxi_raw ✓
    self._load_rows(DIM_VENDOR_DATA,  ...)  # static ✓
    self._load_rows(DIM_PAYMENT_DATA, ...)  # static ✓
    self._load_rows(DIM_RATE_DATA,    ...)  # static ✓
    # dim_time ← KHÔNG CÓ — technical debt từ migration
```

---

## 3. Vấn đề với dbt cũ (trước khi fix)

**Vấn đề 1 — Source khai báo tables không tồn tại:**
```yaml
tables:
  - name: fact_trip    # ← không tồn tại trên BQ
  - name: dim_time     # ← không tồn tại trên BQ
  - name: dim_location # ← không tồn tại trên BQ
```
Spark chỉ upload vào `yellow_taxi_raw`. `fact_trip` chưa bao giờ được tạo.

**Vấn đề 2 — `stg_time` circular dependency:**
```sql
-- Đọc từ dim_time... nhưng dim_time phải được generate bởi dbt
-- Con gà và quả trứng
select * from {{ source('warehouse', 'dim_time') }}
```

**Vấn đề 3 — `stg_trip` sai schema:**
```sql
-- Kỳ vọng fact_trip đã có star-schema (trip_id, vendor_key...)
-- Nhưng data thực là yellow_taxi_raw với VendorID, tpep_pickup_datetime...
select trip_id, vendor_key from {{ source('warehouse', 'fact_trip') }}
```


---

## 4. Giải pháp: Chuyển trách nhiệm generate dim_time sang dbt

### Tại sao dbt là nơi đúng

| | Spark (cũ) | dbt (mới) |
|---|---|---|
| Input | df trong memory | Table đã có trong BQ |
| Engine | JVM distributed | BigQuery SQL engine |
| Idempotent | Tự handle | VIEW tự rebuild mỗi lần query |
| Testable | Cần Spark | `dbt test` thuần SQL |

Sau khi Spark upload `yellow_taxi_raw` lên BQ, data đã có ở đó. dbt query
trực tiếp bằng BigQuery SQL — không cần Spark, không cần Python.

---

## 5. Các thay đổi cụ thể đã thực hiện

### `_stg_sources.yml` — chỉ khai báo tables thực có trên BQ

```yaml
# MỚI — chỉ những gì thực sự tồn tại
tables:
  - name: yellow_taxi_raw  # Spark upload vào đây
  - name: dim_vendor       # BQ client (static, 3 rows)
  - name: dim_payment      # BQ client (static, 6 rows)
  - name: dim_rate         # BQ client (static, 7 rows)
```

### `stg_trip.sql` — derive surrogate keys bằng BigQuery SQL

Port 1-1 logic Spark sang SQL. Kết quả giống hệt nhau, chỉ khác engine:

```sql
-- trip_id: SHA256 hash (giống Spark cũ)
TO_HEX(SHA256(CONCAT(CAST(VendorID AS STRING), ...))) AS trip_id

-- time_key yyyyMMddHH (giống F.date_format("yyyyMMddHH") của Spark)
CAST(FORMAT_TIMESTAMP('%Y%m%d%H', tpep_pickup_datetime) AS INT64)
    AS pickup_time_key

-- vendor_key mapping (giống CASE WHEN của Spark)
CASE WHEN VendorID IN (1, 2) THEN VendorID ELSE 7 END AS vendor_key
```

### `stg_time.sql` — generate dim_time từ raw timestamps bằng SQL

```sql
-- UNION pickup + dropoff để lấy tất cả timestamps
all_timestamps as (
    select tpep_pickup_datetime  as ts from raw
    union distinct
    select tpep_dropoff_datetime as ts from raw
),
-- Extract các thuộc tính thời gian — bản dịch 1-1 của Spark sang SQL
time_dim as (
    select distinct
        CAST(FORMAT_TIMESTAMP('%Y%m%d%H', ts) AS INT64) AS time_key,
        EXTRACT(YEAR FROM ts)   AS year,
        EXTRACT(HOUR FROM ts)   AS hour,
        CASE WHEN EXTRACT(DAYOFWEEK FROM ts) IN (1,7)
             THEN TRUE ELSE FALSE END AS is_weekend,
        CASE WHEN EXTRACT(HOUR FROM ts) BETWEEN 7 AND 9
              OR  EXTRACT(HOUR FROM ts) BETWEEN 17 AND 19
             THEN TRUE ELSE FALSE END AS is_peak_hour, ...
)
```

### `_load_rows` — đổi Streaming Insert → batch load NDJSON

```python
# CŨ: Streaming Insert → 403 Forbidden trên GCP free tier
errors = client.insert_rows(table, rows)

# MỚI: Batch load NDJSON → free tier OK
ndjson = "\n".join(json.dumps(r) for r in rows).encode("utf-8")
job = client.load_table_from_file(io.BytesIO(ndjson), table, job_config)
job.result()
```

GCP Sandbox block Streaming Insert API. Batch load jobs miễn phí và idempotent.

---

## 6. Kiến trúc mới — Toàn cảnh

```
[SPARK]
Raw Parquet → Extract → Transform → Load
                                     │
                        data/processed/yellow_taxi/*.parquet
                                     │
                                     ▼
[BIGQUERY CLIENT] BigQueryLoader.load_all()
    ├── yellow_taxi_raw  (Parquet upload, autodetect schema)
    ├── dim_vendor       (3 rows, NDJSON batch)
    ├── dim_payment      (6 rows, NDJSON batch)
    └── dim_rate         (7 rows, NDJSON batch)
    Dataset: nyc_taxi_raw
                                     │
                                     ▼
[dbt] dbt run
    STAGING (view — query-time computation)
        ├── stg_trip     ← yellow_taxi_raw + derive keys bằng SQL
        ├── stg_time     ← UNION timestamps → extract year/hour/is_weekend
        ├── stg_location ← collect distinct LocationIDs
        ├── stg_vendor / stg_payment / stg_rate ← đọc dim tables
    INTERMEDIATE (view)
        └── int_trips_with_dimensions
              └── JOIN stg_trip + stg_time + stg_vendor + stg_location
    MARTS (table — final output cho BI tools)
        ├── fct_trip_summary
        └── fct_vendor_daily_metrics
    Dataset: nyc_taxi_dbt
```

---

## 7. Trade-offs cần biết

### Trade-off 1: `stg_time` là WVIE → scan lại mỗi lần query

Mỗi lần `int_trips_with_dimensions` được query, BQ phải:
1. Scan toàn bộ `yellow_taxi_raw` để lấy timestamps
2. UNION, DISTINCT, extract fields
3. JOIN với `stg_trip`

- **50,000 rows (hiện tại):** ~1 giây, chấp nhận được
- **10 triệu rows (production):** tốn kém, cần đổi sang `materialized='table'`
  trong `dbt_project.yml`

### Trade-off 2: dim_time chỉ chứa giờ có trong data

Khác với PostgreSQL cũ có thể pre-populate mọi giờ trong năm, `stg_time`
chỉ có giờ xuất hiện thực tế trong `yellow_taxi_raw`. JOIN với timestamp
không có trong data → NULL (do LEFT JOIN trong int_trips_with_dimensions).

### Trade-off 3: dim_location thiếu zone/borough

`stg_location.sql` hiện chỉ collect distinct LocationID, zone/borough = NULL.
Cần dbt seed từ `taxi_zone_lookup.csv` (NYC TLC public dataset) để enrich đầy
đủ. Hiện tại các mart vẫn chạy được nhưng pickup_zone/dropoff_zone sẽ NULL.

### Trade-off 4: Metadata ETL và dbt tách rời

`ETLMetadata` chỉ track Spark pipeline. Không biết dbt có chạy thành công hay
không. Để orchestrate đầy đủ cần Airflow/Prefect chain:
`spark pipeline → dbt run → dbt test`.

---

## 8. Tóm tắt

| Câu hỏi | Trả lời |
|---------|---------|
| Tại sao Postgres tự sinh dim_time được? | Spark giữ df trong memory → truyền thẳng vào hàm → ghi JDBC một lần |
| Tại sao BQ không làm được? | BQ không có JDBC; phải upload file → Spark phải tắt trước → df không còn |
| Giải pháp? | dbt generate dim_time bằng SQL UNION timestamps từ yellow_taxi_raw |
| Trade-off chính? | stg_time VIEW scan lại mỗi query; cần TABLE khi data lớn |
| Còn thiếu gì? | dim_location thiếu zone/borough; orchestration Spark↔dbt chưa có |

