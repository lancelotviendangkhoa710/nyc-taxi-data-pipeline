with source as (
    select * from "postgres"."public"."dim_vendor"
)

select
    vendor_key,
    vendor_name
from source