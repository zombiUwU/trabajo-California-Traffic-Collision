import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import streamlit as st
import os

@st.cache_resource
def iniciar_sesion_drive():
    gauth = GoogleAuth()
    
    # Variables de Entorno
    if "DRIVE_CREDS" in os.environ:
        with open("mycreds.txt", "w") as f:
            f.write(os.environ["DRIVE_CREDS"])
    
    # También necesitamos el client_secrets.json en Render
    if "CLIENT_SECRETS" in os.environ:
        with open("client_secrets.json", "w") as f:
            f.write(os.environ["CLIENT_SECRETS"])
    
    # intentar cargar el archivo de credenciales
    gauth.LoadCredentialsFile("mycreds.txt")
    
    if gauth.credentials is None:
        # si el archivo no existe o está vacío, logueo por primera vez
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # si se venció, lo refresca automaticamente
        try:
            gauth.Refresh()
        except Exception:
            # por si el refresh falla
            gauth.LocalWebserverAuth()
    else:
        # si estan vigentes funciona normal
        gauth.Authorize()
    
    # Guardar SIEMPRE al final para mantener el token actualizado
    gauth.SaveCredentialsFile("mycreds.txt")
    
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