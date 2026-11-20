/**
 * EquiFit — Encuesta en línea con autorreporte (versión 2).
 *
 * Cada persona responde sobre el vehículo en el que viaja con más frecuencia y
 * se toma sus propias medidas en casa con una cinta métrica. Con solo contestar
 * este formulario se obtienen TODAS las columnas que usa EquiFit:
 *
 *   genero, estatura_cm, peso_kg, altura_hombro_sentado_cm, longitud_torso_cm,
 *   contorno_pecho_cm, alcance_brazo_cm, likert_comodidad, likert_ajuste,
 *   cuello_corta, anclaje_adecuado, presion_busto
 *
 * El consentimiento informado va al inicio del mismo formulario, así que NO se
 * pide nombre, correo ni folio: la encuesta es anónima. La app EquiFit reconoce
 * el CSV que exporta Google Sheets y lo convierte sola (pestaña "Cargar datos").
 *
 * CÓMO USARLO
 *   1. https://script.google.com con la cuenta @upy.edu.mx → "Nuevo proyecto".
 *   2. Pega este archivo, elige la función crearEncuestaEquiFit y presiona "Ejecutar".
 *   3. Acepta los permisos. Los enlaces salen en "Registro de ejecución".
 *
 * IMPORTANTE: no cambies el texto de las preguntas marcadas con [EquiFit]; la app
 * las reconoce por su título.
 *
 * Proyecto Integrador I · TSU en Ciencia de Datos · Universidad Politécnica de Yucatán
 */

const CONTACTO = '2509202@upy.edu.mx';

// Títulos que la app reconoce. Si cambias uno aquí, cámbialo también en equifit/forms.py.
const T = {
  acepta: '¿Aceptas participar en el estudio?',
  edad18: '¿Tienes 18 años o más?',
  genero: 'Género',
  estatura: 'Estatura (cm)',
  peso: 'Peso (kg)',
  hombro: 'Altura de hombro sentado (cm)',
  torso: 'Longitud de torso (cm)',
  pecho: 'Contorno de pecho o busto (cm)',
  brazo: 'Alcance de brazo (cm)',
  comodidad: '¿Qué tan cómodo te resulta el cinturón?',
  ajuste: '¿Qué tan bien se ajusta el cinturón a tu cuerpo?',
  cuello: '¿La banda diagonal te roza o te corta el cuello?',
  anclaje: '¿Logras que la banda quede sobre el centro de tu hombro?',
  busto: '¿La banda te presiona de forma incómoda sobre el pecho o el busto?'
};

