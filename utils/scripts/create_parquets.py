# este script se uso para crear los archivos parquets que estan dentro del Drive

import sqlite3
import pandas as pd

db_name = "California_modificada.sqlite"

# Conexión directa
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Consultar el catálogo maestro de SQLite
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = [fila[0] for fila in cursor.fetchall()]

if not tablas:
    print("volvio a fallar")
else:
    for tabla in tablas:
        print(f"Exportando {tabla}...")
        df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
        df.to_parquet(f"{tabla}.parquet", index=False)
    print("listo")

conn.close()