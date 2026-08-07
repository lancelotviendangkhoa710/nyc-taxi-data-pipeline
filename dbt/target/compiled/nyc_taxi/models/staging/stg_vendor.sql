with source as (
    select * from "postgres"."public"."vendor"
)
select
    vendor_key,
    vendor_name
from source
