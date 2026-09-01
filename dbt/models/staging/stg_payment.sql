-- stg_payment.sql
-- Dim payment type tĩnh — hardcode tại đây, không phụ thuộc ETL load.
-- Source: NYC TLC data dictionary.

select payment_key, payment_name
from UNNEST([
    STRUCT(1 AS payment_key, 'Credit card' AS payment_name),
    STRUCT(2,                'Cash'),
    STRUCT(3,                'No charge'),
    STRUCT(4,                'Dispute'),
    STRUCT(5,                'Unknown'),
    STRUCT(6,                'Voided trip')
])
