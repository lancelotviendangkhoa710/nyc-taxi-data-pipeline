# 🎯 PHASE 3A: Ví Dụ Thực Tế & Hành Động Cụ Thể

---

## 🏢 Ví Dụ Thực Tế: NYC Taxi Project

### Hiện Tại Bạn Có (Staging):

```
stg_trip          → 1 trip = 1 row
stg_vendor        → vendor info
stg_location      → zone info
stg_time          → date/time info
```

### Phase 3A Sẽ Thêm:

**INTERMEDIATE:**
- `int_trips_with_dimensions` (JOIN staging tables)
- `int_trip_metrics_by_vendor` (GROUP BY vendor)
- `int_trip_metrics_by_location` (GROUP BY zone)

**MARTS:**
- `fct_trip_summary` (TABLE for BI)
- `fct_vendor_daily_metrics` (TABLE for dashboards)

---

## 🛠️ Step 1: Tạo Intermediate Model

**File: `dbt/models/intermediate/int_trips_with_dimensions.sql`**

```sql
{{
  config(
    materialized='view',
    description='Enrich trips with vendor, location, time'
  )
}}

with stg_trip as (
    select * from {{ ref('stg_trip') }}
),
stg_vendor as (
    select * from {{ ref('stg_vendor') }}
),
stg_location as (
    select * from {{ ref('stg_location') }}
),
stg_time as (
    select * from {{ ref('stg_time') }}
)

select
    t.trip_id,
    t.passenger_count,
    t.trip_distance,
    t.fare_amount,
    t.tip_amount,
    t.total_amount,
    v.vendor_name,
    pickup_loc.zone as pickup_zone,
    dropoff_loc.zone as dropoff_zone,
    pickup_time.date as trip_date,
    pickup_time.hour as pickup_hour,
    pickup_time.is_weekend,
    pickup_time.is_peak_hour

from stg_trip t
left join stg_vendor v
    on t.vendor_key = v.vendor_key
left join stg_location pickup_loc
    on t.pickup_location_key = pickup_loc.location_key
left join stg_location dropoff_loc
    on t.dropoff_location_key = dropoff_loc.location_key
left join stg_time pickup_time
    on t.pickup_time_key = pickup_time.time_key
```

---

## 🛠️ Step 2: Tạo Marts Model

**File: `dbt/models/marts/fct_trip_summary.sql`**

```sql
{{
  config(
    materialized='table',
    description='Final fact table for trip analysis',
    indexes=[
      {'columns': ['trip_date'], 'type': 'btree'},
      {'columns': ['vendor_name'], 'type': 'btree'},
    ]
  )
}}

with enriched_trips as (
    select * from {{ ref('int_trips_with_dimensions') }}
)

select
    trip_id,
    vendor_name,
    pickup_zone,
    dropoff_zone,
    trip_date,
    pickup_hour,
    is_weekend,
    passenger_count,
    trip_distance,
    fare_amount,
    tip_amount,
    total_amount,
    case
        when tip_amount / fare_amount > 0.2 then 'High'
        when tip_amount / fare_amount > 0.1 then 'Medium'
        else 'Low'
    end as tip_category

from enriched_trips
where trip_date >= current_date - interval '12 months'
```

---

## 📊 Data Flow Trước vs Sau Phase 3A

**Trước (chỉ có Staging):**

```
100M rows fact_trip
    ↓
stg_trip VIEW
    ↓
Analyst phải: JOIN 5 bảng sao? 😞
    ↓
Query chậm
```

**Sau (có Intermediate + Marts):**

```
100M rows fact_trip
    ↓
stg_trip VIEW
    ↓
int_trips_with_dimensions VIEW (all JOINs)
    ↓
fct_trip_summary TABLE (indexed, materialized)
    ↓
Analyst: SELECT * FROM fct_trip_summary 🚀
    ↓
Query nhanh!
```

---

## ✅ Checklist Phase 3A

**Intermediate Layer:**
- [ ] Tạo folder `dbt/models/intermediate/`
- [ ] Tạo `int_trips_with_dimensions.sql`
- [ ] Tạo `_int_models.yml`

**Marts Layer:**
- [ ] Tạo folder `dbt/models/marts/`
- [ ] Tạo `fct_trip_summary.sql`
- [ ] Tạo `_mart_models.yml`

**Testing:**
- [ ] Chạy `dbt run`
- [ ] Chạy `dbt test`
- [ ] Verify PostgreSQL tables

---

## 🎯 Kết Quả Sau Phase 3A

✅ **Staging** - Sạch dữ liệu  
✅ **Intermediate** - JOIN & aggregate  
✅ **Marts** - Final analytics tables  
✅ **Performance** - Indexed, materialized  
✅ **Analysts** - Query trực tiếp, nhanh  

**Bạn sẵn sàng bắt đầu?** 🚀
