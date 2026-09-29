{{
  config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['source_month', 'trip_id'],
    on_schema_change='sync_all_columns',
    pre_hook="{{ delete_latest_source_month() }}",
    description='Final trip-grain fact table for analysis'
  )
}}

with enriched_trips as (
  select *
  from {{ ref('int_trips_with_dimensions') }}
  where trip_date >= dateadd(month, -12, current_date)
  {% if is_incremental() %}
    and source_month >= (
      select coalesce(max(source_month), '0000-00')
      from {{ this }}
    )
  {% endif %}
)

select
  source_month,
  trip_id,
  vendor_name,
  pickup_zone,
  dropoff_zone,
  trip_date,
  pickup_hour,
  is_weekend,
  passenger_count,
  trip_distance,
  fare_amount,
  tip_amount,
  total_amount,
  case
    when fare_amount > 0 and tip_amount / fare_amount > 0.2 then 'High'
    when fare_amount > 0 and tip_amount / fare_amount > 0.1 then 'Medium'
    else 'Low'
  end as tip_category
from enriched_trips