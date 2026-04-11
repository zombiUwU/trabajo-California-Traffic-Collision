import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import streamlit as st

@st.cache_resource
def iniciar_sesion_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() 
    return GoogleDrive(gauth)

@st.cache_data
def obtener_datos(nombre_tabla):
    IDS_TABLAS = {
        "victims": "1T4KefyFn2FghnMzLksbyVUXsnRfk_Fwu",
        "parties": "1Q2hJ2A6N9uW-h-14_HTasxigVJLZTouC",
        "case_ids": "1_C3_xRGa3G325_ztT6fw7uTB1sdRQhfD",
        "collisions": "1iDGYdPq2zk-Yi6Sks1K5YayOfN4aJ2d_"
    }
    
    if nombre_tabla not in IDS_TABLAS:
        st.error(f"La tabla '{nombre_tabla}' no está configurada.")
        return pd.DataFrame()

    drive = iniciar_sesion_drive()
    file_id = IDS_TABLAS[nombre_tabla]
    
    temp_file = f"{nombre_tabla}.parquet"
    
    archivo_drive = drive.CreateFile({'id': file_id})
    archivo_drive.GetContentFile(temp_file)
    
    return pd.read_parquet(temp_file)