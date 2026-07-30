-- PostgreSQL DDL for dim_rate
CREATE TABLE IF NOT EXISTS dim_rate (
    rate_key INTEGER PRIMARY KEY,
    rate_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_rate IS 'Dimension: Rate type information';
COMMENT ON COLUMN dim_rate.rate_key IS 'Mã loại cước (RatecodeID)';
COMMENT ON COLUMN dim_rate.rate_name IS 'Tên loại cước (Standard, JFK, etc.)';