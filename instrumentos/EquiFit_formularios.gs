/**
 * EquiFit — Crea los dos formularios del estudio en Google Forms.
 *
 *   1. Consentimiento informado (identifica a la persona: nombre y correo opcional)
 *   2. Instrumento digital: encuesta del estudio (solo folio, sin datos personales)
 *
 * Cada formulario guarda sus respuestas en una hoja de cálculo SEPARADA, dentro de
 * una carpeta nueva "EquiFit — Instrumentos". Así los nombres nunca quedan junto a
 * las respuestas: lo único que une ambos archivos es el folio.
 *
 * CÓMO USARLO
 *   1. Entra a https://script.google.com con la cuenta institucional (@upy.edu.mx).
 *   2. "Nuevo proyecto", borra lo que trae y pega este archivo completo.
 *   3. Arriba elige la función crearFormulariosEquiFit y presiona "Ejecutar".
 *   4. Acepta los permisos (Google pide acceso a Formularios, Drive y Hojas de cálculo).
 *   5. Abre "Registro de ejecución": ahí salen los enlaces para editar y para compartir.
 *
 * Proyecto Integrador I · TSU en Ciencia de Datos · Universidad Politécnica de Yucatán
 */

const CONTACTO = '2509202@upy.edu.mx';
const NOMBRE_ESTUDIO = 'Estudio sobre el ajuste del cinturón de seguridad';
const PATRON_FOLIO = '^P\\d{3}$';
const AYUDA_FOLIO = 'Escribe el folio que te dio el equipo: una P mayúscula y tres números. Ejemplo: P007';

function crearFormulariosEquiFit() {
  const carpeta = DriveApp.createFolder('EquiFit — Instrumentos');

  const consentimiento = crearConsentimiento_();
  const encuesta = crearEncuesta_();

  const hojaConsentimiento = conectarHoja_(consentimiento, 'EquiFit — Respuestas de consentimiento (CONFIDENCIAL)');
  const hojaEncuesta = conectarHoja_(encuesta, 'EquiFit — Respuestas de la encuesta');

  [consentimiento.getId(), encuesta.getId(), hojaConsentimiento.getId(), hojaEncuesta.getId()]
    .forEach(function (id) { DriveApp.getFileById(id).moveTo(carpeta); });

  Logger.log('Listo. Carpeta: ' + carpeta.getUrl());
  Logger.log('1) CONSENTIMIENTO');
  Logger.log('   Editar:     ' + consentimiento.getEditUrl());
  Logger.log('   Compartir:  ' + consentimiento.getPublishedUrl());
  Logger.log('2) ENCUESTA (instrumento digital)');
  Logger.log('   Editar:     ' + encuesta.getEditUrl());
  Logger.log('   Compartir:  ' + encuesta.getPublishedUrl());
  Logger.log('Falta: personalizar el tema de cada formulario (ver README de la carpeta instrumentos).');
}

