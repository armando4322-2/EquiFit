"""Análisis para las preguntas descriptiva y correlacional del protocolo."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import config as C


def descriptiva(df: pd.DataFrame) -> pd.DataFrame:
    """Pregunta descriptiva: frecuencia de molestias y desajuste por grupo."""
    d = df[df[C.COL_GENERO].isin(C.GRUPOS)]
    tabla = d.groupby(C.COL_GENERO).agg(
        n=(C.COL_FOLIO, "count"),
        cuello=("cuello_corta", "mean"),
        busto=("presion_busto", "mean"),
        anclaje_inadecuado=("anclaje_adecuado", lambda s: 1 - s.mean()),
        no_ajusta=(C.COL_OBJETIVO, lambda s: 1 - s.mean()),
        comodidad_media=("likert_comodidad", "mean"),
        ajuste_media=("likert_ajuste", "mean"),
    )
    return tabla.reindex(C.GRUPOS)


def distancia_estandar(df: pd.DataFrame) -> pd.DataFrame:
    """Distancia antropométrica al 'estándar masculino' (mediana del grupo Hombre).

    Distancia euclidiana en unidades de desviación estándar (z) sobre estatura,
    altura de hombro sentado y longitud de torso.
    """
    df = df.copy()
    hombres = df[df[C.COL_GENERO] == "Hombre"]
    ref = hombres[C.VARIABLES_DISTANCIA].median()
    sd = df[C.VARIABLES_DISTANCIA].std(ddof=0).replace(0, 1)
    z = (df[C.VARIABLES_DISTANCIA] - ref) / sd
    df["distancia_estandar"] = np.sqrt((z ** 2).sum(axis=1))
    return df


def correlacion(df: pd.DataFrame) -> dict:
    """Pregunta correlacional: distancia al estándar vs. comodidad reportada.

    Se elige Spearman o Pearson según normalidad (Shapiro-Wilk, α = 0.05).
    """
    d = distancia_estandar(df)
    x, y = d["distancia_estandar"], d["likert_promedio"]
    normal = (
        stats.shapiro(x.sample(min(len(x), 500), random_state=0)).pvalue > 0.05
        and stats.shapiro(y.sample(min(len(y), 500), random_state=0)).pvalue > 0.05
    )
    if normal:
        r, p = stats.pearsonr(x, y)
        metodo = "Pearson"
    else:
        r, p = stats.spearmanr(x, y)
        metodo = "Spearman"
    return {"metodo": metodo, "r": float(r), "p": float(p), "datos": d}


def interpretar_r(r: float) -> str:
    a = abs(r)
    fuerza = "muy débil" if a < 0.2 else "débil" if a < 0.4 else "moderada" if a < 0.6 else "fuerte"
    sentido = "negativa" if r < 0 else "positiva"
    return f"{fuerza} y {sentido}"
