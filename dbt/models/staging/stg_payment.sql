with source as (
    select * from {{ source('warehouse', 'dim_payment') }}
)

select
    payment_key,
    payment_name
from source