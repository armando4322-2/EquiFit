import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from equifit import analysis as A
from equifit import config as C
from equifit import data as D
from equifit import ui

df, es_real = ui.datos_actuales()

st.markdown("# Datos y preguntas de investigación")
ui.aviso_fuente(es_real, df)
st.write("")

# ---------------------------------------------------------------------------
# Pregunta descriptiva
# ---------------------------------------------------------------------------
st.markdown("### ¿Con qué frecuencia reportan molestias mujeres y hombres?")
st.markdown('<p class="ef-sub">Pregunta descriptiva · lista de cotejo y escala Likert</p>', unsafe_allow_html=True)

desc = A.descriptiva(df)
indicadores = {
    "cuello": "Cinturón corta en el cuello",
    "busto": "Presión en busto / pecho",
    "anclaje_inadecuado": "Anclaje no se adapta al hombro",
    "no_ajusta": "No ajusta (variable objetivo)",
}
fig = go.Figure()
for g in C.GRUPOS:
    ys = [desc.loc[g, k] for k in indicadores]
    fig.add_bar(
        name=f"{g}es" if g == "Mujer" else f"{g}s", x=list(indicadores.values()), y=ys,
        marker=dict(color=C.COLOR_GRUPO[g], line=dict(width=2, color="#f7f5f0"), cornerradius=4),
        text=[f"{v:.0%}" for v in ys], textposition="outside", textfont=dict(color=ui.TINTA),
        hovertemplate="%{x}<br>" + g + ": %{y:.1%}<extra></extra>", cliponaxis=False,
    )
fig.update_yaxes(title="Participantes")
st.plotly_chart(ui.layout(fig, None, 380), width="stretch", config={"displayModeBar": False})

c1, c2 = st.columns(2)
for col, g in zip((c1, c2), C.GRUPOS):
    col.metric(
        f"Comodidad media · {g}es" if g == "Mujer" else f"Comodidad media · {g}s",
        f"{desc.loc[g, 'comodidad_media']:.2f} / 5",
        help=f"Ajuste medio: {desc.loc[g, 'ajuste_media']:.2f} / 5 · n = {int(desc.loc[g, 'n'])}",
    )

# ---------------------------------------------------------------------------
# Pregunta correlacional
# ---------------------------------------------------------------------------
st.divider()
st.markdown("### ¿Mientras más lejos del «estándar masculino», más incomodidad?")
st.markdown('<p class="ef-sub">Pregunta correlacional · distancia antropométrica vs. comodidad reportada</p>', unsafe_allow_html=True)

cor = A.correlacion(df)
d = cor["datos"]
izq, der = st.columns([2, 1], gap="large")
with izq:
    rng = np.random.default_rng(0)
    fig = go.Figure()
    for g in C.GRUPOS:
        s = d[d[C.COL_GENERO] == g]
        fig.add_scatter(
            x=s["distancia_estandar"], y=s["likert_promedio"] + rng.uniform(-0.12, 0.12, len(s)),
            mode="markers", name=f"{g}es" if g == "Mujer" else f"{g}s",
            marker=dict(color=C.COLOR_GRUPO[g], size=9, opacity=0.75, line=dict(width=1.5, color="white")),
            customdata=s[[C.COL_FOLIO, "likert_promedio"]].values,
            hovertemplate="%{customdata[0]}<br>Distancia: %{x:.2f}<br>Likert: %{customdata[1]:.1f}<extra></extra>",
        )
    pend, inter = np.polyfit(d["distancia_estandar"], d["likert_promedio"], 1)
    xs = np.linspace(d["distancia_estandar"].min(), d["distancia_estandar"].max(), 20)
    fig.add_scatter(x=xs, y=inter + pend * xs, mode="lines", name="Tendencia",
                    line=dict(color=ui.TINTA, width=2, dash="dash"), hoverinfo="skip")
    fig.update_xaxes(title="Distancia al estándar masculino (desviaciones estándar)")
    fig.update_yaxes(title="Comodidad + ajuste promedio (1–5)", range=[0.6, 5.4], tickformat=None)
    st.plotly_chart(ui.layout(fig, None, 400, pct=False), width="stretch", config={"displayModeBar": False})
with der:
    st.markdown(f'<div class="ef-grande">{cor["r"]:+.2f}</div>', unsafe_allow_html=True)
    p_txt = "< 0.001" if cor["p"] < 0.001 else f"= {cor['p']:.3f}"
    st.markdown(f"Coeficiente de **{cor['metodo']}** · p {p_txt}")
    st.markdown(f"Relación **{A.interpretar_r(cor['r'])}**.")
    st.caption(
        "La distancia combina estatura, altura de hombro sentado y longitud de torso, medida desde la "
        "mediana del grupo de hombres. Se usa Spearman si los datos no son normales (Shapiro-Wilk). "
        "Una correlación muestra asociación, no causa."
    )

# ---------------------------------------------------------------------------
# Tabla
# ---------------------------------------------------------------------------
st.divider()
with st.expander("Ver la base de datos (anonimizada por folio)"):
    st.dataframe(df, hide_index=True, width="stretch")
    st.download_button(
        "Descargar CSV", D.csv_seguro(df).encode("utf-8-sig"),
        file_name="equifit_datos.csv", mime="text/csv",
    )
