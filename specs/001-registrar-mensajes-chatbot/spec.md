# Feature Specification: Registro e Historial de Mensajes del Chatbot de Soporte

**Feature Branch**: `001-registrar-mensajes-chatbot`

**Created**: 2026-09-30

**Status**: Draft

**Input**: User description: "Construir un servicio que registre los mensajes que los alumnos envían al chatbot de soporte de una academia. Cada mensaje guarda: id, nombre, DNI, teléfono, texto del mensaje y fecha/hora. Se necesita: (1) registrar un mensaje nuevo, rechazando datos inválidos (DNI de 8 dígitos, teléfono de 9 dígitos, mensaje no vacío); (2) consultar el historial de mensajes de un alumno por DNI, ordenado del más reciente al más antiguo; (3) clasificar cada mensaje como 'informacion_ciclo', 'devolucion' u 'otro' según palabras clave, porque las devoluciones deben derivarse a una persona y no las responde el bot. El objetivo es que el equipo de soporte tenga el historial centralizado y que el chatbot pueda consultarlo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar un mensaje nuevo con validación (Priority: P1)

El chatbot de soporte envía al servicio cada mensaje que un alumno escribe,
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
   nombre "Ana Prueba", DNI "12345678", teléfono "612345678" y texto
   "Quiero información del ciclo", **Then** el mensaje queda guardado con un
   id único y la fecha/hora de registro.
2. **Given** cualquier estado, **When** se registra un mensaje con DNI
   "12345" (menos de 8 dígitos), **Then** el sistema lo rechaza con un
   mensaje claro indicando que el DNI debe tener 8 dígitos, y el mensaje NO
   se guarda.
3. **Given** cualquier estado, **When** se registra un mensaje con teléfono
   "61234567X" (no son 9 dígitos), **Then** el sistema lo rechaza con un
   mensaje claro y el mensaje NO se guarda.
4. **Given** cualquier estado, **When** se registra un mensaje con texto
   vacío o solo espacios, **Then** el sistema lo rechaza con un mensaje
   claro y el mensaje NO se guarda.

---

### User Story 2 - Consultar el historial de un alumno por DNI (Priority: P2)

El equipo de soporte (y el propio chatbot) consulta el historial de mensajes
de un alumno introduciendo su DNI y obtiene la lista completa de sus
mensajes, del más reciente al más antiguo.

**Why this priority**: Es el valor principal para el equipo de soporte: ver
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

Cada mensaje se clasifica automáticamente al registrarlo como
"informacion_ciclo", "devolucion" u "otro" según sus palabras clave, para
que las devoluciones se deriven a una persona del equipo de soporte en lugar
de responderlas el bot.

**Why this priority**: Es esencial para el flujo de derivación, pero el
servicio ya resulta útil sin ella (historial consultable); además depende
del registro de mensajes.

**Independent Test**: Se registran mensajes de prueba ficticios que contienen
palabras clave de cada categoría y se comprueba que la clasificación asignada
es la esperada.

**Acceptance Scenarios**:

1. **Given** cualquier estado, **When** se registra un mensaje cuyo texto
   contiene palabras clave de devolución (p. ej. "devolución", "reembolso",
   "quiero devolver"), **Then** el mensaje se clasifica como "devolucion".
2. **Given** cualquier estado, **When** se registra un mensaje cuyo texto
   contiene palabras clave de información de ciclo (p. ej. "ciclo",
   "horario", "matrícula") y ninguna de devolución, **Then** el mensaje se
   clasifica como "informacion_ciclo".
3. **Given** cualquier estado, **When** se registra un mensaje sin palabras
   clave de ninguna de las dos primeras categorías, **Then** el mensaje se
   clasifica como "otro".
4. **Given** un mensaje contiene palabras clave de devolución y también de
   información de ciclo, **When** se clasifica, **Then** la categoría es
   "devolucion" (la devolución tiene prioridad para garantizar la derivación
   a una persona).

---

### Edge Cases

