-- stg_trip.sql
-- Đọc raw data từ yellow_taxi_raw, chuẩn hóa tên cột và derive surrogate keys.

with source as (
    select * from {{ source('warehouse', 'yellow_taxi_raw') }}
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

        -- Measures
        passenger_count,
        trip_distance,
        trip_duration_min,
        fare_amount,
        extra,
        tip_amount,
        tip_ratio,
        tolls_amount,
        congestion_surcharge,
        Airport_fee        AS airport_fee,
        cbd_congestion_fee,
        total_amount,
        DATE(tpep_pickup_datetime) AS pickup_date

    from source
    where tpep_pickup_datetime  is not null
      and tpep_dropoff_datetime is not null
)

select * from renamed
