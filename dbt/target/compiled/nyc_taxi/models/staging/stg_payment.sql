with source as (
    select * from "postgres"."public"."dim_payment"
)

select
    payment_key,
    payment_name
from source