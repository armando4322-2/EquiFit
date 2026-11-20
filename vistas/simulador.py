import plotly.graph_objects as go
import streamlit as st

from equifit import config as C
from equifit import model as M
from equifit import ui

df, es_real = ui.datos_actuales()
modelos = ui.modelos_completos(df)

st.markdown("# Pruébalo tú")
st.markdown(
    "Contesta como lo harías en la encuesta y compara lo que opina cada modelo sobre si el cinturón te ajustaría. "
    "No guardamos nada: todo se calcula en el momento."
)
ui.aviso_fuente(es_real, df)
st.write("")


@st.cache_data(show_spinner=False)
def respuestas_tipicas(df):
    """Respuesta más común de cada grupo, para precargar el simulador."""
    return {
        g: {v: int(df.loc[df[C.COL_GENERO] == g, v].mode().iloc[0]) for v in C.ESCALAS}
        for g in C.GRUPOS
    }


tipicas = respuestas_tipicas(df)
PREGUNTAS = {
    "hombro_vs_anclaje": "Sentado(a) en tu auto, la parte alta de tu hombro queda…",
    "talla_superior": "Tu talla de playera o blusa",
    "largo_camisas": "De largo, las camisas o blusas de tu talla te quedan…",
}

izq, der = st.columns([1, 1.3], gap="large")
with izq:
    with st.container(border=True):
        grupo = st.segmented_control("Grupo de referencia", C.GRUPOS, default="Mujer")
        grupo = grupo or "Mujer"
        estatura = st.slider("Estatura (cm)", 140, 200, 158 if grupo == "Mujer" else 171)
        peso = st.slider("Peso (kg)", 40, 130, 63 if grupo == "Mujer" else 76)
        respuestas = {}
        for var, pregunta in PREGUNTAS.items():
            opciones = list(C.ESCALAS[var])
            respuestas[var] = st.selectbox(
                pregunta, opciones,
                index=opciones.index(tipicas[grupo][var]),
                format_func=lambda v, var=var: C.ESCALAS[var][v],
                key=f"sim_{var}_{grupo}",
                help="Viene precargada con la respuesta más común del grupo; cámbiala por la tuya."
                if var == "hombro_vs_anclaje" else None,
            )

persona = {"estatura_cm": estatura, "peso_kg": peso, **respuestas}
prob = M.predecir_persona(modelos, persona)

with der:
    a, b = st.columns(2)
    for col, nombre, clase, vars_ in (
        (a, "Modelo A", "ef-tag-a", "estatura y peso"),
        (b, "Modelo B", "ef-tag-b", "estatura, peso, hombro, talla y largo de torso"),
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
        cambio = round(dif * 100)
        st.success(
            "Ambos modelos coinciden" + (
                f". La probabilidad cambia {cambio:+d} puntos cuando el modelo conoce tus proporciones."
                if cambio else ", con la misma probabilidad."
            )
        )

    # Dónde estás respecto a la muestra
    fig = go.Figure()
    cats = list(C.ESCALAS["hombro_vs_anclaje"])
    CORTAS = {1: "Arriba", 2: "Misma altura", 3: "Un poco abajo", 4: "Muy abajo"}
    etiquetas = [CORTAS[c] for c in cats]
    for g in C.GRUPOS:
        s = df.loc[df[C.COL_GENERO] == g, "hombro_vs_anclaje"].value_counts(normalize=True)
        ys = [float(s.get(c, 0)) for c in cats]
        fig.add_bar(
            x=etiquetas, y=ys, name=f"{g}es" if g == "Mujer" else f"{g}s",
            marker=dict(color=C.COLOR_GRUPO[g], line=dict(width=2, color="#f6f1fb"), cornerradius=4),
            hovertemplate="%{x}<br>" + g + ": %{y:.0%}<extra></extra>",
        )
    fig.add_annotation(x=CORTAS[respuestas["hombro_vs_anclaje"]], y=1.0,
                       yref="paper", text="Tú", showarrow=False,
                       font=dict(color=ui.TINTA, size=13), bgcolor="#fbe6f0", borderpad=3)
    fig.update_yaxes(title="Personas del grupo")
    st.plotly_chart(ui.layout(fig, "Dónde queda el hombro respecto al cinturón", 300),
                    width="stretch", config={"displayModeBar": False})
