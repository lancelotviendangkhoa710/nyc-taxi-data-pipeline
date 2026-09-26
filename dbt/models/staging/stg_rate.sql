-- stg_rate.sql
-- Dim rate code tĩnh — hardcode tại đây, không phụ thuộc ETL load.
-- Source: NYC TLC data dictionary.

select 1 AS rate_key, 'Standard rate'         AS rate_name union all
select 2,              'JFK'                                union all
select 3,              'Newark'                             union all
select 4,              'Nassau or Westchester'              union all
select 5,              'Negotiated fare'                    union all
select 6,              'Group ride'                         union all
select 99,             'Unknown'

