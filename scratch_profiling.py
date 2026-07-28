import os
import sys

# Cấu hình Java và Hadoop cho Windows
os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot"
os.environ["HADOOP_HOME"] = r"D:\NYC_Taxi_Prj\hadoop"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ["JAVA_HOME"], "bin") + os.pathsep + os.path.join(os.environ["HADOOP_HOME"], "bin")

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, round, year, month, max as spark_max, min as spark_min

print("Initializing Spark...")
spark = SparkSession.builder.appName("profiling").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

print("Reading Parquet...")
df = spark.read.parquet("D:\NYC_Taxi_Project\data\raw\yellow\yellow_tripdata_2026_01.parquet")

total_rows = df.count()
print(f"Total Rows: {total_rows}")

# 1. Null counts and percentages
print("\n--- NULL PERCENTAGES ---")
null_exprs = [round((sum(col(c).isNull().cast("int")) / total_rows * 100), 4).alias(c) for c in df.columns]
null_pcts = df.select(null_exprs).collect()[0].asDict()
for k, v in null_pcts.items():
    print(f"{k}: {v}%")

# 2. Outliers
print("\n--- OUTLIERS ---")
trip_dist_zero = df.filter(col("trip_distance") <= 0).count()
trip_dist_large = df.filter(col("trip_distance") > 100).count()
max_trip_dist = df.select(spark_max("trip_distance")).collect()[0][0]
print(f"trip_distance <= 0: {trip_dist_zero} ({trip_dist_zero/total_rows*100:.4f}%)")
print(f"trip_distance > 100: {trip_dist_large} ({trip_dist_large/total_rows*100:.4f}%)")
print(f"Max trip_distance: {max_trip_dist}")

total_amt_neg = df.filter(col("total_amount") < 0).count()
total_amt_zero = df.filter(col("total_amount") == 0).count()
max_total_amt = df.select(spark_max("total_amount")).collect()[0][0]
min_total_amt = df.select(spark_min("total_amount")).collect()[0][0]
print(f"total_amount < 0: {total_amt_neg} ({total_amt_neg/total_rows*100:.4f}%)")
print(f"total_amount == 0: {total_amt_zero} ({total_amt_zero/total_rows*100:.4f}%)")
print(f"Min/Max total_amount: {min_total_amt} / {max_total_amt}")

# 3. Datetime anomalies
print("\n--- DATETIME ANOMALIES ---")
invalid_time = df.filter(col("tpep_dropoff_datetime") <= col("tpep_pickup_datetime")).count()
wrong_date = df.filter((year("tpep_pickup_datetime") != 2026) | (month("tpep_pickup_datetime") != 1)).count()
print(f"Dropoff <= Pickup: {invalid_time} ({invalid_time/total_rows*100:.4f}%)")
print(f"Pickup not in Jan 2026: {wrong_date} ({wrong_date/total_rows*100:.4f}%)")

# 4. Categorical distributions
print("\n--- RatecodeID Distribution ---")
df.groupBy("RatecodeID").count().orderBy("RatecodeID").show()

print("\n--- payment_type Distribution ---")
df.groupBy("payment_type").count().orderBy("payment_type").show()

print("\n--- passenger_count Distribution ---")
df.groupBy("passenger_count").count().orderBy("passenger_count").show()

spark.stop()
