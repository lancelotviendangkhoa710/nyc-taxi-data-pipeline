-- stg_vendor.sql
-- Dim vendor tĩnh — hardcode tại đây, không phụ thuộc ETL load.
-- Source: NYC TLC data dictionary.

select 1 AS vendor_key, 'Creative Mobile Technologies' AS vendor_name union all
select 2,                'Curb Mobility'                               union all
select 7,                'Unknown'

