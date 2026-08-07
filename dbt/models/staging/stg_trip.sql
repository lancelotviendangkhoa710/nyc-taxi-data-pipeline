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
    total_amount
from source
