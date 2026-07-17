CREATE OR REPLACE TABLE dim_rate (
    rate_key INT64 OPTIONS(description="Mã loại cước (RatecodeID)"),
    rate_name STRING OPTIONS(description="Tên loại cước (Standard, JFK, etc.)")
);
