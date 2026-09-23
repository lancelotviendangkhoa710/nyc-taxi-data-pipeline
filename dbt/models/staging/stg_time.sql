with raw as (
    select * from {{ source('warehouse', 'yellow_taxi_raw') }}
),
all_timestamps as (
    select tpep_pickup_datetime as ts
    from raw
    where tpep_pickup_datetime is not null
    union
    distinct
    select tpep_dropoff_datetime as ts
    from raw
    where tpep_dropoff_datetime is not null
),
time_dim as (
    select distinct CAST(TO_CHAR(ts, 'YYYYMMDDHH24') AS INT8) AS time_key,
        DATE_TRUNC('hour', ts) AS datetime,
        CAST(ts AS DATE) AS date,
        EXTRACT(YEAR FROM ts) AS year,
        EXTRACT(MONTH FROM ts) AS month,
        TO_CHAR(ts, 'Month') AS month_name,
        EXTRACT(DAY FROM ts) AS day,
        EXTRACT(DOW FROM ts) + 1 AS day_of_week,
        TO_CHAR(ts, 'Day') AS day_name,
        EXTRACT(HOUR FROM ts) AS hour,
        EXTRACT(QUARTER FROM ts) AS quarter,
        CASE
            WHEN EXTRACT(DOW FROM ts) IN (0, 6) THEN TRUE
            ELSE FALSE
        END AS is_weekend,
        CASE
            WHEN EXTRACT(HOUR FROM ts) BETWEEN 7 AND 9
            OR EXTRACT(HOUR FROM ts) BETWEEN 17 AND 19 THEN TRUE
            ELSE FALSE
        END AS is_peak_hour
    from all_timestamps
)
select *
from time_dim