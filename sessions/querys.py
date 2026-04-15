
import streamlit as st
import duckdb
from utils.database import obtener_datos

def mostrar_querys():

# 1. Cargamos las tablas necesarias desde Drive
    # Usamos st.spinner para que el usuario sepa que estamos bajando la data
    with st.spinner("Cargando tablas desde Drive para la consulta..."):
        collisions = obtener_datos("collisions")
        parties = obtener_datos("parties")
        case_ids = obtener_datos("case_ids")
        victims = obtener_datos("victims")   

    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys: Pregunta 1</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Pregunta 1")
    st.subheader("Conductores Reincidentes en Condiciones de Riesgo Compuesto")
    st.markdown("""**Enunciado:**
Identifica los condados donde la proporción de accidentes que involucran simultáneamente
presencia de alcohol, uso de teléfono celular y condiciones de iluminación deficiente supera
en más de dos desviaciones estándar al promedio estatal de esa misma proporción.

Para cada condado que cumpla la condición, muestra su nombre, el total de accidentes,
la cantidad que cumple los tres factores, la proporción calculada, el promedio estatal
y cuántas desviaciones estándar se aleja de él. Ordena por desviación descendente.""")
    st.markdown("---")

    if not collisions.empty:
        st.subheader("📝 Ejecutar Consulta")
    
        query_default = """
        --query de ejemplo(cambienla)
        SELECT * FROM collisions
        LIMIT 5;
        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu primera consulta:", value=query_default, height=150)

        if st.button("Ejecutar primera Query"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()

                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)

                

            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")
    
    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys: Pregunta 2</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Pregunta 2")
    st.subheader(" Perfil de Victimas Fatales según Franja Horaria y Tipo de Vía")
    st.markdown("""**Enunciado:**
Identifica los condados donde la proporción de accidentes que involucran simultáneamente
presencia de alcohol, uso de teléfono celular y condiciones de iluminación deficiente supera
en más de dos desviaciones estándar al promedio estatal de esa misma proporción.

Para cada condado que cumpla la condición, muestra su nombre, el total de accidentes,
la cantidad que cumple los tres factores, la proporción calculada, el promedio estatal
y cuántas desviaciones estándar se aleja de él. Ordena por desviación descendente.""")
    st.markdown("---")

    if not collisions.empty:
        st.subheader("📝 Ejecutar Consulta Personalizada")
    
        # Ejemplo de una consulta que el profesor podría pedir:
        # "Contar accidentes por tipo de clima"
        query_default = """
        WITH Pre_Analisis AS (
    SELECT 
        -- Clasificación Horaria (Basada en HH:MM:SS)
        CASE 
            WHEN CAST(substr(c.collision_time, 1, 2) AS INT) BETWEEN 0 AND 5 THEN '00-06 (Madrugada)'
            WHEN CAST(substr(c.collision_time, 1, 2) AS INT) BETWEEN 6 AND 11 THEN '06-12 (Mañana)'
            WHEN CAST(substr(c.collision_time, 1, 2) AS INT) BETWEEN 12 AND 17 THEN '12-18 (Tarde)'
            ELSE '18-24 (Noche)'
        END AS Franja_Horaria,

        -- Rangos Etarios Exactos
        CASE 
            WHEN v.victim_age < 18 THEN 'a_Menor <18'
            WHEN v.victim_age BETWEEN 18 AND 30 THEN 'b_18-30'
            WHEN v.victim_age BETWEEN 31 AND 50 THEN 'c_31-50'
            WHEN v.victim_age BETWEEN 51 AND 65 THEN 'd_51-65'
            ELSE 'e_Mayor >65'
        END AS Rango_Etario,

        -- Tipo de Vía
        COALESCE(c.location_type, 'Vía Local/Calle') AS Tipo_Via,

        -- Cantidad de víctimas en esta combinación
        SUM(c.killed_victims) AS Cantidad_Fallecidos
    FROM collisions c
    INNER JOIN victims v ON c.case_id = v.case_id
    WHERE c.killed_victims > 0 
    GROUP BY 1, 2, 3
),
Calculo_Rankings AS (
    SELECT 
        Franja_Horaria,
        Rango_Etario,
        Tipo_Via,
        Cantidad_Fallecidos,
        -- TOTAL ACUMULADO: Se repite en la franja para poder calcular el %
        SUM(Cantidad_Fallecidos) OVER (PARTITION BY Franja_Horaria) AS Total_Franja,
        -- TOP 3: Ranking por cantidad de muertos en la franja
        DENSE_RANK() OVER (PARTITION BY Franja_Horaria ORDER BY Cantidad_Fallecidos DESC) AS Ranking
    FROM Pre_Analisis
)
SELECT 
    Franja_Horaria,
    substr(Rango_Etario, 3) as Rango_Etario, -- Quitamos el prefijo 'a_', 'b_'...
    Tipo_Via,
    Cantidad_Fallecidos,
    Total_Franja as Total_Fallecidos_Franja,
    ROUND((CAST(Cantidad_Fallecidos AS FLOAT) / Total_Franja) * 100, 2) || '%' AS Porcentaje_Impacto
