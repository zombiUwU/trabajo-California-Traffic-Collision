import streamlit as st
import duckdb
from utils.database import obtener_datos


def mostrar_querys_filtrado():

    # 1. Cargamos las tablas necesarias desde Drive
    with st.spinner("Cargando tablas desde Drive para la consulta..."):
        collisions = obtener_datos("collision_lite")
        parties = obtener_datos("parties_lite")
        case_ids = obtener_datos("case_ids_lite")
        victims = obtener_datos("victims_lite")   

    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Panel de Control</h1>", unsafe_allow_html=True)
    st.divider()

    # Creación de 6 pestañas: La de puntos a tener en cuenta + las 5 de consultas
    tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Puntos a tener en cuenta",
        "1. Case IDs", 
        "2. Collisions", 
        "3. Parties", 
        "4. Victims", 
        "5. Involved Victims",
        "6. Denormalizacion1"
    ])

    # --- PESTAÑA 0: PUNTOS A TENER EN CUENTA ---
    with tab0:
        st.header("Puntos a tener en cuenta")
        st.subheader("Definición del trabajo de filtrado")
        st.markdown("""
    Las metricas que se siguieron a la hora de crear la nueva base de datos para el
    estudio, la primera fue el uso de la herramienta que nos ofrece SQlite en su
    interfaz, que es attach database nos permite tener dos base de datos en simultaneo,
    los que nos permitio fue la falicidad y velocidad en el trabajo de la selección y filtro
    de datos.
                                
    Al codigo que se presenta a continuación le faltaria la parte del create table, que no se le
    coloca a estas consultas porque no buscamos obtener una nueva tabla cada vez que ejecutamos
    los scripts,tampoco nos indica la conexión que tienen las tablas en sus  FK's, y realmente este codigo
    va en una sola consulta grande, se separo con la finalidad de mejor comprención y facilitación del 
    analisis interno del trabajo. 
    """)

    # --- PESTAÑA 1: CASE IDS ---
    with tab1:
        st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Primera selección de datos</h1>", unsafe_allow_html=True)
        st.divider()

        st.header("filtado y selección de las variables de la tabla case_ids")
        st.subheader("Los dos años que tenian los datos mas recientes sobre las colisiones de California")
        st.markdown("""**Contexto sobre la base de datos:**
    La base de datos switrs es una composición de 5 bases sobre colisiones de California, 
    respectivamente categorizadas por su año de recoleccón de resultados, las cuales son 
    (2016, 2017, 2018, 2020 y 2021). Donde cada una contiene su linea del tiempo, 
    las de los años 2016, 2017 y 2018 tienen registros de collisiones desde el año 2001,
    y las de los años 2020 y 2021 tienen registros de colisiones desde el año 2009 hasta
    su respectivo año de recoleciones.
    """)
        st.markdown("---")

        if not case_ids.empty:
            st.subheader("📝 Ejecutar Consulta")
            query_default = "SELECT * FROM case_ids WHERE db_year IN ('2020', '2021');"
            sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150, key="sql_1")

            if st.button("Primer ejemplo de filtrado", key="btn_1"):
                try:
                    resultado = duckdb.query(sql_input).to_df()
                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    csv = resultado.to_csv(index=False)
                    st.download_button("Descargar CSV", csv, "resultado_1.csv", "text/csv", key="dl_1")
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")

    # --- PESTAÑA 2: COLLISIONS ---
    with tab2:
        st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Segunda selección de datos</h1>", unsafe_allow_html=True)
        st.divider()
        st.header("filtrado y selección de las variables de la tabla collisions")
        st.subheader("La linea del tiempo sobre las colisiones de interes para el analisis")
        st.markdown("""**Información sobre la linea del tiempo:**
    En el primer filtrado nos quedo una linea del tiempo de 13 años con un total de poco más de 5 millones 
    de colisiones ocurridas en California. Elegimos los ultimos 4 años registrado para una mayor homogeneidad
    en los datos sobre las colisiones ocurridas en California y tener un enfoque en el analisis en las
    influencias de choque antes de la pandemia del covid y durante la pandemia del covid. En esta consulta aparte 
    de la selección de la linea del tiempo tambien llevamos a cabo la selección de las variables de interes
    de la tabla collisions.
    """)
        st.markdown("---")

        if not collisions.empty:
            st.subheader("📝 Ejecutar Consulta")
            query_default = "SELECT case_id, " \
            "collision_severity, " \
            "primary_collision_factor, " \
            "killed_victims, " \
            "injured_victims, " \
            "pcf_violation_category, " \
            "weather_1, lighting, " \
            "type_of_collision, " \
            "longitude, " \
            "latitude, " \
            "party_count, " \
            "collision_date, " \
            "collision_time, " \
            "road_surface, " \
            "location_type " \
            "FROM collisions " \
            "WHERE collision_date BETWEEN '2018-01-01' AND '2021-12-31';"
            sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150, key="sql_2")

            if st.button("Segundo ejemplo de filtrado", key="btn_2"):
                try:
                    resultado = duckdb.query(sql_input).to_df()
                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    csv = resultado.to_csv(index=False)
                    st.download_button("Descargar CSV", csv, "resultado_2.csv", "text/csv", key="dl_2")
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")

    # --- PESTAÑA 3: PARTIES ---
    with tab3:
        st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Tercera selección de datos</h1>", unsafe_allow_html=True)
        st.divider()
        st.header("filtrado y selección de las variables de la tabla parties")
        st.subheader("La elección de las variables de la tabla parties")
        st.markdown("""**Información sobre la elección de las variables de la tabla parties:**
    En esta selección de variables, tomamos en consideración la que tuviera la mayor relación
    refente al analisis de tendencias de los choques en el Estado de California, como por ejemplo 
    cellphone_in_use, party_safety_equipment_1, party_sobriety, etc. 
    """)
        st.markdown("---")

        if not parties.empty:
            st.subheader("📝 Ejecutar Consulta")
            query_default = "SELECT id, " \
            "case_id, " \
            "party_number, " \
            "party_sobriety, " \
            "party_type, " \
            "party_drug_physical, " \
            "movement_preceding_collision, at_fault, " \
            "vehicle_make, " \
            "vehicle_year, " \
            "cellphone_in_use, " \
            "statewide_vehicle_type, " \
            "party_safety_equipment_1, " \
            "party_safety_equipment_2 " \
            "FROM parties;"
            sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150, key="sql_3")

            if st.button("Tercer ejemplo de filtrado", key="btn_3"):
                try:
                    resultado = duckdb.query(sql_input).to_df()
                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    csv = resultado.to_csv(index=False)
                    st.download_button("Descargar CSV", csv, "resultado_3.csv", "text/csv", key="dl_3")
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")

    # --- PESTAÑA 4: VICTIMS ---
    with tab4:
        st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Cuarta selección de datos</h1>", unsafe_allow_html=True)
        st.divider()
        st.header("filtrado y selección de la tabla victims")
        st.subheader("La elección de las variables de la tabla Victims")
        st.markdown("""**Información sobre la elección de las variables de la tabla victims:**
    En esta selección de variables, se seleccionaron casi todas por la buen descripción y 
    relevancia en sus datos, con una ciertas fallas en los registros de edad y sex definitivo de
    las victimas que fueron registrada mas de una vez, entre los datos seleccionados estan
    victim_role, victim_sex, victim_age, victim_degree_of_injury, etc. 
    """)
        st.markdown("---")

        if not victims.empty:
            st.subheader("📝 Ejecutar Consulta")
            query_default = "SELECT id, " \
            "case_id, " \
            "party_number, " \
            "victim_role, " \
            "victim_sex, " \
            "victim_age, " \
            "victim_degree_of_injury, " \
            "victim_seating_position, " \
            "victim_safety_equipment_1, " \
            "victim_safety_equipment_2, " \
            "victim_ejected " \
            "FROM victims;"
            sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150, key="sql_4")

            if st.button("Cuarto ejemplo de filtrado", key="btn_4"):
                try:
                    resultado = duckdb.query(sql_input).to_df()
                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    csv = resultado.to_csv(index=False)
                    st.download_button("Descargar CSV", csv, "resultado_4.csv", "text/csv", key="dl_4")
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")

    # --- PESTAÑA 5: INVOLVED VICTIMS ---
    with tab5:
        st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Quinta selección de datos</h1>", unsafe_allow_html=True)
        st.divider()
        st.header("filtrado y cración de la tabla involved_victims")
        st.subheader("La creación de la tabla involved_victims")
        st.markdown("""**Información sobre la creación de la tabla involved_victims:**
    En esta consulta, se presenta la solución a los datos que fueron de mala manera
    registrados de la tabla victims, se usa metricas como el uso de los datos que 
    más se repiten y las biometria maestra para tener los datos de mayor valor posible
    y reducir los datos que no servian para el analisis, obteniendo la verdadera edad y genero
    de las victimas de de esta base de datos. 
    """)
        st.markdown("---")

        if not victims.empty:
            st.subheader("📝 Ejecutar Consulta")
            query_default = """
    WITH biometria_maestra AS (
        SELECT v.id,
            (SELECT v2.victim_sex FROM victims v2 WHERE v2.id = v.id AND v2.victim_sex IS NOT NULL AND v2.victim_sex NOT IN ('', 'UNKNOWN', 'NOT_SPECIFIED') GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1) AS sexo_real,
            (SELECT (CAST(SUBSTR(c2.collision_date, 1, 4) AS INT) - v3.victim_age) FROM victims v3 JOIN collisions c2 ON v3.case_id = c2.case_id WHERE v3.id = v.id AND v3.victim_age > 0 AND v3.victim_age < 110 GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1) AS anio_nac_real
        FROM victims v WHERE v.id IS NOT NULL GROUP BY v.id
    )
    SELECT v.id, v.case_id, bm.sexo_real,
        CASE 
            WHEN bm.anio_nac_real IS NULL THEN NULL
            WHEN (CAST(SUBSTR(c.collision_date, 1, 4) AS INT) - bm.anio_nac_real) NOT BETWEEN 0 AND 110 THEN NULL
            ELSE (CAST(SUBSTR(c.collision_date, 1, 4) AS INT) - bm.anio_nac_real)
        END AS victim_age
    FROM victims v JOIN collisions c ON v.case_id = c.case_id LEFT JOIN biometria_maestra bm ON v.id = bm.id;
    """
            sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=200, key="sql_5")

            if st.button("Quinto ejemplo de filtrado", key="btn_5"):
                try:
                    resultado = duckdb.query(sql_input).to_df()
                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    csv = resultado.to_csv(index=False)
                    st.download_button("Descargar CSV", csv, "resultado_5.csv", "text/csv", key="dl_5")
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")