/* ------------------------------------------------------------------ */
/* 1. CONSENTIMIENTO INFORMADO                                         */
/* ------------------------------------------------------------------ */
function crearConsentimiento_() {
  const form = FormApp.create('EquiFit · Consentimiento informado');
  configurar_(form,
    'Gracias por tu interés. Antes de participar, lee esta información con calma.\n\n' +
    'QUÉ ES ESTE ESTUDIO\n' +
    NOMBRE_ESTUDIO + '. Es un proyecto académico de la asignatura Proyecto Integrador I ' +
    '(TSU en Ciencia de Datos, Universidad Politécnica de Yucatán).\n\n' +
    'QUÉ HARÍAS\n' +
    '• Te mediremos con cinta métrica, sobre la ropa: estatura, peso, altura de hombro sentado, ' +
    'longitud de torso, contorno de pecho y alcance de brazo.\n' +
    '• Te sentarás en un vehículo, te abrocharás el cinturón y observaremos cómo te queda.\n' +
    '• Contestarás una encuesta corta sobre tu experiencia.\n' +
    'Todo toma unos 10 minutos.\n\n' +
    'TU PARTICIPACIÓN\n' +
    '• Es voluntaria. Puedes no participar o retirarte en cualquier momento, sin dar razones y sin ' +
    'ninguna consecuencia, tampoco en calificaciones.\n' +
    '• Puedes pedir que te mida una persona de tu mismo género o tener un acompañante.\n' +
    '• Los riesgos son mínimos: el contacto de la cinta métrica sobre la ropa.\n' +
    '• No recibirás un beneficio directo; tu participación ayuda a diseñar productos más seguros.',
    'Gracias. Tu respuesta quedó registrada. Si quieres retirar tu participación o tus datos, ' +
    'escribe a ' + CONTACTO + ' indicando tu folio.');

  form.addPageBreakItem()
    .setTitle('Aviso de privacidad simplificado')
    .setHelpText(
      'Responsable: equipo del proyecto EquiFit, Universidad Politécnica de Yucatán.\n\n' +
      'Datos que recabamos: en este formulario, tu nombre y, si quieres, tu correo. En el estudio, ' +
      'medidas corporales, rango de edad, género y tus respuestas a la encuesta.\n\n' +
      'Para qué: solo para fines académicos de este estudio. Los análisis y resultados se publican ' +
      'únicamente de forma agregada (por grupo), nunca por persona.\n\n' +
      'Cómo los protegemos: tus datos del estudio se guardan con un folio, no con tu nombre. Este ' +
      'formulario se guarda aparte, con acceso solo para el equipo y el docente. No compartimos tus ' +
      'datos con terceros.\n\n' +
      'Cuánto tiempo: hasta el cierre del cuatrimestre; después se eliminan los datos que te ' +
      'identifican.\n\n' +
      'Tus derechos: puedes pedir acceso, corrección, cancelación u oposición al uso de tus datos ' +
      'escribiendo a ' + CONTACTO + '.');

  const edad = form.addMultipleChoiceItem()
    .setTitle('¿Tienes 18 años o más?')
    .setHelpText('Por ahora el estudio solo incluye a personas mayores de edad.')
    .setRequired(true);

  const decision = form.addPageBreakItem()
    .setTitle('Tu decisión');

  const acepto = form.addMultipleChoiceItem()
    .setTitle('¿Aceptas participar en el estudio?')
    .setHelpText('Si no aceptas, el formulario termina aquí y no te pediremos ningún dato.')
    .setRequired(true);

  const datos = form.addPageBreakItem()
    .setTitle('Tus datos')
    .setHelpText('Tu nombre solo sirve para documentar tu consentimiento y nunca se une a tus medidas.');

  form.addTextItem()
    .setTitle('Folio')
    .setHelpText(AYUDA_FOLIO)
    .setValidation(FormApp.createTextValidation()
      .requireTextMatchesPattern(PATRON_FOLIO).setHelpText(AYUDA_FOLIO).build())
    .setRequired(true);

  form.addTextItem()
    .setTitle('Nombre completo')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Correo electrónico (opcional)')
    .setHelpText('Solo si quieres recibir una copia de este consentimiento o que te avisemos de los resultados generales.')
    .setValidation(FormApp.createTextValidation()
      .requireTextIsEmail().setHelpText('Escribe un correo válido, por ejemplo nombre@upy.edu.mx').build())
    .setRequired(false);

  form.addPageBreakItem()
    .setTitle('Confirmación');

  form.addCheckboxItem()
    .setTitle('Confirmo que:')
    .setChoiceValues([
      'Leí la información del estudio y el aviso de privacidad.',
      'Pude hacer preguntas y me las respondieron.',
      'Sé que puedo retirarme en cualquier momento sin consecuencias.',
      'Acepto participar de forma libre y voluntaria.'
    ])
    .setValidation(FormApp.createCheckboxValidation()
      .requireSelectExactly(4).setHelpText('Marca las cuatro casillas para registrar tu consentimiento.').build())
    .setRequired(true);

  const menor = form.addPageBreakItem()
    .setTitle('Gracias por tu interés')
    .setHelpText('Por ahora el estudio solo incluye a personas de 18 años o más, así que no necesitas ' +
      'continuar. Presiona "Enviar" para terminar.');

  // Navegación por respuesta:
  //   ¿18 o más?  Sí -> Tu decisión        No -> Gracias por tu interés -> Enviar
  //   ¿Aceptas?   Sí -> Tus datos -> Confirmación -> Enviar     No -> Enviar
  edad.setChoices([
    edad.createChoice('Sí', decision),
    edad.createChoice('No', menor)
  ]);
  acepto.setChoices([
    acepto.createChoice('Sí, acepto participar', datos),
    acepto.createChoice('No acepto participar', FormApp.PageNavigationType.SUBMIT)
  ]);
  // En Apps Script, el salto de una sección se define en el salto de página que la sigue:
  // al terminar "Confirmación" se envía, en vez de seguir a la sección de menores.
  menor.setGoToPage(FormApp.PageNavigationType.SUBMIT);

  return form;
}

