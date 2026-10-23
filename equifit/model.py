"""Experimento A vs B: mismo algoritmo, mismos hiperparámetros, misma partición.

La ÚNICA diferencia entre los dos modelos es qué variables ven
(config.VARIABLES_MODELO_A vs config.VARIABLES_MODELO_B).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from . import config as C
from .metrics import metricas_por_grupo, resumen_equidad


@dataclass
class ResultadoModelo:
    nombre: str
    variables: list[str]
    modelo: RandomForestClassifier
    por_grupo: pd.DataFrame
    equidad: dict
    importancias: pd.Series
    predicciones: pd.DataFrame = field(repr=False)


@dataclass
class Experimento:
    A: ResultadoModelo
    B: ResultadoModelo
    n_entrenamiento: int
    n_prueba: int
    prueba_por_grupo: dict


def particion(df: pd.DataFrame, prop_mujeres_entrenamiento: float | None = None, semilla: int = C.SEMILLA):
    """Partición estratificada por género y objetivo.

    Si `prop_mujeres_entrenamiento` se indica, se submuestrea a las mujeres SOLO
    en el conjunto de entrenamiento (escenario de sub-representación histórica).
    El conjunto de prueba nunca se toca, para que la evaluación sea justa.
    """
    estrato = df[C.COL_GENERO].astype(str) + "_" + df[C.COL_OBJETIVO].astype(str)
    # Si algún estrato es muy pequeño, se estratifica solo por género
    if estrato.value_counts().min() < 2:
        estrato = df[C.COL_GENERO]
    train, test = train_test_split(
        df, test_size=C.PROPORCION_PRUEBA, stratify=estrato, random_state=semilla
    )
    if prop_mujeres_entrenamiento is not None:
        mujeres = train[train[C.COL_GENERO] == "Mujer"]
        resto = train[train[C.COL_GENERO] != "Mujer"]
        p = float(np.clip(prop_mujeres_entrenamiento, 0.02, 0.98))
        n_obj = int(round(p / (1 - p) * len(resto)))
        n_obj = max(5, min(len(mujeres), n_obj))
        mujeres = mujeres.sample(n=n_obj, random_state=semilla)
        train = pd.concat([mujeres, resto]).sample(frac=1, random_state=semilla)
    return train, test


def _entrenar(nombre, variables, train, test) -> ResultadoModelo:
    modelo = RandomForestClassifier(**C.HIPERPARAMETROS)
    modelo.fit(train[variables], train[C.COL_OBJETIVO])
    prob = modelo.predict_proba(test[variables])[:, 1]
    pred = (prob >= 0.5).astype(int)
    preds = pd.DataFrame(
        {
            C.COL_FOLIO: test[C.COL_FOLIO].values,
            C.COL_GENERO: test[C.COL_GENERO].values,
            "real": test[C.COL_OBJETIVO].values,
            "pred": pred,
            "prob": prob,
        }
    )
    por_grupo = metricas_por_grupo(preds)
    return ResultadoModelo(
        nombre=nombre,
        variables=list(variables),
        modelo=modelo,
        por_grupo=por_grupo,
        equidad=resumen_equidad(por_grupo),
        importancias=pd.Series(modelo.feature_importances_, index=variables).sort_values(ascending=False),
        predicciones=preds,
    )


def ejecutar(df: pd.DataFrame, prop_mujeres_entrenamiento: float | None = None) -> Experimento:
    train, test = particion(df, prop_mujeres_entrenamiento)
    A = _entrenar("Modelo A", C.VARIABLES_MODELO_A, train, test)
    B = _entrenar("Modelo B", C.VARIABLES_MODELO_B, train, test)
    return Experimento(
        A=A,
        B=B,
        n_entrenamiento=len(train),
        n_prueba=len(test),
        prueba_por_grupo=test[C.COL_GENERO].value_counts().to_dict(),
    )


def ejecutar_repetido(
    df: pd.DataFrame,
    repeticiones: int = 25,
    prop_mujeres_entrenamiento: float | None = None,
) -> pd.DataFrame:
    """Evaluación pareada en varias particiones.

    Con muestras pequeñas (p. ej. 30 + 30) una sola partición deja ~18
    personas de prueba y el resultado depende del azar. Aquí se repite el
    experimento con distintas semillas; en cada repetición A y B usan
    EXACTAMENTE la misma partición, así la comparación sigue controlada.
    Devuelve una fila por (repetición, modelo) con sus métricas de equidad.
    """
    filas = []
    for i in range(repeticiones):
        semilla = C.SEMILLA + i
        train, test = particion(df, prop_mujeres_entrenamiento, semilla=semilla)
        for nombre, vars_ in (("Modelo A", C.VARIABLES_MODELO_A), ("Modelo B", C.VARIABLES_MODELO_B)):
            r = _entrenar(nombre, vars_, train, test)
            filas.append({"repeticion": i, "modelo": nombre, **r.equidad})
    return pd.DataFrame(filas)


def resumir_repetido(rep: pd.DataFrame) -> pd.DataFrame:
    """Media, desviación e intervalo 10–90 % por métrica y modelo, más
    el % de repeticiones en que B fue mejor que A (comparación pareada)."""
    metricas = [c for c in rep.columns if c not in ("repeticion", "modelo")]
    piv = {m: rep.pivot(index="repeticion", columns="modelo", values=m) for m in metricas}
    filas = []
    for m, t in piv.items():
        mayor_es_mejor = m == "precision_global"
        mejor = (t["Modelo B"] > t["Modelo A"]) if mayor_es_mejor else (t["Modelo B"] < t["Modelo A"])
        empate = np.isclose(t["Modelo B"], t["Modelo A"])
        filas.append(
            {
                "metrica": m,
                "A_media": t["Modelo A"].mean(), "A_sd": t["Modelo A"].std(),
                "B_media": t["Modelo B"].mean(), "B_sd": t["Modelo B"].std(),
                "B_mejor_pct": float((mejor & ~empate).mean()),
                "A_p10": t["Modelo A"].quantile(0.1), "A_p90": t["Modelo A"].quantile(0.9),
                "B_p10": t["Modelo B"].quantile(0.1), "B_p90": t["Modelo B"].quantile(0.9),
            }
        )
    return pd.DataFrame(filas).set_index("metrica")


def entrenar_completo(df: pd.DataFrame) -> dict:
    """Entrena A y B con TODOS los datos (para el simulador del stand)."""
    modelos = {}
    for nombre, vars_ in (("Modelo A", C.VARIABLES_MODELO_A), ("Modelo B", C.VARIABLES_MODELO_B)):
        m = RandomForestClassifier(**C.HIPERPARAMETROS)
        m.fit(df[vars_], df[C.COL_OBJETIVO])
        modelos[nombre] = (m, list(vars_))
    return modelos


def predecir_persona(modelos: dict, persona: dict) -> dict:
    """Probabilidad de ajuste según cada modelo para una persona."""
    fila = pd.DataFrame([persona])
    return {n: float(m.predict_proba(fila[v])[0, 1]) for n, (m, v) in modelos.items()}
