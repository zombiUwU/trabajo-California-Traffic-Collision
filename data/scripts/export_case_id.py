import sqlite3
import pandas as pd
import os
""" este script es para crear los archivos parquet de toda la tabla de
case_ids dentro de una carpeta, solo funciona si tienes el archivo de la BD original
(switrs.sqlite)
"""
DB_PATH = "switrs.sqlite"
OUTPUT_DIR = "parquet_case_ids"

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

chunk_size = 100_000  # ajustable según tu RAM

# iniciamos la exportacion

for i, chunk in enumerate(
    pd.read_sql_query(
        "SELECT * FROM case_ids",
        conn,
        chunksize=chunk_size
    )
):
    output_file = f"{OUTPUT_DIR}/case_ids_part_{i}.parquet"

    chunk.to_parquet(
        output_file,
        engine="pyarrow",
        compression="snappy"
    )

    print(f"Guardado: {output_file}")

conn.close()

print("Exportación finalizada correctamente.")