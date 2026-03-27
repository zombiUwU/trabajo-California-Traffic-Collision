import pandas as pd
import numpy as np 
import os

# --- CONFIGURACIÓN GLOBAL DE RUTAS ---
# Cámbiala aquí una sola vez y afectará a todas las funciones
BASE_PATH = r"C:\trabajo_california\data\delta_lake"

def load_parquet_table(table_name):
    """
    Busca todos los archivos .parquet dentro de una carpeta y los une.
    """
    path = os.path.join(BASE_PATH, table_name)
    
    if not os.path.exists(path):
        print(f"❌ Error: La ruta no existe -> {path}")
        return pd.DataFrame()
    
    # Listar archivos .parquet
    files = [f for f in os.listdir(path) if f.endswith('.parquet')]
    
    if not files:
        print(f"⚠️ Advertencia: No hay archivos .parquet en {table_name}")
        return pd.DataFrame()
    
    # Leer y concatenar
    try:
        full_path_files = [os.path.join(path, f) for f in files]
        df = pd.concat([pd.read_parquet(f) for f in full_path_files], ignore_index=True)
        return df
    except Exception as e:
        print(f"❌ Error al leer {table_name}: {e}")
        return pd.DataFrame()

def load_all_data():
    """
    Carga las 4 tablas principales del proyecto de California.
    """
    print("Iniciando carga de datos maestros...")
    
    data = {
        "collisions": load_parquet_table("collisions"),
        "parties": load_parquet_table("parties"),
        "victims_raw": load_parquet_table("victims"),
        "victims_clean": load_parquet_table("involved_victims") # Tu tabla sin duplicados
    }
    
    # Resumen de carga
    for name, df in data.items():
        print(f"✅ Tabla {name.upper()}: {len(df)} registros cargados.")
        
    return data["collisions"], data["parties"], data["victims_raw"], data["victims_clean"]

# --- BLOQUE DE PRUEBA ---
if __name__ == "__main__":
    # Esto solo se ejecuta si corres el archivo utils.py directamente
    col, part, v_raw, v_clean = load_all_data()
    
    
    ### creacion de funciones de limpieza y preparacion de datos para analisis de datos y visualizaciones 
    
    

def clean_missing_data(df, columns_to_check):
    """
    1. Trata los valores nulos. 
    En seguros, a veces es mejor eliminar el nulo que inventarlo (imputar).
    """
    df_clean = df.copy()
    # Eliminamos filas donde columnas críticas sean nulas
    df_clean = df_clean.dropna(subset=columns_to_check)
    return df_clean

def fix_types_and_ranges(df, col_age=None, col_year=None):
    """
    2. Consistencia y limpieza de valores atípicos imposibles.
    Asegura que no haya conductores de 200 años o autos del futuro.
    """
    df_fix = df.copy()
    
    if col_age in df_fix.columns:
        # Convertir a numérico y marcar como NaN lo que no sea número
        df_fix[col_age] = pd.to_numeric(df_fix[col_age], errors='coerce')
        # Filtrar edades biológicamente posibles para un conductor/víctima
        df_fix = df_fix[(df_fix[col_age] >= 0) & (df_fix[col_age] <= 105)]
        
    if col_year in df_fix.columns:
        df_fix[col_year] = pd.to_numeric(df_fix[col_year], errors='coerce')
        # Solo autos desde 1920 hasta el año actual (2026)
        df_fix = df_fix[(df_fix[col_year] >= 1920) & (df_fix[col_year] <= 2026)]
        
    return df_fix

def standardize_categories(df, column, mapping=None):
    """
    3. Homogeniza categorías. 
    Evita que 'MALE', 'male' y 'M' se cuenten como cosas distintas.
    """
    df_std = df.copy()
    if column in df_std.columns:
        # Pasar a minúsculas y quitar espacios extra
        df_std[column] = df_std[column].get_str().lower().str.strip()
        if mapping:
            df_std[column] = df_std[column].replace(mapping)
    return df_std

def get_ready_for_plot(df, sort_by_col=None, ascending=False):
    """
    4. Preparación final: Ordenar y resetear índices.
    Un gráfico desordenado es difícil de leer.
    """
    df_plot = df.copy()
    if sort_by_col:
        df_plot = df_plot.sort_values(by=sort_by_col, ascending=ascending)
    return df_plot.reset_index(drop=True)
    
    
    
    
def remove_outliers_iqr(df, column):
    """
    Detecta y elimina valores atípicos usando el método IQR.
    Ideal para limpiar variables numéricas como Edad o Número de Víctimas.
    """
    df_clean = df.copy()
    
    # Calculamos los cuartiles 1 (25%) y 3 (75%)
    Q1 = df_clean[column].quantile(0.25)
    Q3 = df_clean[column].quantile(0.75)
    
    # El rango intercuartílico es la 'caja' donde está el 50% de los datos
    IQR = Q3 - Q1
    
    # Definimos los límites (vallas)
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Filtramos: nos quedamos solo con lo que está dentro de los límites
    df_filtered = df_clean[(df_clean[column] >= lower_bound) & (df_clean[column] <= upper_bound)]
    
    # Reporte de limpieza
    eliminados = len(df_clean) - len(df_filtered)
    print(f"--- Limpieza de Outliers en '{column}' ---")
    print(f"Límite inferior: {lower_bound:.2f} | Límite superior: {upper_bound:.2f}")
    print(f"Registros eliminados: {eliminados} ({ (eliminados/len(df_clean))*100 :.2f}%)")
    
    return df_filtered  