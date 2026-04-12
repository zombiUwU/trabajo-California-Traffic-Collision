import sys
import os
# Subimos un nivel para encontrar la carpeta 'utils'
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.join(current_dir, "..")
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import plotly.graph_objects as go
import plotly.express as px
from utils.Utils import preparar_datos_demograficos, obtener_distribucion_genero

def render_piramide_mortalidad(df_victims):
    """
    Genera una pirámide de población (mortalidad) segmentada por edad y sexo.
    """
    # Procesamos los datos usando tu función de Utils
    df_demo = preparar_datos_demograficos(df_victims)
    
    # Filtramos solo fallecidos (victim_degree_of_injury == 1)
    df_fatal = df_demo[df_demo['victim_degree_of_injury'] == 1]
    
    # Agrupamos por rango y sexo
    piramide = df_fatal.groupby(['rango_edad', 'victim_sex']).size().reset_index(name='conteo')
    
    # Separamos datos
    males = piramide[piramide['victim_sex'] == 'male']
    females = piramide[piramide['victim_sex'] == 'female']

    fig = go.Figure()

    # Lado Masculino (Valores negativos para el eje izquierdo)
    fig.add_trace(go.Bar(
        y=males['rango_edad'],
        x=males['conteo'] * -1,
        name='Hombres',
        orientation='h',
        marker_color='#1f77b4'
    ))

    # Lado Femenino
    fig.add_trace(go.Bar(
        y=females['rango_edad'],
        x=females['conteo'],
        name='Mujeres',
        orientation='h',
        marker_color='#e377c2'
    ))

    fig.update_layout(
        title='Pirámide de Mortalidad Vial por Edad y Sexo',
        barmode='relative',
        bargap=0.1,
        xaxis=dict(
            tickvals=[-100, -50, 0, 50, 100], # Ajustable según volumen de datos
            ticktext=['100', '50', '0', '50', '100'],
            title='Número de Víctimas Fatales'
        ),
        yaxis=dict(title='Rango Etario')
    )
    
    return fig

def render_distribucion_genero_donat(df_victims):
    """
    Genera un gráfico de dona con el % de participación por género.
    """
    df_gen = obtener_distribucion_genero(df_victims)
    
    if df_gen is None:
        return None

    fig = px.pie(
        df_gen, 
        values='porcentaje', 
        names='genero', 
        hole=0.5,
        title='Distribución Porcentual por Género',
        color_discrete_sequence=['#1f77b4', '#e377c2']
    )
    
    fig.update_traces(textinfo='percent+label')
    
    return fig