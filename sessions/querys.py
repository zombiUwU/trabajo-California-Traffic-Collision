
import streamlit as st
import duckdb
from utils.database import obtener_datos

def mostrar_querys():

    # 1. Cargamos las tablas necesarias desde Drive
    with st.spinner("Cargando tablas desde Drive para la consulta..."):
        collisions = obtener_datos("collisions")
        parties = obtener_datos("parties")
        case_ids = obtener_datos("case_ids")
        victims = obtener_datos("victims")   

    # Definición de las pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Pregunta 1", "Pregunta 2", "Pregunta 3", "Pregunta 4", "Pregunta 5"])

    with tab1:
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
            st.subheader("📝 Ejecutar Consulta (2 Desviaciones - Enunciado)")
        
            query_default = """
            WITH metricas_por_accidente AS (
    SELECT 
        c.case_id,
        c.location_type AS condado, 
        CASE WHEN (
            (LOWER(p.party_sobriety) LIKE '%had been drinking%') 
            AND (p.cellphone_in_use = '1') 
            AND (LOWER(c.lighting) LIKE '%dark%' OR LOWER(c.lighting) LIKE '%dusk%' OR LOWER(c.lighting) LIKE '%dawn%')
        ) THEN 1 ELSE 0 END AS cumple_factores
    FROM collisions c
    JOIN parties p ON c.case_id = p.case_id
),
estadisticas_condado AS (
    SELECT 
        condado,
        COUNT(*) AS total_accidentes,
        SUM(cumple_factores) AS accidentes_con_factores,
        (CAST(SUM(cumple_factores) AS FLOAT) / NULLIF(COUNT(*), 0)) AS proporcion_condado
    FROM metricas_por_accidente
    GROUP BY condado
),
promedio_estatal AS (
    SELECT 
        AVG(proporcion_condado) AS media_estatal,
        SQRT(AVG(proporcion_condado * proporcion_condado) - (AVG(proporcion_condado) * AVG(proporcion_condado))) AS desv_estatal
    FROM estadisticas_condado
)
SELECT 
    e.condado,
    e.total_accidentes,
    e.accidentes_con_factores,
    ROUND(e.proporcion_condado, 5) AS proporcion,
    ROUND(p.media_estatal, 5) AS promedio_estatal,
    ROUND((e.proporcion_condado - p.media_estatal) / NULLIF(p.desv_estatal, 0), 2) AS desviaciones_estandar
FROM estadisticas_condado e, promedio_estatal p
WHERE (e.proporcion_condado - p.media_estatal) > (2 * p.desv_estatal) -- Mantenemos el 2 del enunciado
ORDER BY desviaciones_estandar DESC;
            """

            # Area de texto para escribir el SQL
            sql_input_1 = st.text_area("Escribe tu primera consulta:", value=query_default, height=150, key="sql_1")

            if st.button("Ejecutar primera Query", key="btn_1"):
                try:
                    resultado = duckdb.query(sql_input_1).to_df()
                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")

            st.divider()
            st.subheader("🔍 Prueba de validación (1 Desviación)")
            st.info("Esta sección ejecuta la misma lógica pero con un umbral de 1 desviación estándar para visualizar datos existentes.")

            query_validacion = """
WITH metricas_por_accidente AS (
   -- usamos las variables party_sobriety, condado y lighting como filtro he indicador 
    SELECT 
        c.case_id,
        c.location_type AS condado, 
        CASE WHEN (
            (LOWER(p.party_sobriety) LIKE '%had been drinking%') 
            AND (p.cellphone_in_use = '1') 
            AND (LOWER(c.lighting) LIKE '%dark%' OR LOWER(c.lighting) LIKE '%dusk%' OR LOWER(c.lighting) LIKE '%dawn%')
        ) THEN 1 ELSE 0 END AS cumple_factores
    FROM collisions c
    JOIN parties p ON c.case_id = p.case_id
),
estadisticas_condado AS (
    -- Agrupamos por condado para obtener totales y proporciones
    SELECT 
        condado,
        COUNT(*) AS total_accidentes,
        SUM(cumple_factores) AS accidentes_con_factores,
        (CAST(SUM(cumple_factores) AS FLOAT) / NULLIF(COUNT(*), 0)) AS proporcion_condado
    FROM metricas_por_accidente
    GROUP BY condado
),
promedio_estatal AS (
    SELECT 
        AVG(proporcion_condado) AS media_estatal,
        -- Fórmula: SQRT( AVG(x^2) - AVG(x)^2 )
        SQRT(AVG(proporcion_condado * proporcion_condado) - (AVG(proporcion_condado) * AVG(proporcion_condado))) AS desv_estatal
    FROM estadisticas_condado
)
SELECT 
    e.condado,
    e.total_accidentes,
    e.accidentes_con_factores,
    ROUND(e.proporcion_condado, 5) AS proporcion,
    ROUND(p.media_estatal, 5) AS promedio_estatal,
    ROUND((e.proporcion_condado - p.media_estatal) / NULLIF(p.desv_estatal, 0), 2) AS desviaciones_estandar
FROM estadisticas_condado e, promedio_estatal p
WHERE (e.proporcion_condado - p.media_estatal) > (1 * p.desv_estatal) 
ORDER BY desviaciones_estandar DESC;
            """
            
            sql_input_1_val = st.text_area("Consulta de Validación (1 DE):", value=query_validacion, height=150, key="sql_1_val")

            if st.button("Ejecutar Validación (1 DE)", key="btn_1_val"):
                try:
                    resultado_val = duckdb.query(sql_input_1_val).to_df()
                    st.markdown("<h3 style='color: #D4AF37;'>Resultado de Validación:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado_val, use_container_width=True)
                except Exception as e:
                    st.error(f"Error en la consulta de validación: {e}")

    with tab2:
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
        
            query_default = """
            WITH Pre_Analisis AS (
        SELECT 
            -- Clasificación Horaria
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
            sql_input = st.text_area("Escribe tu segunda consulta:", value=query_default, height=150, key="sql_2")

            if st.button("Ejecutar segunda Query", key="btn_2"):
                try:
                    # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                    resultado = duckdb.query(sql_input).to_df()

                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)

                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")

    with tab3:
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
            sql_input = st.text_area("Escribe tu tercera consulta:", value=query_default, height=150, key="sql_3")

            if st.button("Ejecutar tercera Query", key="btn_3"):
                try:
                    # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                    resultado = duckdb.query(sql_input).to_df()

                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")

    with tab4:
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
            WITH
            accidentes AS (
                SELECT 
                    case_id,
                    location_type AS ruta,
                    strftime('%Y', CAST(collision_date AS DATE)) AS anio,
                    ROUND(latitude, 2) AS lat_celda,
                    ROUND(longitude, 2) AS lon_celda,
                    latitude,
                    longitude,
                    killed_victims,
                    primary_collision_factor
                FROM collisions
                WHERE LOWER(collision_severity) IN ('fatal', 'pain')
                  AND location_type IS NOT NULL
                  AND latitude IS NOT NULL
                  AND longitude IS NOT NULL
            ),
            celdas AS (
                SELECT
                    ruta,
                    anio,
                    lat_celda,
                    lon_celda,
                    COUNT(*) AS cantidad_accidentes,
                    SUM(killed_victims) AS total_fatalidades,
                    AVG(latitude) AS latitud_central,
                    AVG(longitude) AS longitud_central
                FROM accidentes
                GROUP BY ruta, anio, lat_celda, lon_celda
                HAVING COUNT(*) >= 3
            ),
            factor_moda AS (
                SELECT
                    a.ruta,
                    a.anio,
                    a.lat_celda,
                    a.lon_celda,
                    a.primary_collision_factor,
                    COUNT(*) AS freq,
                    ROW_NUMBER() OVER (
                        PARTITION BY a.ruta, a.anio, a.lat_celda, a.lon_celda 
                        ORDER BY COUNT(*) DESC
                    ) AS rn
                FROM accidentes a
                JOIN celdas c 
                    ON a.ruta = c.ruta 
                    AND a.anio = c.anio 
                    AND a.lat_celda = c.lat_celda 
                    AND a.lon_celda = c.lon_celda
                GROUP BY a.ruta, a.anio, a.lat_celda, a.lon_celda, a.primary_collision_factor
            )
            SELECT
                c.ruta AS ruta_estatal,
                c.anio,
                c.latitud_central,
                c.longitud_central,
                c.cantidad_accidentes,
                c.total_fatalidades,
                f.primary_collision_factor AS factor_colision_mas_frecuente
            FROM celdas c
            LEFT JOIN factor_moda f 
                ON c.ruta = f.ruta 
                AND c.anio = f.anio 
                AND c.lat_celda = f.lat_celda 
                AND c.lon_celda = f.lon_celda 
                AND f.rn = 1
            ORDER BY c.cantidad_accidentes DESC;"""

            # Area de texto para escribir el SQL
            sql_input = st.text_area("Escribe tu cuarta consulta:", value=query_default, height=150, key="sql_4")

            if st.button("Ejecutar cuarta Query", key="btn_4"):
                try:
                    # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                    resultado = duckdb.query(sql_input).to_df()

                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")

    with tab5:
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
            sql_input = st.text_area("Escribe tu quinta consulta:", value=query_default, height=150, key="sql_5")

            if st.button("Ejecutar quinta Query", key="btn_5"):
                try:
                    # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                    resultado = duckdb.query(sql_input).to_df()

                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")