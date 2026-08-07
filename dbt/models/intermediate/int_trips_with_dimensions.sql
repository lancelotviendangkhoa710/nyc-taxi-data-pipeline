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
