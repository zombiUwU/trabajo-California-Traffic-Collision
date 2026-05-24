import streamlit as st
import duckdb
import pandas as pd

# Conexión cacheada a MotherDuck (se abre una sola vez)
@st.cache_resource
def get_md_connection():
    token = st.secrets["motherduck"]["token"]
    return duckdb.connect(f'md:accidentes_california?motherduck_token={token}')

# Función de consulta con caché (10 minutos)
@st.cache_data(ttl=600)
def run_query(query):
    conn = get_md_connection()
    try:
        return conn.execute(query).df()
    except Exception as e:
        st.error(f"Error en consulta: {e}")
        return pd.DataFrame()

# Adaptación de obtener_datos: misma firma, misma funcionalidad
@st.cache_data
def obtener_datos(nombre_tabla):
    """
    Obtiene los datos de la tabla especificada desde MotherDuck.
    Soporta los nombres de tabla que ya usas en tu app:
    'collisions', 'parties', 'victims', 'case_ids'
    """
    # Mapeo de nombres que usas en tu app a los nombres reales en MotherDuck
    mapeo_tablas = {
    "collisions": "collisions",
    "parties": "parties",
    "victims": "victims",
    "case_ids": "case_ids",
    # Si necesitas redirigir versiones lite a la tabla completa:
    "case_ids_lite": "case_ids",
    "collision_lite": "collisions",
    "parties_lite": "parties",
    "victims_lite": "victims",
    "involved_victims_part_0": "involved_victims"
    }
    tabla_real = mapeo_tablas.get(nombre_tabla, nombre_tabla)

    query = f"SELECT * FROM {tabla_real}"
    df = run_query(query)

    if df.empty:
        st.warning(f"La tabla '{nombre_tabla}' no se encontró o está vacía en MotherDuck.")

    return df