import pandas as pd
import numpy as np 
import os
import sqlite3
import zipfile

# Importamos las rutas desde el Config que ya arreglamos
from Config import ZIP_PATH, DB_PATH, EXTRACT_PATH

def extraer_db_si_no_existe():
    """Detecta si el archivo .db ya está extraído; si no, lo saca del ZIP."""
    if not os.path.exists(DB_PATH):
        print(f"📦 Extrayendo Base de Datos desde {ZIP_PATH}...")
        try:
            with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_PATH)
            print("✅ Base de datos lista.")
        except Exception as e:
            print(f"❌ Error al extraer el ZIP: {e}")
    else:
        print("💡 La base de datos ya está disponible.")

def load_query_to_df(query):
    """Conecta a SQLite, ejecuta una consulta y devuelve un DataFrame."""
    extraer_db_si_no_existe()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"❌ Error al ejecutar SQL: {e}")
        return pd.DataFrame()

def load_all_data():
    """Carga las 4 tablas principales desde el archivo .db"""
    print("🚀 Iniciando carga desde SQLite...")
    
    # Aquí hacemos las consultas reales a las tablas de la DB
    collisions = load_query_to_df("SELECT * FROM collisions")
    parties = load_query_to_df("SELECT * FROM parties")
    victims_raw = load_query_to_df("SELECT * FROM victims")
    victims_clean = load_query_to_df("SELECT * FROM involved_victims")
    
    print(f"✅ Tabla COLLISIONS: {len(collisions)} registros.")
    print(f"✅ Tabla PARTIES: {len(parties)} registros.")
    
    return collisions, parties, victims_raw, victims_clean


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
    df_std = df.copy()
    if column in df_std.columns:
        df_std[column] = df_std[column].astype(str).str.lower().str.strip()
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

#------Seccion de analisis especificos------



def obtener_accidentes_graves(df_collisions):

    """

    Filtra solo las colisiones con heridos graves o fallecidos.

    Ideal para visualizaciones de alto impacto.

    """

    # 1 es Fatal, 2 es Lesión Grave (según el estándar de SWITRS)

    return df_collisions[df_collisions['collision_severity'].isin([1, 2])].copy()

def separar_por_sobriedad(df_parties):

    """

    Retorna un DataFrame con una columna booleana 'bajo_influencia'.

    """

    df = df_parties.copy()

    # Definimos los estados que implican consumo

    consumo = ['had been drinking, under influence', 'had been drinking, not under influence', 'had been using drugs']

   

    df['bajo_influencia'] = df['party_sobriety'].isin(consumo)

    return df

def analizar_gravedad_por_turno(df_collisions):

    """

    Agrupa las colisiones por turno y calcula el promedio de heridos y muertos.

    Requiere que la columna 'turno' haya sido pre-procesada.

    """

    # 1. Agrupamos por la columna 'turno'

    # Usamos las métricas de víctimas y el ID único del caso

    resumen = df_collisions.groupby('turno').agg({

        'injured_victims': 'mean',

        'killed_victims': 'mean',

        'case_id': 'count'

    })



    # 2. Renombramos para que sea claro en las tablas del Dashboard

    resumen = resumen.rename(columns={

        'injured_victims': 'promedio_heridos',

        'killed_victims': 'promedio_fallecidos',

        'case_id': 'total_accidentes'

    })

   

    # 3. Ordenamos por volumen de accidentes para ver el turno más frecuente arriba

    return resumen.sort_values(by='total_accidentes', ascending=False)



def preparar_geodatos(df_collisions):

    """

    Limpia coordenadas para mapeo.

    Elimina ceros y valores fuera del rango de California.

    """

    df = df_collisions.copy()

    # Filtro geográfico aproximado de California

    df = df[(df['latitude'] > 32) & (df['latitude'] < 42) &

            (df['longitude'] < -114) & (df['longitude'] > -125)]

    return df.dropna(subset=['latitude', 'longitude'])

def imputar_coordenadas_por_tendencia(df_collisions):
    """
    Identifica la tendencia geográfica (moda) por ciudad para llenar
    registros con latitud o longitud nula.
    """
    df = df_collisions.copy()

    # 1. Calculamos la moda de coordenadas por ciudad (la tendencia local)
    # Usamos transform para que el resultado tenga el mismo tamaño que el df original
    df['lat_moda'] = df.groupby('city')['latitude'].transform(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan)
    df['long_moda'] = df.groupby('city')['longitude'].transform(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan)

    # 2. Llenamos los nulos solo si existen valores de tendencia para esa ciudad
    df['latitude'] = df['latitude'].fillna(df['lat_moda'])
    df['longitude'] = df['longitude'].fillna(df['long_moda'])

    # 3. Limpiamos las columnas auxiliares
    return df.drop(columns=['lat_moda', 'long_moda'])

