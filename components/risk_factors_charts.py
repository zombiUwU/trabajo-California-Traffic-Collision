import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from PIL import Image

GOLD = "#D4AF37"
COFFEE = "#4B3621"
DARK_BG = "#121212"
TEXT_COLOR = "#FFFFFF"

def render_severidad_vs_equipo(df_victims):
    """Barras agrupadas: severidad vs equipo de seguridad (top 5)."""
    df = df_victims.copy()
    df['severidad'] = df['victim_degree_of_injury'].fillna('Desconocido')
    shorten_map = {
        'complaint of pain': 'Dolor',
        'other visible injury': 'Lesión visible',
        'severe injury': 'Grave',
        'killed': 'Fatal',
        'no injury': 'Sin lesión'
    }
    df['severidad'] = df['severidad'].replace(shorten_map)
    df['equipo'] = df['victim_safety_equipment_1'].fillna('Desconocido')
    
    top_severidades = df['severidad'].value_counts().nlargest(5).index.tolist()
    df = df[df['severidad'].isin(top_severidades)]
    
    grouped = df.groupby(['equipo', 'severidad']).size().reset_index(name='conteo')
    
    color_map = {
        'Fatal': COFFEE,
        'Grave': '#8B4513',
        'Lesión visible': '#CD853F',
        'Dolor': '#D2B48C',
        'Sin lesión': GOLD,
        'Desconocido': '#666666'
    }
    
    fig = px.bar(grouped, x='equipo', y='conteo', color='severidad',
                 barmode='group', color_discrete_map=color_map,
                 labels={'equipo': 'Equipo de Seguridad', 'conteo': 'Víctimas'})
    fig.update_layout(title=dict(text='Severidad según Equipo de Seguridad (Top 5)', font=dict(color=GOLD)),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color=COFFEE), xaxis_tickangle=-45,
                      legend=dict(font=dict(color=TEXT_COLOR), bgcolor=DARK_BG, bordercolor=GOLD))
    return fig

def render_tendencia_alcohol_anual(df_merged):
    """Líneas: evolución anual de accidentes con alcohol vs sobrios."""
    df = df_merged.copy()
    df['collision_date'] = pd.to_datetime(df['collision_date'], errors='coerce')
    df['anio'] = df['collision_date'].dt.year
    df = df.dropna(subset=['anio'])
    
    def clasificar_condicion(x):
        x = str(x).lower()
        if 'had been drinking' in x:
            return 'Con Alcohol'
        elif 'had not been drinking' in x:
            return 'Sobrio'
        else:
            return 'Otro/Desconocido'
    
    df['condicion'] = df['party_sobriety'].apply(clasificar_condicion)
    anual = df.groupby(['anio', 'condicion']).size().reset_index(name='conteo')
    
    fig = px.line(anual, x='anio', y='conteo', color='condicion',
                  color_discrete_map={'Con Alcohol': COFFEE, 'Sobrio': GOLD, 'Otro/Desconocido': '#666666'},
                  markers=True, line_shape='linear')
    fig.update_layout(title=dict(text='Evolución Anual de Accidentes según Condición', font=dict(color=GOLD)),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color=COFFEE),
                      xaxis=dict(title='Año', gridcolor='#333', tickfont=dict(color=COFFEE)),
                      yaxis=dict(title='Cantidad de Accidentes', gridcolor='#333', tickfont=dict(color=COFFEE)),
                      legend=dict(font=dict(color=TEXT_COLOR), bgcolor=DARK_BG, bordercolor=GOLD))
    return fig

def render_mapa_california_estatico(df):
    """Mapa con imagen estática de California y puntos de accidentes fatales."""
    df = df.copy()
    df = df[(df['latitude'].notna()) & (df['longitude'].notna())]
    df_fatal = df[df['killed_victims'] > 0].copy()

    
    df_fatal['killed_victims'] = pd.to_numeric(df_fatal['killed_victims'], errors='coerce').fillna(1).astype(int)
    df_fatal['collision_date'] = pd.to_datetime(df_fatal['collision_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df_fatal['case_id'] = df_fatal['case_id'].astype(str)

    # Coordenadas de California
    lat_min, lat_max = 32.5, 42.0
    lon_min, lon_max = -124.5, -114.0

    df_fatal = df_fatal[(df_fatal['latitude'] >= lat_min) & (df_fatal['latitude'] <= lat_max) &
                        (df_fatal['longitude'] >= lon_min) & (df_fatal['longitude'] <= lon_max)]

    img_path = os.path.join('assets', 'california.png')
    if not os.path.exists(img_path):
        fig = px.scatter_mapbox(df_fatal, lat='latitude', lon='longitude', color='collision_severity',
                                zoom=5, mapbox_style='open-street-map')
        fig.update_layout(title='⚠️ Imagen no encontrada, usando mapa alternativo')
        return fig

    img = Image.open(img_path)
    fig = go.Figure()
    fig.add_layout_image(
        dict(
            source=img,
            xref="x",
            yref="y",
            x=lon_min,
            y=lat_max,
            sizex=lon_max - lon_min,
            sizey=lat_max - lat_min,
            sizing="stretch",
            layer="below"
        )
    )

    sev_map = {'fatal': 'Fatal', 'pain': 'Grave', 'other injury': 'Leve', 'property damage only': 'Daños'}
    df_fatal['severidad'] = df_fatal['collision_severity'].str.lower().map(sev_map).fillna('Otro')

    for sev, color in [('Fatal', COFFEE), ('Grave', '#8B4513'), ('Leve', '#CD853F'), ('Daños', GOLD), ('Otro', '#666666')]:
        sub = df_fatal[df_fatal['severidad'] == sev]
        if not sub.empty:
            
            hover_text = sub['case_id'] + '<br>' + sub['collision_date']
            fig.add_trace(go.Scatter(
                x=sub['longitude'],
                y=sub['latitude'],
                mode='markers',
                name=sev,
                marker=dict(size=sub['killed_victims']*3+5, color=color, opacity=0.8, line=dict(width=1, color='white')),
                text=hover_text,
                hoverinfo='text'
            ))

    fig.update_xaxes(range=[lon_min, lon_max], showgrid=False, visible=False)
    fig.update_yaxes(range=[lat_min, lat_max], showgrid=False, visible=False, scaleanchor="x", scaleratio=1)
    fig.update_layout(
        title=dict(text='Accidentes Fatales en California', font=dict(color=GOLD)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COFFEE),
        legend=dict(font=dict(color=TEXT_COLOR), bgcolor=DARK_BG, bordercolor=GOLD),
        width=800, height=600, margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def render_boxplot_edad_por_tipo_colision(df):
    """Boxplot: distribución de edad de víctimas según tipo de colisión (top 5)."""
    df = df.copy()
    top_tipos = df['type_of_collision'].value_counts().nlargest(5).index
    df = df[df['type_of_collision'].isin(top_tipos)]
    df = df[df['victim_age'].notna()]

    fig = px.box(df, x='type_of_collision', y='victim_age', color='type_of_collision',
                 color_discrete_sequence=[COFFEE, GOLD, '#8B4513', '#CD853F', '#D2B48C'],
                 labels={'type_of_collision': 'Tipo de Colisión', 'victim_age': 'Edad de la Víctima'})
    fig.update_layout(title=dict(text='Distribución de Edad de Víctimas por Tipo de Colisión', font=dict(color=GOLD)),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color=COFFEE), xaxis_tickangle=-45,
                      legend=dict(font=dict(color=TEXT_COLOR), bgcolor=DARK_BG, bordercolor=GOLD),
                      showlegend=False)
    return fig