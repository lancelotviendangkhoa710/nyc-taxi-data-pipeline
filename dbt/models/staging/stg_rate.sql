with source as (
    select * from {{ source('warehouse', 'dim_rate') }}
)

select
    rate_key,
    rate_name
from source