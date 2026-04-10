#Para poder conectar la base de datos zip con los utils sin importar el dispositivo

import os

# 1. Ubicación de este archivo (C:/.../proyecto/utils/Config.py)
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Subimos un nivel para llegar a la raíz del proyecto (C:/.../proyecto/)
BASE_DIR = os.path.dirname(UTILS_DIR)

# 3. Definimos la ruta a la carpeta de datos en la raíz
DATA_DIR = os.path.join(BASE_DIR, "data")
ZIP_PATH = os.path.join(DATA_DIR, "California_modificada.zip")

# 4. Ruta de extracción para la base de datos SQLite
# Se guardará en: proyecto/data/db_extracted/California_modificada.db
EXTRACT_PATH = os.path.join(DATA_DIR, "db_extracted")
DB_PATH = os.path.join(EXTRACT_PATH, "California_modificada.db")

# Crear la carpeta de extracción automáticamente si no existe
if not os.path.exists(EXTRACT_PATH):
    os.makedirs(EXTRACT_PATH)