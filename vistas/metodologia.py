import streamlit as st

from equifit import ui

st.markdown("# Metodología y equipo")

st.markdown("### Pregunta de investigación")
st.markdown(
    "> ¿Reduce la brecha de error entre mujeres y hombres entrenar el modelo predictivo de ajuste del "
    "cinturón con variables antropométricas femeninas (longitud de torso, altura de hombro y busto), "
    "frente a entrenarlo únicamente con el dataset basado en el estándar masculino?"
)
st.caption(
    "Pregunta aplicada/experimental. La descriptiva (frecuencia de molestias por grupo) y la correlacional "
    "(distancia al estándar vs. incomodidad) sirven como sustento y se exploran en «Datos y preguntas»."
)

st.markdown("### Diseño del experimento")
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown("**Variable independiente**")
        st.markdown("Qué datos ve el modelo: Versión A (estatura y peso) o Versión B (+ torso, hombro sentado y busto).")
with c2:
    with st.container(border=True):
        st.markdown("**Variables dependientes**")
        st.markdown("Exactitud global (accuracy), tasa de error por grupo, falso «seguro» y métricas de equidad.")
with c3:
    with st.container(border=True):
        st.markdown("**Controles**")
        st.markdown("Mismo algoritmo, mismos hiperparámetros, misma partición de entrenamiento y prueba.")

st.markdown("### Recolección (UPY, 2–5 de noviembre de 2026)")
st.markdown(
    """
**Población:** estudiantes y personal de la Universidad Politécnica de Yucatán.
**Muestra:** no probabilística por conveniencia; meta de al menos 30 mujeres y 30 hombres.
**Unidad de observación:** cada participante con el cinturón de un mismo vehículo, en las mismas condiciones
(limpio, con aire acondicionado y posición estándar del asiento).

| Instrumento | Qué registra |
|---|---|
| Encuesta (Google Forms) | Datos sociodemográficos, comodidad y ajuste en escala Likert 1–5, historial de conducción |
| Medición antropométrica | Estatura, altura de hombro sentado, longitud de torso, alcance de brazo y contorno de pecho, con cinta métrica y hoja de registro |
| Prueba de uso (lista de cotejo) | ¿Corta en el cuello? ¿El anclaje se adapta a la altura del hombro? ¿Presiona sobre el busto/pecho? |
"""
)

st.markdown("### Procedimiento")
st.markdown(
    """
1. Prueba piloto con 5 personas para afinar preguntas e instrucciones de medición.
2. Aplicación de encuesta, medición y prueba de uso en sesiones.
3. Registro con folios anónimos (P01, P02…).
4. Limpieza en pandas, codificación y construcción de los datasets A y B.
5. Entrenamiento de ambos modelos, cálculo de métricas y publicación en este dashboard.
"""
)

st.markdown("### Ética")
st.markdown(
    """
- Consentimiento informado firmado y participación 100 % voluntaria.
- Sin nombres, correos ni datos personales: solo folio.
- Solo medidas antropométricas externas; no se piden datos de salud ni información íntima.
- El sistema se usa para auditar datos y promover seguridad vial inclusiva, nunca para clasificar personas.
"""
)

st.markdown("### Privacidad y seguridad de los datos")
st.markdown(
    """
- **Minimización:** solo se registran las medidas que usa el modelo; nada de nombres, correos, matrícula ni datos de salud.
- **Seudonimización:** cada persona es un folio. La relación folio–nombre (necesaria solo para atender una solicitud de baja)
  se guarda aparte, en papel bajo llave o en un archivo cifrado, y se destruye al cerrar el proyecto.
- **Dónde viven los datos:** en una carpeta institucional con acceso solo para el equipo y verificación en dos pasos.
  Nunca en WhatsApp, correos personales, memorias USB sin cifrar ni en este repositorio.
- **Demo pública = solo datos simulados.** La carga de archivos está desactivada en la versión en línea; los datos reales
  se analizan en la copia local del equipo y solo se publican resultados agregados por grupo.
- **Derechos de las personas:** cualquier participante puede pedir ver, corregir o retirar sus datos con su folio.
"""
)

st.markdown("### Limitaciones")
st.markdown(
    """
- Muestra pequeña y no probabilística: los resultados no se generalizan a toda la población.
- La comodidad es subjetiva; por eso se combina con medición y lista de cotejo.
- Con 30 + 30 participantes, la prueba de cada partición tiene ~9 mujeres; por eso EquiFit repite el
  experimento en varias particiones y reporta promedio y variación.
- La demo pública usa datos simulados hasta tener los datos de campo; no anticipa resultados.
"""
)

st.markdown("### Más allá del cinturón")
st.markdown(
    "El método es el mismo para cualquier producto: medir a quienes lo usan, comparar un modelo entrenado "
    "con el «estándar» contra uno que incluye a todas las personas, y auditar dónde falla cada uno. "
    "Asientos, equipo de protección, herramientas, dispositivos médicos o tallas de uniformes son "
    "candidatos naturales."
)

st.markdown("### Equipo")
st.markdown(
    """
**Equipo 2 · TSU en Ciencia de Datos 3°B · Universidad Politécnica de Yucatán**
Ivanna Núñez Hernández · Luisa Fernanda Trochez Rodríguez · Camila Berenice Borrego Ayala ·
Jesse Velázquez Rojas · Armando Karin Molina Marrufo

Docente: Omar Adrián Ortiz Monzón · Asignatura: Proyecto Integrador I
"""
)
st.link_button("Código fuente en GitHub", ui.REPO_URL)
