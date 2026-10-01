# Feature Specification: Registro e Historial de Mensajes del Chatbot de Ventas

**Feature Branch**: `001-registrar-mensajes-chatbot`

**Created**: 2026-09-30

**Status**: Draft

**Input**: User description: "Construir un servicio que registre los mensajes que los alumnos envían al chatbot de soporte de una academia. Cada mensaje guarda: id, nombre, DNI, teléfono, texto del mensaje y fecha/hora. Se necesita: (1) registrar un mensaje nuevo, rechazando datos inválidos (DNI de 8 dígitos, teléfono de 9 dígitos, mensaje no vacío); (2) consultar el historial de mensajes de un alumno por DNI, ordenado del más reciente al más antiguo; (3) clasificar cada mensaje como 'informacion_ciclo', 'devolucion' u 'otro' según palabras clave, porque las devoluciones deben derivarse a una persona y no las responde el bot. El objetivo es que el equipo de soporte tenga el historial centralizado y que el chatbot pueda consultarlo."

## Clarifications

### Session 2026-10-01

- Q: ¿El chatbot es un bot de soporte o un agente de ventas, y quién recibe las derivaciones? → A: Es un agente de ventas de la academia; las categorías "devolucion" e "interes_inscripcion" se escalan a un asesor de ventas humano, y el chatbot solo responde lo que puede resolver ("informacion_ciclo" y "otro").
- Q: ¿Qué categorías de clasificación existen? → A: Cuatro: "informacion_ciclo", "devolucion", "interes_inscripcion" y "otro".
- Q: ¿Este servicio deriva activamente los mensajes a una persona o solo clasifica? → A: Solo clasifica; la clasificación es la señal que usa el chatbot para decidir qué mensajes responde él y cuáles se escalan a un asesor de ventas.
- Q: ¿Qué ocurre si el chatbot reintenta y envía el mismo mensaje dos veces? → A: Se rechaza como duplicado si es idéntico (mismo DNI y mismo texto) y llega dentro de una ventana corta (10 segundos) desde el registro previo; fuera de esa ventana se guarda como mensaje nuevo.
- Q: ¿Durante cuánto tiempo se conservan los mensajes con datos personales (DNI, teléfono, texto)? → A: Fuera de alcance en esta fase: no se define plazo de conservación; decisión pendiente registrada en Assumptions (se retiró el requisito de 24 meses).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar un mensaje nuevo con validación (Priority: P1)

El chatbot de ventas envía al servicio cada mensaje que un alumno escribe,
junto con su nombre, DNI, teléfono y el texto. El servicio valida los datos
(ya sea rechazando los inválidos) y guarda el mensaje con un id y la
fecha/hora del registro.

**Why this priority**: Sin registro no hay historial centralizado; es la base
de la que dependen las otras dos funcionalidades.

**Independent Test**: Se puede probar enviando mensajes con datos válidos y
con datos inválidos (DNI corto, teléfono con letras, texto vacío) y
comprobando que los válidos quedan guardados y los inválidos se rechazan con
un mensaje claro.

**Acceptance Scenarios**:

1. **Given** no hay mensajes registrados, **When** se registra un mensaje con
   nombre "Ana Prueba", DNI "12345678", teléfono "987654321" y texto
   "Quiero información del ciclo", **Then** el mensaje queda guardado con un
   id único y la fecha/hora de registro.
2. **Given** cualquier estado, **When** se registra un mensaje con DNI
   "12345" (menos de 8 dígitos), **Then** el sistema lo rechaza con un
   mensaje claro indicando que el DNI debe tener 8 dígitos, y el mensaje NO
   se guarda.
3. **Given** cualquier estado, **When** se registra un mensaje con teléfono
   "98765432X" (no son 9 dígitos), **Then** el sistema lo rechaza con un
   mensaje claro y el mensaje NO se guarda.
4. **Given** cualquier estado, **When** se registra un mensaje con texto
   vacío o solo espacios, **Then** el sistema lo rechaza con un mensaje
   claro y el mensaje NO se guarda.
5. **Given** ya existe un mensaje con DNI "12345678" y texto "hola"
   registrado hace menos de 10 segundos, **When** el chatbot reintenta el
   envío del mismo DNI y el mismo texto, **Then** el sistema lo rechaza como
   duplicado con un mensaje claro y NO guarda una copia.
6. **Given** ya existe un mensaje con DNI "12345678" y texto "hola"
   registrado hace más de 10 segundos, **When** el alumno vuelve a enviar
   el mismo texto, **Then** el sistema lo registra como un mensaje nuevo.

