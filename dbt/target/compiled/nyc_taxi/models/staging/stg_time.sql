with source as (
    select * from "postgres"."public"."dim_time"
)

select
    time_key,
    datetime,
    date,
    year,
    month,
    month_name,
    day,
    day_of_week,
    day_name,
    hour,
    is_weekend,
    is_peak_hour,
    quarter
from source