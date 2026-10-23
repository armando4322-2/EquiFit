import os
from functools import reduce
from pathlib import Path

import pandas as pd
import streamlit as st

from equifit import config as C
from equifit import data as D

st.markdown("# Cargar datos de campo")
st.markdown(
    "Sube los datos reales y toda la demo (auditoría, preguntas y simulador) se recalcula con ellos. "
    "Puedes subir **un archivo combinado** o **los tres instrumentos por separado** "
    "(encuesta de Google Forms, hoja antropométrica y lista de cotejo): se unen por la columna `folio`."
)

with st.expander("Columnas que se esperan", expanded=False):
    filas = (
        [("folio", "Identificador anónimo (P001, P002…)", "Todos los instrumentos")]
        + [("genero", "Mujer / Hombre (también acepta M, F, H, femenino, masculino)", "Encuesta")]
        + [(k, v, "Medición antropométrica") for k, v in C.ANTROPOMETRIA.items()]
        + [(k, v, "Encuesta") for k, v in C.LIKERT.items()]
        + [(k, v + " (1 = sí, 0 = no)", "Lista de cotejo") for k, v in C.COTEJO.items()]
    )
    st.dataframe(pd.DataFrame(filas, columns=["Columna", "Qué es", "Instrumento"]),
                 hide_index=True, width="stretch")
    st.caption(
        f"La variable objetivo «{C.COL_OBJETIVO}» se calcula sola: 1 si el promedio Likert es ≥ "
        f"{C.UMBRAL_LIKERT:g} y no hay falla en cuello ni busto; 0 en otro caso."
    )

st.download_button(
    "Descargar plantilla CSV",
    D.plantilla().to_csv(index=False).encode("utf-8-sig"),
    file_name="equifit_plantilla.csv",
    mime="text/csv",
    icon=":material/download:",
)



def es_copia_local() -> bool:
    """La carga de archivos solo se habilita en la copia local del equipo.

    En la demo pública (Streamlit Cloud) los datos se procesarían en servidores
    de terceros fuera de México; por política del proyecto, ahí solo se usan
    datos simulados. EQUIFIT_PERMITIR_CARGA=1 la habilita a propósito.
    """
    if os.environ.get("EQUIFIT_PERMITIR_CARGA") == "1":
        return True
    try:
        host = (st.context.headers.get("Host") or "").split(":")[0].lower()
    except Exception:
        return False
    return host in ("localhost", "127.0.0.1", "::1", "[::1]")


def leer(f) -> pd.DataFrame:
    if f.name.lower().endswith(".xlsx"):
        return pd.read_excel(f)
    return D.leer_csv(f)


class _Ejemplo:
    """Archivo de ejemplo con datos simulados, para mostrar la carga en la demo pública."""
    name = "demo_simulado.csv"

    def read(self):
        return open(RUTA_EJEMPLO, "rb").read()


RUTA_EJEMPLO = Path(__file__).resolve().parents[1] / "datos" / "demo_simulado.csv"

if es_copia_local():
    archivos = st.file_uploader(
        "Archivos CSV o Excel (máximo 5 MB)", type=["csv", "xlsx"], accept_multiple_files=True
    )
else:
    st.info(
        "**En la demo pública no se suben datos de participantes.** Este servidor está fuera de México y "
        "es compartido, así que por política del proyecto aquí solo se usan datos simulados. Los datos reales "
        "se cargan en la copia local del equipo (`streamlit run app.py` en una computadora del equipo), "
        "donde nunca salen del equipo. Puedes probar cómo funciona la carga con el archivo de ejemplo.",
        icon=":material/lock:",
    )
    archivos = [_Ejemplo()] if st.button("Probar la carga con el archivo de ejemplo") or st.session_state.get("_ejemplo") else []
    if archivos:
        st.session_state["_ejemplo"] = True

if archivos:
    try:
        tablas = [leer(f) for f in archivos]
        for t in tablas:
            t.columns = [c.strip().lower() for c in t.columns]
        if len(tablas) > 1:
            if not all("folio" in t.columns for t in tablas):
                raise D.ErrorDatos("Para unir varios archivos, todos deben tener la columna «folio».")
            crudo = reduce(lambda a, b: a.merge(b, on="folio", how="inner", suffixes=("", "_dup")), tablas)
            crudo = crudo[[c for c in crudo.columns if not c.endswith("_dup")]]
            st.caption(f"Se unieron {len(tablas)} archivos por folio: {len(crudo)} participantes en común.")
        else:
            crudo = tablas[0]
        limpio, avisos = D.validar(crudo)
    except D.ErrorDatos as e:
        st.error(str(e))
    except Exception as e:  # archivo ilegible
        st.error(f"No se pudo leer el archivo: {e}")
    else:
        for a in avisos:
            st.warning(a)
        n_m = int((limpio[C.COL_GENERO] == "Mujer").sum())
        n_h = int((limpio[C.COL_GENERO] == "Hombre").sum())
        st.success(f"Datos válidos: {len(limpio)} participantes ({n_m} mujeres, {n_h} hombres).")
        st.dataframe(limpio.head(20), hide_index=True, width="stretch")
        if st.button("Usar estos datos en toda la demo", type="primary"):
            st.session_state["df_real"] = limpio
            st.session_state["usar_reales"] = True
            st.switch_page("vistas/auditoria.py")

if st.session_state.get("df_real") is not None:
    st.divider()
    st.info("Hay datos reales cargados en esta sesión. Puedes alternar con los simulados desde la barra lateral.")
    if st.button("Quitar datos reales"):
        st.session_state["df_real"] = None
        st.session_state["usar_reales"] = False
        st.rerun()

st.caption("Los archivos se procesan en memoria durante esta sesión y no se escriben en disco ni en el repositorio.")