# --- PESTAÑA 6: DENORMALIZACION_1 ---
    with tab4:
        st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de denormalización: ¿Cúal es el perfil demografico de las victimas y la severidad de sus lesiones sufridas?</h1>", unsafe_allow_html=True)
        st.divider()
        st.markdown("""**Se seleccionaron los campos de victim_age, sexo_real, victim_degree_of_injury y victim_role, entre otros; para responder a criterios de análisis de riesgo y vulnerabilidad. Ademas, el codigo implementa una clasificación basada en rangos de edad mediante una estructura condicional**""")
        st.markdown("---")

        if not victims.empty:
            st.subheader("📝 Ejecutar Consulta")
            query_default = """ SELECT  
    iv.id_victim as id, 
    iv.case_id,
    iv.victim_age,
    CASE
        WHEN iv.victim_age BETWEEN 16 AND 17 THEN 'Young'
        WHEN iv.victim_age BETWEEN 18 AND 30 THEN 'Young_Adult'
        WHEN iv.victim_age BETWEEN 31 AND 65 THEN 'Adult'
        WHEN iv.victim_age BETWEEN 66 AND 120 THEN 'Older_Adult' 
        ELSE 'Unlicensed_Driver'
    END AS Age_classification,
    iv.sexo_real,
    v.victim_degree_of_injury,
    v.victim_role,
    c.collision_date
FROM involved_victims iv
JOIN victims v ON v.id_victim = iv.id_victim
JOIN collisions c ON c.case_id = iv.case_id;"""

            sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150, key="sql_4")

            if st.button("Cuarto ejemplo de filtrado", key="btn_4"):
                try:
                    resultado = duckdb.query(sql_input).to_df()
                    st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                    st.dataframe(resultado, use_container_width=True)
                    csv = resultado.to_csv(index=False)
                    st.download_button("Descargar CSV", csv, "resultado_4.csv", "text/csv", key="dl_4")
                except Exception as e:
                    st.error(f"Error en la consulta SQL: {e}")










