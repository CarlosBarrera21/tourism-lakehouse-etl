"""Smoke test del entorno: comprueba Java 17 + PySpark + escritura Parquet.

Uso:
    python scripts/smoke_test.py
"""

import shutil
from pathlib import Path

from pyspark.sql import SparkSession

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "data" / "_smoke"


def main() -> None:
    spark = (
        SparkSession.builder.master("local[*]")
        .appName("smoke-test")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    jvm = spark.sparkContext._jvm
    print(f"Spark     : {spark.version}")
    print(f"Java      : {jvm.java.lang.System.getProperty('java.version')}")
    print(f"JAVA_HOME : {jvm.java.lang.System.getProperty('java.home')}")

    shutil.rmtree(OUT_DIR, ignore_errors=True)
    spark.range(5).write.mode("overwrite").parquet(str(OUT_DIR))
    total = spark.read.parquet(str(OUT_DIR)).count()
    print(f"Parquet write/read OK -> {total} filas en {OUT_DIR}")

    spark.stop()
    shutil.rmtree(OUT_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
