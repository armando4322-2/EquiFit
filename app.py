"""EquiFit — sistema de auditoría de la brecha de datos de género.

Ejecutar:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="EquiFit · Auditoría de sesgo antropométrico",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="auto",  # cerrado en celular, abierto en escritorio
)

from equifit import ui  # noqa: E402

ui.estilos()

paginas = [
    st.Page("vistas/inicio.py", title="Inicio", icon=":material/home:", default=True),
    st.Page("vistas/auditoria.py", title="Auditoría A vs B", icon=":material/balance:"),
    st.Page("vistas/datos.py", title="Datos y preguntas", icon=":material/query_stats:"),
    st.Page("vistas/simulador.py", title="Pruébalo tú", icon=":material/accessibility_new:"),
    st.Page("vistas/cargar.py", title="Cargar datos", icon=":material/upload_file:"),
    st.Page("vistas/metodologia.py", title="Metodología y equipo", icon=":material/menu_book:"),
]

nav = st.navigation(paginas)
ui.barra_lateral()
nav.run()