function crearEncuestaEquiFit() {
  const form = FormApp.create('EquiFit · Encuesta del estudio (en línea)');
  form.setDescription(
    'Estudio sobre el ajuste del cinturón de seguridad · Proyecto Integrador I, ' +
    'TSU en Ciencia de Datos, Universidad Politécnica de Yucatán.\n\n' +
    'Toma unos 10 minutos. Vas a necesitar una cinta métrica (de costura sirve) y, de ' +
    'preferencia, que alguien te ayude a medir.\n\n' +
    'Responde pensando en el vehículo en el que viajas con más frecuencia.')
    .setConfirmationMessage('Gracias por participar. Tus respuestas son anónimas y quedaron registradas.')
    .setProgressBar(true)
    .setCollectEmail(false)
    .setAllowResponseEdits(false)
    .setShowLinkToRespondAgain(false)
    .setPublishingSummary(false)
    .setAcceptingResponses(true);
  if (typeof form.setPublished === 'function') form.setPublished(true);

  /* ---------- 1. Consentimiento ---------- */
  form.addPageBreakItem()
    .setTitle('Consentimiento informado')
    .setHelpText(
      'QUÉ HARÍAS: contestar preguntas sobre cómo te queda el cinturón de seguridad en tu vehículo ' +
      'habitual y anotar algunas medidas de tu cuerpo que tú mismo(a) tomas con cinta métrica.\n\n' +
      'TU PARTICIPACIÓN es voluntaria y anónima: no pedimos nombre, correo ni ningún dato que te ' +
      'identifique. Puedes dejar el formulario en cualquier momento sin ninguna consecuencia, ' +
      'tampoco en calificaciones. Si una medida te incomoda, puedes no participar.\n\n' +
      'AVISO DE PRIVACIDAD SIMPLIFICADO\n' +
      'Responsable: equipo del proyecto EquiFit, Universidad Politécnica de Yucatán.\n' +
      'Datos: género, rango de edad, medidas corporales, datos de tu vehículo y tus opiniones.\n' +
      'Finalidad: solo académica. Los resultados se publican agrupados, nunca por persona.\n' +
      'Protección: las respuestas se guardan con acceso solo para el equipo y el docente, y se ' +
      'eliminan al cierre del cuatrimestre. No se comparten con terceros.\n' +
      'Dudas o derechos de acceso, corrección o cancelación: ' + CONTACTO + '.');

  const edad18 = form.addMultipleChoiceItem().setTitle(T.edad18).setRequired(true);

  const decision = form.addPageBreakItem().setTitle('Tu decisión');
  const acepta = form.addMultipleChoiceItem().setTitle(T.acepta)
    .setHelpText('Al aceptar confirmas que leíste la información anterior.').setRequired(true);

  /* ---------- 2. Datos generales ---------- */
  const generales = form.addPageBreakItem()
    .setTitle('Datos generales')
    .setHelpText('Nos ayudan a comparar grupos. Ninguna de estas respuestas te identifica.');

  form.addMultipleChoiceItem().setTitle(T.genero)
    .setChoiceValues(['Mujer', 'Hombre', 'Prefiero no decir']).showOtherOption(true).setRequired(true);
  form.addMultipleChoiceItem().setTitle('Rango de edad')
    .setChoiceValues(['18 a 20 años', '21 a 24 años', '25 a 29 años', '30 a 39 años', '40 años o más'])
    .setRequired(true);
  form.addMultipleChoiceItem().setTitle('¿Cuál es tu relación con la UPY?')
    .setChoiceValues(['Estudiante', 'Docente', 'Personal administrativo']).showOtherOption(true).setRequired(true);

  /* ---------- 3. Medidas ---------- */
  form.addPageBreakItem()
    .setTitle('Tus medidas')
    .setHelpText(
      'Usa una cinta métrica y escribe todo en CENTÍMETROS (por ejemplo 165, no 1.65). Mide sobre ropa ' +
      'ligera. Si no tienes cinta, usa una cuerda y después mídela con una regla. Las medidas de hombro, ' +
      'torso y brazo salen mejor si alguien te ayuda.');

  numero_(form, T.estatura, 'Descalzo(a), de pie contra la pared. Ejemplo: 162', 120, 220);
  numero_(form, T.peso, 'Aproximado, en kilogramos. Ejemplo: 64', 30, 200);
  numero_(form, T.hombro,
    'Siéntate en una silla dura con la espalda recta. Mide desde el asiento hasta la parte más alta ' +
    'del hombro. Ejemplo: 56', 35, 80);
  numero_(form, T.torso,
    'Desde el hueso que sobresale en la base del cuello (al inclinar la cabeza) hasta la altura del ' +
    'ombligo, por la espalda. Ejemplo: 45', 30, 75);
  numero_(form, T.pecho,
    'Rodea la parte más amplia del pecho o busto con la cinta, sin apretar. Ejemplo: 92', 60, 160);
  numero_(form, T.brazo,
    'Con el brazo extendido al frente, desde la punta del hombro hasta la punta del dedo medio. ' +
    'Ejemplo: 72', 50, 110);

  form.addMultipleChoiceItem().setTitle('¿Cómo obtuviste tus medidas?')
    .setHelpText('Nos sirve para saber qué tan precisas son. Responde con sinceridad.')
    .setChoiceValues([
      'Las medí con cinta y alguien me ayudó',
      'Las medí con cinta yo solo(a)',
      'Algunas las medí y otras las estimé',
      'Las estimé sin medir'
    ]).setRequired(true);

  /* ---------- 4. Tu vehículo ---------- */
  form.addPageBreakItem()
    .setTitle('Tu vehículo')
    .setHelpText('Piensa en el vehículo en el que viajas con más frecuencia.');

  form.addMultipleChoiceItem().setTitle('¿Qué tipo de vehículo es?')
    .setChoiceValues(['Sedán', 'Hatchback (compacto)', 'SUV o camioneta', 'Pickup', 'Van o minivan'])
    .showOtherOption(true).setRequired(true);
  form.addMultipleChoiceItem().setTitle('¿De qué año es, aproximadamente?')
    .setChoiceValues(['2020 o más reciente', '2015 a 2019', '2010 a 2014', 'Antes de 2010', 'No sé'])
    .setRequired(true);
  form.addMultipleChoiceItem().setTitle('¿En qué lugar viajas con más frecuencia?')
    .setChoiceValues(['Conductor(a)', 'Copiloto', 'Asiento trasero']).setRequired(true);
  form.addMultipleChoiceItem().setTitle('¿El cinturón permite subir o bajar su altura a la altura del hombro?')
    .setChoiceValues(['Sí', 'No', 'No sé']).setRequired(true);
  form.addMultipleChoiceItem().setTitle('¿Con qué frecuencia usas el cinturón de seguridad?')
    .setChoiceValues(['Siempre', 'Casi siempre', 'A veces', 'Casi nunca', 'Nunca']).setRequired(true);

  /* ---------- 5. Cómo te queda el cinturón ---------- */
  form.addPageBreakItem()
    .setTitle('Cómo te queda el cinturón')
    .setHelpText('Si puedes, contesta sentado(a) en tu vehículo con el cinturón puesto y el asiento como lo usas siempre.');

  form.addScaleItem().setTitle(T.comodidad).setBounds(1, 5)
    .setLabels('Muy incómodo', 'Muy cómodo').setRequired(true);
  form.addScaleItem().setTitle(T.ajuste).setBounds(1, 5)
    .setLabels('Muy mal', 'Muy bien').setRequired(true);
  form.addMultipleChoiceItem().setTitle(T.cuello)
    .setChoiceValues(['Sí, casi siempre', 'A veces', 'No']).setRequired(true);
  form.addMultipleChoiceItem().setTitle(T.anclaje)
    .setHelpText('Ajustando la altura del cinturón si tu vehículo lo permite.')
    .setChoiceValues(['Sí', 'No, queda cerca del cuello', 'No, queda en el borde del hombro o en el brazo'])
    .setRequired(true);
  form.addMultipleChoiceItem().setTitle(T.busto)
    .setChoiceValues(['Sí, casi siempre', 'A veces', 'No']).setRequired(true);
  form.addCheckboxItem().setTitle('Por incomodidad, ¿alguna vez has hecho alguna de estas cosas?')
    .setHelpText('Marca todas las que apliquen.')
    .setChoiceValues([
      'Pasar la banda por debajo del brazo',
      'Pasar la banda por detrás de la espalda',
      'Separarla del cuello con la mano mientras viajo',
      'Usar un accesorio o ajustador',
      'Ninguna'
    ]).setRequired(true);
  form.addParagraphTextItem()
    .setTitle('¿Algo más que quieras contarnos sobre cómo te queda el cinturón? (opcional)');

  /* ---------- Final para quien no participa ---------- */
  const fin = form.addPageBreakItem()
    .setTitle('Gracias por tu interés')
    .setHelpText('No necesitas continuar. Presiona "Enviar" para terminar.');

  // Navegación: solo continúa quien es mayor de edad y acepta; los demás terminan sin dar datos.
  edad18.setChoices([edad18.createChoice('Sí', decision), edad18.createChoice('No', fin)]);
  acepta.setChoices([
    acepta.createChoice('Sí, acepto participar', generales),
    acepta.createChoice('No acepto', fin)
  ]);
  // Al terminar la sección 5 se envía, en vez de pasar a la sección "Gracias por tu interés".
  fin.setGoToPage(FormApp.PageNavigationType.SUBMIT);

  const hoja = SpreadsheetApp.create('EquiFit — Respuestas de la encuesta en línea');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, hoja.getId());

  Logger.log('Editar:     ' + form.getEditUrl());
  Logger.log('Compartir:  ' + form.getPublishedUrl());
  Logger.log('Respuestas: ' + hoja.getUrl());
}

function numero_(form, titulo, ayuda, min, max) {
  return form.addTextItem().setTitle(titulo).setHelpText(ayuda)
    .setValidation(FormApp.createTextValidation()
      .requireNumberBetween(min, max)
      .setHelpText('Escribe un número entre ' + min + ' y ' + max + ', en ' +
        (titulo.indexOf('(kg)') >= 0 ? 'kilogramos.' : 'centímetros.'))
      .build())
    .setRequired(true);
}
