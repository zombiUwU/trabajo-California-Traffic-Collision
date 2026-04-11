
import streamlit as st
import duckdb
from utils.database import obtener_datos

def mostrar_querys():
    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Análisis de Colisiones SWITRS")
    st.subheader("Pregunta 1: Conductores Reincidentes en Condiciones de Riesgo Compuesto")
    st.markdown("""**Enunciado:**
Identifica los condados donde la proporción de accidentes que involucran simultáneamente
presencia de alcohol, uso de teléfono celular y condiciones de iluminación deficiente supera
en más de dos desviaciones estándar al promedio estatal de esa misma proporción.

Para cada condado que cumpla la condición, muestra su nombre, el total de accidentes,
la cantidad que cumple los tres factores, la proporción calculada, el promedio estatal
y cuántas desviaciones estándar se aleja de él. Ordena por desviación descendente.""")
    st.markdown("---")

# 1. Cargamos las tablas necesarias desde Drive
    # Usamos st.spinner para que el usuario sepa que estamos bajando la data
    with st.spinner("Cargando tablas desde Drive para la consulta..."):
        collisions = obtener_datos("collisions")
        parties = obtener_datos("parties")
        case_ids = obtener_datos("case_ids")
        victims = obtener_datos("victims")

    if not collisions.empty:
        st.subheader("📝 Ejecutar Consulta Personalizada")
        
        # Ejemplo de una consulta que el profesor podría pedir:
        # "Contar accidentes por tipo de clima"
        query_default = """
        #consulta de ejemplo
        SELECT 
            weather_1, 
            COUNT(*) as total_accidentes 
        FROM collisions 
        GROUP BY weather_1 
        ORDER BY total_accidentes DESC 
        LIMIT 10
        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150)

        if st.button("Ejecutar Query"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()
                
                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)
                
                # Opcional: Descargar resultado en CSV
                csv = resultado.to_csv(index=False)
                st.download_button("Descargar CSV", csv, "resultado_query.csv", "text/csv")
                
            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")