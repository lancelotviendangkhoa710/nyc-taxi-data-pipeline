{{
  config(
    materialized='table',
    description='Final fact table for trip analysis'
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
where trip_date >= date_sub(current_date(), interval 12 month)

