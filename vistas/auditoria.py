import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from equifit import config as C
from equifit import model as M
from equifit import ui

df, es_real = ui.datos_actuales()

st.markdown("# Auditoría A vs B")
st.markdown(
    "Mismo algoritmo (Random Forest), mismos hiperparámetros y la misma partición de "
    "entrenamiento/prueba. La única diferencia es qué variables ve cada modelo."
)
ui.aviso_fuente(es_real, df)
st.write("")

# ---------------------------------------------------------------------------
# Controles del experimento
# ---------------------------------------------------------------------------
with st.container(border=True):
    c1, c2 = st.columns([1.6, 1])
    with c1:
        escenario = st.segmented_control(
            "Datos de entrenamiento",
            ["Protocolo (todos los participantes)", "Histórico (pocas mujeres)"],
            default="Protocolo (todos los participantes)",
            help=(
                "Protocolo: se entrena con la muestra tal como se recolecta. "
                "Histórico: se imita una base de datos antigua donde casi no hay mujeres; "
                "solo se quitan mujeres del entrenamiento, nunca de la prueba."
            ),
        )
        prop_train = None
        if escenario == "Histórico (pocas mujeres)":
            prop_train = st.slider("Porcentaje de mujeres en el entrenamiento", 5, 45, 15, 5) / 100
    with c2:
        repeticiones = st.select_slider(
            "Repeticiones del experimento", [5, 10, 15, 20, 30], value=15,
            help="Cada repetición usa otra partición; A y B siempre comparten la misma. Más repeticiones = resultado más estable.",
        )

with st.spinner("Entrenando y evaluando los dos modelos…"):
    rep = ui.repetido(df, repeticiones, prop_train)
    res = M.resumir_repetido(rep)
    exp = ui.experimento(df, prop_train)


def m(metrica, modelo):
    return res.loc[metrica, f"{modelo}_media"]


# ---------------------------------------------------------------------------
# Indicadores principales
# ---------------------------------------------------------------------------
st.write("")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Exactitud global", ui.pct(m("precision_global", "B")),
          delta=f"{(m('precision_global','B') - m('precision_global','A'))*100:+.0f} pts vs A",
          help=f"Modelo A: {ui.pct(m('precision_global','A'))}. Porcentaje de predicciones correctas (accuracy).")
k2.metric("Error en mujeres", ui.pct(m("error_mujeres", "B")),
          delta=f"{(m('error_mujeres','B') - m('error_mujeres','A'))*100:+.0f} pts vs A", delta_color="inverse",
          help=f"Modelo A: {ui.pct(m('error_mujeres','A'))}.")
k3.metric('Falso "seguro" en mujeres', ui.pct(m("falso_seguro_mujeres", "B")),
          delta=f"{(m('falso_seguro_mujeres','B') - m('falso_seguro_mujeres','A'))*100:+.0f} pts vs A", delta_color="inverse",
          help=f"Modelo A: {ui.pct(m('falso_seguro_mujeres','A'))}. De las mujeres a quienes el cinturón NO les ajusta, cuántas el modelo aprueba como «sí ajusta».")
k4.metric("Brecha de error entre grupos", ui.pct(m("brecha_error", "B")),
          delta=f"{(m('brecha_error','B') - m('brecha_error','A'))*100:+.0f} pts vs A", delta_color="inverse",
          help=f"Modelo A: {ui.pct(m('brecha_error','A'))}. Diferencia absoluta entre el error en mujeres y en hombres.")
st.caption(f"Valores del Modelo B; la flecha compara contra el Modelo A. Promedio de {repeticiones} repeticiones.")

