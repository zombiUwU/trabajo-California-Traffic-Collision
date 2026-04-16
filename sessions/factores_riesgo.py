import streamlit as st
import pandas as pd
from utils.database import obtener_datos
from components.risk_factors_charts import (
    render_severidad_vs_equipo,
    render_tendencia_alcohol_anual,
    render_mapa_california_estatico,
    render_boxplot_edad_por_tipo_colision
)

def mostrar_factores_riesgo():
    st.markdown("""
    <div style="background-color: #121212; padding: 20px; border-radius: 10px; border-left: 5px solid #D4AF37; margin-bottom: 20px;">
        <h1 style="color: #D4AF37; margin: 0;">🚦 Factores de Riesgo en Colisiones</h1>
        <p style="color: #FFFFFF; font-size: 18px; margin-top: 5px;">
            <span style="color: #D4AF37; font-weight: bold;">Conductas, Equipamiento y Condiciones</span> · 
            Análisis del impacto en la severidad de los accidentes
        </p>
        <p style="color: #CCCCCC; margin-bottom: 0;">
            Fuente: <span style="color: #D4AF37;">California Highway Patrol</span> – SWITRS
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Cargando datos..."):
        collisions = obtener_datos("collisions")
        parties = obtener_datos("parties")
        victims = obtener_datos("victims")

    if collisions.empty or parties.empty or victims.empty:
        st.error("No se pudieron cargar los datos necesarios.")
        return

    df_merged = collisions.merge(parties, on='case_id', how='left', suffixes=('', '_party'))
    df_victims_merged = victims.merge(collisions[['case_id', 'collision_severity', 'type_of_collision']], on='case_id', how='left')

    total_acc = len(df_merged)
    total_vic = len(df_victims_merged)
    fatalidades = df_merged['killed_victims'].sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Accidentes", f"{total_acc:,}")
    col2.metric("Total Víctimas", f"{total_vic:,}")
    col3.metric("Total Fatalidades", f"{int(fatalidades):,}")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🛡️ Equipo de Seguridad", 
        "📈 Tendencia Alcohol", 
        "🗺️ Mapa de California", 
        "📊 Edad vs Tipo Colisión"
    ])

    with tab1:
        st.subheader("Filtros")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            severidades = victims['victim_degree_of_injury'].dropna().unique().tolist()
            selected_severidad = st.multiselect("Severidad", severidades, default=severidades[:5], key='sev')
        with col_f2:
            equipos = victims['victim_safety_equipment_1'].dropna().unique().tolist()
            selected_equipos = st.multiselect("Equipo de Seguridad", equipos, default=equipos[:5], key='eq')
        victims_f1 = victims.copy()
        if selected_severidad:
            victims_f1 = victims_f1[victims_f1['victim_degree_of_injury'].isin(selected_severidad)]
        if selected_equipos:
            victims_f1 = victims_f1[victims_f1['victim_safety_equipment_1'].isin(selected_equipos)]
        df_victims_f1 = victims_f1.merge(collisions[['case_id', 'collision_severity']], on='case_id', how='left')
        st.plotly_chart(render_severidad_vs_equipo(df_victims_f1), use_container_width=True)

    with tab2:
        st.subheader("Filtros")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            tipos_col = df_merged['type_of_collision'].dropna().unique().tolist()
            selected_tipos = st.multiselect("Tipo de Colisión", tipos_col, default=tipos_col[:5], key='tipo_alc')
        with col_a2:
            climas = df_merged['weather_1'].dropna().unique().tolist()
            selected_clima = st.multiselect("Clima", climas, default=climas[:3], key='clima_alc')
        df_merged_f2 = df_merged.copy()
        if selected_tipos:
            df_merged_f2 = df_merged_f2[df_merged_f2['type_of_collision'].isin(selected_tipos)]
        if selected_clima:
            df_merged_f2 = df_merged_f2[df_merged_f2['weather_1'].isin(selected_clima)]
        st.plotly_chart(render_tendencia_alcohol_anual(df_merged_f2), use_container_width=True)

    with tab3:
        st.subheader("Filtros")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            climas_map = df_merged['weather_1'].value_counts().nlargest(10).index.tolist()
            selected_clima_map = st.multiselect("Clima", climas_map, default=climas_map[:3], key='clima_map')
        with col_m2:
            luces_map = df_merged['lighting'].value_counts().nlargest(10).index.tolist()
            selected_luz_map = st.multiselect("Iluminación", luces_map, default=luces_map[:3], key='luz_map')
        df_merged_f3 = df_merged.copy()
        if selected_clima_map:
            df_merged_f3 = df_merged_f3[df_merged_f3['weather_1'].isin(selected_clima_map)]
        if selected_luz_map:
            df_merged_f3 = df_merged_f3[df_merged_f3['lighting'].isin(selected_luz_map)]
        st.plotly_chart(render_mapa_california_estatico(df_merged_f3), use_container_width=True)

    with tab4:
        st.subheader("Filtros")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            tipos_box = df_victims_merged['type_of_collision'].value_counts().nlargest(10).index.tolist()
            selected_tipos_box = st.multiselect("Tipo de Colisión", tipos_box, default=tipos_box[:5], key='tipos_box')
        with col_b2:
            sex_map = {'male': 'Masculino', 'female': 'Femenino'}
            sexos_validos = [s for s in df_victims_merged['victim_sex'].dropna().unique() if s in sex_map]
            sexos_opciones = [sex_map[s] for s in sexos_validos]
            selected_display = st.multiselect("Sexo", sexos_opciones, default=sexos_opciones, key='sexo_box')
            inv_map = {v: k for k, v in sex_map.items()}
            selected_sexo = [inv_map[d] for d in selected_display]
        df_victims_f4 = df_victims_merged.copy()
        df_victims_f4['victim_age'] = pd.to_numeric(df_victims_f4['victim_age'], errors='coerce')
        df_victims_f4 = df_victims_f4.dropna(subset=['victim_age', 'type_of_collision'])
        if selected_tipos_box:
            df_victims_f4 = df_victims_f4[df_victims_f4['type_of_collision'].isin(selected_tipos_box)]
        if selected_sexo:
            df_victims_f4 = df_victims_f4[df_victims_f4['victim_sex'].isin(selected_sexo)]
        if not df_victims_f4.empty:
            st.plotly_chart(render_boxplot_edad_por_tipo_colision(df_victims_f4), use_container_width=True)
        else:
            st.warning("Sin datos con los filtros actuales.")