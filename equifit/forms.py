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
    "Altura de hombro sentado (cm)": "altura_hombro_sentado_cm",
    "Longitud de torso (cm)": "longitud_torso_cm",
    "Contorno de pecho o busto (cm)": "contorno_pecho_cm",
    "Alcance de brazo (cm)": "alcance_brazo_cm",
    "¿Qué tan cómodo te resulta el cinturón?": "likert_comodidad",
    "¿Qué tan bien se ajusta el cinturón a tu cuerpo?": "likert_ajuste",
    "¿La banda diagonal te roza o te corta el cuello?": "cuello_corta",
    "¿Logras que la banda quede sobre el centro de tu hombro?": "anclaje_adecuado",
    "¿La banda te presiona de forma incómoda sobre el pecho o el busto?": "presion_busto",
}
ACEPTA = "¿Aceptas participar en el estudio?"
COMO_MIDIO = "¿Cómo obtuviste tus medidas?"
_MAPA = {_norm(k): v for k, v in TITULOS.items()}


def es_exportacion_forms(df: pd.DataFrame) -> bool:
    """True si el archivo trae los títulos de la encuesta en línea."""
    cols = {_norm(c) for c in df.columns}
    return sum(k in cols for k in _MAPA) >= 8


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

    col_como = next((c for c, n in normal.items() if n == _norm(COMO_MIDIO)), None)

    salida = pd.DataFrame(index=df.index)
    for col, n in normal.items():
        if n in _MAPA:
            salida[_MAPA[n]] = df[col]
    if col_como is not None:
        salida["como_midio"] = df[col_como]
        estimadas = int(df[col_como].map(_norm).str.startswith("las estime").sum())
        if estimadas:
            avisos.append(
                f"{estimadas} {'persona estimó' if estimadas == 1 else 'personas estimaron'} sus medidas "
                "sin medirlas. Se incluyen, pero conviene "
                "revisar si cambian los resultados al excluirlas (columna «como_midio»)."
            )

    for c in ("cuello_corta", "presion_busto", "anclaje_adecuado"):
        if c in salida:
            salida[c] = _si_no(salida[c])
    for c in ("estatura_cm", "peso_kg", "altura_hombro_sentado_cm", "longitud_torso_cm",
              "contorno_pecho_cm", "alcance_brazo_cm"):
        if c in salida:  # acepta coma decimal: "45,5"
            salida[c] = pd.to_numeric(salida[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")

    salida = salida.reset_index(drop=True)
    salida.insert(0, "folio", [f"R{i:03d}" for i in range(1, len(salida) + 1)])
    avisos.insert(0, f"Archivo reconocido como exportación de la encuesta en línea ({len(salida)} respuestas).")
    return salida, avisos
