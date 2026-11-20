"""Convierte la exportación de la encuesta en línea de Google Forms al esquema de EquiFit.

La encuesta (instrumentos/EquiFit_encuesta_autorreporte.gs) usa títulos fijos. Aquí
se reconocen por su texto, sin importar mayúsculas, acentos ni espacios, y se
traducen a las columnas que usa la app. Las respuestas de la lista de cotejo
(Sí / A veces / No) se convierten a 1 / 0.
"""

from __future__ import annotations

import unicodedata

import pandas as pd


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(t.lower().replace("¿", "").replace("?", "").split())


# Título de la pregunta en Google Forms -> columna de EquiFit
TITULOS = {
    "Género": "genero",
    "Estatura (cm)": "estatura_cm",
    "Peso (kg)": "peso_kg",
    "Sentado(a) en tu auto, ¿dónde queda la parte alta de tu hombro?": "hombro_vs_anclaje",
    "¿Cuál es tu talla de playera o blusa?": "talla_superior",
    "De largo, ¿cómo te quedan las camisas o blusas de tu talla?": "largo_camisas",
    "¿Qué tan cómodo te resulta el cinturón?": "likert_comodidad",
    "¿Qué tan bien se ajusta el cinturón a tu cuerpo?": "likert_ajuste",
    "¿La banda diagonal te roza o te corta el cuello?": "cuello_corta",
    "¿Logras que la banda quede sobre el centro de tu hombro?": "anclaje_adecuado",
    "¿La banda te presiona de forma incómoda sobre el pecho o el busto?": "presion_busto",
}
ACEPTA = "¿Aceptas participar en el estudio?"
_MAPA = {_norm(k): v for k, v in TITULOS.items()}

# Texto de cada opción (inicio, normalizado) -> valor ordinal de config.ESCALAS
OPCIONES = {
    "hombro_vs_anclaje": {"arriba": 1, "a la misma altura": 2, "un poco abajo": 3, "muy abajo": 4},
    "talla_superior": {"xs": 1, "s": 2, "m": 3, "l": 4, "xl": 5, "xxl": 6},
    "largo_camisas": {"cortas": 1, "bien": 2, "largas": 3},
}


def _ordinal(serie: pd.Series, opciones: dict) -> pd.Series:
    def uno(v):
        n = _norm(v)
        # la coincidencia más larga gana ("xl" antes que "x", "xxl" antes que "xl")
        for texto in sorted(opciones, key=len, reverse=True):
            if n == texto or n.startswith(texto + " "):
                return opciones[texto]
        return pd.NA
    return serie.map(uno)


def es_exportacion_forms(df: pd.DataFrame) -> bool:
    """True si el archivo trae los títulos de la encuesta en línea."""
    cols = {_norm(c) for c in df.columns}
    return sum(k in cols for k in _MAPA) >= 7


def _si_no(serie: pd.Series) -> pd.Series:
    """'Sí' / 'Sí, casi siempre' / 'A veces' -> 1;  'No...' -> 0."""
    s = serie.map(_norm)
    return s.map(lambda v: 0 if v.startswith("no") else (1 if v.startswith(("si", "a veces")) else pd.NA))


def desde_google_forms(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Devuelve (df con el esquema de EquiFit, avisos)."""
    avisos: list[str] = []
    df = df.copy()
    normal = {c: _norm(c) for c in df.columns}

    col_acepta = next((c for c, n in normal.items() if n == _norm(ACEPTA)), None)
    if col_acepta is not None:
        acepto = df[col_acepta].map(_norm).str.startswith("si")
        rechazos = int((~acepto).sum())
        if rechazos:
            avisos.append(f"Se excluyeron {rechazos} respuestas sin consentimiento o de menores de edad.")
        df = df[acepto]

    salida = pd.DataFrame(index=df.index)
    for col, n in normal.items():
        if n in _MAPA:
            salida[_MAPA[n]] = df[col]

    for c in ("cuello_corta", "presion_busto", "anclaje_adecuado"):
        if c in salida:
            salida[c] = _si_no(salida[c])
    for c, opciones in OPCIONES.items():
        if c in salida:
            salida[c] = _ordinal(salida[c], opciones)
    for c in ("estatura_cm", "peso_kg"):
        if c in salida:  # acepta coma decimal: "45,5"
            salida[c] = pd.to_numeric(salida[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")

    salida = salida.reset_index(drop=True)
    salida.insert(0, "folio", [f"R{i:03d}" for i in range(1, len(salida) + 1)])
    avisos.insert(0, f"Archivo reconocido como exportación de la encuesta en línea ({len(salida)} respuestas).")
    return salida, avisos
