with source as (
    select * from "postgres"."public"."dim_rate"
)

select
    rate_key,
    rate_name
from source