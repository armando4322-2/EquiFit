# Instrumentos del estudio (Google Forms)

> **Versión vigente: encuesta en línea con autorreporte** (`EquiFit_encuesta_autorreporte.gs`).
> Cada persona responde sobre el vehículo en el que viaja con más frecuencia y se toma sus propias
> medidas con cinta métrica. El consentimiento va al inicio del mismo formulario y la encuesta es
> anónima: no pide nombre, correo ni folio. Con solo contestarla se obtienen todas las columnas que
> usa EquiFit.
>
> **Para usarla:** crea el formulario igual que se explica abajo, pero con la función
> `crearEncuestaEquiFit`. Usa el encabezado `encabezado_encuesta.png`.
>
> **Para analizar las respuestas:** en la hoja de respuestas, Archivo → Descargar → CSV, y súbelo
> en «Cargar datos» de la copia local de EquiFit. La app reconoce el archivo de Google Forms y lo
> convierte sola: descarta a quien no dio su consentimiento, pasa «Sí / A veces / No» a 1 y 0, y
> acepta decimales con coma. **No cambies el texto de las preguntas**, porque la app las reconoce
> por su título.
>
> Los formularios de la versión 1 (`EquiFit_formularios.gs`: consentimiento con nombre y encuesta
> con folio) describen una prueba en persona con un vehículo del equipo. No los usen con la
> encuesta en línea, porque su texto ya no corresponde a lo que se hace.

## Versión 1 (prueba en persona)

Los dos primeros entregables del plan de trabajo:

| Entregable | Archivo |
|---|---|
| Diseño de la Carta de Consentimiento Informado | Formulario «EquiFit · Consentimiento informado» |
| Diseño del Instrumento Digital (Google Forms) | Formulario «EquiFit · Encuesta del estudio» |

`EquiFit_formularios.gs` crea los dos formularios completos con un solo clic, cada uno con su propia hoja de respuestas, dentro de una carpeta nueva en tu Google Drive.

## 1. Crear los formularios (5 minutos)

1. Entra a [script.google.com](https://script.google.com) con la cuenta **institucional** (@upy.edu.mx).
2. Presiona **Nuevo proyecto**, borra el código que trae y pega todo `EquiFit_formularios.gs`.
3. Guarda (ícono de disquete). En la barra de arriba elige la función **crearFormulariosEquiFit** y presiona **Ejecutar**.
4. Google pide permisos para Formularios, Drive y Hojas de cálculo: **Revisar permisos → tu cuenta → Permitir**. Si aparece «Google no verificó esta app», entra a **Configuración avanzada → Ir a (proyecto)**; es tu propio script.
5. Al terminar, abre **Registro de ejecución**: ahí están los enlaces para editar y para compartir cada formulario.

En tu Drive aparece la carpeta **EquiFit — Instrumentos** con los 2 formularios y sus 2 hojas de respuestas.

## 2. Aplicar la marca (2 minutos por formulario)

Google no permite cambiar el tema desde un script, así que esta parte es manual. En cada formulario, presiona el ícono de **paleta (Personalizar tema)**, arriba a la derecha:

| Opción | Qué elegir |
|---|---|
| Encabezado | **Elegir imagen → Subir**: `encabezado_consentimiento.png` o `encabezado_encuesta.png` |
| Color | **+** (color personalizado) → `#5B3A95` |
| Fondo | El tono más claro que ofrezca |
| Estilo de texto | La fuente sans serif más parecida a Archivo; si no hay una parecida, deja la predeterminada |

## 3. Revisar antes de compartir

- Arriba a la derecha, si el botón dice **Publicar**, presiónalo. Desde 2025 los formularios creados por script pueden quedar sin publicar.
- **Configuración → Respuestas → Recopilar direcciones de correo electrónico: No recopilar.** El script ya lo deja así; confírmalo.
- Contesta cada formulario una vez como prueba y luego borra esas respuestas de prueba.

## Cómo está pensado

**Consentimiento.** Pregunta primero si la persona es mayor de edad y si acepta participar. Solo si acepta se le piden nombre, folio y correo (este último es opcional). Termina con cuatro confirmaciones obligatorias. Quien no acepta, o es menor de edad, termina sin dar ningún dato.

**Encuesta.** Solo pide el folio, nunca el nombre. Tiene tres secciones: datos generales (con edad en rangos, no exacta), experiencia habitual con el cinturón y la prueba con el vehículo. La sección C contiene las dos preguntas Likert que alimentan la variable objetivo de EquiFit. Se contesta **justo después** de la prueba de uso, sobre ese mismo cinturón.

**Privacidad.** Nombres y respuestas quedan en hojas separadas; lo único que las une es el folio. La hoja de consentimiento se comparte solo con el equipo y el docente.

**Neutralidad.** Los formularios describen el estudio como «ajuste del cinturón de seguridad» y no adelantan la hipótesis de género, para no sesgar las respuestas.

## El día de la recolección

1. Prepara folios impresos (P001, P002…) y entrega uno a cada participante.
2. Consentimiento → medición (hoja antropométrica con el mismo folio) → prueba de uso (lista de cotejo) → encuesta.
3. Para cargar los datos en EquiFit, renombra estas columnas de la hoja de la encuesta:

| Título en Google Forms | Columna en EquiFit |
|---|---|
| Folio | `folio` |
| Género | `genero` |
| ¿Qué tan cómodo te resultó el cinturón? | `likert_comodidad` |
| ¿Qué tan bien se ajustó el cinturón a tu cuerpo? | `likert_ajuste` |