/* ------------------------------------------------------------------ */
/* 2. INSTRUMENTO DIGITAL: ENCUESTA                                    */
/* ------------------------------------------------------------------ */
function crearEncuesta_() {
  const form = FormApp.create('EquiFit · Encuesta del estudio');
  configurar_(form,
    NOMBRE_ESTUDIO + '.\n\n' +
    'Contesta esta encuesta justo después de la prueba con el cinturón. Tarda unos 4 minutos.\n\n' +
    '• No pedimos tu nombre: solo el folio que te dio el equipo.\n' +
    '• No hay respuestas correctas o incorrectas; nos interesa tu experiencia real.\n' +
    '• Si una pregunta no aplica para ti, elige la opción más cercana.',
    'Gracias por participar. Tus respuestas quedaron registradas con tu folio.');

  form.addTextItem()
    .setTitle('Folio')
    .setHelpText(AYUDA_FOLIO)
    .setValidation(FormApp.createTextValidation()
      .requireTextMatchesPattern(PATRON_FOLIO).setHelpText(AYUDA_FOLIO).build())
    .setRequired(true);

  /* --- Sección A: datos generales --- */
  form.addPageBreakItem()
    .setTitle('A. Datos generales')
    .setHelpText('Nos ayudan a comparar grupos. Ninguna de estas respuestas te identifica.');

  form.addMultipleChoiceItem()
    .setTitle('Género')
    .setChoiceValues(['Mujer', 'Hombre', 'Prefiero no decir'])
    .showOtherOption(true)
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Rango de edad')
    .setChoiceValues(['18 a 20 años', '21 a 24 años', '25 a 29 años', '30 a 39 años', '40 años o más'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('¿Cuál es tu relación con la UPY?')
    .setChoiceValues(['Estudiante', 'Docente', 'Personal administrativo'])
    .showOtherOption(true)
    .setRequired(true);

  /* --- Sección B: uso habitual del cinturón --- */
  form.addPageBreakItem()
    .setTitle('B. Tu experiencia habitual')
    .setHelpText('Piensa en los vehículos en los que viajas normalmente, no en el de la prueba.');

  form.addMultipleChoiceItem()
    .setTitle('¿Tienes licencia de conducir?')
    .setChoiceValues(['Sí', 'No'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('¿Con qué frecuencia viajas en automóvil?')
    .setChoiceValues(['Todos los días', 'Varias veces por semana', 'Una vez por semana o menos', 'Casi nunca'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('¿En qué lugar viajas con más frecuencia?')
    .setChoiceValues(['Conductor(a)', 'Copiloto', 'Asiento trasero'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('¿Con qué frecuencia usas el cinturón de seguridad?')
    .setChoiceValues(['Siempre', 'Casi siempre', 'A veces', 'Casi nunca', 'Nunca'])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Por incomodidad, ¿alguna vez has hecho alguna de estas cosas con el cinturón?')
    .setHelpText('Marca todas las que apliquen.')
    .setChoiceValues([
      'Pasar la banda por debajo del brazo',
      'Pasar la banda por detrás de la espalda',
      'Separarla del cuello con la mano mientras viajo',
      'Usar un accesorio o ajustador',
      'Ninguna'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('El vehículo que más usas, ¿permite subir o bajar la altura del cinturón a la altura del hombro?')
    .setChoiceValues(['Sí', 'No', 'No sé'])
    .setRequired(true);

  /* --- Sección C: la prueba de hoy (variable objetivo) --- */
  form.addPageBreakItem()
    .setTitle('C. La prueba de hoy')
    .setHelpText('Responde sobre el cinturón del vehículo de la prueba que acabas de hacer.');

  form.addScaleItem()
    .setTitle('¿Qué tan cómodo te resultó el cinturón?')
    .setBounds(1, 5)
    .setLabels('Muy incómodo', 'Muy cómodo')
    .setRequired(true);

  form.addScaleItem()
    .setTitle('¿Qué tan bien se ajustó el cinturón a tu cuerpo?')
    .setBounds(1, 5)
    .setLabels('Muy mal', 'Muy bien')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('¿Por dónde pasó la banda diagonal del cinturón?')
    .setChoiceValues([
      'Sobre el cuello',
      'Entre el cuello y el hombro',
      'Sobre el centro del hombro',
      'En el borde del hombro o sobre el brazo'
    ])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('¿Dónde sentiste molestia o presión?')
    .setHelpText('Marca todas las que apliquen.')
    .setChoiceValues(['Cuello', 'Hombro', 'Pecho o busto', 'Abdomen o cadera', 'En ninguna parte'])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('¿Algo más que quieras contarnos sobre cómo te quedó el cinturón? (opcional)')
    .setRequired(false);

  return form;
}

/* ------------------------------------------------------------------ */
/* Utilidades                                                          */
/* ------------------------------------------------------------------ */
function configurar_(form, descripcion, confirmacion) {
  form.setDescription(descripcion)
    .setConfirmationMessage(confirmacion)
    .setProgressBar(true)
    .setCollectEmail(false)          // no se recopilan correos automáticamente
    .setAllowResponseEdits(false)
    .setShowLinkToRespondAgain(false)
    .setPublishingSummary(false)     // nadie ve las respuestas de otras personas
    .setAcceptingResponses(true);
  // Desde 2025, los formularios creados por script pueden quedar sin publicar.
  if (typeof form.setPublished === 'function') {
    form.setPublished(true);
  }
}

function conectarHoja_(form, nombre) {
  const hoja = SpreadsheetApp.create(nombre);
  form.setDestination(FormApp.DestinationType.SPREADSHEET, hoja.getId());
  return hoja;
}
