from pyspark.sql.functions import col, concat_ws, current_timestamp, to_date, when
from spark_session import get_spark_session


def run_silver_transformation():
  spark = get_spark_session("SilverTransformation")
  spark.sparkContext.setLogLevel("ERROR")

  bronze_path = "lakehouse/bronze/hotel_bookings"
  silver_path = "lakehouse/silver/hotel_bookings"

  df_bronze = spark.read.format("delta").load(bronze_path)

  business_columns = [
      c
      for c in df_bronze.columns
      if c not in ["ingestion_timestamp", "source_file"]
  ]

  df_dropDuplicates = df_bronze.drop_duplicates(business_columns)

  df_null = df_dropDuplicates.fillna({
      "children": 0,
      "country": "Unknown",
      "company": "No Company",
      "agent": "No Agent",
  })

  df_valid = df_null.filter(
      (col("children") + col("adults") + col("babies") > 0)
      & (col("adr") >= 0)
  )

  df_final_date = df_valid.withColumn(
      "arrival_date",
      to_date(
          concat_ws(
              "-",
              col("arrival_date_year"),
              col("arrival_date_month"),
              col("arrival_date_day_of_month"),
          ),
          "yyyy-MMMM-d",
      ),
  )

  df_metrics = df_final_date.withColumn(
      "total_nights",
      col("stays_in_weekend_nights") + col("stays_in_week_nights"),
  ).withColumns({
      "total_revenue": when(
          col("is_canceled") == 0, col("adr") * col("total_nights")
      ).otherwise(0.0),
      "silver_processed_timestamp": current_timestamp(),
  })

  df_metrics.write.format("delta").mode("overwrite").save(silver_path)

  # Validación final desde Delta
  df_silver_check = spark.read.format("delta").load(silver_path)
  print(
      "[SILVER] Transformación completada. Total de registros limpios:"
      f" {df_silver_check.count()}"
  )

  spark.stop()


if __name__ == "__main__":
  run_silver_transformation()