def obtener_tendencia_mensual(df_collisions):

    """

    Extrae el mes de la colisión y cuenta accidentes.

    Ayuda a identificar meses con mayor siniestralidad.

    """

    df = df_collisions.copy()

    df['collision_date'] = pd.to_datetime(df['collision_date'], errors='coerce')

    df['mes'] = df['collision_date'].dt.month

   

    # Mapeo para que el gráfico sea legible

    nombres_meses = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun',

                     7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}

   

    resumen = df.groupby('mes')['case_id'].count().reset_index()

    resumen['mes_nombre'] = resumen['mes'].map(nombres_meses)

    return resumen.sort_values('mes')

def obtener_calles_mas_peligrosas(df_collisions, top_n=10):

    """

    Identifica las calles con mayor volumen de accidentes fatales.

    """

    df_fatales = df_collisions[df_collisions['collision_severity'] == 1]

    calles = df_fatales.groupby('primary_rd')['case_id'].count().reset_index()

    calles.columns = ['calle', 'conteo_fatales']

    return calles.sort_values(by='conteo_fatales', ascending=False).head(top_n)

def analizar_impacto_clima(df_collisions):

    """

    Calcula el % de accidentes fatales bajo diferentes condiciones climáticas.

    """

    df = df_collisions.copy()

    # Agrupamos por clima y calculamos la media de fatalidad

    resumen = df.groupby('weather_1').agg({

        'collision_severity': lambda x: (x == 1).mean() * 100,

        'case_id': 'count'

    }).reset_index()

   

    resumen.columns = ['condicion_clima', 'porcentaje_fatalidad', 'total_accidentes']

    return resumen.sort_values(by='porcentaje_fatalidad', ascending=False)

#------------- Seccion KPI's------------

def obtener_total_fatalidades(df_collisions):

    """

    Suma el total de víctimas fatales en el dataset de colisiones.

    Usa la columna 'killed_victims' de la tabla collision.

    """

    # 1. Sumamos la columna y convertimos a int para evitar el formato float

    # Usamos fillna(0) por si hay nulos en la columna y evitar errores en la suma

    total = df_collisions['killed_victims'].fillna(0).sum()

   

    return int(total)


def obtener_genero_mayor_fatalidad(df_victims):

    """

    Identifica el género con mayor índice de fatalidad basado en victim_degree_of_injury == 1.

    """

    # 1. Filtramos solo las víctimas fallecidas (Código 1 en SWITRS)

    df_fatales = df_victims[df_victims['victim_degree_of_injury'] == 1]

   

    if not df_fatales.empty:

        # 2. Retorna el valor más frecuente (moda) de la columna victim_sex

        # .mode() devuelve una Serie, por lo que tomamos el índice [0]

        return df_fatales['victim_sex'].mode()[0]

   

    return "N/A"

def obtener_promedio_edad(df_victims):
    """
    Calcula la edad promedio de las víctimas.
    """
    # 1. Limpieza: eliminamos nulos para no sesgar el cálculo
    edades = df_victims['victim_age'].dropna()
    
    if edades.empty:
        return 0.0
    
    # 2. Retornamos el promedio redondeado a un decimal
    return round(float(edades.mean()), 1)

def obtener_moda_edad(df_victims):
    """
    Identifica la edad que más se repite entre las víctimas.
    """
    # 1. Limpieza de datos
    edades = df_victims['victim_age'].dropna()
    
    if not edades.empty:
        # 2. .mode() devuelve una Serie (por si hay empate), tomamos el primer valor
        return int(edades.mode()[0])
    
    return "N/A"

def obtener_distribucion_genero(df_victims):
    """
    Calcula el porcentaje de participación de cada género en el total de víctimas.
    """
    # 1. Limpiamos nulos y estandarizamos a minúsculas
    generos = df_victims['victim_sex'].dropna().astype(str).str.lower().str.strip()
    
    if generos.empty:
        return None

    # 2. Contamos frecuencias y convertimos a porcentaje
    # value_counts(normalize=True) devuelve la proporción (0.0 a 1.0)
    distribucion = generos.value_counts(normalize=True) * 100
    
    # 3. Formateamos como DataFrame para facilitar la lectura en el Dashboard
    df_resumen = distribucion.reset_index()
    df_resumen.columns = ['genero', 'porcentaje']
    
    # Redondeamos a un decimal para limpieza visual
    df_resumen['porcentaje'] = df_resumen['porcentaje'].round(1)
    
    return df_resumen

