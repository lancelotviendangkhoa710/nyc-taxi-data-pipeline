-- PostgreSQL DDL for dim_vendor
CREATE TABLE IF NOT EXISTS dim_vendor (
    vendor_key INTEGER PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dim_vendor IS 'Dimension: Taxi vendor information';
COMMENT ON COLUMN dim_vendor.vendor_key IS 'Mã nhà cung cấp (1=CMT, 2=VeriFone)';
COMMENT ON COLUMN dim_vendor.vendor_name IS 'Tên nhà cung cấp';