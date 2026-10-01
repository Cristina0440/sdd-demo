# Quickstart: guía de validación local (Windows)

**Branch**: `001-registrar-mensajes-chatbot` | **Date**: 2026-10-01 | **Spec**: [spec.md](./spec.md)

Guía para ejecutar el servicio en local y comprobarlo extremo a extremo.
No incluye implementación: los contratos están en
[contracts/api-mensajes.md](./contracts/api-mensajes.md) y las reglas de datos
en [data-model.md](./data-model.md).

## Requisitos previos

- Node.js 20 LTS o superior y npm (comprobar: `node --v`, `npm -v`).
- Una cuenta de Supabase con un proyecto creado (https://supabase.com).
- Terminal PowerShell (Windows).

## Puesta en marcha

```powershell
# 1. Instalar dependencias
npm install

# 2. Crear el archivo de entorno a partir de la plantilla (sin valores reales)
Copy-Item .env.example .env
#    Editar .env y rellenar la URL del proyecto y la service role key de Supabase

# 3. Crear la tabla: pegar y ejecutar db/schema.sql en el SQL Editor de Supabase

# 4. Arrancar en desarrollo (http://localhost:3000 por defecto)
npm run dev
```

Si falta alguna variable obligatoria en `.env`, el servicio debe arrancar con
un mensaje claro indicando cuál (constitución IV).

## Ejecutar los tests (sin base de datos real)

```powershell
npm test
```

**Resultado esperado**: todos los tests en verde con `supabase-js` mockeado y
solo datos ficticios (constitución VII).

## Escenarios de validación manual

Referencias: contratos en [contracts/api-mensajes.md](./contracts/api-mensajes.md).

### 1. Registrar un mensaje válido (US1)

`POST /mensajes` con `{"nombre":"Ana Prueba","dni":"12345678","telefono":"612345678","texto":"Quiero información del ciclo"}`

→ Esperado: `201` con `id`, `fecha_hora` y `clasificacion: "informacion_ciclo"`.

### 2. Rechazar datos inválidos (US1, FR-002/003/004)

- DNI `"12345"` → esperado `400`, campo `dni`, y el mensaje NO se guarda.
- Teléfono `"61234567X"` → esperado `400`, campo `telefono`.
- Texto `"   "` → esperado `400`, campo `texto`.

### 3. Rechazar duplicado dentro de 10 s (FR-016)

Reenviar exactamente el mismo body del paso 1 en menos de 10 segundos →
esperado `409` y una única fila en la base. Repetir el mismo texto pasados
10 s → esperado `201` (mensaje nuevo).

### 4. Consultar historial ordenado (US2, FR-007)

Registrar 3 mensajes con el mismo DNI y distintos textos, luego
`GET /mensajes?dni=12345678` → esperado `200` con los 3 mensajes del más
reciente al más antiguo. `GET /mensajes?dni=87654321` (sin mensajes) →
esperado `200` con `[]`. `GET /mensajes?dni=123` → esperado `400`.

### 5. Clasificación y destino bot/asesor (US3, FR-009/011/015)

Registrar textos con palabras clave de cada categoría y comprobar en la
respuesta `201`:

| Texto de prueba (ficticio) | `clasificacion` esperada | Destino |
|----------------------------|--------------------------|---------|
| "Quiero una devolución del curso" | `devolucion` | asesor humano |
| "Me quiero inscribir en el ciclo" | `interes_inscripcion` | asesor humano |
| "¿Cuál es el horario del ciclo?" | `informacion_ciclo` | bot |
| "Gracias, ya lo sé" | `otro` | bot |

Texto mixto con keywords de devolución y de ciclo → `devolucion` (prioridad).

### 6. Rendimiento del historial (SC-003) — validación manual

Insertar 10.000 mensajes ficticios de un mismo DNI en Supabase (SQL de
ejemplo, solo datos ficticios):

```sql
insert into mensajes (nombre, dni, telefono, texto, fecha_hora, clasificacion)
select 'Alumno Ficticio', '11111111', '999999999',
       'mensaje de prueba ' || g,
       now() - (g || ' minutes')::interval,
       'otro'
from generate_series(1, 10000) as g;
```

Luego `GET /mensajes?dni=11111111` y medir el tiempo de respuesta (p. ej.
con `Measure-Command` de PowerShell o las herramientas del navegador) →
esperado: menos de 2 segundos. Validación manual, sin herramienta de carga.

## Criterios de aceptación de la guía

- `npm test` en verde sin red ni base de datos.
- Los 6 escenarios anteriores producen exactamente los resultados esperados.
- `README.md` (en español) reproduce estos pasos para un compañero en Windows.