def obtener_edad_promedio_por_genero(df_victims):
    """
    Calcula la edad promedio separada por cada género.
    Ayuda a entender el perfil generacional de cada grupo.
    """
    # 1. Limpieza de datos esenciales
    df = df_victims.dropna(subset=['victim_age', 'victim_sex']).copy()
    
    # 2. Estandarización rápida de etiquetas
    df['victim_sex'] = df['victim_sex'].astype(str).str.lower().str.strip()
    
    # 3. Agrupamos y calculamos el promedio
    resumen = df.groupby('victim_sex')['victim_age'].mean().reset_index()
    resumen.columns = ['genero', 'edad_promedio']
    
    # 4. Redondeo para estética del Dashboard
    resumen['edad_promedio'] = resumen['edad_promedio'].round(1)
    
    return resumen

def obtener_accesorio_seguridad_mas_usado(df_victims):
    """
    Identifica el equipo de seguridad más frecuente en el dataset.
    Filtra valores nulos y categorías de 'no uso'.
    """
    # 1. Definimos qué valores NO cuentan como equipo (nulos o 'ninguno')
    no_equipo = ['null', 'unknown', 'not required', 'none in vehicle', 'none', 'nan', 'n', '0']
    
    # 2. Limpiamos y filtramos la columna victim_safety_equipment_1
    # Convertimos a string y minúsculas para una comparación robusta
    seguridad = df_victims['victim_safety_equipment_1'].astype(str).str.lower().str.strip()
    
    # Filtramos para quedarnos solo con los que SÍ usaron algo
    usaron_equipo = seguridad[~seguridad.isin(no_equipo)]
    
    if not usaron_equipo.empty:
        # 3. Retornamos la moda (el más frecuente) con formato limpio
        return usaron_equipo.mode()[0].capitalize()
    
    return "No registrado"


#--------------Sección de Demografia y funciones para futuros graficos-----------------



def preparar_datos_demograficos(df_victims):

    """

    Prepara el DataFrame de víctimas para análisis demográfico.

    Estandariza victim_sex y crea la columna rango_edad.

    """

    df = df_victims.copy()



    # 1. Limpieza básica: Eliminar filas sin edad o sin sexo definido

    # Usamos los nombres exactos de tu tabla victims

    df = df.dropna(subset=['victim_age', 'victim_sex'])

   

    # 2. Estandarizar Sexo: Mantenemos solo 'male' y 'female'

    # SWITRS a veces trae 'm', 'f' o 'X' (desconocido). Filtramos lo analizable.

    df['victim_sex'] = df['victim_sex'].astype(str).str.lower().str.strip()

   

    # Mapeo rápido para normalizar m/f a male/female si fuera necesario

    mapeo_sex = {'m': 'male', 'f': 'female', 'male': 'male', 'female': 'female'}

    df['victim_sex'] = df['victim_sex'].map(mapeo_sex)

   

    # Filtramos para quedarnos solo con categorías claras

    df = df[df['victim_sex'].isin(['male', 'female'])]



    # 3. Crear Rangos Etarios: Agrupamos victim_age en bloques de 5 años

    bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 115]

    labels = [

        '0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39',

        '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85+'

    ]

   

    # Creamos la columna rango_edad usando pd.cut

    df['rango_edad'] = pd.cut(df['victim_age'], bins=bins, labels=labels, right=False)

   

    return df

def clasificar_rol_victima(df_victims):

    """

    Clasifica y estandariza el rol de las víctimas en cuatro categorías:

    Conductor, Pasajero, Peatón, Ciclista.

    Basado en la columna 'victim_role'.

    """

    df = df_victims.copy()



    # 1. Diccionario de mapeo extendido

    # Incluimos códigos numéricos (estándar SWITRS) y strings

    mapeo_roles = {

        'driver': 'Conductor', '1': 'Conductor',

        'passenger': 'Pasajero', '2': 'Pasajero',

        'pedestrian': 'Peatón', '3': 'Peatón',

        'bicyclist': 'Ciclista', '4': 'Ciclista',

        'other': 'Otro/Desconocido', '5': 'Otro/Desconocido'

    }



    # 2. Limpieza de la columna original (usando victim_role de tu lista)

    df['victim_role_str'] = df['victim_role'].astype(str).str.lower().str.strip()



    # 3. Aplicar la clasificación

    # .map() buscará la coincidencia; si no existe, .fillna() lo agrupa en 'Otro'

    df['rol_simplificado'] = df['victim_role_str'].map(mapeo_roles).fillna('Otro/Desconocido')



    # 4. Eliminamos la columna temporal para devolver un DataFrame limpio

    return df.drop(columns=['victim_role_str'])

