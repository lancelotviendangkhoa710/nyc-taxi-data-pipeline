CREATE OR REPLACE TABLE dim_vendor (
    vendor_key INT64 OPTIONS(description="Mã nhà cung cấp (1=CMT, 2=VeriFone)"),
    vendor_name STRING OPTIONS(description="Tên nhà cung cấp")
);
