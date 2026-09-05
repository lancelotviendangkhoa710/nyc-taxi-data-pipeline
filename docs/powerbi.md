# Power BI Setup and Dashboard Plan

## Purpose

Power BI is the presentation layer for the NYC Taxi warehouse. It connects to BigQuery and reads dbt marts after the Spark and dbt containers complete.

## Workflow

```powershell
docker compose -f infrastructure/docker/docker-compose.yml up --build
```

After `dbt run` and `dbt test` succeed, connect Power BI Desktop to Google BigQuery using the same GCP project configured in `.env`.

## Warehouse Connection

Use the **Google BigQuery** connector in Power BI and select the dbt output dataset configured in `dbt/profiles.yml` (`nyc_taxi_dbt` by default). Select tables in the `marts` schema, not raw or staging tables.

## Recommended Dashboards

### 1. Executive Overview

Use `dbt` mart tables for a top-level view:

- total trips
- total revenue
- average fare
- average tip ratio
- trips by day

Suggested source: `fct_trip_summary`

### 2. Vendor Performance

Track vendor activity and revenue:

- trips by vendor
- revenue by vendor
- average fare by vendor
- daily vendor trend

Suggested source: `fct_vendor_daily_metrics`

### 3. Trip Operations

Explore operational behavior:

- trip distance distribution
- trip duration by hour
- pickup and dropoff patterns
- weekend versus weekday activity

Suggested source: `fct_trip_summary` and staging/intermediate models where needed

## Refresh Process

Power BI reads from BigQuery, so the dashboard data refreshes after the warehouse and dbt marts are rebuilt.

Recommended order:

1. Run Spark ETL
2. Load the BigQuery raw table
3. Run `dbt run`
4. Run `dbt test`
5. Refresh the Power BI dataset or report

## Next Step

The next implementation step is to build the actual Power BI report pages and document the final KPI definitions here.
