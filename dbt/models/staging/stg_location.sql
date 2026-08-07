with source as (
    select * from {{ source('warehouse', 'dim_location') }}
)

select
    location_key,
    zone,
    borough,
    service_zone
from source