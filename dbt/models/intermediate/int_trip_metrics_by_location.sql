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
    location_name,count(*) as total_trips,
    avg(fare_amount) as average_fare,
    sum(total_amount) as total_revenue
from enriched_trips
group by location_name,zone,  borough,service_zone

