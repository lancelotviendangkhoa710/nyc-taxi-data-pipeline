-- stg_vendor.sql
-- Dim vendor tĩnh — hardcode tại đây, không phụ thuộc ETL load.
-- Source: NYC TLC data dictionary.

select vendor_key, vendor_name
from UNNEST([
    STRUCT(1 AS vendor_key, 'Creative Mobile Technologies' AS vendor_name),
    STRUCT(2,                'Curb Mobility'),
    STRUCT(7,                'Unknown')
])
