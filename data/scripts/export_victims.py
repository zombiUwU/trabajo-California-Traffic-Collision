import sqlite3
import pandas as pd
import os

""" este script es para crear los archivos parquet de toda la tabla de
victims dentro de una carpeta, solo funciona si tienes el archivo de la BD original
(switrs.sqlite)
"""

DB_PATH = "switrs.sqlite"
OUTPUT_DIR = "parquet_victims"

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

chunk_size = 100_000  # ajustable según tu RAM

# iniciamos la exportacion

for i, chunk in enumerate(
    pd.read_sql_query(
        "SELECT * FROM victims",
        conn,
        chunksize=chunk_size
    )
):
    output_file = f"{OUTPUT_DIR}/victims_part_{i}.parquet"

    chunk.to_parquet(
        output_file,
        engine="pyarrow",
        compression="snappy"
    )

    print(f"Guardado: {output_file}")

conn.close()

print("Exportación finalizada correctamente.")