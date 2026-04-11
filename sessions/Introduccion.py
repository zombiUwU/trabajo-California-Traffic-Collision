import streamlit as st

def mostrar_introduccion():
    st.markdown("<h1 style='color: #D4AF37;'>📖 Introducción</h1>",unsafe_allow_html=True)
    st.divider()
    
    st.header("Análisis de Colisiones SWITRS")
    st.write("""
    Este proyecto realiza un análisis exploratorio de los accidentes de tráfico en California utilizando datos públicos del sistema SWITRS (Statewide Integrated Traffic Records System).

A pesar de las mejoras en tecnología vehicular, California sigue registrando altos índices de fatalidad vial. Existe una falta de herramientas interactivas que permitan a las autoridades y ciudadanos entender no sólo donde ocurren los accidentes, sino quienes son las víctimas más vulnerables y cómo influyen factores específicos (distracción por celular o falta de equipo de seguridad) en la supervivencia de un siniestro entre 2018 y 2021.

""") 
    st.markdown("---")