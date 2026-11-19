# Entorno local (Java 17 + PySpark)

Configuración aislada **solo para este proyecto**: el Java 25 instalado en el sistema
no se modifica, ni se toca `JAVA_HOME` a nivel de usuario/máquina.

## Componentes y rutas

| Componente | Versión | Ruta |
| --- | --- | --- |
| JDK | Temurin 17.0.21 | `C:\Users\caalb\.jdks\jdk-17` |
| Hadoop winutils | 3.3.6 | `C:\Users\caalb\.hadoop\bin` |
| Python venv | 3.14.3 | `.venv\` (en el proyecto) |
| PySpark | 3.5.3 | dentro del venv |

## Cómo se activa

**En VSCode (automático):** abre esta carpeta como workspace. `.vscode/settings.json`
inyecta `JAVA_HOME`, `HADOOP_HOME`, `PATH` y el Python del venv en cada terminal
integrada nueva, y fija el intérprete de Python del proyecto.

**En cualquier terminal (manual):**

```powershell
. .\scripts\activate-env.ps1
```

(El punto inicial es obligatorio: el script debe ejecutarse en la sesión actual.)

Comprobación rápida de todo el stack:

```powershell
python .\scripts\smoke_test.py
```

Debe imprimir `Java: 17.0.21` y `Parquet write/read OK`.

## Notas

- Si el JDK 17 se borra o se mueve, basta con volver a extraer el `.msi`:
  ```powershell
  msiexec /a "C:\Users\caalb\Downloads\jdk-17\OpenJDK17U-jdk_x64_windows_hotspot_17.0.21_9.msi" /qn TARGETDIR="C:\Users\caalb\.jdks\tmp"
  # luego mover el contenido de ...\tmp\PFiles64\Eclipse Adoptium\jdk-17.0.21.9-hotspot a C:\Users\caalb\.jdks\jdk-17
  ```
  El `/a` es una instalación administrativa: extrae los archivos sin registrar nada en Windows.
- `winutils.exe` + `hadoop.dll` son necesarios para que Spark escriba Parquet/CSV en Windows.
  Sin ellos, `.write...` falla con `HADOOP_HOME and hadoop.home.dir are unset`.
- El venv vive dentro de OneDrive, así que OneDrive sincronizará `.venv\`. Si molesta,
  excluye esa carpeta de la sincronización (OneDrive → Configuración → Elegir carpetas)
  o marca `.venv` como "Liberar espacio".