- DNI con más de 8 dígitos o que contenga letras → rechazado como inválido.
- Teléfono con más de 9 dígitos, espacios o prefijo "+34" → se acepta
  únicamente si tras normalizar quedan exactamente 9 dígitos; si no,
  rechazado.
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

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST registrar un mensaje nuevo con los campos:
  id, nombre del alumno, DNI, teléfono, texto del mensaje, fecha/hora de
  registro y clasificación.
- **FR-002**: El sistema MUST rechazar todo mensaje cuyo DNI no tenga
  exactamente 8 dígitos, indicando el motivo en el mensaje de error.
- **FR-003**: El sistema MUST rechazar todo mensaje cuyo teléfono no tenga
  exactamente 9 dígitos, indicando el motivo en el mensaje de error.
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
  tres categorías exactas: "informacion_ciclo", "devolucion" u "otro".
- **FR-010**: La clasificación MUST basarse en una lista de palabras clave
  por categoría, distingiendo mayúsculas/minúsculas y acentos de forma
  tolerante.
- **FR-011**: Cuando un mensaje contiene palabras clave de varias
  categorías, "devolucion" MUST tener prioridad sobre "informacion_ciclo",
  y esta sobre "otro", para garantizar que toda devolución llega a una
  persona.
- **FR-012**: El sistema MUST rechazar los datos inválidos con mensajes de
  error claros que indiquen qué campo es inválido y por qué, sin guardar
  nada.
- **FR-013**: Todo mensaje registrado MUST conservarse con su clasificación
  para que el chatbot y el equipo de soporte puedan consultarlo
  posteriormente.
- **FR-014**: Las palabras clave de clasificación MUST poder ampliarse sin
  cambiar la lógica de clasificación (p. ej. añadir sinónimos de
  devolución).

### Key Entities *(include if feature involves data)*

- **Mensaje**: un mensaje enviado por un alumno al chatbot de soporte.
  Atributos: id único, nombre del alumno, DNI (8 dígitos), teléfono
  (9 dígitos), texto del mensaje (no vacío), fecha/hora de registro y
  clasificación ("informacion_ciclo" | "devolucion" | "otro").
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
  de devolución se clasifican como "devolucion", incluidos los que también
  contienen palabras de otras categorías.
- **SC-005**: El equipo de soporte localiza un mensaje concreto de un alumno
  en su historial en menos de 30 segundos desde que abre la consulta.
- **SC-006**: Cero mensajes con datos personales reales se usan en las
  pruebas automatizadas (solo datos ficticios).

## Assumptions

- El DNI se valida por formato: exactamente 8 dígitos numéricos; no se
  verifica su letra ni se comprueba contra un padrón oficial.
- El teléfono se valida por formato: exactamente 9 dígitos numéricos; se
  acepta un prefijo internacional "+34" si tras normalizar quedan 9
  dígitos.
- La fecha/hora la asigna el sistema en el momento del registro; el
  emisor no la proporciona.
- El id se genera de forma única e irrepetible para cada mensaje; su
  formato no está especificado.
- La clasificación se calcula una sola vez, al registrar el mensaje, y
  queda almacenada junto a él.
- La lista inicial de palabras clave es un conjunto de partida que
  ampliará el equipo de soporte; no se especifica aquí el listado
  definitivo (las palabras clave de ejemplo en los escenarios son solo
  ilustrativas).
- Coincidencia de palabras clave por palabra completa (no por subcadena),
  para evitar falsos positivos como "devolucionista" → "devolucion".
- Sin palabras clave aplicables, la categoría por defecto es "otro".
- El servicio es de uso interno (chatbot y equipo de soporte); los
  mecanismos de acceso y autenticación no se especifican en esta fase y se
  definirán en la planificación.
- No se ha definido un periodo de retención de mensajes: se conservan de
  forma indefinida hasta que se establezca una política.
- El objetivo de volumen asumido es de hasta 10.000 mensajes almacenados
  sin degradación perceptible; volúmenes mayores se evaluarán después.
- Todas las pruebas se escribirán con datos ficticios, conforme a la
  constitución del proyecto.
