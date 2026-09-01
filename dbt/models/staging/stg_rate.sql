-- stg_rate.sql
-- Dim rate code tĩnh — hardcode tại đây, không phụ thuộc ETL load.
-- Source: NYC TLC data dictionary.

select rate_key, rate_name
from UNNEST([
    STRUCT(1  AS rate_key, 'Standard rate'         AS rate_name),
    STRUCT(2,              'JFK'),
    STRUCT(3,              'Newark'),
    STRUCT(4,              'Nassau or Westchester'),
    STRUCT(5,              'Negotiated fare'),
    STRUCT(6,              'Group ride'),
    STRUCT(99,             'Unknown')
])