# ---------------------------------------------------------------------------
# Veredicto honesto
# ---------------------------------------------------------------------------
gana_err = res.loc["error_mujeres", "B_mejor_pct"]
gana_fs = res.loc["falso_seguro_mujeres", "B_mejor_pct"]
n_prueba_m = exp.prueba_por_grupo.get("Mujer", 0)
if gana_err >= 0.8:
    clase = ""
    texto = (
        f"<b>El Modelo B se equivoca menos con las mujeres en {gana_err:.0%} de las repeticiones.</b> "
        f"Su error promedio en mujeres pasa de {ui.pct(m('error_mujeres','A'))} a {ui.pct(m('error_mujeres','B'))}, "
        f"y el falso «seguro» de {ui.pct(m('falso_seguro_mujeres','A'))} a {ui.pct(m('falso_seguro_mujeres','B'))}. "
        "Con estos datos, incluir torso, hombro y busto mejora el sistema de forma consistente."
    )
elif gana_err >= 0.6:
    clase = ""
    texto = (
        f"<b>El Modelo B tiende a equivocarse menos con las mujeres ({gana_err:.0%} de las repeticiones)</b>, "
        "pero la ventaja no es constante. Con más participantes el resultado sería más firme."
    )
else:
    clase = "neutro"
    texto = (
        f"<b>Con estos datos la diferencia no es concluyente</b> (B mejora el error en mujeres en "
        f"{gana_err:.0%} de las repeticiones). Cada partición deja solo ~{n_prueba_m} mujeres en la prueba, "
        "así que el azar pesa más que el efecto. Esto no significa que no exista: significa que la muestra "
        "es pequeña para detectarlo."
    )
