# Power BI Setup and Dashboard Plan

## Purpose

Power BI is the presentation layer for the NYC Taxi warehouse. It connects to PostgreSQL and reads the dbt marts and warehouse tables to power dashboards.

## Local Workflow

Power BI is usually run as a desktop or service application rather than inside the Docker stack. The project stack prepares the source data in PostgreSQL, and Power BI connects to that database from the host machine.

Recommended order:

```powershell
docker compose -f infrastructure/docker/docker-compose.local.yml up -d postgres
docker compose -f infrastructure/docker/docker-compose.local.yml run --rm --no-deps dbt
```

After the warehouse and marts are ready, open Power BI and connect to PostgreSQL.

## Warehouse Connection

Connect Power BI to the project PostgreSQL database:

- Host: `localhost` when connecting from the host
- Port: `5432`
- Database: `nyc_taxi`
- Schema: `public`
- User: `postgres`
- Password: same value as `PG_PASSWORD` in `.env`

If you use Power BI inside a managed environment or gateway, point it at the same PostgreSQL database and keep the schema as `public`.

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

Power BI reads from PostgreSQL, so the dashboard data refreshes whenever the warehouse and dbt marts are rebuilt.

Recommended order:

1. Run Spark ETL
2. Load PostgreSQL warehouse
3. Run `dbt run`
4. Run `dbt test`
5. Refresh the Power BI dataset or report

## Next Step

The next implementation step is to build the actual Power BI report pages and document the final KPI definitions here.
