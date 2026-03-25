import pandas as pd
import os
import numpy as np 

base_path = r"C:\Users\EQUIPO\trabajo-California-Traffic-Collision-main\data\delta_lake"

def cargar_y_unir_pedazos(nombre_carpeta):
    """
    Lee todos los archivos Parquet de una carpeta y los une.
    """
    ruta = os.path.join(base_path, nombre_carpeta)
    
    # 1. Verificación de ruta
    if not os.path.exists(ruta):
        print(f"ERROR: No encuentro la carpeta: {ruta}")
        return pd.DataFrame()
    
    # 2. Identificación de archivos
    archivos = [f for f in os.listdir(ruta) if f.endswith('.parquet')]
    if not archivos:
        print(f" Carpeta vacía o sin archivos parquet: {ruta}")
        return pd.DataFrame()
    
    # 3. Lectura y Unión
    print(f"Leyendo {len(archivos)} archivos de la carpeta '{nombre_carpeta}'...")
    lista_df = [pd.read_parquet(os.path.join(ruta, f)) for f in archivos]
    
    # Combinamos todo en un solo DataFrame
    return pd.concat(lista_df, ignore_index=True)

def limpieza_profunda_y_curaduria(df_p_crudo, df_v_crudo):
    """
    Aplica filtros y estandarizaciones para curar las irregularidades encontradas.
    """
    print("\n🧹 Iniciando la curaduría profunda de datos...")
    
    # SUB-SECCIÓN A: CURADURÍA DE VÍCTIMAS (Edad Atípica 999)
    
    #Elimino registros donde la edad es > 100 años o nula,

    df_v_limpio = df_v_crudo[
        (df_v_crudo['victim_age'] >= 0) & (df_v_crudo['victim_age'] <= 100)
    ].copy()
    
    # También eliminamos víctimas donde el sexo no está reportado (esencial para la pirámide)
    df_v_limpio = df_v_limpio.dropna(subset=['victim_sex']).copy()
    
    print(f"Curaduría de Víctimas: De {len(df_v_crudo)} registros crudos, nos quedamos con {len(df_v_limpio)} curados.")
    
    # SUB-SECCIÓN B: ESTANDARIZACIÓN DE CONDUCTAS (Sobriedad Caótica)
    
    # Simplifico 7 categorías de alcohol en solo 3 claras para el Streamlit
    def simplificar_sobriedad(texto):
        texto = str(texto).lower()
        if 'not been drinking' in texto: return 'Sobrio'
        if 'had been drinking' in texto: return 'Bajo Influencia'
        if texto == 'none' or texto == 'not applicable': return 'Desconocido/NA'
        return 'No reportado'
    
    # Creamos una columna nueva y eliminamos la vieja para ahorrar memoria
    df_p_limpio = df_p_crudo.copy()
    df_p_limpio['sobriedad_limpia'] = df_p_limpio['party_sobriety'].apply(simplificar_sobriedad)
    df_p_limpio = df_p_limpio.drop(columns=['party_sobriety'])
    
    print(f"Estandarización de Conductas: Categorías de sobriedad simplificadas de 7 a 4.")
    
    return df_p_limpio, df_v_limpio

print("INICIANDO PROCESO DE LIMPIEZA INDUSTRIAL")

#Cargamos y unimos todos los pedazos Parquet
parties_crudo = cargar_y_unir_pedazos("parties")
victims_crudo = cargar_y_unir_pedazos("victims")

#Ejecutamos la función de limpieza profunda si la carga fue exitosa
if not parties_crudo.empty and not victims_crudo.empty:
    parties_final, victims_final = limpieza_profunda_y_curaduria(parties_crudo, victims_crudo)
    
    #Reporte Final de Calidad
    print("\nREPORTE FINAL DE LA DATA CURADA")
    print(f"=================================")
    
    # Reporte Demográfico (Edades)
    edad_maxima = victims_final['victim_age'].max()
    print(f"Tabla Victims: Limpia de valores atípicos. Edad Máxima: {edad_maxima} años.")
    
    # Reporte de Conductas (Sobriedad)
    print("\nTabla Parties: Categorías de sobriedad estandarizadas.")
    print(parties_final['sobriedad_limpia'].value_counts())
    
    # Reporte de Nulos Finales (para verificar que no haya ruido)
    print("\nConteo de nulos restantes en columnas críticas:")
    print("En Victims:")
    print(victims_final[['case_id', 'victim_age', 'victim_sex']].isnull().sum())
    
    #PRÓXIMO PASO LÓGICO (JOIN)
    print("\nData lista para el COMMIT.")
    print("Lo siguiente es hacer el JOIN de estas dos tablas maestras limpias.")

else:
    print("El proceso falló. Revisa que las carpetas en 'data/delta_lake' contengan archivos .parquet.")
    
    #FASE DE UNIÓN (JOIN)
print("\n Iniciando unión de tablas para análisis final...")

# Uní Victims y Parties usando el 'case_id'

# Usé 'inner' para quedarnos solo con los casos que aparecen en ambas

df_analisis = pd.merge(victims_final, parties_final, on='case_id', how='inner')

print(f" UNIÓN EXITOSA: Tenemos {len(df_analisis)} filas listas para graficar.")

# INSIGHT REAL (CRUCE DE DATOS)
print("\nTENDENCIA DETECTADA: Sobriedad vs Severidad de Lesiones")

# Aquí cruzamos la sobriedad que limpiaste con la gravedad de la lesión
print(pd.crosstab(df_analisis['sobriedad_limpia'], df_analisis['victim_degree_of_injury']))