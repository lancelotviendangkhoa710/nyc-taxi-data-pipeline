-- stg_trip.sql
-- Đọc raw data từ yellow_taxi_raw.
-- T2 transform: filter outliers, derive metrics, chuẩn hóa surrogate keys.

with source as (
    select * from {{ source('warehouse', 'yellow_taxi_raw') }}
),

cleaned as (
    select *
    from source
    where tpep_pickup_datetime  is not null
      and tpep_dropoff_datetime is not null
      -- Filter outliers (business logic — thực hiện trong warehouse, không phải ETL)
      and trip_distance  > 0
      and trip_distance  <= 100
      and fare_amount    >= 2.5
      and fare_amount    <= 1000
      and COALESCE(RatecodeID, 1) != 99
),

renamed as (
    select
        -- trip_id: SHA256 hash của các trường định danh chuyến đi
        TO_HEX(SHA256(CONCAT(
            COALESCE(CAST(VendorID AS STRING),               ''),
            COALESCE(CAST(tpep_pickup_datetime  AS STRING),  ''),
            COALESCE(CAST(tpep_dropoff_datetime AS STRING),  ''),
            COALESCE(CAST(PULocationID AS STRING),           ''),
            COALESCE(CAST(DOLocationID AS STRING),           '')
        ))) AS trip_id,

        -- Dim foreign keys
        CASE WHEN VendorID IN (1, 2) THEN VendorID ELSE 7 END AS vendor_key,
        CAST(FORMAT_TIMESTAMP('%Y%m%d%H', tpep_pickup_datetime)  AS INT64) AS pickup_time_key,
        CAST(FORMAT_TIMESTAMP('%Y%m%d%H', tpep_dropoff_datetime) AS INT64) AS dropoff_time_key,
        COALESCE(PULocationID, 0)  AS pickup_location_key,
        COALESCE(DOLocationID, 0)  AS dropoff_location_key,
        COALESCE(payment_type, 5)  AS payment_key,
        COALESCE(RatecodeID, 1)    AS rate_key,

        -- Measures (raw)
        passenger_count,
        trip_distance,
        fare_amount,
        extra,
        tip_amount,
        tolls_amount,
        congestion_surcharge,
        Airport_fee        AS airport_fee,
        cbd_congestion_fee,
        total_amount,

        -- Derived metrics (T2: business logic trong warehouse)
        ROUND(
            TIMESTAMP_DIFF(tpep_dropoff_datetime, tpep_pickup_datetime, SECOND) / 60.0,
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

    from cleaned
)

select * from renamed

