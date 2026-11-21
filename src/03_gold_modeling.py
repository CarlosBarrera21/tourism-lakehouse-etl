from spark_session import get_spark_session
from pyspark.sql import Window
from pyspark.sql.functions import col, date_format, row_number,month,year,quarter,dayofweek

def run_gold_modeling():
    spark = get_spark_session("GoldModeling")
    spark.sparkContext.setLogLevel("ERROR")

    silver_path = "lakehouse/silver/hotel_bookings"
    gold_path = "lakehouse/gold/hotel_bookings"

    df_silver = spark.read.format("delta").load(silver_path)

    dim_hotel = (
        df_silver.select(col("hotel").alias("hotel_name"))
        .distinct()
        .withColumn("hotel_id", row_number().over(Window.orderBy("hotel_name")))
        .select("hotel_id", "hotel_name")
    )

    dim_country = (
        df_silver.select(col("country").alias("country_code"))
        .distinct()
        .withColumn("country_id", row_number().over(Window.orderBy("country_code")))
        .select("country_id", "country_code")
    )

    dim_market = (
        df_silver.select("market_segment", "distribution_channel", "customer_type")
        .distinct()
        .withColumn(
            "market_id",
            row_number().over(
                Window.orderBy(
                    "market_segment", "distribution_channel", "customer_type"
                )
            ),
        )
        .select(
            "market_id", "market_segment", "distribution_channel", "customer_type"
        )
    )

    dim_date = (
        df_silver.select("arrival_date")
        .distinct()
        .withColumns({
            "year": year(col("arrival_date")),
            "month": month(col("arrival_date")),
            "month_name": date_format(col("arrival_date"), "MMMM"),
            "quarter": quarter(col("arrival_date")),
            "day_of_week": dayofweek(col("arrival_date")),
            "day_name": date_format(col("arrival_date"), "EEEE"),

        })
    
    )

    fact_bookings = (
        df_silver.join(dim_hotel, df_silver.hotel == dim_hotel.hotel_name, "left")
        .join(dim_country, df_silver.country == dim_country.country_code, "left")
        .join(dim_market, 
              on=["market_segment", "distribution_channel", "customer_type"], how="left")

        .select("hotel_id", "country_id", "market_id", "adr", "total_nights", "total_revenue", "is_canceled", "arrival_date", )
    )

    gold_base_path = "lakehouse/gold"

    gold_tables = {
        "dim_hotel": dim_hotel,
        "dim_country": dim_country,
        "dim_market": dim_market,
        "dim_date": dim_date,
        "fact_bookings": fact_bookings,
    }

    for table_name, df_table in gold_tables.items():
        path = f"{gold_base_path}/{table_name}"
        df_table.write.format("delta").mode("overwrite").save(path)
        print(f"[GOLD] Tabla '{table_name}' {df_table.count()} registros")

    spark.stop()

if __name__ == "__main__":
    run_gold_modeling()