with source as (
    select * from "postgres"."public"."dim_location"
)

select
    location_key,
    zone,
    borough,
    service_zone
from source