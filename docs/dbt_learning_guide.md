# Hướng dẫn học dbt cho project NYC Taxi

## 1. dbt là gì?

dbt (data build tool) là công cụ **transform** trong pipeline ELT. Nó **không extract, không load** — chỉ viết SQL để biến đổi dữ liệu đã có sẵn trong database.

Trong project này:

```
PySpark load data → PostgreSQL (fact_trip, dim_*) → dbt transform → mart tables → Power BI
```

dbt đọc từ bảng nguồn trong PostgreSQL, chạy SQL tạo ra bảng/view mới cũng trong PostgreSQL.

---

## 2. Cài đặt

```bash
pip install dbt-postgres
```

Chỉ cần package `dbt-postgres` — nó kéo theo `dbt-core` tự động.

Kiểm tra:

```bash
dbt --version
```

---

## 3. Cấu trúc project dbt

```
dbt/
├── dbt_project.yml          # Config chính: tên project, materialization mặc định
├── profiles.yml             # Connection đến PostgreSQL (đã tạo sẵn)
├── models/
│   ├── staging/             # Lớp 1: SELECT thẳng từ source, lọc/rename
│   │   ├── _stg_sources.yml # Khai báo bảng nguồn (source)
│   │   ├── stg_fact_trip.sql
│   │   ├── stg_dim_location.sql
│   │   └── ...
│   ├── intermediate/        # Lớp 2: JOIN, business logic
│   │   └── int_trip_enriched.sql
│   └── marts/               # Lớp 3: Bảng cuối cho dashboard
│       ├── mart_revenue_daily.sql
│       ├── mart_trip_by_zone.sql
│       └── _mart_schema.yml
├── tests/                   # Custom SQL tests
├── seeds/                   # CSV nhỏ load vào DB
├── macros/                  # Jinja reusable functions
└── snapshots/               # SCD Type 2 (không cần trong project này)
```

---

## 4. Hai file config quan trọng nhất

### 4.1 `dbt_project.yml`

```yaml
name: 'nyc_taxi'
version: '1.0.0'
config-version: 2
profile: 'nyc_taxi'        # Phải khớp tên trong profiles.yml

model-paths: ["models"]

models:
  nyc_taxi:
    staging:
      +materialized: view   # staging = view (nhẹ, luôn fresh)
    intermediate:
      +materialized: view
    marts:
      +materialized: table  # mart = table (nhanh khi query)
```

**Materialization** (cách dbt tạo output):

| Loại | SQL sinh ra | Khi nào dùng |
| ------ | ------------ | ------------- |
| `view` | `CREATE VIEW` | Staging, intermediate — data nhỏ, cần luôn cập nhật |
| `table` | `CREATE TABLE AS` | Mart — query thường xuyên, cần performance |
| `incremental` | `INSERT / MERGE` | Fact table cực lớn — chỉ xử lý data mới |
| `ephemeral` | CTE inline | Logic tạm, không cần bảng vật lý |

### 4.2 `profiles.yml`

```yaml
nyc_taxi:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('PG_HOST', 'localhost') }}"
      port: "{{ env_var('PG_PORT', '5432') | int }}"
      user: "{{ env_var('PG_USER', 'postgres') }}"
      password: "{{ env_var('PG_PASSWORD', '') }}"
      dbname: "{{ env_var('PG_DATABASE', 'postgres') }}"
      schema: public
      threads: 4
```

`env_var()` đọc từ biến môi trường (file `.env`). Không hardcode password.

---

## 5. Khái niệm cốt lõi

### 5.1 `source()` — Khai báo bảng nguồn

File `_stg_sources.yml`:

```yaml
version: 2
sources:
  - name: warehouse
    schema: public
    tables:
      - name: fact_trip
      - name: dim_vendor
      - name: dim_location
```

Dùng trong SQL:

```sql
select * from {{ source('warehouse', 'fact_trip') }}
-- dbt biên dịch thành: select * from public.fact_trip
```

### 5.2 `ref()` — Tham chiếu model khác

