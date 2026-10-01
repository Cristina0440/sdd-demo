# Contrato de la API REST: Mensajes

**Branch**: `001-registrar-mensajes-chatbot` | **Date**: 2026-10-01 | **Spec**: [spec.md](../spec.md)

Contrato de interfaz externa del servicio (lo consumen el chatbot de ventas y
el equipo de ventas). Formato: JSON en request y response. Todas las rutas
descartan datos inválidos sin persistir nada (FR-012).

## Convenciones

- **Content-Type**: `application/json` en peticiones y respuestas (salvo GET
  sin body).
- **Errores**: siempre cuerpo `{"mensaje": "<explicación clara>"}` y, cuando
  aplique, `{"campo": "<nombre del campo inválido>"}`. Nunca se devuelven
  stack traces ni detalles internos (constitución V).
- **Códigos HTTP**: `200` ok · `201` creado · `400` entrada inválida ·
  `409` duplicado · `500` error interno.

---

## POST /mensajes

Registra un mensaje nuevo enviado por el chatbot. Valida, clasifica y guarda.

### Request

```json
{
  "nombre": "Ana Prueba",
  "dni": "12345678",
  "telefono": "987654321",
  "texto": "Quiero información del ciclo"
}
```

| Campo | Tipo | Regla (franja de error) |
|-------|------|--------------------------|
| `nombre` | string | obligatorio, no vacío |
| `dni` | string | obligatorio, exactamente 8 dígitos (FR-002) |
| `telefono` | string | obligatorio, celular peruano: exactamente 9 dígitos que empiezan por 9; se admiten espacios o guiones y un prefijo opcional `+51`/`51` (FR-003) |
| `texto` | string | obligatorio, no vacío ni solo espacios (FR-004) |

### Respuestas

**`201 Created`** — mensaje registrado:

```json
{
  "id": "3f6b2f0e-…",
  "nombre": "Ana Prueba",
  "dni": "12345678",
  "telefono": "987654321",
  "texto": "Quiero información del ciclo",
  "fecha_hora": "2026-10-01T12:34:56.789Z",
  "clasificacion": "informacion_ciclo"
}
```

**`400 Bad Request`** — validación fallida, nada guardado (FR-002/003/004/012):

```json
{ "campo": "dni", "mensaje": "El DNI debe tener exactamente 8 dígitos" }
```

(análogo para `telefono` y `texto`; si fallan varios campos, se informa el
primero en orden: `nombre`, `dni`, `telefono`, `texto`)

**`409 Conflict`** — duplicado: mismo `dni` y mismo `texto` (tras recortar espacios al inicio y al final)
dentro de la ventana de 10 segundos (FR-016), nada guardado:

```json
{ "mensaje": "Mensaje duplicado: idéntico a uno registrado en los últimos 10 segundos" }
```

**`500 Internal Server Error`** — fallo inesperado (p. ej. Supabase
inalcanzable); el detalle completo solo en el log del servidor:

```json
{ "mensaje": "Error interno al registrar el mensaje" }
```

---

## GET /mensajes?dni={dni}

Historial de mensajes de un alumno, del más reciente al más antiguo (FR-007).

### Parámetros de consulta

| Parámetro | Tipo | Regla |
|-----------|------|-------|
| `dni` | string (query, obligatorio) | exactamente 8 dígitos; si falta o es inválido → `400` |

### Respuestas

**`200 OK`** — lista ordenada por `fecha_hora` descendente (desempate por
`id` descendente); solo mensajes de ese DNI (FR-008); vacía —no error— si no
hay mensajes:

```json
[
  {
    "id": "9a1c…",
    "nombre": "Ana Prueba",
    "dni": "12345678",
    "telefono": "987654321",
    "texto": "Quiero información del ciclo",
    "fecha_hora": "2026-10-01T12:34:56.789Z",
    "clasificacion": "informacion_ciclo"
  }
]
```

**`400 Bad Request`** — `dni` ausente o con formato distinto de 8 dígitos:

```json
{ "campo": "dni", "mensaje": "El DNI debe tener exactamente 8 dígitos" }
```

**`500 Internal Server Error`** — fallo inesperado al consultar (p. ej.
Supabase inalcanzable); el detalle completo solo en el log del servidor:

```json
{ "mensaje": "Error interno al consultar el historial" }
```

---

## Catálogo de `clasificacion`

Valores exactos posibles (FR-009), en el orden de prioridad que aplica ante
texto mixto (FR-011): `devolucion` > `interes_inscripcion` >
`informacion_ciclo` > `otro`. El chatbot usa este campo para decidir destino:
`devolucion` e `interes_inscripcion` → asesor de ventas humano;
`informacion_ciclo` y `otro` → el bot responde (FR-015).

## Relaciones con otros artefactos

- Entidades y reglas de datos: [data-model.md](../data-model.md)
- Escenarios de verificación de este contrato: [quickstart.md](../quickstart.md)
