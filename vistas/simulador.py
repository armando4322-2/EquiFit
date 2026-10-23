import numpy as np
import plotly.graph_objects as go
import streamlit as st

from equifit import config as C
from equifit import model as M
from equifit import ui

df, es_real = ui.datos_actuales()
modelos = ui.modelos_completos(df)

st.markdown("# Pruébalo tú")
st.markdown(
    "Escribe tus medidas y compara lo que opina cada modelo sobre si el cinturón te ajustaría. "
    "No guardamos nada: todo se calcula en el momento."
)
ui.aviso_fuente(es_real, df)
st.write("")


@st.cache_data(show_spinner=False)
def proporciones(df):
    """Regresión lineal por grupo para estimar medidas a partir de la estatura."""
    out = {}
    for g in C.GRUPOS:
        s = df[df[C.COL_GENERO] == g]
        out[g] = {
            v: np.polyfit(s["estatura_cm"], s[v], 1)
            for v in ("altura_hombro_sentado_cm", "longitud_torso_cm", "contorno_pecho_cm")
        }
    return out


reg = proporciones(df)

izq, der = st.columns([1, 1.3], gap="large")
with izq:
    with st.container(border=True):
        grupo = st.segmented_control("Grupo de referencia", C.GRUPOS, default="Mujer")
        grupo = grupo or "Mujer"
        estatura = st.slider("Estatura (cm)", 140, 200, 158 if grupo == "Mujer" else 171)
        peso = st.slider("Peso (kg)", 40, 130, 63 if grupo == "Mujer" else 76)
        conozco = st.toggle(
            "Conozco mis medidas de hombro, torso y pecho",
            help="Si no, las estimamos a partir de tu estatura con las proporciones típicas del grupo.",
        )
        est = {v: float(np.polyval(reg[grupo][v], estatura)) for v in reg[grupo]}
        if conozco:
            hombro = st.slider("Altura de hombro sentado (cm)", 40.0, 75.0, round(est["altura_hombro_sentado_cm"], 1), 0.5,
                               help="Sentado con la espalda recta: del asiento a la parte alta del hombro.")
            torso = st.slider("Longitud de torso (cm)", 35.0, 65.0, round(est["longitud_torso_cm"], 1), 0.5)
            pecho = st.slider("Contorno de pecho / busto (cm)", 65.0, 140.0, round(est["contorno_pecho_cm"], 1), 0.5)
        else:
            hombro, torso, pecho = est["altura_hombro_sentado_cm"], est["longitud_torso_cm"], est["contorno_pecho_cm"]
            st.caption(f"Estimado: hombro {hombro:.1f} cm · torso {torso:.1f} cm · pecho {pecho:.1f} cm")

persona = {
    "estatura_cm": estatura, "peso_kg": peso,
    "altura_hombro_sentado_cm": hombro, "longitud_torso_cm": torso, "contorno_pecho_cm": pecho,
}
prob = M.predecir_persona(modelos, persona)

with der:
    a, b = st.columns(2)
    for col, nombre, clase, vars_ in (
        (a, "Modelo A", "ef-tag-a", "estatura y peso"),
        (b, "Modelo B", "ef-tag-b", "estatura, peso, hombro, torso y pecho"),
    ):
        p = prob[nombre]
        veredicto = "Te ajusta" if p >= 0.5 else "No te ajusta"
        with col:
            st.markdown(
                f'<div class="ef-modelo"><span class="ef-tag {clase}">{nombre}</span>'
                f'<div class="ef-grande" style="margin-top:.6rem">{veredicto}</div>'
                f'<p class="ef-sub" style="margin:.4rem 0 0">Probabilidad de ajuste: <b>{p:.0%}</b><br>'
                f"Ve: {vars_}</p></div>",
                unsafe_allow_html=True,
            )
    st.write("")
    dif = prob["Modelo B"] - prob["Modelo A"]
    if (prob["Modelo A"] >= 0.5) != (prob["Modelo B"] >= 0.5):
        if prob["Modelo A"] >= 0.5:
            st.warning(
                "**Los modelos no coinciden.** El Modelo A te aprueba solo por tu estatura y peso; "
                "el Modelo B, que también ve tus proporciones, detecta que el cinturón probablemente no te ajusta. "
                "Ese es exactamente el error que un dataset sin datos de mujeres deja pasar."
            )
        else:
            st.info(
                "**Los modelos no coinciden.** El Modelo A te descarta por tu estatura, pero tus proporciones "
                "reales sí son compatibles con el cinturón. Sin esos datos, el modelo generaliza de más."
            )
    else:
        st.success(
            f"Ambos modelos coinciden. La probabilidad cambia {dif * 100:+.0f} puntos cuando el modelo "
            "conoce tus proporciones."
        )

    # Dónde estás respecto a la muestra
    fig = go.Figure()
    for g in C.GRUPOS:
        s = df[df[C.COL_GENERO] == g]["altura_hombro_sentado_cm"]
        fig.add_histogram(
            x=s, name=f"{g}es" if g == "Mujer" else f"{g}s", opacity=0.7, nbinsx=24,
            marker=dict(color=C.COLOR_GRUPO[g], line=dict(width=1, color="#f7f5f0")),
            hovertemplate="%{x} cm: %{y} personas<extra></extra>",
        )
    fig.add_vline(x=hombro, line=dict(color=ui.TINTA, width=2), annotation_text="Tú",
                  annotation_position="top")
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title="Altura de hombro sentado (cm)")
    fig.update_yaxes(title="Personas")
    st.plotly_chart(ui.layout(fig, "Tu altura de hombro frente a la muestra", 280, pct=False),
                    width="stretch", config={"displayModeBar": False})
