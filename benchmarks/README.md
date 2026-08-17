# Spark ETL benchmark

Run the same read, transform, repartition, and Parquet write workload across CPU,
partition, and input groups.

## Select input by time (recommended)

Each raw file represents a month. Pass one or more `start_month:file_count` groups:

```powershell
python -m spark.benchmark.etl_benchmark --cpus 1,2,4 --partitions 1,2,4,8 --time-windows 2025-01:1,2025-01:3,2025-01:6,2025-07:3
```

For example, `2025-01:3` means January through March 2025. The runner requires every
month in the requested range to exist, so a group can never silently omit a month.
The CSV includes `input_start_month`, `input_end_month`, and `input_files`.

## Select input by size

```powershell
python -m spark.benchmark.etl_benchmark --cpus 1,2,4 --partitions 1,2,4,8 --data-sizes-mb 64,128,256
```

The runner selects chronological raw Parquet files until it reaches each requested
input size. Since a Parquet file is the smallest selectable unit, `actual_input_size_mb`
in `benchmarks/results/etl_benchmark.csv` is the value to compare, not the requested size.

Each result records CPU cap (`local[N]`), requested shuffle/write partition count,
input/output row counts, input/output bytes, and read, transform, write, and total
duration. The written Parquet is placed under `data/benchmark-output/` and is replaced
only for the identical benchmark case.

For useful comparisons, run while the machine is otherwise idle, execute each case at
least three times, and compare the median `total_seconds` (or `write_seconds` when
tuning output layout).
