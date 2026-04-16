import streamlit as st

def mostrar_delta_lake():
    st.markdown("<h1 style='color: #D4AF37;'>🐍 Delta Lake</h1>",unsafe_allow_html=True)
    st.divider()
    
    st.header("Ques es?")
    st.write("""
    Es un formato de almacenamiento que combina lo mejor de los Data Warehouses (orden y transacciones) con
    los Data Lakes (flexibilidad y gran volumen). Para evitar trabajar con CSV y Parquets sueltos utilizamos el
    Delta Lake que organiza los datos en tablas que mantienen un registro histórico de cada cambio.""")
    st.markdown("---")
    
    
    st.subheader("Porque lo utilizamos?")
    st.write("""
            Debido a que no es posible subir la BD de SWITRS completa se utilizaron parquets (100.000 filas) de cada
            tabla a modo de ejemplo, de esta manera y utilizando el delta lake se guardo un registro/versiones de todos
            los cambios y filtrados que se realizaronn en la BD original""")
    st.markdown("---")
    
    st.info("para entrar al delta_Lake usamos la ruta 'data/delta_lake'")