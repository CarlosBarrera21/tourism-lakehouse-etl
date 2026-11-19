from pyspark.sql.functions import current_timestamp, input_file_name
from pyspark.sql.types import DateType, DoubleType, IntegerType, StringType, StructField, StructType
from spark_session import get_spark_session


def run_bronze_ingestion():
  spark = get_spark_session("BronzeIngestion")
  spark.sparkContext.setLogLevel("ERROR")

  bronze_schema = StructType([
      StructField("hotel", StringType(), True),
      StructField("is_canceled", IntegerType(), True),
      StructField("lead_time", IntegerType(), True),
      StructField("arrival_date_year", IntegerType(), True),
      StructField("arrival_date_month", StringType(), True),
      StructField("arrival_date_week_number", IntegerType(), True),
      StructField("arrival_date_day_of_month", IntegerType(), True),
      StructField("stays_in_weekend_nights", IntegerType(), True),
      StructField("stays_in_week_nights", IntegerType(), True),
      StructField("adults", IntegerType(), True),
      StructField("children", IntegerType(), True),
      StructField("babies", IntegerType(), True),
      StructField("meal", StringType(), True),
      StructField("country", StringType(), True),
      StructField("market_segment", StringType(), True),
      StructField("distribution_channel", StringType(), True),
      StructField("is_repeated_guest", IntegerType(), True),
      StructField("previous_cancellations", IntegerType(), True),
      StructField("previous_bookings_not_canceled", IntegerType(), True),
      StructField("reserved_room_type", StringType(), True),
      StructField("assigned_room_type", StringType(), True),
      StructField("booking_changes", IntegerType(), True),
      StructField("deposit_type", StringType(), True),
      StructField("agent", StringType(), True),
      StructField("company", StringType(), True),
      StructField("days_in_waiting_list", IntegerType(), True),
      StructField("customer_type", StringType(), True),
      StructField("adr", DoubleType(), True),
      StructField("required_car_parking_spaces", IntegerType(), True),
      StructField("total_of_special_requests", IntegerType(), True),
      StructField("reservation_status", StringType(), True),
      StructField("reservation_status_date", DateType(), True),
  ])

  raw_path = "data/raw/hotel_bookings.csv"
  delta_path = "lakehouse/bronze/hotel_bookings"

  df_bronze = (
      spark.read.csv(
          raw_path, nullValue="NA", header=True, schema=bronze_schema
      )
      .withColumn("ingestion_timestamp", current_timestamp())
      .withColumn("source_file", input_file_name())
  )

  df_bronze.write.format("delta").mode("overwrite").save(delta_path)

  # Validación
  total_rows = spark.read.format("delta").load(delta_path).count()
  print(f"[BRONZE] Ingesta exitosa. Total de registros: {total_rows}")

  spark.stop()


if __name__ == "__main__":
  run_bronze_ingestion()