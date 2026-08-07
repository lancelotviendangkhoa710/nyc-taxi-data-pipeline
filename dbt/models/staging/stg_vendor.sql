with source as (
    select * from {{ source('warehouse', 'dim_vendor') }}
)

select
    vendor_key,
    vendor_name
from source