{{
  config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['vendor_name', 'trip_date'],
    on_schema_change='sync_all_columns',
    pre_hook="{{ delete_latest_source_month() }}",
    description='Daily vendor metrics at one row per vendor and trip date'
  )
}}

with enriched_trips as (
    select *
    from {{ ref('int_trips_with_dimensions') }}
    where vendor_name is not null
    {% if is_incremental() %}
      and source_month >= (
        select coalesce(max(source_month), '0000-00')
        from {{ this }}
      )
    {% endif %}
)

select
    vendor_name,
    trip_date,
    max(source_month) as source_month,
    count(trip_id) as total_trips,
    avg(fare_amount) as average_fare,
    sum(total_amount) as total_revenue
from enriched_trips
group by
    vendor_name,
    trip_date
having count(trip_id) > 0
   and avg(fare_amount) > 0
   and sum(total_amount) > 0
