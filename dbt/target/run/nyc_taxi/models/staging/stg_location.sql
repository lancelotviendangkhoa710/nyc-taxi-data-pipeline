
  create view "postgres"."public_staging"."stg_location__dbt_tmp"
    
    
  as (
    with source as (
    select * from "postgres"."public"."dim_location"
)

select
    location_key,
    zone,
    borough,
    service_zone
from source
  );