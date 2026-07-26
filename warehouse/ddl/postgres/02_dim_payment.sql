-- PostgreSQL DDL for dim_payment
CREATE TABLE IF NOT EXISTS dim_payment (
    payment_key INTEGER PRIMARY KEY,
    payment_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_payment IS 'Dimension: Payment method information';
COMMENT ON COLUMN dim_payment.payment_key IS 'Mã phương thức thanh toán (1=Credit card, 2=Cash, etc.)';
COMMENT ON COLUMN dim_payment.payment_name IS 'Tên phương thức thanh toán';