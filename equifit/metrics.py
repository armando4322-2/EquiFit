"""Métricas de desempeño y equidad (fairness), calculadas a mano para que
cada número sea explicable en la expo.

Glosario (positivo = "el cinturón ajusta"):
- Precisión (accuracy): % de predicciones correctas.
- Tasa de error: 1 − precisión.
- Falso "seguro" (FPR): de las personas a quienes el cinturón NO les ajusta,
  % que el modelo marca como "sí ajusta". Es el error peligroso: aprueba un
  diseño que en realidad lastima o no protege.
- Falsa alarma (FNR): de quienes SÍ les ajusta, % marcado como "no ajusta".
- Tasa de selección: % que el modelo predice como "ajusta".
- Brecha de error: |error mujeres − error hombres|.
- Diferencia de paridad demográfica: |selección mujeres − selección hombres|.
- Diferencia de probabilidades igualadas (equalized odds):
  max(|ΔTPR|, |ΔFPR|) entre grupos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def _seguro(num, den):
    return float(num) / float(den) if den else np.nan


def metricas_por_grupo(preds: pd.DataFrame) -> pd.DataFrame:
    filas = []
    grupos = [("Total", preds)] + [
        (g, preds[preds[C.COL_GENERO] == g]) for g in C.GRUPOS
    ]
    for nombre, d in grupos:
        y, p = d["real"].values, d["pred"].values
        vp = int(((y == 1) & (p == 1)).sum())
        vn = int(((y == 0) & (p == 0)).sum())
        fp = int(((y == 0) & (p == 1)).sum())
        fn = int(((y == 1) & (p == 0)).sum())
        n = len(d)
        filas.append(
            {
                "grupo": nombre,
                "n": n,
                "precision": _seguro(vp + vn, n),
                "error": _seguro(fp + fn, n),
                "fpr": _seguro(fp, fp + vn),
                "fnr": _seguro(fn, fn + vp),
                "tpr": _seguro(vp, vp + fn),
                "seleccion": _seguro(vp + fp, n),
                "tasa_real_ajuste": _seguro(vp + fn, n),
                "VP": vp, "VN": vn, "FP": fp, "FN": fn,
            }
        )
    return pd.DataFrame(filas).set_index("grupo")


def resumen_equidad(por_grupo: pd.DataFrame) -> dict:
    m, h = por_grupo.loc["Mujer"], por_grupo.loc["Hombre"]
    return {
        "precision_global": por_grupo.loc["Total", "precision"],
        "brecha_error": abs(m["error"] - h["error"]),
        "paridad_demografica": abs(m["seleccion"] - h["seleccion"]),
        "probabilidades_igualadas": max(abs(m["tpr"] - h["tpr"]), abs(m["fpr"] - h["fpr"])),
        "falso_seguro_mujeres": m["fpr"],
        "falso_seguro_hombres": h["fpr"],
        "error_mujeres": m["error"],
        "error_hombres": h["error"],
    }
