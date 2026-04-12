import streamlit as st
from utils.Utils import get_data_cached, get_cleaned_demographics, obtener_total_fatalidades, obtener_genero_mayor_fatalidad
from components.demographics_charts import render_piramide_mortalidad, render_distribucion_genero_donat

def mostrar_demografia():
    # Título con estilo dorado igual a Introducción
    st.markdown("<h1 style='color: #D4AF37;'>📊 Perfil Demográfico</h1>", unsafe_allow_html=True)
    st.divider()

    st.write("""
    En esta sección se analiza el perfil de las víctimas involucradas en incidentes viales. 
    El objetivo es identificar los grupos de edad y género con mayor vulnerabilidad para enfocar 
    estrategias de prevención efectivas.
    """)

    # 1. Carga de datos procesados (Sincronizado a 3 valores)
    with st.spinner("Procesando datos demográficos..."):
        df_collisions, _, df_demo = get_data_cached()

    if df_demo.empty:
        st.warning("No se encontraron datos para mostrar el análisis demográfico.")
        return

    # 2. Sección de KPIs Rápidos (Métricas clave)
    st.markdown("### Indicadores Clave")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        # Usamos df_collisions para obtener 'killed_victims'
        total_muertos = obtener_total_fatalidades(df_collisions)
        st.metric("Total Fallecidos (2018-2021)", f"{total_muertos}")
    
    with kpi2:
        # Usamos df_demo (victims) para el género
        genero_top = obtener_genero_mayor_fatalidad(df_demo)
        label_genero = "Masculino" if genero_top == "male" else "Femenino"
        st.metric("Género de Mayor Riesgo", label_genero)

    with kpi3:
        # Usamos df_demo (victims) para la edad
        edad_media = df_demo['victim_age'].mean()
        st.metric("Edad Promedio de Víctimas", f"{edad_media:.1f} años")

    st.markdown("---")

    # 3. Visualizaciones
    col1, col2 = st.columns([2, 1]) # La pirámide es más ancha que la dona

    with col1:
        st.markdown("<h4 style='color: #D4AF37; text-align: center;'>Pirámide de Mortalidad</h4>", unsafe_allow_html=True)
        fig_piramide = render_piramide_mortalidad(df_demo)
        st.plotly_chart(fig_piramide, use_container_width=True)

    with col2:
        st.markdown("<h4 style='color: #D4AF37; text-align: center;'>Distribución por Género</h4>", unsafe_allow_html=True)
        fig_dona = render_distribucion_genero_donat(df_demo)
        st.plotly_chart(fig_dona, use_container_width=True)

    # 4. Conclusión breve
    st.info("""
    **Nota:** La pirámide muestra una clara tendencia de mayor mortalidad en hombres jóvenes. 
    Este patrón es fundamental para el desarrollo de políticas de seguridad vial enfocadas.
    """)