import streamlit as st
from utils.database import obtener_datos
<<<<<<< Updated upstream
from sessions import Introduccion, dict_DB, querys, ejemplo_filtrado, demografia, delta_lake, delimitacion
=======
from sessions import Introduccion, querys, ejemplo_filtrado, demografia, factores_riesgo
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        ["Presentación", "Introducción", "Delimitacion de datos","Diccionario de datos", "Delta Lake", "Perfil Demográfico", "Querys", "Querys de filtrado"]
=======
        ["Presentación", "Introducción", "Perfil Demográfico", "Querys", "Querys de filtrado", "Factores de Riesgo"]
>>>>>>> Stashed changes
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

elif opcion == "Diccionario de datos":
    # Llamada al nuevo archivo demografia.py
    dict_DB.mostrar_diccionario_datos()

elif opcion == "Perfil Demográfico":
    # Llamada al nuevo archivo demografia.py
    demografia.mostrar_demografia()

elif opcion ==  "Delta Lake":
    # llamamos el delta lake
    delta_lake.mostrar_delta_lake()

elif opcion ==  "Delimitacion de datos":
    # llamamos la delimitacion
    delimitacion.mostrar_delimitacion()

elif opcion == "Querys":
    # mostrando la pestanha de querys.py
    querys.mostrar_querys()

elif opcion == "Querys de filtrado":
    # mostrando la pestanha de querys_filtrado.py
    ejemplo_filtrado.mostrar_querys_filtrado()

elif opcion == "Factores de Riesgo":
    factores_riesgo.mostrar_factores_riesgo()