```sql
-- Trong int_trip_enriched.sql
select * from {{ ref('stg_fact_trip') }}
-- dbt tự biết stg_fact_trip là view nào, schema nào
```

**Tại sao dùng `ref()` thay vì tên bảng trực tiếp?**

- dbt tự xây dependency graph (DAG)
- Tự chạy đúng thứ tự: staging → intermediate → mart
- Đổi schema/database không cần sửa SQL

### 5.3 Jinja templating

dbt dùng Jinja2 (giống Python template):

```sql
-- Điều kiện
{% if target.name == 'dev' %}
  LIMIT 1000
{% endif %}

-- Biến
{{ var('start_date', '2024-01-01') }}

-- Vòng lặp
{% for col in ['fare_amount', 'tip_amount', 'total_amount'] %}
  SUM({{ col }}) as total_{{ col }}{% if not loop.last %},{% endif %}
{% endfor %}
```

---

## 6. Viết model — 3 lớp

### Lớp 1: Staging (`stg_`)

Quy tắc: 1 source → 1 staging model. Chỉ SELECT, rename, cast, filter rõ ràng.

```sql
-- models/staging/stg_fact_trip.sql
with source as (
    select * from {{ source('warehouse', 'fact_trip') }}
)

select
    trip_id,
    vendor_key,
    pickup_time_key,
    dropoff_time_key,
    pickup_location_key,
    dropoff_location_key,
    payment_key,
    rate_key,
    passenger_count,
    trip_distance,
    trip_duration_min,
    fare_amount,
    tip_amount,
    tip_ratio,
    total_amount,
    pickup_date
from source
where trip_duration_min > 0      -- loại chuyến đi vô nghĩa
  and trip_distance > 0
  and total_amount > 0
```

### Lớp 2: Intermediate (`int_`)

JOIN các staging lại, thêm business logic:

```sql
-- models/intermediate/int_trip_enriched.sql
with trips as (
    select * from {{ ref('stg_fact_trip') }}
),

vendors as (
    select * from {{ ref('stg_dim_vendor') }}
),

pickup_loc as (
    select * from {{ ref('stg_dim_location') }}
),

time_dim as (
    select * from {{ ref('stg_dim_time') }}
)

select
    t.trip_id,
    v.vendor_name,
    pl.borough as pickup_borough,
    pl.zone as pickup_zone,
    tm.year,
    tm.month,
    tm.day_of_week,
    tm.hour,
    tm.is_weekend,
    tm.is_peak_hour,
    t.passenger_count,
    t.trip_distance,
    t.trip_duration_min,
    t.fare_amount,
    t.tip_amount,
    t.tip_ratio,
    t.total_amount,
    t.pickup_date
from trips t
left join vendors v on t.vendor_key = v.vendor_key
left join pickup_loc pl on t.pickup_location_key = pl.location_key
left join time_dim tm on t.pickup_time_key = tm.time_key
```

### Lớp 3: Mart (`mart_`)

Aggregate cho dashboard:

```sql
-- models/marts/mart_revenue_daily.sql
with enriched as (
    select * from {{ ref('int_trip_enriched') }}
)

select
    pickup_date,
    pickup_borough,
    count(*) as total_trips,
    sum(total_amount) as total_revenue,
    avg(total_amount) as avg_revenue,
    sum(tip_amount) as total_tips,
    avg(tip_ratio) as avg_tip_ratio,
    avg(trip_distance) as avg_distance,
    avg(trip_duration_min) as avg_duration_min
from enriched
group by pickup_date, pickup_borough
```

---

## 7. Testing — `dbt test`

### 7.1 Generic tests (trong YAML)

```yaml
# models/marts/_mart_schema.yml
version: 2

models:
  - name: mart_revenue_daily
    columns:
      - name: pickup_date
        tests:
          - not_null
      - name: total_trips
        tests:
          - not_null
      - name: total_revenue
        tests:
          - not_null
```

4 generic tests có sẵn:

