
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip


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