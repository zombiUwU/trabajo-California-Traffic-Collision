import plotly.express as px
import pandas as pd

GOLD = "#D4AF37"
COFFEE = "#4B3621"
DARK_BG = "#121212"
TEXT_COLOR = "#FFFFFF"

def render_areas_severidad(df, anio_inicio=2018, anio_fin=2021):
    """Áreas apiladas: evolución anual de accidentes por severidad."""
    df = df.copy()
    df['collision_date'] = pd.to_datetime(df['collision_date'], errors='coerce')
    df['anio'] = df['collision_date'].dt.year
    df = df[(df['anio'] >= anio_inicio) & (df['anio'] <= anio_fin)]
    
    sev_map = {
        'fatal': 'Fatal',
        'pain': 'Lesión Grave',
        'other injury': 'Lesión Leve',
        'property damage only': 'Solo Daños'
    }
    df['severidad'] = df['collision_severity'].str.lower().map(sev_map).fillna('Otro')
    anual = df.groupby(['anio', 'severidad']).size().reset_index(name='conteo')
    
    fig = px.area(anual, x='anio', y='conteo', color='severidad',
                  color_discrete_map={
                      'Fatal': COFFEE,
                      'Lesión Grave': '#8B4513',
                      'Lesión Leve': '#CD853F',
                      'Solo Daños': GOLD,
                      'Otro': '#666666'
                  },
                  line_shape='linear')
    fig.update_layout(
        title=dict(text='Evolución de Accidentes por Severidad', font=dict(color=GOLD)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COFFEE),
        xaxis=dict(title='Año', dtick=1, gridcolor='#333', tickfont=dict(color=COFFEE)),
        yaxis=dict(title='Cantidad de Accidentes', gridcolor='#333', tickfont=dict(color=COFFEE)),
        legend=dict(font=dict(color=TEXT_COLOR), bgcolor=DARK_BG, bordercolor=GOLD)
    )
    return fig

def _calc_proporcion_factores(df):
    """Calcula los porcentajes de 5 factores de riesgo."""
    total = len(df)
    def pct(serie, pat):
        return serie.str.lower().str.contains(pat, na=False).sum() / total * 100 if total else 0
    
    return [
        pct(df['party_sobriety'], 'drinking'),          # Alcohol
        pct(df['party_sobriety'], 'drug'),              # Drogas
        (df['cellphone_in_use'] == '1').sum() / total * 100 if total else 0,  # Celular
        pct(df['weather_1'], 'rain|snow|fog'),          # Clima adverso
        pct(df['lighting'], 'dark|night')                # Oscuridad
    ]

def render_radar_factores(df_pre, df_pan):
    """Radar comparativo de factores de riesgo (pre‑pandemia vs pandemia)."""
    categorias = ['Alcohol', 'Drogas', 'Celular', 'Clima Adverso', 'Oscuridad']
    pre_vals = _calc_proporcion_factores(df_pre)
    pan_vals = _calc_proporcion_factores(df_pan)
    
    # Crear un DataFrame largo para px.line_polar
    data = []
    for i, cat in enumerate(categorias):
        data.append({'Factor': cat, 'Periodo': 'Pre-pandemia', 'Porcentaje': pre_vals[i]})
        data.append({'Factor': cat, 'Periodo': 'Pandemia', 'Porcentaje': pan_vals[i]})
    df_radar = pd.DataFrame(data)
    
    fig = px.line_polar(df_radar, r='Porcentaje', theta='Factor', color='Periodo',
                        line_close=True,
                        color_discrete_map={'Pre-pandemia': COFFEE, 'Pandemia': GOLD})
    fig.update_layout(
        title=dict(text='Factores de Riesgo: Pre‑pandemia vs Pandemia', font=dict(color=GOLD)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COFFEE),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color=COFFEE, gridcolor='#333'),
            angularaxis=dict(color=COFFEE, gridcolor='#333')
        ),
        legend=dict(font=dict(color=TEXT_COLOR), bgcolor=DARK_BG, bordercolor=GOLD)
    )
    return fig

def render_waterfall_anual(df, anio_inicio=2018, anio_fin=2021):
    """Cascada: cambio interanual en número de accidentes."""
    df = df.copy()
    df['collision_date'] = pd.to_datetime(df['collision_date'], errors='coerce')
    df['anio'] = df['collision_date'].dt.year
    df = df[(df['anio'] >= anio_inicio) & (df['anio'] <= anio_fin)]
    anual = df.groupby('anio').size().reset_index(name='total')
    
    years = sorted(anual['anio'].unique())
    tot = anual.set_index('anio')['total']
    
    y = [tot.iloc[0]] + [tot.iloc[i] - tot.iloc[i-1] for i in range(1, len(years))]
    text = [f"{v:+,}" for v in y]
    
    fig = px.bar(x=[str(y) for y in years], y=y, text=text,
                 color=[0 if i==0 else (1 if y[i]>0 else -1) for i in range(len(y))],
                 color_continuous_scale=[[0, COFFEE], [0.5, GOLD], [1, '#8B4513']])
    fig.update_traces(textposition='outside')
    fig.update_layout(
        title=dict(text='Cambio Interanual de Accidentes', font=dict(color=GOLD)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COFFEE),
        xaxis=dict(title='Año', gridcolor='#333', tickfont=dict(color=COFFEE)),
        yaxis=dict(title='Cambio en Cantidad', gridcolor='#333', tickfont=dict(color=COFFEE)),
        showlegend=False, coloraxis_showscale=False
    )
    return fig

def render_scatter_animado(df):
    """Mapa animado (scatter_mapbox): evolución geográfica anual de accidentes fatales."""
    df = df.copy()
    df['collision_date'] = pd.to_datetime(df['collision_date'], errors='coerce')
    df['anio'] = df['collision_date'].dt.year
    df = df.dropna(subset=['latitude', 'longitude', 'anio'])
    df = df[df['killed_victims'] > 0]
    
    sev_map = {'fatal': 'Fatal', 'pain': 'Grave', 'other injury': 'Leve', 'property damage only': 'Daños'}
    df['severidad'] = df['collision_severity'].str.lower().map(sev_map).fillna('Otro')
    df['size'] = df['killed_victims'].clip(upper=10) * 2
    
    fig = px.scatter_mapbox(
        df,
        lat='latitude', lon='longitude',
        color='severidad',
        size='size',
        animation_frame='anio',
        color_discrete_map={'Fatal': COFFEE, 'Grave': '#8B4513', 'Leve': '#CD853F', 'Daños': GOLD, 'Otro': '#666666'},
        size_max=10,
        zoom=5, center=dict(lat=36.7783, lon=-119.4179),
        mapbox_style='open-street-map',
        labels={'severidad': 'Severidad'}
    )
    fig.update_layout(
        title=dict(text='Evolución Geográfica de Accidentes Fatales', font=dict(color=GOLD)),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color=COFFEE),
        legend=dict(font=dict(color=TEXT_COLOR), bgcolor=DARK_BG, bordercolor=GOLD)
    )
    return fig