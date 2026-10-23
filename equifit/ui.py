"""Piezas compartidas de la interfaz Streamlit: estado, caché, estilos y gráficas."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import config as C
from . import data as D
from . import model as M

REPO_URL = "https://github.com/armando4322-2/EquiFit"

TINTA = "#1c2430"
TINTA_2 = "#4f5867"
REJILLA = "#e6e3dc"

CSS = """
<style>
:root { --tinta:#1c2430; --tinta2:#4f5867; --a:#eb6834; --b:#2a78d6; --mujer:#6250d6; --hombre:#008300; --papel:#f7f5f0; }
.block-container { padding-top: 2.2rem; max-width: 1180px; }
h1, h2, h3 { letter-spacing: -0.01em; }
.ef-aviso { border-left: 4px solid #eda100; background: #fff7e3; padding: .7rem 1rem; border-radius: 6px; color: var(--tinta); font-size: .93rem; }
.ef-real { border-left-color: var(--hombre); background: #eaf6ea; }
.ef-modelo { border-radius: 10px; padding: 1rem 1.1rem; border: 1px solid #e3e0d8; background: white; height: 100%; }
.ef-modelo h4 { margin: 0 0 .35rem 0; font-size: 1.05rem; }
.ef-tag { display:inline-block; font-size:.78rem; font-weight:600; padding:.12rem .55rem; border-radius:999px; color:white; }
.ef-tag-a { background: var(--a); } .ef-tag-b { background: var(--b); }
.ef-veredicto { border-radius: 10px; padding: 1rem 1.2rem; background: #eef4fc; border: 1px solid #cfe0f6; color: var(--tinta); }
.ef-veredicto.neutro { background: #f3f2ee; border-color: #e0ddd5; }
.ef-grande { font-size: 2.6rem; font-weight: 700; line-height: 1; }
.ef-sub { color: var(--tinta2); font-size: .92rem; }
</style>
"""


def estilos():
    st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Estado: qué datos está usando la app
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _simulados(n: int, prop_mujeres: float, semilla: int) -> pd.DataFrame:
    return D.simular(n=n, prop_mujeres=prop_mujeres, semilla=semilla)


def datos_actuales() -> tuple[pd.DataFrame, bool]:
    """Devuelve (df, es_real)."""
    s = st.session_state
    if s.get("usar_reales") and s.get("df_real") is not None:
        return s["df_real"], True
    return _simulados(s.get("sim_n", 300), s.get("sim_prop", 0.5), s.get("sim_semilla", C.SEMILLA)), False


@st.cache_resource(show_spinner=False, ttl=3600, max_entries=8)
def experimento(df: pd.DataFrame, prop_train: float | None):
    return M.ejecutar(df, prop_train)


@st.cache_data(show_spinner=False, ttl=3600, max_entries=16)
def repetido(df: pd.DataFrame, repeticiones: int, prop_train: float | None) -> pd.DataFrame:
    return M.ejecutar_repetido(df, repeticiones, prop_train)


@st.cache_resource(show_spinner=False, ttl=3600, max_entries=8)
def modelos_completos(df: pd.DataFrame):
    return M.entrenar_completo(df)


def aviso_fuente(es_real: bool, df: pd.DataFrame):
    n_m = int((df[C.COL_GENERO] == "Mujer").sum())
    n_h = int((df[C.COL_GENERO] == "Hombre").sum())
    if es_real:
        st.markdown(
            f'<div class="ef-aviso ef-real"><b>Datos reales del equipo</b> · {len(df)} participantes '
            f"({n_m} mujeres, {n_h} hombres).</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="ef-aviso"><b>Datos simulados para demostración.</b> {len(df)} participantes '
            f"ficticios ({n_m} mujeres, {n_h} hombres) generados con el mismo esquema que los instrumentos "
            "del protocolo. No son resultados del proyecto: la recolección en la UPY es del 2 al 5 de noviembre "
            "de 2026. Puedes cargar los datos reales en «Cargar datos».</div>",
            unsafe_allow_html=True,
        )


def barra_lateral():
    s = st.session_state
    with st.sidebar:
        st.markdown("### Fuente de datos")
        if s.get("df_real") is not None:
            s["usar_reales"] = st.toggle("Usar datos reales cargados", value=s.get("usar_reales", True))
        if not s.get("usar_reales") or s.get("df_real") is None:
            s["sim_n"] = st.slider(
                "Participantes simulados", 60, 600, s.get("sim_n", 300), step=20,
                help="La meta del protocolo es 30 mujeres + 30 hombres (60). Prueba con 60 para ver cuánto pesa el azar con muestras pequeñas.",
            )
            s["sim_semilla"] = st.number_input(
                "Semilla de simulación", 0, 9999, s.get("sim_semilla", C.SEMILLA),
                help="Cambia la semilla para generar otra muestra ficticia.",
            )
        st.divider()
        st.caption(
            "EquiFit · Proyecto Integrador I · TSU en Ciencia de Datos 3°B · "
            "Universidad Politécnica de Yucatán"
        )
        st.link_button("Ver código en GitHub", REPO_URL, width="stretch")


# ---------------------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------------------
def layout(fig: go.Figure, titulo: str | None = None, alto: int = 360, pct: bool = True) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=15, color=TINTA), x=0, xanchor="left") if titulo else None,
        height=alto,
        margin=dict(l=10, r=10, t=50 if titulo else 20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=TINTA_2, size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, title=None),
        bargap=0.28,
        bargroupgap=0.06,
        hoverlabel=dict(bgcolor="white", font_size=13),
    )
    fig.update_xaxes(showgrid=False, linecolor=REJILLA, ticks="")
    fig.update_yaxes(gridcolor=REJILLA, zeroline=False, linecolor=REJILLA)
    if pct:
        fig.update_yaxes(tickformat=".0%", rangemode="tozero")
    return fig


def barras_agrupadas(valores: dict, errores: dict | None, titulo: str, eje: str) -> go.Figure:
    """valores = {"Modelo A": {"Mujer": x, "Hombre": y}, "Modelo B": {...}}"""
    fig = go.Figure()
    for modelo, por_g in valores.items():
        grupos = list(por_g)
        ys = [por_g[g] for g in grupos]
        err = None
        if errores:
            lo = [por_g[g] - errores[modelo][g][0] for g in grupos]
            hi = [errores[modelo][g][1] - por_g[g] for g in grupos]
            err = dict(type="data", array=hi, arrayminus=lo, color=TINTA_2, thickness=1.2, width=5)
        fig.add_bar(
            name=modelo, x=[f"{g}es" if g == "Mujer" else f"{g}s" for g in grupos], y=ys,
            marker=dict(color=C.COLOR_MODELO[modelo], line=dict(width=2, color="#f7f5f0"), cornerradius=4),
            error_y=err,
            text=[f"{v:.0%}" for v in ys], textposition="inside", insidetextanchor="start",
            textfont=dict(color="white", size=14), textangle=0,
            hovertemplate="%{x}<br>" + modelo + ": %{y:.1%}<extra></extra>",
        )
    fig.update_yaxes(title=eje)
    return layout(fig, titulo)


def pct(x: float) -> str:
    return "—" if pd.isna(x) else f"{x:.0%}"
