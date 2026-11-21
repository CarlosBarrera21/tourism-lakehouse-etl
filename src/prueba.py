from spark_session import get_spark_session

spark = get_spark_session("InspectSilver")
spark.sparkContext.setLogLevel("ERROR")

df_silver = spark.read.format("delta").load("lakehouse/silver/hotel_bookings")

# 1. Ver el esquema completo (nombres y tipos de datos)
df_silver.printSchema()

# 2. Ver una muestra de las columnas originales vs. las nuevas métricas
df_silver.select(
    "hotel",
    "is_canceled",
    "adr",
    "total_nights",
    "total_revenue",
    "arrival_date",
    "silver_processed_timestamp",
).show(10, truncate=False)

# 3. Comprobar que las reservas canceladas (is_canceled == 1) tengan total_revenue = 0.0
df_silver.filter("is_canceled = 1").select(
    "is_canceled", "adr", "total_nights", "total_revenue"
).show(10)

spark.stop()