{{
  config(
    materialized='table',
    description='Daily vendor metrics with trip count, average fare, and total revenue'
  )
}}

with vendor_metrics as (
    select * from {{ ref('int_trip_metrics_by_vendor') }}
)

select
    vendor_name,
    total_trips,
    average_fare,
    total_revenue,
    current_date as metric_date

from vendor_metrics
