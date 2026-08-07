
  create view "postgres"."public_staging"."stg_rate__dbt_tmp"
    
    
  as (
    with source as (
    select * from "postgres"."public"."dim_rate"
)

select
    rate_key,
    rate_name
from source
  );