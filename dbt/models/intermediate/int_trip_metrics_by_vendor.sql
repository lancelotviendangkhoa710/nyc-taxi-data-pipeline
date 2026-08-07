{{
  config(
    materialized='view',
    description='Group trips by vendor and calculate metrics such as total trips, average fare, and total revenue'
  )
}}

with enriched_trips as (
    select * from {{ ref('int_trips_with_dimensions') }}
)

select
    vendor_name,
    count(trip_id) as total_trips,
    avg(fare_amount) as average_fare,
    sum(total_amount) as total_revenue
from enriched_trips
where vendor_name is not null
group by vendor_name
having count(trip_id) > 0 and avg(fare_amount) > 0 and sum(total_amount) > 0
