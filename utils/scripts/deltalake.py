import os
from pyspark.sql import SparkSession
from delta import *

# --- 1. CONFIGURACIÓN DE RUTAS DINÁMICAS ---
# Ubicación del archivo deltalake.py
script_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos un nivel para llegar a la carpeta 'data'
data_dir = os.path.dirname(script_dir)

# Definimos las rutas finales
raw_path = os.path.join(data_dir, "raw")
delta_path = os.path.join(data_dir, "delta_lake")

print(f"Directorio de datos: {data_dir}")
print(f"Buscando RAW en: {raw_path}")

# --- 2. INICIALIZAR SPARK ---
builder = SparkSession.builder.appName("SWITRS_Delta_Lake") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

tablas = ["collisions", "case_ids", "parties", "victims"]

# --- 3. CREAR VERSIÓN 0 (ORIGINALES) ---
print("\n>>> Creando Versión 0 (Datos Originales)...")
for tabla in tablas:
    input_file = os.path.join(raw_path, f"{tabla}_part_0.parquet")
    output_folder = os.path.join(delta_path, tabla)
    
    # Leer y escribir
    df = spark.read.parquet(input_file)
    df.write.format("delta").mode("overwrite").save(output_folder)
    
    # Registrar vista para SQL
    df.createOrReplaceTempView(tabla)
    print(f"Tabla {tabla} guardada en Delta.")

# --- 4. CREAR VERSIÓN 1 (FILTRADO SQL) ---
print("\n>>> Creando Versión 1 (Filtrado 2020-2021)...")

# Tu consulta original adaptada a Spark SQL
spark.sql("""
    SELECT * FROM case_ids 
    WHERE db_year IN ('2020', '2021', 2020, 2021)
""").createOrReplaceTempView("case_ids_filtered")

queries = {
    "case_ids": "SELECT * FROM case_ids_filtered",
    "collisions": "SELECT * FROM collisions WHERE case_id IN (SELECT case_id FROM case_ids_filtered)",
    "parties": "SELECT * FROM parties WHERE case_id IN (SELECT case_id FROM case_ids_filtered)",
    "victims": "SELECT * FROM victims WHERE case_id IN (SELECT case_id FROM case_ids_filtered)"
}

for nombre, query in queries.items():
    df_v1 = spark.sql(query)
    output_folder = os.path.join(delta_path, nombre)
    
    # Overwrite en Delta crea la Versión 1 automáticamente
    df_v1.write.format("delta").mode("overwrite").save(output_folder)
    print(f"Tabla {nombre} filtrada y actualizada a V1.")

from pyspark.sql.functions import col, when

print("\n>>> Creando Versión 2 (Selección de columnas y nuevas variables)...")

# 1. Transformar COLLISIONS (Selección de columnas + Nueva columna 'turno')
df_collisions_v1 = spark.read.format("delta").load(os.path.join(delta_path, "collisions"))

df_collisions_v2 = df_collisions_v1.select(
    "case_id", "collision_severity", "primary_collision_factor", 
    "killed_victims", "injured_victims", "pcf_violation_category", 
    "weather_1", "lighting", "type_of_collision", "longitude", 
    "latitude", "county_city_location", "county_location", 
    "party_count", "collision_date", "collision_time", 
    "road_surface", "location_type"
).withColumn("turno", 
    when(col("collision_time").between("00:00:00", "05:59:59"), "early morning")
    .when(col("collision_time").between("06:00:00", "11:59:59"), "morning")
    .when(col("collision_time").between("12:00:00", "18:59:59"), "afternoon")
    .otherwise("night")
)

# Guardar con overwriteSchema=True porque estamos cambiando las columnas
df_collisions_v2.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save(os.path.join(delta_path, "collisions"))

# 2. Transformar PARTIES (Selección de columnas)
df_parties_v1 = spark.read.format("delta").load(os.path.join(delta_path, "parties"))
df_parties_v2 = df_parties_v1.select(
    "id", "case_id", "party_number", "party_sobriety", "party_type", 
    "party_drug_physical", "movement_preceding_collision", "at_fault", 
    "vehicle_make", "vehicle_year", "cellphone_in_use", 
    "statewide_vehicle_type", "party_safety_equipment_1", "party_safety_equipment_2"
)
df_parties_v2.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .save(os.path.join(delta_path, "parties"))

# 3. Transformar VICTIMS (Selección de columnas)
df_victims_v1 = spark.read.format("delta").load(os.path.join(delta_path, "victims"))
df_victims_v2 = df_victims_v1.select(
    "id", "case_id", "party_number", "victim_role", "victim_sex", 
    "victim_age", "victim_degree_of_injury", "victim_seating_position", 
    "victim_safety_equipment_1", "victim_safety_equipment_2", "victim_ejected"
)
df_victims_v2.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .save(os.path.join(delta_path, "victims"))

# 4. Crear tabla nueva: INVOLVED_VICTIMS
df_involved_victims = df_victims_v2.select("id", "case_id", "victim_sex", "victim_age")
df_involved_victims.write.format("delta").mode("overwrite") \
    .save(os.path.join(delta_path, "involved_victims"))
    
print("dios mio al fin funciono")