import plotly.express as px
import pandas as pd
from utils.Utils import preparar_datos_demograficos

# Paleta 
GOLD = "#D4AF37"
COFFEE = "#4B3621"
DARK_BG = "#121212"
TEXT_COLOR = "#FFFFFF"

def render_piramide_poblacional(df_victims):
    """
    Genera la pirámide poblacional con colores Dorado (Mujeres) y Marrón (Hombres).
    """
    df_demo = preparar_datos_demograficos(df_victims)
    
    # Limpieza: Solo géneros definidos
    df_demo = df_demo[df_demo['victim_sex'].isin(['male', 'female'])]
    
    # Orden de rangos de edad (natural, de menor a mayor)
    edad_order = [
        '0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39',
        '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85+'
    ]
    # Invertimos para que el menor aparezca abajo y el mayor arriba
    edad_order_reversed = edad_order[::-1]
    
    df_demo['rango_edad'] = pd.Categorical(df_demo['rango_edad'], categories=edad_order, ordered=True)
    
    df_plot = df_demo.groupby(['rango_edad', 'victim_sex'], observed=False).size().reset_index(name='Cantidad')
    
    # Invertir valores masculinos para el lado izquierdo
    df_plot.loc[df_plot['victim_sex'] == 'male', 'Cantidad'] *= -1

    # Calcular máximo absoluto para ticks simétricos
    max_cantidad = df_plot['Cantidad'].abs().max()
    if max_cantidad > 10000:
        step = 5000
    elif max_cantidad > 5000:
        step = 2000
    elif max_cantidad > 1000:
        step = 1000
    else:
        step = 500
    
    tick_vals = []
    tick_text = []
    valor = 0
    while valor <= max_cantidad + step:
        tick_vals.extend([-valor, valor])
        tick_text.extend([str(valor), str(valor)])
        valor += step
    tick_vals = sorted(list(set(tick_vals)))
    tick_text = [str(abs(v)) for v in tick_vals]

    fig = px.bar(
        df_plot, 
        x='Cantidad', 
        y='rango_edad', 
        color='victim_sex',
        orientation='h',
        color_discrete_map={'female': GOLD, 'male': COFFEE},
        labels={'rango_edad': 'Rango de Edad', 'victim_sex': 'Género'},
        category_orders={'rango_edad': edad_order_reversed}
    )

    fig.update_layout(
        title=dict(text='Distribución Poblacional de Víctimas', font=dict(color=GOLD, size=20)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COFFEE),
        xaxis=dict(
            title=dict(text='Cantidad de Víctimas', font=dict(color=GOLD)),
            gridcolor="#333333",
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_text,
            tickfont=dict(color=COFFEE)
            
        ),
        yaxis=dict(
            gridcolor="#333333", 
            tickfont=dict(color=COFFEE),
            title=None
        ),
        legend=dict(
            font=dict(color=TEXT_COLOR), 
            bgcolor=DARK_BG, 
            bordercolor=GOLD, 
            borderwidth=1
        ),
        bargap=0.1
    )
    
    return fig

def render_distribucion_sexo(df_victims):
    """
    Gráfico de dona con limpieza de etiquetas y colores Dorado/Marrón.
    """
    # Filtro de limpieza para la leyenda
    df_clean = df_victims[df_victims['victim_sex'].isin(['male', 'female'])].copy()
    df_clean['victim_sex'] = df_clean['victim_sex'].str.capitalize()

    conteo_sexo = df_clean['victim_sex'].value_counts().reset_index()
    conteo_sexo.columns = ['Género', 'Total']

    fig = px.pie(
        conteo_sexo, 
        values='Total', 
        names='Género', 
        hole=0.5,
        color='Género',
        color_discrete_map={'Female': GOLD, 'Male': COFFEE}
    )

    fig.update_traces(
        textfont_color=TEXT_COLOR, 
        marker=dict(line=dict(color=DARK_BG, width=2))
    )

    fig.update_layout(
        title=dict(text='Participación por Género', font=dict(color=GOLD, size=18)),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COFFEE),
        legend=dict(
            font=dict(color=TEXT_COLOR), 
            bgcolor=DARK_BG, 
            bordercolor=GOLD, 
            borderwidth=1
        )
    )
    
    return fig