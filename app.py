import streamlit as st
from utils.database import obtener_datos
from sessions import Introduccion, querys
import pandas as pd

# Configuración de página
st.set_page_config(page_title="SWITRS California",
                page_icon="🚗",
                layout="wide")

# INYECCIÓN DE CSS GLOBAL (Dorado y Gris)
st.markdown("""
    <style>
        /* Fondo Principal */
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        
        /* Barra Lateral (Sidebar) */
        [data-testid="stSidebar"] {
            background-color: #2D2D2D;
            border-right: 2px solid #D4AF37;
        }
        
        /* Títulos en la Sidebar */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
            color: #D4AF37;
            text-align: center;
        }

        /* Color Dorado para Radio Buttons Activos (Navegación) */
        div[data-testid="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
            color: #FFFFFF; /* Texto no seleccionado en blanco */
        }
        
        /* Estilo para la opción seleccionada */
        div[data-testid="stRadio"] div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            background-color: #D4AF37; /* Fondo del círculo dorado */
            border-color: #D4AF37;
        }
        
        /* Divisores Dorados */
        hr {
            border: 1px solid #D4AF37;
        }
        
        /* Estilo para Dataframes (Tablas) */
        .stDataFrame {
            border: 1px solid #D4AF37;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar - Menú de Navegación (Siempre abierto)
with st.sidebar:
    st.title("Navegación") 
    opcion = st.radio(
        "Seleccione una página:",
        ["Presentación", "Introducción","Querys"]
    )

# Lógica de "Páginas"
# Si la opción es Introducción, NO se ejecuta nada de la Presentación
if opcion == "Presentación":
    st.markdown("<h1 style='color: #D4AF37; text-align: center; font-size: 40px;'>🚗 SWITRS: Presentación Principal</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; color: #FFFFFF; font-size: 18px; margin-bottom: 20px;'>
                BIENVENIDOS!!, si todo funciona perfect deberian ver la tabla de abajo.
        </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Cargando base de datos..."):
        df = obtener_datos("collisions")
        if not df.empty:
            st.dataframe(df.head(50), use_container_width=True)

elif opcion == "Introducción":
    # Aquí solo se muestra lo que definimos en introduccion.py
    Introduccion.mostrar_introduccion()
    
elif opcion == "Querys":
    # mostrando la pestanha de querys.py
    querys.mostrar_querys()