| Test | Ý nghĩa |
| ------ | --------- |
| `unique` | Không trùng lặp |
| `not_null` | Không có NULL |
| `accepted_values` | Giá trị nằm trong danh sách cho phép |
| `relationships` | FK tồn tại trong bảng khác (referential integrity) |

Ví dụ `accepted_values`:

```yaml
- name: vendor_key
  tests:
    - accepted_values:
        values: [1, 2]
```

Ví dụ `relationships`:

```yaml
- name: vendor_key
  tests:
    - relationships:
        to: source('warehouse', 'dim_vendor')
        field: vendor_key
```

### 7.2 Singular tests (SQL file)

File SQL trả về **rows vi phạm**. Nếu query trả về 0 rows → PASS, >0 rows → FAIL.

```sql
-- tests/assert_positive_revenue.sql
select *
from {{ ref('mart_revenue_daily') }}
where total_revenue < 0
```

---

## 8. Commands cần biết

```bash
# Từ thư mục dbt/

dbt debug            # Kiểm tra connection PostgreSQL
dbt run              # Chạy tất cả models (staging → int → mart)
dbt test             # Chạy tất cả tests
dbt run --select staging     # Chỉ chạy staging models
dbt run --select +mart_revenue_daily  # Chạy model + tất cả upstream
dbt test --select mart_revenue_daily  # Test 1 model cụ thể
dbt docs generate    # Tạo documentation
dbt docs serve       # Mở docs trên browser (có DAG visualization)
```

**Workflow thường ngày:**

```bash
dbt run && dbt test
```

---

## 9. DAG — dbt tự xây

Khi chạy `dbt docs serve`, bạn sẽ thấy graph:

```
source.fact_trip ─→ stg_fact_trip ─→ int_trip_enriched ─→ mart_revenue_daily
source.dim_vendor ─→ stg_dim_vendor ─┘                 ─→ mart_trip_by_zone
source.dim_location ─→ stg_dim_location                ─→ mart_tip_analysis
source.dim_time ─→ stg_dim_time
```

dbt đọc `ref()` và `source()` để xây graph này. Nó đảm bảo chạy đúng thứ tự.

---

## 10. Tích hợp Airflow

Trong Airflow DAG, task gọi dbt:

```python
run_dbt = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /path/to/dbt && dbt run && dbt test',
    env={'DBT_PROFILES_DIR': '/path/to/dbt'},
)
```

Thứ tự trong DAG:

```
download_data → run_spark_etl → load_to_postgres → run_dbt_models → refresh_dashboard
```

---

## 11. Checklist tự học

- [ ] Đọc hiểu `dbt_project.yml` và `profiles.yml` (đã có sẵn trong `dbt/`)
- [ ] Chạy `dbt debug` — xác nhận kết nối PostgreSQL thành công
- [ ] Tạo file `_stg_sources.yml` — khai báo sources
- [ ] Viết 1 staging model đơn giản (vd: `stg_dim_vendor.sql`)
- [ ] Chạy `dbt run --select stg_dim_vendor` — xác nhận view xuất hiện trong PG
- [ ] Thêm test `unique` + `not_null` cho model đó
- [ ] Chạy `dbt test` — xác nhận PASS
- [ ] Viết `stg_fact_trip.sql` với filter cơ bản
- [ ] Viết `int_trip_enriched.sql` — JOIN fact + dims
- [ ] Viết 1 mart model (vd: `mart_revenue_daily.sql`)
- [ ] Chạy `dbt run && dbt test` toàn bộ
- [ ] Chạy `dbt docs generate && dbt docs serve` — xem DAG

---

## 12. Tài liệu tham khảo

- [dbt docs chính thức](https://docs.getdbt.com/)
- [dbt best practices](https://docs.getdbt.com/best-practices)
- [Jinja template primer](https://docs.getdbt.com/docs/build/jinja-macros)
- [dbt-postgres adapter](https://docs.getdbt.com/docs/core/connect-data-platform/postgres-setup)
