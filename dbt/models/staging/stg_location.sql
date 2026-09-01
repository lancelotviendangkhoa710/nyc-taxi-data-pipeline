-- stg_location.sql
-- JOIN LocationID từ yellow_taxi_raw với taxi_zone_lookup seed
-- để có zone, borough, service_zone đầy đủ.

with raw as (
    select * from {{ source('warehouse', 'yellow_taxi_raw') }}
),

all_locations as (
    select COALESCE(PULocationID, 0) AS location_key from raw
    union distinct
    select COALESCE(DOLocationID, 0) AS location_key from raw
),

zone_lookup as (
    select
        LocationID  as location_key,
        Zone        as zone,
        Borough     as borough,
        service_zone
    from {{ ref('taxi_zone_lookup') }}
)

select
    l.location_key,
    COALESCE(z.zone,         'Unknown') as zone,
    COALESCE(z.borough,      'Unknown') as borough,
    COALESCE(z.service_zone, 'Unknown') as service_zone
from all_locations l
left join zone_lookup z using (location_key)
where l.location_key > 0