---

### User Story 2 - Consultar el historial de un alumno por DNI (Priority: P2)

El equipo de ventas (y el propio chatbot) consulta el historial de mensajes
de un alumno introduciendo su DNI y obtiene la lista completa de sus
mensajes, del más reciente al más antiguo.

**Why this priority**: Es el valor principal para el equipo de ventas: ver
el historial centralizado. Depende de que existan mensajes registrados
(User Story 1), pero puede probarse de forma independiente con datos de
prueba ficticios.

**Independent Test**: Se registran varios mensajes de un mismo alumno con
fechas distintas y se consulta por su DNI; se verifica el orden y que
mensajes de otros alumnos no aparecen.

**Acceptance Scenarios**:

1. **Given** el alumno con DNI "12345678" tiene 3 mensajes registrados,
   **When** se consulta el historial por ese DNI, **Then** se devuelven sus
   3 mensajes ordenados del más reciente al más antiguo.
2. **Given** un alumno tiene mensajes con la misma fecha/hora, **When** se
   consulta su historial, **Then** el orden devuelto es estable y no pierde
   ningún mensaje.
3. **Given** el alumno con DNI "87654321" no tiene mensajes, **When** se
   consulta su historial, **Then** se devuelve una lista vacía (no un
   error).
4. **Given** existen mensajes de varios alumnos, **When** se consulta el
   historial de un DNI, **Then** solo aparecen los mensajes de ese DNI.

---

### User Story 3 - Clasificación automática por palabras clave (Priority: P3)

Cada mensaje se clasifica automáticamente al registrarlo en una de cuatro
categorías: "informacion_ciclo", "devolucion", "interes_inscripcion" u
"otro". El chatbot usa esta clasificación para decidir qué mensajes responde
él mismo y cuáles se escalan a un asesor de ventas humano: las devoluciones y el
interés en inscripción no los responde el bot.

**Why this priority**: Sin clasificación el chatbot no puede decidir qué
resolver y qué derivar; pero el servicio ya resulta útil sin ella
(historial consultable) y depende del registro de mensajes.

**Independent Test**: Se registran mensajes de prueba ficticios que contienen
palabras clave de cada categoría y se comprueba que la clasificación asignada
y el destino (bot o asesor humano) son los esperados.

**Acceptance Scenarios**:

1. **Given** cualquier estado, **When** se registra un mensaje cuyo texto
   contiene palabras clave de devolución (p. ej. "devolución", "reembolso",
   "devolver"), **Then** el mensaje se clasifica como "devolucion" y
   se destina a un asesor de ventas humano.
2. **Given** cualquier estado, **When** se registra un mensaje cuyo texto
   contiene palabras clave de información de ciclo (p. ej. "ciclo",
   "horario", "turno") y ninguna de devolución ni de interés en
   inscripción, **Then** el mensaje se clasifica como "informacion_ciclo" y
   lo responde el chatbot.
3. **Given** cualquier estado, **When** se registra un mensaje cuyo texto
   contiene palabras clave de interés en inscripción (p. ej. "inscribirme",
   "matricularme", "separar vacante"), **Then** el mensaje se clasifica como
   "interes_inscripcion" y se destina a un asesor de ventas humano para que
   haga seguimiento.
4. **Given** cualquier estado, **When** se registra un mensaje sin palabras
   clave de ninguna categoría, **Then** el mensaje se clasifica como "otro"
   y lo responde el chatbot.
5. **Given** un mensaje contiene palabras clave de varias categorías,
   **When** se clasifica, **Then** el orden de prioridad es "devolucion" >
   "interes_inscripcion" > "informacion_ciclo" > "otro", de modo que toda
   devolución y todo interés en inscripción llega a una persona.

---

### Edge Cases

- DNI con más de 8 dígitos o que contenga letras → rechazado como inválido.
- Teléfono con separadores (espacios o guiones) o con el prefijo peruano
  "+51"/"51" → se normaliza a los 9 dígitos; cualquier otro código de país
  (incluido "+34"), un primer dígito distinto de 9 o una longitud distinta
  de 9 → rechazado.
- Texto con solo espacios en blanco o caracteres no visibles → considerado
  vacío y rechazado.
- Dos alumnos distintos comparten el mismo DNI no es posible (el DNI
  identifica al alumno); si el mismo DNI se usa con nombres distintos, el
  historial se consulta por DNI y agrupa todos sus mensajes.
- Mensajes con acentos y mayúsculas/minúsculas en las palabras clave
  (p. ej. "DEVOLUCIÓN") → la clasificación debe reconocerlas igual.
