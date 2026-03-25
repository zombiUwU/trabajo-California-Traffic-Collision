# trabajo-California-Traffic-Collision.

Este proyecto realiza un análisis exploratorio de los accidentes de tráfico en California utilizando datos públicos del sistema SWITRS (Statewide Integrated Traffic Records System).

A pesar de las mejoras en tecnología vehicular, California sigue registrando altos índices de fatalidad vial. Existe una falta de herramientas interactivas que permitan a las autoridades y ciudadanos entender no sólo donde ocurren los accidentes, sino quienes son las víctimas más vulnerables y cómo influyen factores específicos (distracción por celular o falta de equipo de seguridad) en la supervivencia de un siniestro entre 2018 y 2021.

----------------------------------------------------------------
## Objetivo General:
Desarrollar un análisis de datos sobre la siniestralidad vial en California (2018-2021), centrado en la identificación de perfiles de vulnerabilidad y factores de riesgo.

----------------------------------------------------------------
## Objetivos especificos:

- Analizar el perfil demográfico de las víctimas: Construir una pirámide de mortalidad segmentada por edad (victim_age) y sexo (victim_sex) para identificar qué grupos poblacionales sufren mayor impacto en colisiones fatales.

- Determinar factores externos determinantes de una colisión: Determinar el impacto de las conductas de riesgo (cellphone_in_use, party_sobriety) y la eficacia del equipo de seguridad (victim_safety_equipment) en la severidad de las lesiones y la ocurrencia de víctimas fatales.

- Visualizar la criticidad geográfica y temporal: Mapear los incidentes y su evolución anual para detectar si las políticas de seguridad vial han surtido efecto post-pandemia.

----------------------------------------------------------------

## Diccionario de Datos (Resumen)

El proyecto se sustenta en tres tablas principales conectadas a través del identificador único de colisión (case_id).

1. Tabla: Collisions (El Evento)
Contiene la información contextual de dónde, cuándo y por qué ocurrió el accidente.

Variable | Descripción | Uso en el Proyecto |
| :--- | :--- | :--- |
| **collision_severity** | Nivel de gravedad del accidente. | Variable objetivo para medir impacto. |
| **primary_collision_factor** | La causa principal del siniestro. | Identificar causas raíz de accidentes. |
| **killed_victims** | Número de personas fallecidas en el evento. | KPI de mortalidad y análisis crítico. |
| **weather_1** | Condiciones climáticas al momento del choque. | Análisis de factores del entorno. |
| **lighting** | Nivel de iluminación (Día, Noche, Alumbrado). | Análisis de factores del entorno. |
| **latitude / longitude** | Coordenadas geográficas del siniestro. | Mapeo de Hotspots en Power BI / Python. |


2. Tabla: Parties (Los Involucrados)
Información sobre los conductores, vehículos y sus conductas.

| Variable | Descripción | Uso en el Proyecto |
| :--- | :--- | :--- |
| **party_sobriety** | Estado de sobriedad del conductor (Alcohol/Drogas). | Análisis de conductas de riesgo. |
| **cellphone_in_use** | Indica si se estaba usando el celular en el momento. | Análisis de conductas de riesgo y distracción. |
| **at_fault** | Indica quién fue el responsable legal del choque. | Cruzar culpabilidad con el tipo de vehículo. |
| **vehicle_make / year** | Marca y modelo del vehículo involucrado. | Análisis del parque automotor y antigüedad. |
| **party_safety_equipment** | Equipo de seguridad utilizado (Cinturón, Casco, etc.). | Evaluación de medidas preventivas y protección. | |


3. Tabla: Victims (Las Víctimas)
Detalle demográfico y físico de las personas afectadas.

| Variable | Descripción | Uso en el Proyecto |
| :--- | :--- | :--- |
| **victim_age** | Edad de la víctima involucrada en el siniestro. | Eje vertical (Y) de la Pirámide de Mortalidad. |
| **victim_sex** | Sexo de la víctima (Masculino / Femenino). | Segmentación lateral de la Pirámide. |
| **victim_degree_of_injury** | Grado de la lesión sufrida (Fatal, Grave, Leve). | Medición de la eficacia de sistemas de seguridad. |
| **victim_ejected** | Indica si la víctima fue expulsada del vehículo. | Análisis de relación con el uso de cinturón/casco. |

