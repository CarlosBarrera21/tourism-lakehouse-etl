from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession


def get_spark_session(app_name="TourismLakehouseETL"):
  builder = (
      SparkSession.builder.appName(app_name)
      .master("local[*]")
      .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
      .config(
          "spark.sql.catalog.spark_catalog",
          "org.apache.spark.sql.delta.catalog.DeltaCatalog",
      )
      .config("spark.driver.memory", "2g")
  )
  return configure_spark_with_delta_pip(builder).getOrCreate()


if __name__ == "__main__":
  spark = get_spark_session()
  spark.sparkContext.setLogLevel("ERROR")

  # Prueba de escritura y lectura en formato Delta
  data = [(1, "Cartagena", 450.0), (2, "Santa Marta", 320.5)]
  df = spark.createDataFrame(data, ["id", "destination", "price"])

  delta_path = "lakehouse/test_delta"
  df.write.format("delta").mode("overwrite").save(delta_path)

  df_read = spark.read.format("delta").load(delta_path)
  df_read.show()
  print("PySpark + Delta Lake configurado correctamente.")
  spark.stop()