- Historial con un único mensaje o vacío → respuesta correcta en ambos
  casos.
- Registro simultáneo de mensajes → cada mensaje conserva su id único.
- Un texto que contiene la palabra clave como parte de otra palabra (p. ej.
  "devolucionista") → decisión de coincidencia documentada en Assumptions.
- Un mensaje contiene palabras clave de información de ciclo y también de
  interés en inscripción (p. ej. "quiero información del ciclo para
  inscribirme") → se clasifica como "interes_inscripcion": ante la duda, el
  seguimiento humano tiene prioridad sobre la respuesta automática.
- Reintento del chatbot: el mismo DNI y el mismo texto dentro de los 10
  segundos → rechazado como duplicado; el mismo texto pasado ese tiempo, o
  con un texto distinto, → se registra como mensaje nuevo (un alumno puede
  escribir "hola" legítimamente varias veces).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST registrar un mensaje nuevo con los campos:
  id, nombre del alumno, DNI, teléfono, texto del mensaje, fecha/hora de
  registro y clasificación.
- **FR-002**: El sistema MUST rechazar todo mensaje cuyo DNI no tenga
  exactamente 8 dígitos, indicando el motivo en el mensaje de error.
- **FR-003**: El sistema MUST rechazar todo mensaje cuyo teléfono no sea un
  celular peruano válido: exactamente 9 dígitos que empiezan por 9, tras
  normalizar (se admiten espacios o guiones como separadores y un prefijo
  opcional "+51" o "51"; cualquier otro código de país, incluido "+34", se
  rechaza), indicando el motivo en el mensaje de error.
- **FR-004**: El sistema MUST rechazar todo mensaje cuyo texto esté vacío o
  contenga solo espacios en blanco.
- **FR-005**: El sistema MUST asignar un id único y la fecha/hora de
  registro a cada mensaje aceptado.
- **FR-006**: El sistema MUST permitir consultar el historial de mensajes de
  un alumno a partir de su DNI.
- **FR-007**: El historial MUST devolver los mensajes del alumno ordenados
  del más reciente al más antiguo según su fecha/hora de registro.
- **FR-008**: El historial MUST incluir únicamente los mensajes cuyo DNI
  coincide con el consultado; si no hay mensajes, MUST devolver una lista
  vacía sin error.
- **FR-009**: El sistema MUST clasificar cada mensaje registrado en una de
  cuatro categorías exactas: "informacion_ciclo", "devolucion",
  "interes_inscripcion" u "otro".
- **FR-010**: La clasificación MUST basarse en una lista de palabras clave
  por categoría, distingiendo mayúsculas/minúsculas y acentos de forma
  tolerante.
- **FR-011**: Cuando un mensaje contiene palabras clave de varias
  categorías, la prioridad MUST ser "devolucion" > "interes_inscripcion" >
  "informacion_ciclo" > "otro", para garantizar que toda devolución y todo
  interés en inscripción llegue a una persona.
- **FR-012**: El sistema MUST rechazar los datos inválidos con mensajes de
  error claros que indiquen qué campo es inválido y por qué, sin guardar
  nada.
- **FR-013**: Todo mensaje registrado MUST conservarse con su clasificación
  para que el chatbot y el equipo de ventas puedan consultarlo
  posteriormente.
- **FR-014**: Las palabras clave de clasificación MUST poder ampliarse sin
  cambiar la lógica de clasificación (p. ej. añadir sinónimos de
  devolución).
- **FR-015**: La clasificación MUST determinar el destino del mensaje: los
  mensajes "devolucion" e "interes_inscripcion" MUST quedar marcados para
  derivación a un asesor de ventas humano, y los mensajes "informacion_ciclo"
  y "otro" para respuesta del chatbot. La marca es el propio campo
  `clasificacion`; no se requiere un indicador adicional. El comportamiento
  del chatbot (responder o no cada mensaje) está fuera del alcance de este
  servicio.
- **FR-016**: El sistema MUST rechazar como duplicado todo mensaje con el
  mismo DNI y el mismo texto (ignorando espacios al inicio y al final) que
  uno ya registrado en los últimos 10 segundos, indicando el motivo y sin
  guardar nada; fuera de esa ventana MUST registrarse como mensaje nuevo.
- **FR-017**: El sistema MUST rechazar todo mensaje cuyo nombre esté vacío
  o contenga solo espacios en blanco, indicando el motivo en el mensaje de
  error.

### Key Entities *(include if feature involves data)*

- **Mensaje**: un mensaje enviado por un alumno al chatbot de ventas.
  Atributos: id único, nombre del alumno (no vacío), DNI (8 dígitos),
  teléfono (9 dígitos), texto del mensaje (no vacío), fecha/hora de registro y
  clasificación ("informacion_ciclo" | "devolucion" | "interes_inscripcion"
  | "otro").
- **Alumno** (derivado): se identifica por su DNI; su historial es el
  conjunto de mensajes con ese DNI, ordenado por fecha/hora de registro.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los mensajes con DNI, teléfono o texto inválidos
  se rechazan en el intento de registro y ninguno queda almacenado.
- **SC-002**: El 100% de los mensajes válidos enviados se registran con id
  y fecha/hora correctos (cero registros perdidos en las pruebas
  automatizadas).
- **SC-003**: El historial de cualquier alumno consultado devuelve
  correctamente sus mensajes en menos de 2 segundos con hasta 10.000
  mensajes almacenados.
- **SC-004**: El 100% de los mensajes de prueba que contienen palabras clave
  de devolución se clasifican como "devolucion", y el 100% de los que
  contienen palabras clave de interés en inscripción se clasifican como
  "interes_inscripcion", incluidos los que también contienen palabras de
  otras categorías.
- **SC-005**: El equipo de ventas localiza un mensaje concreto de un alumno
  en su historial en menos de 30 segundos desde que abre la consulta.
- **SC-006**: Cero mensajes con datos personales reales se usan en las
  pruebas automatizadas (solo datos ficticios).
- **SC-007**: El 100% de los mensajes clasificados como "devolucion" o
  "interes_inscripcion" quedan marcados para derivación a un asesor de
  ventas humano. Verificar que el chatbot no los responde queda fuera del
  alcance de este servicio (responsabilidad del chatbot).
- **SC-008**: En las pruebas, el 100% de los reenvíos idénticos dentro de
  la ventana de 10 segundos se rechazan (cero duplicados almacenados) y el
  100% de las repeticiones legítimas fuera de la ventana se registran.

## Assumptions

- El DNI se valida por formato: exactamente 8 dígitos numéricos; no se
  verifica su letra ni se comprueba contra un padrón oficial.
- El teléfono se valida por formato de celular peruano: exactamente 9
  dígitos numéricos que empiezan por 9; se aceptan espacios o guiones como
  separadores y un prefijo opcional "+51" o "51" que se elimina al
  normalizar; cualquier otro código de país (incluido "+34") se rechaza.
- La fecha/hora la asigna el sistema en el momento del registro; el
  emisor no la proporciona.
- El id se genera de forma única e irrepetible para cada mensaje; su
  formato no está especificado.
- La clasificación se calcula una sola vez, al registrar el mensaje, y
  queda almacenada junto a él.
- Las listas iniciales de palabras clave están definidas en el Apéndice A
  de data-model.md (con ejemplos en español peruano); el equipo de ventas
  podrá ampliarlas sin cambiar la lógica de clasificación (FR-014). La
  palabra "cancelar" queda deliberadamente fuera de las listas (en el
  Perú significa "pagar", no "anular").
- El destino por clasificación: "devolucion" e "interes_inscripcion" se
  escalan a un asesor de ventas humano; "informacion_ciclo" y "otro" los
  resuelve el chatbot. El mecanismo concreto por el que la derivación
  llega al asesor (notificación, cola, etc.) forma parte del chatbot, no
  de este servicio, que solo expone la clasificación.
- Coincidencia de palabras clave por palabra completa (no por subcadena),
  para evitar falsos positivos como "devolucionista" → "devolucion".
- Sin palabras clave aplicables, la categoría por defecto es "otro".
- La ventana anti-duplicados son 10 segundos contados desde la fecha/hora
  de registro del mensaje previo; la comparación de texto ignora espacios
  al inicio y al final pero no reformulatea el mensaje.
- El servicio es de uso interno (chatbot de ventas y equipo de ventas); los
  mecanismos de acceso y autenticación no se especifican en esta fase y se
  definirán en la planificación.
- **(Decisión pendiente)** La retención de datos se declaró fuera de
  alcance en esta fase: no se define plazo de conservación de mensajes y no
  se ejecuta ninguna purga; deberá fijarse una política antes de usar datos
  personales reales.
- El objetivo de volumen asumido es de hasta 10.000 mensajes almacenados
  sin degradación perceptible; volúmenes mayores se evaluarán después.
- Todas las pruebas se escribirán con datos ficticios, conforme a la
  constitución del proyecto.
