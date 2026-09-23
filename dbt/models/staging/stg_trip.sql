-- stg_trip.sql
-- Đọc raw data từ yellow_taxi_raw.
-- T2 transform: filter outliers, derive metrics, chuẩn hóa surrogate keys.
with source as (
    select *
    from {{ source('warehouse', 'yellow_taxi_raw') }}
),
cleaned as (
    select *
    from source
),
identified as (
    select *,
        {{ dbt_utils.generate_surrogate_key([
            'VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime',
            'passenger_count', 'trip_distance', 'RatecodeID', 'PULocationID',
            'DOLocationID', 'payment_type', 'fare_amount', 'extra', 'tip_amount',
            'tolls_amount', 'congestion_surcharge', 'Airport_fee', 'cbd_congestion_fee',
            'total_amount'
        ]) }} AS trip_id
    from cleaned
),
renamed as (
    select trip_id,
        -- Dim foreign keys
        CASE
            WHEN VendorID IN (1, 2) THEN VendorID
            ELSE 7
        END AS vendor_key,
        CAST(
            TO_CHAR(tpep_pickup_datetime, 'YYYYMMDDHH24') AS INT8
        ) AS pickup_time_key,
        CAST(
            TO_CHAR(tpep_dropoff_datetime, 'YYYYMMDDHH24') AS INT8
        ) AS dropoff_time_key,
        COALESCE(PULocationID, 0) AS pickup_location_key,
        COALESCE(DOLocationID, 0) AS dropoff_location_key,
        COALESCE(payment_type, 5) AS payment_key,
        COALESCE(RatecodeID, 1) AS rate_key,
        -- Measures (raw)
        passenger_count,
        trip_distance,
        fare_amount,
        extra,
        tip_amount,
        tolls_amount,
        congestion_surcharge,
        Airport_fee AS airport_fee,
        cbd_congestion_fee,
        total_amount,
        -- Derived metrics (T2: business logic trong warehouse)
        ROUND(
            DATEDIFF(
                second,
                tpep_pickup_datetime,
                tpep_dropoff_datetime
            ) / 60.0,
            2
        ) AS trip_duration_min,
        ROUND(
            CASE
                WHEN fare_amount > 0 THEN tip_amount / fare_amount
                ELSE 0.0
            END,
            4
        ) AS tip_ratio,
        DATE(tpep_pickup_datetime) AS pickup_date
    from identified
)
select *
except (duplicate_rank)
from (
        select *,
            ROW_NUMBER() over (
                partition by trip_id
                order by trip_id
            ) as duplicate_rank
        from renamed
    )
where duplicate_rank = 1
  and tip_ratio <= 10
  and tip_ratio >= 0