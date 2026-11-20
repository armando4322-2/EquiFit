/**
 * EquiFit — Encuesta en línea con autorreporte (versión 2).
 *
 * Cada persona responde sobre el vehículo en el que viaja con más frecuencia. No
 * necesita cinta métrica: estatura y peso, más tres preguntas que cualquiera sabe
 * contestar. Con solo contestar este formulario se obtienen TODAS las columnas
 * que usa EquiFit:
 *
 *   genero, estatura_cm, peso_kg, hombro_vs_anclaje, talla_superior, largo_camisas,
 *   likert_comodidad, likert_ajuste, cuello_corta, anclaje_adecuado, presion_busto
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
  hombro: 'Sentado(a) en tu auto, ¿dónde queda la parte alta de tu hombro?',
  talla: '¿Cuál es tu talla de playera o blusa?',
  largo: 'De largo, ¿cómo te quedan las camisas o blusas de tu talla?',
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
    'Toma unos 5 minutos y no necesitas medirte.\n\n' +
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
      'habitual y algunos datos generales de tu cuerpo, como tu estatura y tu talla de ropa.\n\n' +
      'TU PARTICIPACIÓN es voluntaria y anónima: no pedimos nombre, correo ni ningún dato que te ' +
      'identifique. Puedes dejar el formulario en cualquier momento sin ninguna consecuencia, ' +
      'tampoco en calificaciones. Si alguna pregunta te incomoda, puedes no participar.\n\n' +
      'AVISO DE PRIVACIDAD SIMPLIFICADO\n' +
      'Responsable: equipo del proyecto EquiFit, Universidad Politécnica de Yucatán.\n' +
      'Datos: género, rango de edad, estatura, peso, talla de ropa, datos de tu vehículo y tus opiniones.\n' +
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

  /* ---------- 3. Tu cuerpo ---------- */
  form.addPageBreakItem()
    .setTitle('Tu cuerpo')
    .setHelpText('No necesitas medirte: responde con lo que sabes. Si tienes duda entre dos opciones, elige la que más se acerque.');

  numero_(form, T.estatura, 'En centímetros, sin decimales. Ejemplo: 162 (no 1.62)', 120, 220);
  numero_(form, T.peso, 'Aproximado, en kilogramos. Ejemplo: 64', 30, 200);

  form.addMultipleChoiceItem().setTitle(T.hombro)
    .setHelpText('Siéntate en tu lugar habitual, con el asiento como lo usas siempre. Compara la parte alta de ' +
      'tu hombro con la pieza de donde sale la banda del cinturón, en el poste junto a la ventana.')
    .setChoiceValues(['Arriba de donde sale el cinturón', 'A la misma altura', 'Un poco abajo', 'Muy abajo'])
    .setRequired(true);
  form.addMultipleChoiceItem().setTitle(T.talla)
    .setHelpText('La que compras con más frecuencia para la parte de arriba.')
    .setChoiceValues(['XS', 'S', 'M', 'L', 'XL', 'XXL o más'])
    .setRequired(true);
  form.addMultipleChoiceItem().setTitle(T.largo)
    .setHelpText('Piensa solo en el largo del cuerpo de la prenda (de los hombros hacia abajo), no en las mangas.')
    .setChoiceValues(['Cortas', 'Bien', 'Largas'])
    .setRequired(true);

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
        (titulo.indexOf('(kg)') >= 0 ? 'kilogramos.' : 'centímetros (por ejemplo 162, no 1.62).'))
      .build())
    .setRequired(true);
}
