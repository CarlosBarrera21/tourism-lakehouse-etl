from spark_session import get_spark_session

spark = get_spark_session("GoldSQLAnalytics")
spark.sparkContext.setLogLevel("ERROR")

for table in [
    "dim_hotel",
    "dim_country",
    "dim_market",
    "dim_date",
    "fact_bookings",
]:
    spark.read.format("delta").load(
      f"lakehouse/gold/{table}"
  ).createOrReplaceTempView(table)

    query = "SELECT dim_hotel.hotel_name,COUNT(*) AS total_bookings, ROUND(AVG(fact_bookings.is_canceled) * 100,2) AS cancelation_rate,ROUND(SUM(fact_bookings.total_revenue),2) AS total_revenue FROM fact_bookings JOIN dim_hotel ON fact_bookings.hotel_id = dim_hotel.hotel_id  GROUP BY dim_hotel.hotel_name"
    query2 = "SELECT c.country_code, SUM(f.total_nights), ROUND (SUM(f.total_revenue),2) AS total_revenue FROM fact_bookings AS f JOIN dim_country AS c ON f.country_id = c.country_id JOIN dim_date AS d ON f.arrival_date = d.arrival_date WHERE d.month IN (7,8) AND c.country_code != 'PRT' AND f.is_canceled = 0 GROUP BY c.country_code ORDER BY total_revenue DESC LIMIT 5"
    query3 = "SELECT m.market_segment, m.distribution_channel, COUNT(*) AS total_bookings, ROUND(AVG(is_canceled) * 100,2) AS cancelation_rate, FORMAT_NUMBER(SUM(f.total_revenue),2) AS total_revenue FROM fact_bookings AS f JOIN dim_market AS m ON f.market_id = m.market_id GROUP BY m.market_segment, m.distribution_channel HAVING total_bookings > 1000 AND cancelation_rate > 30 ORDER BY cancelation_rate DESC"
    query4 = "WITH resumen_mensual AS (SELECT d.year, d.month_name, RANK() OVER (PARTITION BY d.year ORDER BY SUM(f.total_revenue) DESC) AS ranking, ROUND(SUM(f.total_revenue),2) AS monthly_revenue FROM fact_bookings AS f JOIN dim_date AS d ON f.arrival_date = d.arrival_date WHERE f.is_canceled = 0 GROUP BY d.year, d.month_name) SELECT * FROM resumen_mensual WHERE ranking <= 2 ORDER BY year, ranking"

spark.sql("DESCRIBE fact_bookings").show(truncate=False)
spark.sql("DESCRIBE dim_hotel").show(truncate=False)
spark.sql("DESCRIBE dim_date").show(truncate=False)
spark.sql("DESCRIBE dim_country").show(truncate=False)
spark.sql("DESCRIBE dim_market").show(truncate=False)


spark.sql(query4).show(truncate=False)
spark.stop()