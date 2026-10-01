# Modelo de Datos: Registro e Historial de Mensajes del Chatbot de Ventas

**Branch**: `001-registrar-mensajes-chatbot` | **Date**: 2026-10-01 | **Spec**: [spec.md](./spec.md)

## Entidad: Mensaje

Un mensaje enviado por un alumno al chatbot de ventas. Es la única entidad
persistente del servicio (el alumno se deriva de su DNI — ver más abajo).

| Campo | Tipo | Obligatorio | Reglas de validación | Origen |
|-------|------|-------------|----------------------|--------|
| `id` | uuid | sí | único e irrepetible | lo genera el sistema al registrar (FR-005) |
| `nombre` | texto | sí | no vacío ni solo espacios (tras recortar espacios al inicio y al final) (FR-017) | lo aporta el chatbot |
| `dni` | texto (8 c.) | sí | exactamente 8 dígitos numéricos `^[0-9]{8}$` (FR-002) | lo aporta el chatbot |
| `telefono` | texto (9 c.) | sí | celular peruano: exactamente 9 dígitos `^9[0-9]{8}$` tras normalizar (FR-003); admite espacios o guiones y prefijo opcional `+51`/`51` | lo aporta el chatbot |
| `texto` | texto | sí | no vacío ni solo espacios en blanco (FR-004); se compara recortando espacios al inicio y al final para anti-duplicados | lo aporta el chatbot |
| `fecha_hora` | timestamp con zona | sí | la asigna el sistema en el registro; el emisor no la proporciona | sistema (FR-005) |
| `clasificacion` | texto | sí | uno de: `informacion_ciclo` \| `devolucion` \| `interes_inscripcion` \| `otro` (FR-009); calculada al registrar y no cambia después | sistema (FR-009, FR-011) |

**Restricciones de la base de datos** (red de seguridad bajo la validación con Pydantic
de la entrada — constitución III):

- `CHECK` por cada regla de formato: `dni ~ '^[0-9]{8}$'`,
  `telefono ~ '^9[0-9]{8}$'`, `length(btrim(texto)) > 0`,
  `clasificacion IN (...)`.
- Índice en `(dni, fecha_hora DESC)` para la consulta de historial (SC-003:
  < 2 s con 10.000 mensajes).
- El SQL de creación completo se entrega en `db/schema.sql` (implementación).

### Normalizaciones de entrada (capa de validación con Pydantic)

- `dni`: recortar espacios al inicio y al final → debe ser exactamente 8 dígitos.
- `telefono`: recortar espacios al inicio y al final → se eliminan espacios y guiones → se elimina el
  prefijo peruano `+51` o `51` si existe → deben quedar exactamente 9
  dígitos empezando por 9 (celular peruano); cualquier otro código de país
  (incluido `+34`) se rechaza.
- `texto`: se valida recortando espacios al inicio y al final (vacío → rechazo) pero se conserva tal cual
  como llegó para el historial.
- Todo dato inválido se rechaza **antes** de persistir nada, con mensaje que
  indica campo y motivo (FR-012).

### Regla de duplicados (10 segundos)

Comprobación previa al insert: existe ya un mensaje con el mismo `dni` y el
mismo `texto` (tras recortar espacios al inicio y al final) con `fecha_hora > ahora − 10 s` → **409**, no se
guarda. Fuera de la ventana se registra como mensaje nuevo (FR-016).

### Retención (fuera de alcance)

**(Decisión pendiente)** No se define plazo de conservación ni purga de
mensajes en esta fase (la retención se declaró fuera de alcance); la política
de retención deberá fijarse antes de usar datos personales reales.

## Entidad derivada: Alumno

No tiene tabla propia: se identifica por su DNI (`^[0-9]{8}$`). Su historial
es el conjunto de mensajes con ese DNI, ordenado por `fecha_hora DESC` con
desempate por `id DESC` (orden estable, escenario US2-2), devolviendo lista
vacía —no error— si no hay mensajes (FR-008).

Nota de dominio: si el mismo DNI aparece con nombres distintos, el historial
agrupa igualmente todos sus mensajes (el DNI es la identidad).

## Clasificación (dominio)

| Categoría | Destino | Palabras clave (ver Apéndice A — FR-014) |
|-----------|---------|-------------------------------------------|
| `devolucion` | marcado para derivación a un asesor de ventas | devolución, devolver, reembolso, anular matrícula… |
| `interes_inscripcion` | marcado para derivación a un asesor de ventas | matricularme, inscribirme, separar vacante… |
| `informacion_ciclo` | para respuesta del chatbot | ciclo, horario, turno, modalidad… |
| `otro` | para respuesta del chatbot (por defecto) | — (sin coincidencia) |

Prioridad ante texto mixto (FR-011): `devolucion` > `interes_inscripcion` >
`informacion_ciclo` > `otro`.

## Apéndice A: Listas iniciales de palabras clave (aprobadas)

Punto de partida aprobado para la clasificación (FR-009, FR-014), en español
peruano. Coincidencia por palabra o frase con límites de palabra, sobre texto
en minúsculas y sin acentos (research D3). Prioridad ante texto mixto:
`devolucion` > `interes_inscripcion` > `informacion_ciclo` > `otro` (FR-011).

| Categoría | Palabras clave iniciales |
|-----------|--------------------------|
| `devolucion` | devolución, devolver, devuelvan, reembolso, reembolsar, anular matrícula, retirarme, me quiero retirar |
| `interes_inscripcion` | matrícula, matricular, matricularme, quiero matricularme, inscribir, inscribirme, inscripción, separar vacante, separar mi vacante, vacante, cómo me inscribo, quiero inscribirme |
| `informacion_ciclo` | ciclo, ciclos, horario, horarios, turno, turnos, fecha de inicio, cuándo empieza, cursos, modalidad, virtual, presencial, precio, costo, cuánto cuesta, mensualidad, simulacro |
| `otro` | sin palabras clave (categoría por defecto cuando no hay coincidencia) |

Notas:

- Las variantes con acentos ("devolución", "inscripción", "cuándo empieza")
  se comparan sin acentos gracias a la normalización; se listan en su forma
  natural para facilitar su lectura.
- "matrícula" y "matricular" pertenecen a `interes_inscripcion`: la
  intención de matrícula requiere seguimiento humano. Solo la frase
  "anular matrícula" va a `devolucion`, que tiene prioridad (FR-011).
- Los infinitivos "inscribir" y "matricular" cubren expresiones como
  "me quiero inscribir" y "me quiero matricular" (además de las formas
  conjugadas ya listadas).
- "cancelar" queda fuera de las listas deliberadamente: en el Perú significa
  "pagar", no "anular".
- Las listas son ampliables por el equipo de ventas sin cambiar la lógica de
  clasificación (FR-014).

## Relaciones con otros artefactos

- Contrato de los endpoints: [contracts/api-mensajes.md](./contracts/api-mensajes.md)
- Escenarios de validación extremo a extremo: [quickstart.md](./quickstart.md)
- Decisiones de diseño: [research.md](./research.md)
