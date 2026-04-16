import streamlit as st
import duckdb
from utils.database import obtener_datos


def mostrar_querys_filtrado():

# 1. Cargamos las tablas necesarias desde Drive
    # Usamos st.spinner para que el usuario sepa que estamos bajando la data
    with st.spinner("Cargando tablas desde Drive para la consulta..."):
        collisions = obtener_datos("collision_lite")
        parties = obtener_datos("parties_lite")
        case_ids = obtener_datos("case_ids_lite")
        victims = obtener_datos("victims_lite")   

    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Primera selección de datos</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Primera selección de datos")
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
    
        query_default = """
        
        SELECT * FROM case_ids
        where db_year IN ('2020', '2021');

        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150)

        if st.button("Primer ejemplo de filtrado"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()

                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)

               
                csv = resultado.to_csv(index=False)
                st.download_button("Descargar CSV", csv, "resultado_query.csv", "text/csv")

            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")

    
    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Segunda selección de datos</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Segunda selección de datos")
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
    
        query_default = """
        
        SELECT 
         case_id, 
         collision_severity,
         primary_collision_factor,
         killed_victims,
         injured_victims,
         injured_victims,
         pcf_violation_category,
         weather_1,
         lighting,
         type_of_collision,
         longitude,
         latitude,
         party_count,
         collision_date,
         collision_time,
         road_surface,
         location_type
         FROM collisions
         WHERE collision_date BETWEEN '2018-01-01' AND '2021-12-31';
    
    

        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150)

        if st.button("Segundo ejemplo de filtrado"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()

                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)

               
                csv = resultado.to_csv(index=False)
                st.download_button("Descargar CSV", csv, "resultado_query.csv", "text/csv")

            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")



    st.markdown("<h1 style='color: #D4AF37;'>⛁ Querys de filtrado: Tercera selección de datos</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Tercera selección de datos")
    st.subheader("La elección de las variables de la tabla parties")
    st.markdown("""**Información sobre l:**
En esta selección de variables, tomamos en consideración la que tuviera la mayor relación
refente al analisis de tendencias de los choques en el Estado de California, como por ejemplo 
cellphone_in_use, party_safety_equipment_1, party_sobriety, etc. 
  """)
    st.markdown("---")

    if not parties.empty:
        st.subheader("📝 Ejecutar Consulta")
    
        query_default = """
        
        SELECT id,
        case_id,
        party_number,
        party_sobriety,
        party_type,
        party_drug_physical,
        movement_preceding_collision,
        at_fault,
        vehicle_make,
        vehicle_year,
        cellphone_in_use,
        statewide_vehicle_type,
        party_safety_equipment_1,
        party_safety_equipment_2
        FROM parties;
    
    

        """

        # Area de texto para escribir el SQL
        sql_input = st.text_area("Escribe tu consulta SQL aquí:", value=query_default, height=150)

        if st.button("Tercer ejemplo de filtrado"):
            try:
                # DuckDB puede leer directamente el DataFrame 'collisions' que cargamos arriba
                resultado = duckdb.query(sql_input).to_df()

                st.markdown("<h3 style='color: #D4AF37;'>Resultado:</h3>", unsafe_allow_html=True)
                st.dataframe(resultado, use_container_width=True)

               
                csv = resultado.to_csv(index=False)
                st.download_button("Descargar CSV", csv, "resultado_query.csv", "text/csv")

            except Exception as e:
                st.error(f"Error en la consulta SQL: {e}")















