# Adaptive Spark Partitioning Strategy

## Objective

Keep physical Parquet files near a useful size while retaining the logical
`pickup_date` layout needed for partition pruning. Use 128–256 MiB for normal
workloads and 256–512 MiB for heavier scans or more expensive jobs.

## Calculation

For every batch, the loader sums the size of raw files matching
`yellow_tripdata_*.parquet`, then calculates:

```text
write_partitions = clamp(ceil(raw_batch_bytes / target_file_bytes), min, max)
```

The raw files are already Parquet, so their compressed on-disk size is a
practical first-order estimate of output size. The loader logs the source size,
target, and selected number on every write.

| Raw batch size | Standard (256 MiB) | Heavy (512 MiB) |
|---:|---:|---:|
| 128 MiB | 1 | 1 |
| 256 MiB | 1 | 1 |
| 1 GiB | 4 | 2 |
| 10 GiB | 40 | 20 |

## Configuration

| Environment variable | Default | Purpose |
|---|---:|---|
| `ETL_PARTITION_PROFILE` | `standard` | `standard` selects 256 MiB; `heavy` selects 512 MiB. |
| `ETL_TARGET_FILE_SIZE_MB` | 256 / 512 | Explicit target override, such as 128, 256, or 512. |
| `ETL_MIN_WRITE_PARTITIONS` | 1 | Lower safety bound. |
| `ETL_MAX_WRITE_PARTITIONS` | 2000 | Upper safety bound against runaway task counts. |
| `ETL_INPUT_SIZE_BYTES` | unset | Exact batch byte count supplied by an orchestrator; useful for remote input. |

```powershell
# Default 256 MiB target
python -m spark.etl.main

# Heavy workload: use a 512 MiB target
$env:ETL_PARTITION_PROFILE = "heavy"
python -m spark.etl.main

# Small-file-sensitive workload: use 128 MiB
$env:ETL_TARGET_FILE_SIZE_MB = "128"
python -m spark.etl.main
```

## Physical versus logical partitions

- If more parallelism is needed, `repartition(n)` creates approximately `n`
  balanced write tasks (and performs a shuffle). If fewer are needed,
  `coalesce(n)` avoids that extra shuffle.
- `partitionBy("pickup_date")` retains folders such as `pickup_date=2026-01-01`.
- Actual file sizes can vary because transformations filter rows, Parquet
  compression varies by column, and date values can be skewed.

After representative runs, inspect output-file sizes. If they are consistently
too small or large, tune `ETL_TARGET_FILE_SIZE_MB`; retain the formula. For a
very skewed date, use a smaller date-range batch or add dedicated skew handling.
