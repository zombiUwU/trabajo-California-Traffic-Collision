import pandas as pd
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json

@st.cache_resource
def iniciar_sesion_drive():
    # Cargamos las credenciales desde los Secrets para no exponer archivos en GitHub
    if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
        creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    else:
        st.error("No se encontraron las credenciales de la Cuenta de Servicio.")
        st.stop()

    settings = {
        "client_config_backend": "service",
        "service_config": {
            "client_json_dict": creds_dict
        }
    }
    
    gauth = GoogleAuth(settings=settings)
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

@st.cache_data
def obtener_datos(nombre_tabla):
    IDS_TABLAS = {
        "victims": "1T4KefyFn2FghnMzLksbyVUXsnRfk_Fwu",
        "parties": "1Q2hJ2A6N9uW-h-14_HTasxigVJLZTouC",
        "case_ids": "1_C3_xRGa3G325_ztT6fw7uTB1sdRQhfD",
        "collisions": "1iDGYdPq2zk-Yi6Sks1K5YayOfN4aJ2d_",
        
        ### las tablas lite son para el ejemplo de la selección y normalización  ###

        "case_ids_lite": "1L1y1xijvDHnod8XMrb1vU54KYPXbhmza",
        "collision_lite":"1wj3MI6odBf2zikvuRm2xAuxnXX2UV-Zx",
        "parties_lite":"1javvbygFD4Cha8arZd1hoFUuuTbx2r2n",
        "victims_lite":"1buJmDwvaHUdSf640Wen93BLqCD-vlz1g"
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