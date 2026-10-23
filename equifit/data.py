"""Datos de EquiFit: simulación para la demo, validación y carga de datos reales.

IMPORTANTE: los datos simulados NO son resultados del proyecto. Sirven para que
el sistema de auditoría funcione antes del trabajo de campo (2–5 nov 2026).
Las distribuciones son aproximaciones de referencia para población adulta
mexicana; la geometría del cinturón es un supuesto de diseño documentado
abajo. Cuando el equipo tenga sus datos reales, se cargan con el mismo esquema
y todo el análisis se recalcula.
"""

from __future__ import annotations

import io

import numpy as np
import pandas as pd

from . import config as C


# ---------------------------------------------------------------------------
# Supuestos de la simulación (editables y visibles en la app)
# ---------------------------------------------------------------------------
SUPUESTOS = {
    # Medias y desviaciones (cm, kg) por grupo
    "estatura": {"Mujer": (157.5, 6.0), "Hombre": (170.5, 7.0)},
    "peso": {"Mujer": (64.0, 10.0), "Hombre": (76.0, 11.0)},
    "pecho": {"Mujer": (95.0, 9.0), "Hombre": (98.0, 8.0)},
    # El anclaje del cinturón está pensado para un hombre promedio:
    # altura de hombro sentado ≈ 57.5 cm, con ±4.5 cm de regulación.
    "anclaje_cm": 57.5,
    "regulacion_cm": 4.5,
}


def _sigmoide(x):
    return 1.0 / (1.0 + np.exp(-x))


def simular(n: int = 300, prop_mujeres: float = 0.5, semilla: int = C.SEMILLA) -> pd.DataFrame:
    """Genera un dataset con el mismo esquema que los instrumentos reales."""
    rng = np.random.default_rng(semilla)
    n_m = int(round(n * prop_mujeres))
    genero = np.array(["Mujer"] * n_m + ["Hombre"] * (n - n_m))
    rng.shuffle(genero)
    es_m = genero == "Mujer"

    def normal(clave):
        mu = np.where(es_m, SUPUESTOS[clave]["Mujer"][0], SUPUESTOS[clave]["Hombre"][0])
        sd = np.where(es_m, SUPUESTOS[clave]["Mujer"][1], SUPUESTOS[clave]["Hombre"][1])
        return rng.normal(mu, sd)

    estatura = normal("estatura")
    # El peso se asocia con la estatura (IMC razonable) más variación individual
    peso = normal("peso") + 0.45 * (estatura - np.where(es_m, 157.5, 170.5))
    # Proporciones: a igual estatura, el hombro sentado y el torso varían
    # entre personas; por eso la estatura sola no basta para predecir el ajuste.
    hombro = 0.345 * estatura + rng.normal(0, 2.6, n) + np.where(es_m, -0.4, 0.6)
    torso = 0.29 * estatura + rng.normal(0, 1.8, n) + np.where(es_m, -0.3, 0.3)
    pecho = normal("pecho") + 0.25 * (peso - np.where(es_m, 64, 76))
    alcance = 0.44 * estatura + rng.normal(0, 2.5, n)

    # --- Geometría del cinturón (supuesto de diseño) -----------------------
    anclaje, reg = SUPUESTOS["anclaje_cm"], SUPUESTOS["regulacion_cm"]
    desfase = hombro - anclaje  # negativo = hombro por debajo del anclaje
    # Si el hombro queda muy por debajo del anclaje, la banda cruza el cuello
    p_cuello = _sigmoide((-desfase - reg) / 1.1)
    cuello = rng.random(n) < p_cuello
    # El anclaje regulable cubre ±reg cm alrededor del diseño
    anclaje_ok = np.abs(desfase) <= reg + rng.normal(0, 0.6, n)
    # Presión en busto: depende del contorno, mucho más marcada en mujeres
    p_busto = np.where(
        es_m,
        _sigmoide((pecho - 103) / 3.5),
        _sigmoide((pecho - 117) / 3.5),
    )
    busto = rng.random(n) < p_busto
    # Torso corto: la banda diagonal queda alta (efecto menor)
    torso_corto = torso < 45

    # --- Encuesta Likert: percepción con ruido subjetivo ---------------------
    base = 4.7 - 1.5 * cuello - 0.9 * (~anclaje_ok) - 1.4 * busto - 0.5 * torso_corto
    comodidad = np.clip(np.rint(base + rng.normal(0, 0.55, n)), 1, 5).astype(int)
    ajuste = np.clip(np.rint(base + 0.1 + rng.normal(0, 0.55, n)), 1, 5).astype(int)

    df = pd.DataFrame(
        {
            C.COL_FOLIO: [f"P{i:03d}" for i in range(1, n + 1)],
            C.COL_GENERO: genero,
            "estatura_cm": estatura.round(1),
            "peso_kg": peso.round(1),
            "altura_hombro_sentado_cm": hombro.round(1),
            "longitud_torso_cm": torso.round(1),
            "contorno_pecho_cm": pecho.round(1),
            "alcance_brazo_cm": alcance.round(1),
            "likert_comodidad": comodidad,
            "likert_ajuste": ajuste,
            "cuello_corta": cuello.astype(int),
            "anclaje_adecuado": anclaje_ok.astype(int),
            "presion_busto": busto.astype(int),
        }
    )
    return derivar_objetivo(df)


