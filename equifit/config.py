"""Configuración central de EquiFit.

Todo lo que define el experimento vive aquí: columnas del dataset, variables
de cada modelo, hiperparámetros compartidos y reglas de la variable objetivo.
Cambiar algo aquí cambia el experimento completo de forma consistente.
"""

# ---------------------------------------------------------------------------
# Esquema del dataset (coincide con los instrumentos del protocolo)
# ---------------------------------------------------------------------------
COL_FOLIO = "folio"
COL_GENERO = "genero"

# Instrumento 2: medición antropométrica (cm / kg)
ANTROPOMETRIA = {
    "estatura_cm": "Estatura",
    "peso_kg": "Peso",
    "altura_hombro_sentado_cm": "Altura de hombro sentado",
    "longitud_torso_cm": "Longitud de torso",
    "contorno_pecho_cm": "Contorno de pecho / busto",
    "alcance_brazo_cm": "Alcance de brazo",
}

# Instrumento 1: encuesta (escala Likert 1–5)
LIKERT = {
    "likert_comodidad": "Comodidad del cinturón (1–5)",
    "likert_ajuste": "Ajuste del cinturón (1–5)",
}

# Instrumento 3: lista de cotejo (sí = 1 / no = 0)
COTEJO = {
    "cuello_corta": "¿El cinturón corta directo en el cuello?",
    "anclaje_adecuado": "¿El anclaje permite ajuste adecuado a la altura del hombro?",
    "presion_busto": "¿El cinturón presiona de forma incómoda sobre busto/pecho?",
}

COL_OBJETIVO = "ajusta"  # 1 = ajusta bien / seguro, 0 = no ajusta / molestia

COLUMNAS_REQUERIDAS = (
    [COL_GENERO] + list(ANTROPOMETRIA) + list(LIKERT) + list(COTEJO)
)

GRUPOS = ["Mujer", "Hombre"]

# ---------------------------------------------------------------------------
# Variable independiente: qué ve cada modelo
# ---------------------------------------------------------------------------
# Versión A — dataset "estándar": solo métricas generales, sin proporciones.
VARIABLES_MODELO_A = ["estatura_cm", "peso_kg"]

# Versión B — dataset inclusivo: agrega torso, hombro sentado y busto.
VARIABLES_MODELO_B = VARIABLES_MODELO_A + [
    "altura_hombro_sentado_cm",
    "longitud_torso_cm",
    "contorno_pecho_cm",
]

# ---------------------------------------------------------------------------
# Controles: lo que debe ser idéntico entre A y B
# ---------------------------------------------------------------------------
SEMILLA = 42
PROPORCION_PRUEBA = 0.30
HIPERPARAMETROS = {
    "n_estimators": 150,
    "max_depth": 6,
    "min_samples_leaf": 4,
    "random_state": SEMILLA,
    "n_jobs": -1,
}

# ---------------------------------------------------------------------------
# Regla de la variable objetivo (definida ANTES de recolectar)
# ---------------------------------------------------------------------------
# Ajusta (1) si el promedio Likert es 4–5 y la lista de cotejo no marca
# ninguna falla crítica (cuello o busto). En cualquier otro caso: 0.
UMBRAL_LIKERT = 4.0

# Referencia del "estándar masculino" para la pregunta correlacional.
# Se calcula a partir del grupo Hombre de los datos cargados (percentil 50).
VARIABLES_DISTANCIA = ["estatura_cm", "altura_hombro_sentado_cm", "longitud_torso_cm"]

# ---------------------------------------------------------------------------
# Identidad visual (paleta validada para daltonismo)
# ---------------------------------------------------------------------------
COLOR_MODELO = {"Modelo A": "#eb6834", "Modelo B": "#2a78d6"}
COLOR_GRUPO = {"Mujer": "#6250d6", "Hombre": "#008300"}