----------------------------------------------------------------

## Tecnologías utilizadas
El proyecto utiliza varias herramientas para el análisis y visualización de datos:

SQLite -> Manipulación y consultas de datos

Python -> Limpieza, análisis y procesamiento de datos

Streamlit -> Desarrollo de la aplicación interactiva

Power BI -> Creación del dashboard de visualización

----------------------------------------------------------------

## Ejecución del Proyecto

Sigue estos pasos para replicar el análisis y visualizar los dashboards en tu entorno local.

### 1. Requisitos Previos
Asegúrate de tener instalado:
-Python 3.8+
-Power BI Desktop (para abrir el archivo .pbix)
-Java 8.0 
-hadoop
-SQLite

NOTA:  Descarga el archivo de instalación del Hadoop 3.3.5 y el archivo binario auxiliar para que hadoop pueda ejecutarse en sistemas operativos Windows (winutils.exe) en el siguiente repositorio público:
.https://github.com/cdarlint/winutils/tree/master/hadoop-3.3.5/bin


### 2. Delta Lake
Luego de haber instalado los archivos previos, se crea en el disco duro una carpeta para alojar los archivos previamente instalados. El siguiente paso es entrar al editor de variables del sistema operativo de windows para crear un entorno donde esté asignada la herramienta y su respectiva ruta para proceder a la instalación del PySpark dentro de la terminal de Python.

### 3. Instalación de Dependencias
Clona este repositorio y ejecuta el siguiente comando en tu terminal para instalar las librerías necesarias para Streamlit:
pip install -r requirements.txt

Nota: El archivo requirements.txt incluye: pandas, streamlit, plotly sqlite3,os,sys,plotly.express,plotly.graph_objets,numpy,utils y matplotlib.  

### 4. Visualización de la App (Streamlit)
Para lanzar la aplicación interactiva, usa:
streamlit run app.py

### 5. Dashboard de Inteligencia de Negocios (Power BI)
Dirígete a la carpeta dashboard/.
Abre el archivo Analisis_SWITRS_California.pbix.
(Opcional) Si los datos no cargan, actualiza la ruta de la fuente de datos apuntando al archivo SQLite o CSV en la carpeta data/.

----------------------------------------------------------------
## Lógica detrás de la delimitación de la data

La base de datos switrs.sqlite contiene una recolección amplia de accidentes en el estado de California, con registros que datan de 2009 a 2021. Para delimitar la magnitud del análisis, primero se trabajó con la variable db_year, que indica el año en que se extrajeron los registros de California Highway Patrol (CHP) para esta data SWITRS (“California Traffic Collision Data”). De este campo se depuraron los años con menor volumen de información (específicamente 2016, 2017) y los datos de 2018, conservando la información recogida en 2020 y 2021, las cuales cubren colisiones ocurridas entre 2009 y 2021.
Posteriormente, se seleccionaron únicamente los incidentes de los últimos cuatro años con la variable de (collision_date). La elección de los campos se basó en su relación directa con los objetivos del estudio, incluyendo variables como victim_sex, cellphone_in_use, collision_severity, entre otros...

----------------------------------------------------------------

## Estructura del Repositorio
Para mantener el orden que definimos, tu carpeta de GitHub debería verse así:
Plaintext
├── components/    #Elementos visuales aislados (gráficos, tablas, filtros) 
├── sections/         #Estructuras que organizan los componentes
├── .gitignore/
├── .gitattributes/
├── data/               # Archivos parquets con la data (2018-2021)
├── app.py              # Código principal de la App de Streamlit
├── pruebas.ipynb  #Código de testeo de las funciones y gráficas
├── utils/              # Scripts de limpieza y procesamiento
├── dashboardd/          # Archivo .pbix de Power BI
├── requirements.txt    # Listado de librerías de Python
└── README.md           # Este archivo

----------------------------------------------------------------
## Fuente de datos
Kaggle Dataset:
https://www.kaggle.com/datasets/alexgude/california-traffic-collision-data-from-switrs

----------------------------------------------------------------

## Autores
Proyecto realizado por estudiantes del segundo semestre de la carrera de Estadística y Ciencias Actuariales en la Universidad Central de Venezuela (UCV)


-Kleyber Montoya
-Milena Martinez
-Zadquiel Nieves
-Sebastian Valbuena