def derivar_objetivo(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica la regla del protocolo para construir la variable objetivo."""
    df = df.copy()
    df["likert_promedio"] = df[list(C.LIKERT)].mean(axis=1)
    df[C.COL_OBJETIVO] = (
        (df["likert_promedio"] >= C.UMBRAL_LIKERT)
        & (df["cuello_corta"] == 0)
        & (df["presion_busto"] == 0)
    ).astype(int)
    return df


# ---------------------------------------------------------------------------
# Carga y validación de datos reales
# ---------------------------------------------------------------------------
class ErrorDatos(ValueError):
    """Error de validación con un mensaje claro para el equipo."""


_SINONIMOS_GENERO = {
    "mujer": "Mujer", "m": "Mujer", "f": "Mujer", "femenino": "Mujer", "female": "Mujer",
    "hombre": "Hombre", "h": "Hombre", "masculino": "Hombre", "male": "Hombre",
}


def validar(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Valida y limpia un dataset cargado. Devuelve (df_limpio, avisos)."""
    avisos: list[str] = []
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    faltan = [c for c in C.COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltan:
        raise ErrorDatos(
            "Faltan columnas en el archivo: " + ", ".join(faltan)
            + ". Descarga la plantilla y copia tus datos en esas columnas."
        )

    if C.COL_FOLIO not in df.columns:
        df[C.COL_FOLIO] = [f"P{i:03d}" for i in range(1, len(df) + 1)]
        avisos.append("No había columna «folio»; se asignaron folios P001, P002…")

    g = df[C.COL_GENERO].astype(str).str.strip().str.lower()
    df[C.COL_GENERO] = g.map(_SINONIMOS_GENERO).fillna(df[C.COL_GENERO].astype(str).str.strip())
    otros = df.loc[~df[C.COL_GENERO].isin(C.GRUPOS), C.COL_GENERO].unique()
    if len(otros):
        avisos.append(
            f"Se encontraron otros valores de género ({', '.join(map(str, otros))}). "
            "Se conservan en los datos, pero la comparación de equidad se calcula entre Mujer y Hombre."
        )

    numericas = list(C.ANTROPOMETRIA) + list(C.LIKERT) + list(C.COTEJO)
    for c in numericas:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    antes = len(df)
    df = df.dropna(subset=numericas)
    if len(df) < antes:
        avisos.append(f"Se descartaron {antes - len(df)} filas con valores vacíos o no numéricos.")

    fuera = ~df[list(C.LIKERT)].isin([1, 2, 3, 4, 5]).all(axis=1)
    if fuera.any():
        avisos.append(f"{int(fuera.sum())} filas tenían Likert fuera de 1–5 y se descartaron.")
        df = df[~fuera]
    bin_mal = ~df[list(C.COTEJO)].isin([0, 1]).all(axis=1)
    if bin_mal.any():
        avisos.append(f"{int(bin_mal.sum())} filas tenían la lista de cotejo distinta de 0/1 y se descartaron.")
        df = df[~bin_mal]

    rangos = {"estatura_cm": (120, 220), "peso_kg": (30, 200),
              "altura_hombro_sentado_cm": (35, 80), "longitud_torso_cm": (30, 75),
              "contorno_pecho_cm": (60, 160), "alcance_brazo_cm": (50, 110)}
    for c, (lo, hi) in rangos.items():
        raro = ~df[c].between(lo, hi)
        if raro.any():
            avisos.append(f"{int(raro.sum())} valores de «{c}» fuera de {lo}–{hi}; revisa la hoja de registro.")

    por_grupo = df[C.COL_GENERO].value_counts()
    for gname in C.GRUPOS:
        if por_grupo.get(gname, 0) < 10:
            raise ErrorDatos(
                f"Se necesitan al menos 10 registros de «{gname}» para comparar grupos "
                f"(hay {por_grupo.get(gname, 0)})."
            )

    return derivar_objetivo(df.reset_index(drop=True)), avisos


def leer_csv(archivo) -> pd.DataFrame:
    """Lee CSV con coma o punto y coma (Excel en español usa ';')."""
    contenido = archivo.read() if hasattr(archivo, "read") else open(archivo, "rb").read()
    texto = contenido.decode("utf-8-sig", errors="replace")
    sep = ";" if texto.splitlines()[0].count(";") > texto.splitlines()[0].count(",") else ","
    return pd.read_csv(io.StringIO(texto), sep=sep)


def plantilla() -> pd.DataFrame:
    """Plantilla vacía con dos filas de ejemplo para el registro de campo."""
    ejemplo = simular(n=2, semilla=7)
    return ejemplo[[C.COL_FOLIO] + C.COLUMNAS_REQUERIDAS]
