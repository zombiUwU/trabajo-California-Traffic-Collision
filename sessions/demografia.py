import streamlit as st
import pandas as pd
from utils.database import obtener_datos
from components.demographics_charts import render_piramide_poblacional, render_distribucion_sexo

def mostrar_demografia():
    # Encabezado principal
    st.markdown("""
    <div style="background-color: #121212; padding: 20px; border-radius: 10px; border-left: 5px solid #D4AF37; margin-bottom: 20px;">
        <h1 style="color: #D4AF37; margin: 0;">🚦 Análisis de Colisiones de Tránsito en California</h1>
        <p style="color: #FFFFFF; font-size: 18px; margin-top: 5px;">
            <span style="color: #D4AF37; font-weight: bold;">SWITRS 2018–2021</span> · 
            Dashboard interactivo de datos geograficos de el estado de California
        </p>
        <p style="color: #CCCCCC; margin-bottom: 0;">
            Fuente: <span style="color: #D4AF37;">California Highway Patrol</span> – 
            Statewide Integrated Traffic Records System
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Cargar datos
    with st.spinner("Cargando datos de víctimas..."):
        df_victims = obtener_datos("victims")
        df_collisions = obtener_datos("collisions")

    if df_victims.empty or df_collisions.empty:
        st.error("No se pudieron cargar los datos. Verifica la conexión o los archivos fuente.")
        return

    # Estilo CSS para el slider (color dorado)
    st.markdown("""
    <style>
        /* Punto del slider (thumb) */
        div[data-baseweb="slider"] div[role="slider"] {
            background-color: #D4AF37 !important;
            border-color: #D4AF37 !important;
        }
        /* Valor encima del thumb */
        div[data-baseweb="slider"] div[data-testid="stThumbValue"] {
            color: #D4AF37 !important;
        }
        /* Barra de progreso */
        div[data-baseweb="slider"] > div > div {
            background-color: #D4AF37 !important;
        }
        /* Track completo */
        div[data-baseweb="slider"] div[data-testid="stTrack"] {
            background-color: #D4AF37 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Filtro por fecha
    if 'collision_date' in df_collisions.columns:
        df_collisions['collision_date'] = pd.to_datetime(df_collisions['collision_date'], errors='coerce')
        min_date = df_collisions['collision_date'].min().date()
        max_date = df_collisions['collision_date'].max().date()

        fecha_inicio_default = pd.to_datetime('2018-01-01').date()
        fecha_fin_default    = pd.to_datetime('2021-12-31').date()

        if fecha_inicio_default < min_date:
            fecha_inicio_default = min_date
        if fecha_fin_default > max_date:
            fecha_fin_default = max_date

        st.markdown("### 🗓️ Filtrar por Fecha de Colisión")
        fecha_inicio, fecha_fin = st.slider(
            "Seleccione el rango:",
            min_value=min_date,
            max_value=max_date,
            value=(fecha_inicio_default, fecha_fin_default),
            format="YYYY-MM-DD"
        )

        mask_collisions = (df_collisions['collision_date'].dt.date >= fecha_inicio) & \
                          (df_collisions['collision_date'].dt.date <= fecha_fin)
        df_collisions_filtrado = df_collisions[mask_collisions]

        casos_validos = df_collisions_filtrado['case_id'].unique()
        df_victims_filtrado = df_victims[df_victims['case_id'].isin(casos_validos)]
    else:
        st.warning("No se encontró la columna 'collision_date'. Se muestran todos los datos sin filtro de fecha.")
        df_victims_filtrado = df_victims
        fecha_inicio, fecha_fin = None, None

    # Métricas resumen
    total_victimas = len(df_victims_filtrado)

    df_sex_clean = df_victims_filtrado[df_victims_filtrado['victim_sex'].isin(['male', 'female'])].copy()
    conteo_sexo = df_sex_clean['victim_sex'].value_counts()
    masculino = conteo_sexo.get('male', 0)
    femenino  = conteo_sexo.get('female', 0)
    total_sexo = masculino + femenino
    pct_masc = (masculino / total_sexo * 100) if total_sexo > 0 else 0

    edad_promedio = df_victims_filtrado['victim_age'].mean() if 'victim_age' in df_victims_filtrado.columns else 0.0

    col_met1, col_met2, col_met3 = st.columns(3)
    with col_met1:
        st.metric(label="Total de Víctimas", value=f"{total_victimas:,}")
    with col_met2:
        st.metric(label="Edad Promedio", value=f"{edad_promedio:.1f} años")
    with col_met3:
        st.metric(label="Hombres", value=f"{masculino:,} ({pct_masc:.1f}%)")

    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns([2, 1])

    with col1:
        st.plotly_chart(render_piramide_poblacional(df_victims_filtrado), use_container_width=True)

    with col2:
        st.plotly_chart(render_distribucion_sexo(df_victims_filtrado), use_container_width=True)

    if fecha_inicio and fecha_fin:
        st.caption(f"📊 Datos del {fecha_inicio} al {fecha_fin} | Víctimas filtradas: {total_victimas:,}")