FROM Calculo_Rankings
WHERE Ranking <= 3
ORDER BY Franja_Horaria ASC, Cantidad_Fallecidos DESC;
        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu segunda consulta:", value=query_default, height=150)

        if st.button("Ejecutar segunda Query"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()

                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)

            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")

    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys: Pregunta 3</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Pregunta 3")
    st.subheader("Evolución Mensual de la Severidad y Detección de Meses Atípicos")
    st.markdown("""**Enunciado:**
Para cada año disponible en la base de datos, calcula mes a mes el índice de severidad
promedio de los accidentes (definido como: víctimas fatales * 3 + víctimas con lesión grave * 2
+ otras víctimas lesionadas * 1, dividido entre el total de accidentes del mes).
Luego identifica, por año, qué meses presentaron un índice de severidad superior
en más de un 30% al promedio anual de ese mismo año.
Muestra el año, el mes, el índice del mes, el promedio anual y la variación porcentual.""")
    st.markdown("---")

    if not collisions.empty:
        st.subheader("📝 Ejecutar Consulta")
    
        query_default = """
        --query de ejemplo(cambienla)
        SELECT * FROM collisions
        LIMIT 5;
        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu tercera consulta:", value=query_default, height=150)

        if st.button("Ejecutar tercera Query"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()

                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")

    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys: Pregunta 4</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Pregunta 4")
    st.subheader("Rutas Estatales con Patrón de Reincidencia en el Mismo Tramo")
    st.markdown("""**Enunciado:**
Detecta las rutas estatales donde hayan ocurrido al menos 3 accidentes graves o fatales
en un radio de 0.5 millas (usando latitud y longitud) dentro de un mismo año calendario.
Para cada clúster detectado, muestra la ruta, el año, las coordenadas del punto central
del clúster, la cantidad de accidentes agrupados, el total de víctimas fatales y el factor
de colisión primario más frecuente en ese clúster. Ordena por cantidad de accidentes
por clúster de forma descendente.""")
    st.markdown("---")

    if not collisions.empty:
        st.subheader("📝 Ejecutar Consulta")
    
        query_default = """
        --query de ejemplo(cambienla)
        SELECT * FROM collisions
        LIMIT 5;
        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu cuarta consulta:", value=query_default, height=150)

        if st.button("Ejecutar cuarta Query"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()

                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")

    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys: Pregunta 5</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Pregunta 5")
    st.subheader("Comparativa de Comportamiento de Riesgo por Grupo Demográfico y Tendencia Temporal")
    st.markdown("""**Enunciado:**
Construye un reporte que, para cada combinación de género y rango etario de los conductores declarados responsables del accidente (at_fault), muestre:
1) La tasa de accidentes con alcohol involucrado sobre el total de accidentes donde ese
grupo fue responsable.
2) El ranking de esa tasa dentro de su mismo grupo de género.
3) La variación de esa tasa respecto al año inmediatamente anterior.
Incluye únicamente los grupos con más de 100 accidentes registrados como responsables
y que muestren una tendencia creciente en al menos 2 años consecutivos.""")
    st.markdown("---")

    if not collisions.empty:
        st.subheader("📝 Ejecutar Consulta")
    
        query_default = """
        --query de ejemplo(cambienla)
        SELECT * FROM collisions
        LIMIT 5;
        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu quinta consulta:", value=query_default, height=150)

        if st.button("Ejecutar quinta Query"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()

                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")