# Fija Java 17 + Hadoop dentro de los scripts de activación del venv.
# Asi, cualquier terminal donde actives el venv usa Java 17 (no el 25 del sistema).
#
# Se ejecuta una sola vez, y otra vez si borras/recreas el venv:
#   .\scripts\patch-venv.ps1
# Es idempotente: si ya estaba parcheado, lo reemplaza limpiamente.

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$jdkHome     = "C:\Users\caalb\.jdks\jdk-17"
$hadoopHome  = "C:\Users\caalb\.hadoop"
$scriptsDir  = Join-Path $projectRoot ".venv\Scripts"
$marker      = "tourism-lakehouse-etl: Java 17"

if (-not (Test-Path $scriptsDir)) {
    throw "No existe '$scriptsDir'. Crea el venv primero: python -m venv .venv"
}

$psTemplate = @'
# === tourism-lakehouse-etl: Java 17 + Hadoop ===
if (-not $env:TOURISM_JAVA17_ACTIVE) {
    $env:TOURISM_JAVA17_ACTIVE = "1"
    $env:JAVA_HOME       = "__JDK__"
    $env:HADOOP_HOME     = "__HADOOP__"
    $env:PATH            = "$env:JAVA_HOME\bin;$env:HADOOP_HOME\bin;$env:PATH"
    $env:PYSPARK_PYTHON  = Join-Path $PSScriptRoot "python.exe"
    $env:PYSPARK_DRIVER_PYTHON = $env:PYSPARK_PYTHON
}
'@

# Sin bloque entre parentesis: en cmd, %VAR% se expande al parsear el bloque
# completo, asi que un "if (...)" interno romperia la expansion de %JAVA_HOME%.
$batTemplate = @'
rem === tourism-lakehouse-etl: Java 17 + Hadoop ===
if defined TOURISM_JAVA17_ACTIVE goto tourism_env_done
set "TOURISM_JAVA17_ACTIVE=1"
set "JAVA_HOME=__JDK__"
set "HADOOP_HOME=__HADOOP__"
set "PATH=%JAVA_HOME%\bin;%HADOOP_HOME%\bin;%PATH%"
set "PYSPARK_PYTHON=%~dp0python.exe"
set "PYSPARK_DRIVER_PYTHON=%~dp0python.exe"
:tourism_env_done
'@

function Set-ActivationScript {
    param(
        [string]$Path,
        [string]$Template
    )

    if (-not (Test-Path $Path)) {
        Write-Warning "No existe $Path, se omite."
        return
    }

    $text = [System.IO.File]::ReadAllText($Path)

    # Quita un parche anterior, si existe
    $idx = $text.IndexOf($marker)
    if ($idx -ge 0) {
        $lineStart = $text.LastIndexOf("`n", $idx)
        if ($lineStart -lt 0) { $lineStart = 0 }
        $text = $text.Substring(0, $lineStart)
    }

    $block = $Template.Replace("__JDK__", $jdkHome).Replace("__HADOOP__", $hadoopHome).Trim()

    # Normaliza a LF, une y devuelve todo a CRLF (cmd exige CRLF)
    $text = $text.TrimEnd("`r", "`n")
    $new = "$text`n`n$block`n"
    $new = $new.Replace("`r`n", "`n").Replace("`n", "`r`n")

    [System.IO.File]::WriteAllText($Path, $new, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "Parcheado: $Path"
}

Set-ActivationScript -Path (Join-Path $scriptsDir "Activate.ps1") -Template $psTemplate
Set-ActivationScript -Path (Join-Path $scriptsDir "activate.bat") -Template $batTemplate