st.markdown(f'<div class="ef-veredicto {clase}">{texto}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Gráficas por grupo
# ---------------------------------------------------------------------------
st.write("")
g1, g2 = st.columns(2, gap="large")


def por_grupo(m_mujer, m_hombre):
    val = {mod: {"Mujer": res.loc[m_mujer, f"{mod[-1]}_media"], "Hombre": res.loc[m_hombre, f"{mod[-1]}_media"]}
           for mod in ("Modelo A", "Modelo B")}
    err = {mod: {"Mujer": (res.loc[m_mujer, f"{mod[-1]}_p10"], res.loc[m_mujer, f"{mod[-1]}_p90"]),
                 "Hombre": (res.loc[m_hombre, f"{mod[-1]}_p10"], res.loc[m_hombre, f"{mod[-1]}_p90"])}
           for mod in ("Modelo A", "Modelo B")}
    return val, err


with g1:
    v, e = por_grupo("error_mujeres", "error_hombres")
    st.plotly_chart(ui.barras_agrupadas(v, e, "Tasa de error por grupo", "Predicciones incorrectas"),
                    width="stretch", config={"displayModeBar": False})
    st.caption("Barra = promedio; línea = rango del 80 % central de las repeticiones.")
with g2:
    v, e = por_grupo("falso_seguro_mujeres", "falso_seguro_hombres")
    st.plotly_chart(ui.barras_agrupadas(v, e, 'Falso "seguro" por grupo', "Aprobados sin ajustar"),
                    width="stretch", config={"displayModeBar": False})
    st.caption(
        "El error más grave: decir que el cinturón ajusta cuando no. En hombres hay muy pocos casos de "
        "«no ajusta», por eso su barra es inestable."
    )

# ---------------------------------------------------------------------------
# Detalle
# ---------------------------------------------------------------------------
st.write("")
t1, t2, t3, t4 = st.tabs(["Métricas de equidad", "Matrices de confusión", "Qué variables pesan", "Qué se controla"])

with t1:
    nombres = {
        "precision_global": ("Exactitud global (accuracy)", "Más alto es mejor"),
        "error_mujeres": ("Error en mujeres", "Más bajo es mejor"),
        "error_hombres": ("Error en hombres", "Más bajo es mejor"),
        "brecha_error": ("Brecha de error |mujeres − hombres|", "Más bajo es mejor"),
        "falso_seguro_mujeres": ('Falso "seguro" en mujeres', "Más bajo es mejor"),
        "falso_seguro_hombres": ('Falso "seguro" en hombres', "Más bajo es mejor"),
        "probabilidades_igualadas": ("Diferencia de probabilidades igualadas", "Más bajo es mejor"),
        "paridad_demografica": ("Diferencia de paridad demográfica", "Ver nota"),
    }
    tabla = pd.DataFrame(
        {
            "Métrica": [nombres[k][0] for k in nombres],
            "Modelo A": [f"{res.loc[k,'A_media']:.1%} ± {res.loc[k,'A_sd']:.1%}" for k in nombres],
            "Modelo B": [f"{res.loc[k,'B_media']:.1%} ± {res.loc[k,'B_sd']:.1%}" for k in nombres],
            "B mejor en": [f"{res.loc[k,'B_mejor_pct']:.0%}" if k != "paridad_demografica" else "—" for k in nombres],
            "Lectura": [nombres[k][1] for k in nombres],
        }
    )
    st.dataframe(tabla, hide_index=True, width="stretch")
    st.markdown(
        "**Nota sobre la paridad demográfica.** Mide si el modelo dice «ajusta» con la misma frecuencia a "
        "mujeres y hombres. Aquí no es la métrica correcta: si el cinturón realmente le ajusta peor a las "
        "mujeres, un modelo honesto *debe* decirlo más seguido. Forzar la paridad escondería el problema. "
        "Por eso EquiFit prioriza el error por grupo y el falso «seguro», que comparan la predicción contra "
        "lo que de verdad pasó."
    )

with t2:
    st.caption("Una sola partición (la primera), para ver los conteos concretos.")
    cols = st.columns(2)
    for col, r in zip(cols, (exp.A, exp.B)):
        with col:
            st.markdown(f"**{r.nombre}** · exactitud {r.por_grupo.loc['Total','precision']:.0%}")
            pg = r.por_grupo.loc[C.GRUPOS, ["n", "VP", "FN", "FP", "VN"]].rename(
                columns={"VP": "Ajusta → dijo ajusta", "FN": "Ajusta → dijo no",
                         "FP": "No ajusta → dijo ajusta", "VN": "No ajusta → dijo no"}
            )
            st.dataframe(pg, width="stretch")

with t3:
    imp = exp.B.importancias.rename(index=C.ANTROPOMETRIA)
    fig = go.Figure(go.Bar(
        x=imp.values[::-1], y=imp.index[::-1], orientation="h",
        marker=dict(color=C.COLOR_MODELO["Modelo B"], cornerradius=4),
        text=[f"{v:.0%}" for v in imp.values[::-1]], textposition="outside",
        hovertemplate="%{y}: %{x:.1%}<extra></extra>", cliponaxis=False,
    ))
    fig.update_xaxes(tickformat=".0%", title="Importancia en el Modelo B")
    st.plotly_chart(ui.layout(fig, "Qué variables usa más el Modelo B", 320, pct=False),
                    width="stretch", config={"displayModeBar": False})
    st.caption(
        "Si las variables que el Modelo A no tiene (hombro, torso, busto) aparecen arriba, "
        "son justo la información que faltaba."
    )

with t4:
    st.markdown(
        f"""
| Control | Valor |
|---|---|
| Algoritmo | Random Forest (scikit-learn) |
| Hiperparámetros | {", ".join(f"{k}={v}" for k, v in C.HIPERPARAMETROS.items() if k != "n_jobs")} |
| Partición | {int((1-C.PROPORCION_PRUEBA)*100)} % entrenamiento / {int(C.PROPORCION_PRUEBA*100)} % prueba, estratificada por género y resultado |
| Variables Modelo A | {", ".join(C.ANTROPOMETRIA[v] for v in C.VARIABLES_MODELO_A)} |
| Variables Modelo B | {", ".join(C.ANTROPOMETRIA[v] for v in C.VARIABLES_MODELO_B)} |
| Variable objetivo | Ajusta (1) si el promedio Likert es ≥ {C.UMBRAL_LIKERT:g} y la lista de cotejo no marca cuello ni busto; si no, 0 |
| Entrenamiento / prueba | {exp.n_entrenamiento} / {exp.n_prueba} participantes por repetición |
"""
    )
