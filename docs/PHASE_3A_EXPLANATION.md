# 📚 PHASE 3A: dbt Transformation Layers - Giải Thích Chi Tiết

> **Dành cho những ai vừa học vừa làm và chưa hiểu rõ Phase 3A là gì**

---

## 🎯 Tại Sao Lại Cần Phase 3A?

Hãy tưởng tượng bạn có một **nhà bếp**:

```
Raw Ingredients (Nguyên liệu thô)
    ↓
Spark ETL (Chuẩn bị nguyên liệu - rửa, cắt, kiểm tra)
    ↓
PostgreSQL Warehouse (Kho chứa)
    ↓
dbt (Nấu ăn - tạo các dish từ nguyên liệu)
    ↓
Analytics (Bày biện - dễ ăn & dễ hiểu)
```

---

## 🏗️ Kiến Trúc 3 Layers Của dbt

```
STAGING (đã có)        → Làm sạch dữ liệu cơ bản
    ↓
INTERMEDIATE (Phase 3A) → JOIN dimensions, aggregates
    ↓
MARTS (Phase 3A)       → Final tables cho BI tools
    ↓
ANALYTICS              → Metabase, Tableau
```

---

## 📖 So Sánh 3 Layers

| Thuộc tính | STAGING | INTERMEDIATE | MARTS |
|-----------|---------|--------------|-------|
| **Mục đích** | Chuẩn bị dữ liệu | Xử lý logic | Phục vụ phân tích |
| **Materialized** | View | View | Table |
| **Tính toán** | Lọc, rename | JOIN, aggregate | Grouped |
| **Dùng cho ai** | dbt developers | dbt developers | Analysts & BI |

---

## 🔍 STAGING LAYER (Đã Có)

Ví dụ: `stg_trip.sql` - làm sạch dữ liệu từ warehouse

```sql
with source as (
    select * from {{ source('warehouse', 'fact_trip') }}
)
select
    trip_id, vendor_key, trip_distance, total_amount
from source
where trip_duration_min > 0 and trip_distance > 0
```

---

## ⚙️ INTERMEDIATE LAYER (Phase 3A)

### Ý Tưởng: Kết hợp nhiều bảng, tính toán logic phức tạp

**Ví dụ: `int_trips_with_dimensions.sql`**

```sql
with stg_trip as (
    select * from {{ ref('stg_trip') }}
),
stg_vendor as (
    select * from {{ ref('stg_vendor') }}
),
stg_location as (
    select * from {{ ref('stg_location') }}
)

select
    t.trip_id,
    t.fare_amount,
    t.tip_amount,
    v.vendor_name,
    pickup_loc.zone as pickup_zone,
    dropoff_loc.zone as dropoff_zone
from stg_trip t
left join stg_vendor v on t.vendor_key = v.vendor_key
left join stg_location pickup_loc 
    on t.pickup_location_key = pickup_loc.location_key
left join stg_location dropoff_loc
    on t.dropoff_location_key = dropoff_loc.location_key
```

**Kết quả:** Dữ liệu trips + tên vendor + zone names (enriched data)

---

## 🎁 MARTS LAYER (Phase 3A)

### Ý Tưởng: Tạo TABLE tối ưu cho BI tools

**Ví dụ: `fct_trip_summary.sql`**

```sql
{{ config(materialized='table') }}

with enriched_trips as (
    select * from {{ ref('int_trips_with_dimensions') }}
)

select
    trip_id,
    vendor_name,
    pickup_zone,
    fare_amount,
    tip_amount,
    case
        when tip_amount / fare_amount > 0.2 then 'High'
        else 'Low'
    end as tip_category
from enriched_trips
```

**Kết quả:** TABLE cuối cùng, sẵn sàng cho Metabase

---

## 📊 Luồng Dữ Liệu

```
PostgreSQL → Staging (VIEW) → Intermediate (VIEW) → Marts (TABLE) → BI
```

---

## 🎓 Concepts

**`source()`** = tham chiếu PostgreSQL tables  
**`ref()`** = tham chiếu dbt models  
**View** = không lưu data, query mỗi lần  
**Table** = lưu kết quả, nhanh hơn

---

## 🚀 Tại Sao Phase 3A Quan Trọng?

1. **Reusability** - Intermediate models được dùng bởi nhiều marts
2. **Testability** - Kiểm tra từng layer riêng
3. **Performance** - Marts tables được index
4. **Maintainability** - Dễ modify logic

---

**Bạn sẵn sàng bắt đầu Phase 3A chưa?** 🎯
