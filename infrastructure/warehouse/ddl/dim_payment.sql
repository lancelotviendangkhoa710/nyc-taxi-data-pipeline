CREATE OR REPLACE TABLE dim_payment (
    payment_key INT64 OPTIONS(description="Mã phương thức thanh toán (1=Credit card, 2=Cash, etc.)"),
    payment_name STRING OPTIONS(description="Tên phương thức thanh toán")
);
