-- stg_payment.sql
-- Dim payment type tĩnh — hardcode tại đây, không phụ thuộc ETL load.
-- Source: NYC TLC data dictionary.

select 1 AS payment_key, 'Credit card'   AS payment_name union all
select 2,                'Cash'                           union all
select 3,                'No charge'                      union all
select 4,                'Dispute'                        union all
select 5,                'Unknown'                        union all
select 6,                'Voided trip'

