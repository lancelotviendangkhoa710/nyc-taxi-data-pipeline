{{
  config(
    materialized='view',
    description='Group trips by pickup zone and calculate metrics such as total trips, average fare, and total revenue'
  )
}}

with enriched_trips as (
    select * from {{ ref('int_trips_with_dimensions') }}
)

select
    pickup_zone,
    count(trip_id) as total_trips,
    avg(fare_amount) as average_fare,
    sum(total_amount) as total_revenue
from enriched_trips
where pickup_zone is not null
group by pickup_zone
having count(trip_id) > 0 and avg(fare_amount) > 0 and sum(total_amount) > 0

