{{
  config(
    materialized='table',
    description='Revenue and trip metrics aggregated by pickup location zone and hour of day. location_id maps to LocationID key in TopoJSON for Shape Map visual.',
    indexes=[
      {'columns': ['location_id'], 'type': 'btree'},
      {'columns': ['pickup_hour'], 'type': 'btree'},
    ]
  )
}}

with trips as (
    select * from {{ ref('stg_trip') }}
),

locations as (
    select * from {{ ref('stg_location') }}
),

times as (
    select * from {{ ref('stg_time') }}
)

select
    loc.location_key                            as location_id,
    loc.zone                                    as zone_name,
    loc.borough,
    t.hour                                      as pickup_hour,
    count(tr.trip_id)                           as trip_count,
    round(sum(tr.fare_amount)::numeric, 2)      as total_revenue,
    round(avg(tr.tip_ratio)::numeric, 4)        as avg_tip_ratio,
    round(avg(tr.fare_amount)::numeric, 2)      as avg_fare,
    round(avg(tr.trip_distance)::numeric, 2)    as avg_distance_miles

from trips tr
inner join locations loc
    on tr.pickup_location_key = loc.location_key
inner join times t
    on tr.pickup_time_key = t.time_key

group by
    loc.location_key,
    loc.zone,
    loc.borough,
    t.hour
