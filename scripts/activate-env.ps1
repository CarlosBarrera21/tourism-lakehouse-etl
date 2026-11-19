# Activa el entorno del proyecto: Java 17 + venv de Python.
# Uso (desde la raíz del proyecto):
#   . .\scripts\activate-env.ps1
# El punto inicial es importante: hace que el script se ejecute en la sesión actual.

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$jdkHome     = "C:\Users\caalb\.jdks\jdk-17"
$hadoopHome  = "C:\Users\caalb\.hadoop"
$venvPython  = Join-Path $projectRoot ".venv\Scripts\python.exe"
$venvActivate = Join-Path $projectRoot ".venv\Scripts\Activate.ps1"

if (-not (Test-Path (Join-Path $jdkHome "bin\java.exe"))) {
    throw "No se encontro el JDK 17 en '$jdkHome'. Revisa la ruta o vuelve a extraer el .msi."
}
if (-not (Test-Path (Join-Path $hadoopHome "bin\winutils.exe"))) {
    Write-Warning "No se encontro winutils.exe en '$hadoopHome\bin'. Spark no podra escribir archivos locales."
}
if (-not (Test-Path $venvActivate)) {
    throw "No se encontro el venv en '$projectRoot\.venv'. Crealo con: python -m venv .venv"
}

# Java 17 solo en esta sesion (no toca el Java 25 del sistema)
$env:JAVA_HOME = $jdkHome
$env:PATH      = "$jdkHome\bin;$env:PATH"

# Hadoop winutils (necesario para escribir Parquet/CSV en Windows)
$env:HADOOP_HOME = $hadoopHome
$env:PATH        = "$hadoopHome\bin;$env:PATH"

# PySpark debe usar el Python del venv tambien en los workers locales
$env:PYSPARK_PYTHON        = $venvPython
$env:PYSPARK_DRIVER_PYTHON = $venvPython

# Activa el venv (python/pip apuntan al del proyecto)
. $venvActivate

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "JAVA_HOME   = $env:JAVA_HOME" -ForegroundColor Cyan
& java -version 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "HADOOP_HOME = $env:HADOOP_HOME" -ForegroundColor Cyan
Write-Host "Python      = $(& python --version 2>&1)" -ForegroundColor Cyan
Write-Host "PySpark     = $(& python -c 'import pyspark; print(pyspark.__version__)' 2>&1)" -ForegroundColor Cyan
Write-Host ""
