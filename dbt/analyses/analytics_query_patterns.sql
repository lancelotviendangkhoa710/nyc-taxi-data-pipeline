-- Read-only Redshift query patterns over dbt marts.
-- Run with: dbt compile --select analytics_query_patterns

-- 1. Window-function deduplication is implemented in models/staging/stg_trip.sql.
--    ROW_NUMBER partitions deterministic SHA-256 trip IDs and retains duplicate_rank = 1.

-- 2. Top five pickup zones within each borough.
--    Uses the zone/hour aggregate mart instead of scanning trip-grain facts.
with zone_revenue as (
    select
        borough,
        zone_name,
        sum(trip_count) as trip_count,
        sum(total_revenue) as total_revenue
    from {{ ref('mart_revenue_by_zone_hour') }}
    group by borough, zone_name
),
ranked_zones as (
    select
        borough,
        zone_name,
        trip_count,
        total_revenue,
        dense_rank() over (
            partition by borough
            order by total_revenue desc
        ) as revenue_rank
    from zone_revenue
)
select
    borough,
    zone_name,
    trip_count,
    total_revenue,
    revenue_rank
from ranked_zones
where revenue_rank <= 5
order by borough, revenue_rank, zone_name;

-- 3. Running daily revenue by vendor.
--    The daily vendor mart avoids aggregating the trip-grain fact for every BI query.
with daily_revenue as (
    select
        vendor_name,
        trip_date,
        total_trips,
        total_revenue
    from {{ ref('fct_vendor_daily_metrics') }}
)
select
    vendor_name,
    trip_date,
    total_trips,
    total_revenue,
    sum(total_revenue) over (
        partition by vendor_name
        order by trip_date
        rows between unbounded preceding and current row
    ) as running_revenue
from daily_revenue
order by vendor_name, trip_date;