def clasificar_seguridad_victima(df_victims):

    """

    Clasifica el uso de equipo y calcula el porcentaje de sobrevivencia

    basado en victim_safety_equipment_1 y victim_degree_of_injury.

    """

    df = df_victims.copy()

   

    # 1. Definimos códigos de NO uso según el estándar de SWITRS

    no_equipo = ['null', 'unknown', 'not required', 'none in vehicle', 'none', 'nan', 'n']

   

    # 2. Clasificamos el uso de equipo (usando tu columna victim_safety_equipment_1)

    df['safety_status'] = df['victim_safety_equipment_1'].astype(str).str.lower().str.strip().apply(

        lambda x: 'Sin Equipo' if x in no_equipo else 'Con Equipo'

    )



    # 3. Definimos Sobrevivencia:

    # victim_degree_of_injury != 1 (Donde 1 es Fatal en SWITRS)

    df['sobrevivio'] = df['victim_degree_of_injury'] != 1



    # 4. Agrupamos para obtener el porcentaje de sobrevivencia por estado de seguridad

    resumen = df.groupby('safety_status')['sobrevivio'].mean() * 100

   

    # 5. Lo convertimos a DataFrame para que Streamlit lo lea fácil

    resumen_df = resumen.reset_index(name='porcentaje_sobrevivencia')

   

    return resumen_df


def preparar_accidentes_por_hora(df_collisions):

    """

    Extrae la hora de la colisión y cuenta la frecuencia de accidentes.

    Prepara los datos para gráficos de líneas o áreas.

    """

    df = df_collisions.copy()



    # 1. Convertimos la columna a datetime (usando tu columna 'collision_time')

    df['collision_time'] = pd.to_datetime(df['collision_time'], errors='coerce')

   

    # 2. Extraemos solo la hora (0-23)

    df['hora_dia'] = df['collision_time'].dt.hour

   

    # 3. Limpiamos valores nulos (usando el nombre de la nueva columna creada)

    df = df.dropna(subset=['hora_dia'])



    # 4. Agrupamos por hora para contar accidentes (usando tu 'case_id')

    conteo_horas = df.groupby('hora_dia')['case_id'].count().reset_index()

    conteo_horas.columns = ['hora', 'total_accidentes']



    # 5. Aseguramos que el orden sea cronológico (0 a 23)

    return conteo_horas.sort_values(by='hora')





#fin de seccion para graficos


#------- Seccion de Datos curiosos-------------



def obtener_causa_principal_muerte(df_collisions):

    """

    Busca la categoría de violación más frecuente en accidentes con víctimas fatales.

    """

    # Filtramos donde killed_victims > 0

    fatales = df_collisions[df_collisions['killed_victims'] > 0]

   

    if not fatales.empty:

        return fatales['pcf_violation_category'].mode()[0]

    return "Desconocida"

def obtener_vehiculo_mas_peligroso(df_merged):

    """

    Identifica el tipo de vehículo involucrado en más accidentes fatales.

    Usa collision_severity == 1 (Fatal) y statewide_vehicle_type.

    """

    # 1. Filtramos choques fatales (Severidad 1)

    df_fatales = df_merged[df_merged['collision_severity'] == 1].copy()

   

    if df_fatales.empty:

        return "Sin datos fatales registrados"



    # 2. Identificamos el tipo de vehículo más común (statewide_vehicle_type)

    # Limpiamos nulos y valores 'unknown'

    df_limpio = df_fatales.dropna(subset=['statewide_vehicle_type'])

    df_limpio = df_limpio[df_limpio['statewide_vehicle_type'].astype(str).str.lower() != 'unknown']



    if not df_limpio.empty:

        top_tipo = df_limpio['statewide_vehicle_type'].mode()[0]

       

        # 3. Dato Curioso Adicional: El año de fabricación más común en esos choques

        # Usamos la columna 'vehiclle_year' según tu esquema

        top_anio = int(df_limpio['vehiclle_year'].mode()[0]) if not df_limpio['vehiclle_year'].isnull().all() else "N/A"

       

        # Retornamos un string dinámico listo para la tarjeta

        return f"{top_tipo.capitalize()} (Modelos año {top_anio})"

   

    return "Tipo de vehículo no especificado"

# --- BLOQUE DE PRUEBA AL FINAL ---
if __name__ == "__main__":
    col, part, v_raw, v_clean = load_all_data()
    if not col.empty:
        print(f"✅ Prueba exitosa: {len(col)} colisiones cargadas.")