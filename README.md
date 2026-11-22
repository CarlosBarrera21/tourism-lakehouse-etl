# Tourism Lakehouse ETL Pipeline

Pipeline de ingeniería de datos construido con **PySpark**, **Delta Lake** y **Spark SQL** bajo una **Arquitectura Medallion (Bronze, Silver, Gold)** para transformar datos crudos de reservas hoteleras en un **Esquema Estrella** optimizado para analítica de negocio.

---

## Arquitectura del Proyecto

El flujo procesa el dataset histórico de reservas hoteleras a través de tres capas de refinamiento progresivo:

1. ** Capa Bronze (`src/01_bronze_ingestion.py`)**
   * Ingesta del archivo CSV crudo hacia formato columnar **Delta Lake** sin alteraciones, garantizando trazabilidad y auditoría histórica.
2. ** Capa Silver (`src/02_silver_cleaning.py`)**
   * Eliminación de registros duplicados (~32,000 filas redundantes).
   * Limpieza e imputación de valores nulos y estandarización de fechas (`arrival_date`).
   * Aplicación de reglas de negocio: filtrado de tarifas diarias (`adr`) inválidas/negativas, validación de huéspedes totales (> 0), cálculo de `total_nights` y cálculo de `total_revenue` (asignando `0.0` a reservas canceladas).
3. ** Capa Gold (`src/03_gold_modeling.py`)**
   * Modelado dimensional en **Esquema Estrella** con llaves subrogadas enteras para consultas analíticas de alto rendimiento:
     * **Tabla de Hechos:** (`total_nights`, `total_revenue`, `is_canceled`, `adr`, llaves foráneas).
     * **Dimensiones:** `dim_hotel`, `dim_country`, `dim_market`, `dim_date`.
4. ** Capa Analítica (`src/04_gold_analytics.py`)**
   * Consultas  en Spark SQL

##  Estructura del Repositorio

```text
tourism-lakehouse-etl/
├── data/
│   └── raw/
│       └── hotel_bookings.csv        # Dataset CSV original 
├── docs/                             
├── lakehouse/                        
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── scripts/                          
├── sql/                              # Consultas SQL 
├── src/
│   ├── spark_session.py              # Configuración de Spark + Delta Lake
│   ├── 01_bronze_ingestion.py        # Ingesta CSV -> Bronze Delta
│   ├── 02_silver_transformation.py   # Limpieza y reglas de negocio -> Silver Delta
│   ├── 03_gold_modeling.py           # Modelado Esquema Estrella -> Gold Delta
│   └── 04_gold_sqlanalytics.py       # Consultas analíticas en Spark SQL
├── .gitignore
├── requirements.txt
├── SETUP.md                          # Guía de configuración del entorno
└── README.md


##  Cómo Ejecutar el Proyecto

1. **Clonar el repositorio y configurar el entorno virtual:**
   *(Asegúrate de tener instalados Java 11/17 y WinUtils/Hadoop según lo detallado en `SETUP.md`)*.

```bash
git clone https://github.com/tu-usuario/tourism-lakehouse-etl.git
cd tourism-lakehouse-etl
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. **Colocar el dataset crudo:**
   Descarga el archivo `hotel_bookings.csv` y ubícalo en la ruta `data/raw/hotel_bookings.csv`.

3. **Ejecutar el pipeline completo (Bronze -> Silver -> Gold -> Analytics):**

```bash
python src/01_bronze_ingestion.py && python src/02_silver_transformation.py && python src/03_gold_modeling.py && python src/04_gold_sqlanalytics.py
```



##  Hallazgos Analíticos
A través de `src/04_gold_sqlanalytics.py` se resolvieron preguntas clave de negocio utilizando agregaciones, múltiples `JOIN`s, `HAVING`, CTEs (`WITH`) y Window Functions (`RANK() OVER`):
### 1. Rendimiento General por Tipo de Hotel
<img width="432" height="100" alt="image" src="https://github.com/user-attachments/assets/e807e414-7cbe-41aa-84e7-e012de42066f" />

### 2. Top 5 Mercados Internacionales en Temporada Alta (Julio - Agosto, excluyendo Portugal)
<img width="298" height="157" alt="image" src="https://github.com/user-attachments/assets/d282fbd8-d91e-419b-a388-6d4f141a3db2" />

### 3. Segmentos de Alto Volumen y Alta Cancelación (> 1,000 reservas y > 30% cancelación)
<img width="588" height="106" alt="image" src="https://github.com/user-attachments/assets/5e7a30cb-9a5b-4502-aa5e-7fae1e83157f" />

### 4. Top 2 Meses con Mayores Ingresos por Año (`RANK() OVER`)
<img width="301" height="170" alt="image" src="https://github.com/user-attachments/assets/fbe8587f-2c0a-455d-9322-daef7aa73d62" />


