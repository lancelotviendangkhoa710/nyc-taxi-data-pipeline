-- stg_time.sql
-- Generate dim_time từ tất cả pickup + dropoff timestamps trong yellow_taxi_raw.
-- Mỗi row là 1 giờ duy nhất (time_key = yyyyMMddHH).

with raw as (
    select * from {{ source('warehouse', 'yellow_taxi_raw') }}
),

-- Gộp pickup và dropoff timestamps thành 1 tập hợp
all_timestamps as (
    select tpep_pickup_datetime  as ts from raw where tpep_pickup_datetime  is not null
    union distinct
    select tpep_dropoff_datetime as ts from raw where tpep_dropoff_datetime is not null
),

time_dim as (
    select distinct
        CAST(FORMAT_TIMESTAMP('%Y%m%d%H', ts) AS INT64) AS time_key,
        TIMESTAMP_TRUNC(ts, HOUR)                        AS datetime,
        DATE(ts)                                         AS date,
        EXTRACT(YEAR    FROM ts)                         AS year,
        EXTRACT(MONTH   FROM ts)                         AS month,
        FORMAT_TIMESTAMP('%B', ts)                       AS month_name,
        EXTRACT(DAY     FROM ts)                         AS day,
        EXTRACT(DAYOFWEEK FROM ts)                       AS day_of_week,
        FORMAT_TIMESTAMP('%A', ts)                       AS day_name,
        EXTRACT(HOUR    FROM ts)                         AS hour,
        EXTRACT(QUARTER FROM ts)                         AS quarter,
        CASE WHEN EXTRACT(DAYOFWEEK FROM ts) IN (1, 7)
             THEN TRUE ELSE FALSE END                    AS is_weekend,
        CASE WHEN EXTRACT(HOUR FROM ts) BETWEEN 7 AND 9
              OR  EXTRACT(HOUR FROM ts) BETWEEN 17 AND 19
             THEN TRUE ELSE FALSE END                    AS is_peak_hour
    from all_timestamps
)

select * from time_dim
