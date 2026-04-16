import streamlit as st

def mostrar_diccionario_datos():
    st.markdown("<h1 style='color: #D4AF37;'>Diccionario de datos</h1>",unsafe_allow_html=True)
    st.divider()
    
    st.header("Resumen")
    st.markdown("""El proyecto se sustenta en tres tablas principales **(Collisions, Parties y Victims)** conectadas a través del identificador
                único de la tabla **case_id**.""")
    
    st.markdown("---")
    
    # Definición de las pestañas
    tab1, tab2, tab3 = st.tabs(["Tabla Collisions", "Tabla Parties", "Tabla Victim"])
    
    with tab1:
        st.markdown("""**1. Tabla:** *Collisions* (El Evento) Contiene la información contextual de 
                dónde, cuándo y por qué ocurrió el accidente.""")
                
        st.markdown("""Variable | Descripción | Uso en el Proyecto
 :--- | :--- | :---
 **collision_severity** | Nivel de gravedad del accidente. | Variable objetivo para medir impacto.
 **primary_collision_factor** | La causa principal del siniestro. | Identificar causas raíz de accidentes.
 **killed_victims** | Número de personas fallecidas en el evento. | KPI de mortalidad y análisis crítico.
 **weather_1** | Condiciones climáticas al momento del choque. | Análisis de factores del entorno.
 **lighting** | Nivel de iluminación (Día, Noche, Alumbrado). | Análisis de factores del entorno.
 **latitude / longitude** | Coordenadas geográficas del siniestro. | Mapeo de Hotspots en Power BI / Python.""")
    
    
    with tab2:
        st.markdown("""**2. Tabla:** *Parties* (Los Involucrados)
                Información sobre los conductores, vehículos y sus conductas.""")
    
        st.markdown("""Variable | Descripción | Uso en el Proyecto
 :--- | :--- | :---
 **party_sobriety** | Estado de sobriedad del conductor (Alcohol/Drogas). | Análisis de conductas de riesgo.
 **cellphone_in_use** | Indica si se estaba usando el celular en el momento. | Análisis de conductas de riesgo y distracción.
 **at_fault** | Indica quién fue el responsable legal del choque. | Cruzar culpabilidad con el tipo de vehículo.
 **vehicle_make / year** | Marca y modelo del vehículo involucrado. | Análisis del parque automotor y antigüedad.
 **party_safety_equipment** | Equipo de seguridad utilizado (Cinturón, Casco, etc.). | Evaluación de medidas preventivas y protección.""")
    
    
    with tab3:
        st.markdown("""3. **Tabla:** *Victims* (Las Víctimas) Detalle demográfico y físico de las personas afectadas.""")
    
        st.markdown("""Variable | Descripción | Uso en el Proyecto
 :--- | :--- | :---
 **victim_age** | Edad de la víctima involucrada en el siniestro. | Eje vertical (Y) de la Pirámide de Mortalidad.
 **victim_sex** | Sexo de la víctima (Masculino / Femenino). | Segmentación lateral de la Pirámide.
 **victim_degree_of_injury** | Grado de la lesión sufrida (Fatal, Grave, Leve). | Medición de la eficacia de sistemas de seguridad.
 **victim_ejected** | Indica si la víctima fue expulsada del vehículo. | Análisis de relación con el uso de cinturón/casco.""")
        

    st.markdown("""## Fuente de datos

Kaggle Dataset:
[BD-SWITRS](https://www.kaggle.com/datasets/alexgude/california-traffic-collision-data-from-switrs)""")