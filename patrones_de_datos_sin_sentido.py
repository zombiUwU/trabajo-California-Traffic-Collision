import pandas as pd
import os

# La carpeta 'data' está dentro de 'trabajo-California-Traffic-Collision-main'
base_path = r"C:\Users\EQUIPO\trabajo-California-Traffic-Collision-main\data\delta_lake"

def cargar_tabla_optimizada(nombre_carpeta):
    ruta = os.path.join(base_path, nombre_carpeta)
    
    if not os.path.exists(ruta):
        print(f" SIGUE SIN ESTAR: {ruta}")
        return pd.DataFrame()
    
    archivos = [f for f in os.listdir(ruta) if f.endswith('.parquet')]
    if not archivos:
        print(f" Carpeta vacía: {ruta}")
        return pd.DataFrame()
    
    # Leemos solo el primer pedazo para encontrar las irregularidades rápido
    return pd.read_parquet(os.path.join(ruta, archivos[0]))

print("INICIANDO EXPLORACIÓN DE TENDENCIAS (Ruta fija)...")

# 1. EXPLORAR PARTIES (CONDUCTAS)
df_parties = cargar_tabla_optimizada("parties")
if not df_parties.empty:
    print("\n TABLA PARTIES CARGADA CON ÉXITO")
    print("--- DISTRIBUCIÓN DE SOBRIEDAD (Irregularidades) ---")
    # Esto nos dirá si usan códigos como A, B, C o palabras
    if 'party_sobriety' in df_parties.columns:
        print(df_parties['party_sobriety'].value_counts(dropna=False))
    else:
        print("La columna 'party_sobriety' no se llama así. Columnas:", df_parties.columns.tolist())

# 2. EXPLORAR VICTIMS (DEMOGRAFÍA)
df_victims = cargar_tabla_optimizada("victims")
if not df_victims.empty:
    print("\nTABLA VICTIMS CARGADA CON ÉXITO")
    print("--- REVISIÓN DE EDADES ---")
    if 'victim_age' in df_victims.columns:
        print(df_victims['victim_age'].describe())
    else:
        print("La columna 'victim_age' no se llama así. Columnas:", df_victims.columns.tolist())