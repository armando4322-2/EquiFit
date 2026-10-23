import streamlit as st

from equifit import config as C
from equifit import ui

df, es_real = ui.datos_actuales()

st.markdown("# EquiFit")
st.markdown(
    "#### Auditoría de la brecha de datos de género en el diseño de productos"
)
st.markdown(
    '<p class="ef-sub">Caso piloto: el cinturón de seguridad vehicular · Universidad Politécnica de Yucatán</p>',
    unsafe_allow_html=True,
)

st.write("")
izq, der = st.columns([1.25, 1], gap="large")
with izq:
    st.markdown(
        """
Muchos productos se diseñan con medidas del cuerpo masculino como si fueran el
estándar de todas las personas. Cuando las medidas y la comodidad de las mujeres no
están en los datos, el producto parece funcionar "para todos", pero no es así.
Y los modelos de inteligencia artificial que aprenden de esos datos heredan el mismo
punto ciego.

**EquiFit** mide ese punto ciego. Entrenamos el mismo algoritmo dos veces, con los
mismos participantes, y solo cambiamos qué datos ve:
"""
    )
    a, b = st.columns(2)
    with a:
        st.markdown(
            '<div class="ef-modelo"><span class="ef-tag ef-tag-a">Modelo A</span>'
            "<h4>Dataset estándar</h4>Solo estatura y peso: las métricas generales "
            "con las que suele diseñarse un producto.</div>",
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            '<div class="ef-modelo"><span class="ef-tag ef-tag-b">Modelo B</span>'
            "<h4>Dataset inclusivo</h4>Agrega longitud de torso, altura de hombro "
            "sentado y contorno de pecho/busto.</div>",
            unsafe_allow_html=True,
        )
    st.write("")
    st.markdown(
        "Si el Modelo B se equivoca menos con las mujeres, la evidencia es clara: "
        "**incluir los datos de la otra mitad de la población hace que los sistemas sean "
        "más precisos y más seguros.** El cinturón es nuestra prueba de campo, pero el "
        "método sirve para auditar cualquier producto o servicio."
    )

with der:
    with st.container(border=True):
        st.markdown("**Resultado con los datos actuales**")
        with st.spinner("Entrenando los dos modelos…"):
            rep = ui.repetido(df, 15, None)
        from equifit import model as M

        res = M.resumir_repetido(rep)
        ea, eb = res.loc["error_mujeres", "A_media"], res.loc["error_mujeres", "B_media"]
        c1, c2 = st.columns(2)
        c1.metric("Error en mujeres · Modelo A", ui.pct(ea))
        c2.metric("Error en mujeres · Modelo B", ui.pct(eb), delta=f"{(eb - ea) * 100:+.0f} pts", delta_color="inverse")
        pa, pb = res.loc["precision_global", "A_media"], res.loc["precision_global", "B_media"]
        c3, c4 = st.columns(2)
        c3.metric("Exactitud global · A", ui.pct(pa))
        c4.metric("Exactitud global · B", ui.pct(pb), delta=f"{(pb - pa) * 100:+.0f} pts")
        st.caption("Promedio de 15 particiones de entrenamiento/prueba.")
    ui.aviso_fuente(es_real, df)

st.write("")
st.markdown("### Recorre la demo")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.page_link("vistas/auditoria.py", label="Auditoría A vs B", icon=":material/balance:")
    st.caption("Las métricas de exactitud y equidad de los dos modelos, lado a lado.")
with c2:
    st.page_link("vistas/simulador.py", label="Pruébalo tú", icon=":material/accessibility_new:")
    st.caption("Escribe tus medidas y mira qué opina cada modelo.")
with c3:
    st.page_link("vistas/datos.py", label="Datos y preguntas", icon=":material/query_stats:")
    st.caption("Frecuencia de molestias por grupo y su relación con las medidas.")
with c4:
    st.page_link("vistas/cargar.py", label="Cargar datos", icon=":material/upload_file:")
    st.caption("Sube los datos de campo y recalcula toda la auditoría.")
