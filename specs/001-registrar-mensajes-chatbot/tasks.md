---

description: "Lista de tareas para la implementación de la feature"
---

# Tareas: Registro e Historial de Mensajes del Chatbot de Ventas

**Entrada**: Documentos de diseño de `/specs/001-registrar-mensajes-chatbot/`

**Prerrequisitos**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/api-mensajes.md](./contracts/api-mensajes.md), [quickstart.md](./quickstart.md)

**Stack**: Python + FastAPI + `supabase-py` + Pydantic (`pydantic-settings` para `.env`) + pytest/FastAPI `TestClient`, gestionado con **uv** (research D5–D10).

**Tests**: INCLUIDOS — solicitados explícitamente en la entrada de planificación ("Tests with pytest and FastAPI TestClient, using an in-memory fake repository so tests run without a real database") y exigidos por la constitución II. Todos usan el repositorio falso en memoria en lugar de `supabase-py` y solo datos ficticios (constitución VII).

**Organización**: Las tareas están agrupadas por historia de usuario para permitir implementación y prueba independientes de cada una.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: ¿Ejecutable en paralelo? (archivos distintos, sin dependencias)
- **[Historia]**: Historia de usuario a la que pertenece (p. ej. US1, US2, US3)
- Cada descripción incluye la ruta exacta del archivo

## Convención de rutas

- **Proyecto único**: `app/`, `tests/`, `db/` en la raíz del repositorio (según plan.md)

---

## Fase 1: Inicialización (Infraestructura compartida)

**Propósito**: Retirar el stack Node.js anterior y dejar el proyecto Python listo con uv

- [ ] T001 Eliminar todos los ficheros y carpetas de Node.js — `src/`, `tests/`, `package.json`, `package-lock.json`, `tsconfig.json`, `vitest.config.mts` y `node_modules/` (en PowerShell: `Remove-Item -Recurse -Force`) — conservando intactos `db/schema.sql`, `specs/`, `.specify/`, `.gitignore` y `.env.example`
- [ ] T002 Crear `pyproject.toml` con el proyecto uv según research D10: `[project]` con Python >=3.12 y dependencias de ejecución `fastapi`, `uvicorn`, `supabase`, `pydantic`, `pydantic-settings`; `[dependency-groups]` de desarrollo con `pytest` y `httpx` (backend del `TestClient`); y `[tool.pytest.ini_options]` con `testpaths = ["tests"]` en `pyproject.toml`
- [ ] T003 [P] Ejecutar `uv sync` para instalar el entorno `.venv` y generar `uv.lock` (versionar `uv.lock` en el repositorio)
- [ ] T004 [P] Actualizar `.gitignore` con los patrones de Python/uv (`.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`), manteniendo `.env` ignorado y `uv.lock` versionado
- [ ] T005 [P] Verificar que `.env.example` contiene `SUPABASE_URL=` y `SUPABASE_SERVICE_ROLE_KEY=` con valores vacíos (sin secretos reales) y que `.env` figura en `.gitignore`

**Punto de control**: `uv sync` instala el proyecto y `uv run pytest` puede invocarse (aún sin tests).

---

## Fase 2: Fundacional (Prerrequisitos bloqueantes)

**Propósito**: Infraestructura base que DEBE estar lista ANTES de cualquier historia de usuario

**⚠️ CRÍTICO**: No puede empezar ninguna historia de usuario hasta completar esta fase

- [ ] T006 [P] Verificar que `db/schema.sql` se mantiene **tal cual** (decisión del usuario: sin cambios) y que sus CHECK coinciden con los de data-model.md — `dni ~ '^[0-9]{8}$'`, `telefono ~ '^9[0-9]{8}$'`, `length(btrim(texto)) > 0`, `clasificacion IN ('informacion_ciclo','devolucion','interes_inscripcion','otro')` — e índice `(dni, fecha_hora DESC)` en `db/schema.sql`
- [ ] T007 [P] Implementar la carga de `.env` con `pydantic-settings` y su validación, fallando el arranque con un mensaje claro que indique la variable que falta (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`), en `app/config.py`
- [ ] T008 [P] Implementar `AppError` (código HTTP + mensaje + campo opcional) y los exception handlers de FastAPI: `RequestValidationError` → 400 con el campo y el motivo, `AppError` 409 para duplicados, 500 genérico con el detalle solo en el log del servidor y sin stack traces al cliente (constitución V), en `app/errors.py`
- [ ] T009 [P] Crear el repositorio falso en memoria con `insertar(mensaje)` y `buscar_reciente(dni, texto, ventana_segundos)` (misma interfaz que el repositorio real; base de todos los tests, se amplía en US2) en `tests/support/repositorio_falso.py`
- [ ] T010 Crear la estructura del paquete `app/` (`__init__.py` en cada subpaquete) y `app/main.py` con la fábrica `crear_app(repositorio=None)`: parser de JSON, exception handlers de T008, registro de rutas y validación del entorno de T007 solo cuando se crea la app con el repositorio por defecto (los tests inyectan el falso sin necesitar `.env`) (depende de T007, T008)

**Punto de control**: Base lista — las historias de usuario ya pueden empezar en paralelo.

---

## Fase 3: Historia de usuario 1 - Registrar un mensaje nuevo con validación (Prioridad: P1)

**Objetivo**: El chatbot envía un mensaje; el servicio valida (`nombre` no vacío, DNI 8 dígitos, teléfono 9 dígitos, texto no vacío), rechaza duplicados dentro de 10 s y guarda con `id`, `fecha_hora` y `clasificacion` (valor temporal `"otro"` hasta que US3 instale el clasificador — FR-009).

> Nota: este incremento es la base técnica; el **MVP funcional (objetivo de negocio) es US1 + US3** — ver *Estrategia de implementación* al final.

**Prueba independiente**: `POST /mensajes` con datos válidos → `201` con id/fecha_hora; datos inválidos → `400` sin persistir; mismo body dentro de 10 s → `409`. Todo con repositorio falso en memoria y `uv run pytest` sin base de datos.

### Pruebas para la historia de usuario 1 (solicitados)

> **NOTA: Escribir estos tests PRIMERO y verificar que FALLAN antes de implementar**

- [ ] T011 [P] [US1] Test de contrato: POST `/mensajes` con body válido cuyo texto sea "Hola, buenas tardes" (sin palabras clave, para que la expectativa `clasificacion: "otro"` siga siendo válida tras US3) → `201` con `id`, `fecha_hora`, `clasificacion: "otro"`, usando `TestClient` con el repositorio falso, en `tests/contract/test_mensajes_post.py`
- [ ] T012 [P] [US1] Test de contrato: POST rechaza `nombre` vacío («no vacío»), `dni` "12345" («exactamente 8 dígitos»), `telefono` "98765432X" («celular peruano de 9 dígitos») y `texto` "   " («no vacío ni solo espacios») con `400` + `campo`, y el repositorio falso NUNCA recibe `insertar`, en `tests/contract/test_mensajes_post_validacion.py`
- [ ] T013 [P] [US1] Test de contrato: POST idéntico (mismo dni + mismo texto tras `strip()`) dentro de la ventana de 10 segundos → `409`, sin guardar; fuera de la ventana → `201`, en `tests/contract/test_mensajes_post_duplicado.py`
- [ ] T014 [P] [US1] Test unitario del modelo Pydantic de registro: `«nombre: obligatorio, no vacío (tras strip)»`, `«dni: exactamente 8 dígitos numéricos ^[0-9]{8}$»`, `«telefono: celular peruano, exactamente 9 dígitos numéricos ^9[0-9]{8}$»` tras normalizar, `«texto: no vacío ni solo espacios en blanco»`, en `tests/unit/test_modelo_registro.py`
- [ ] T015 [P] [US1] Test unitario de normalización de teléfono: `+51 987 654 321` / `51 987654321` / `987-654-321` → `987654321` válido; `+34 612 345 678`, `+35161234567` y `876543210` (no empieza por 9) → rechazados, en `tests/unit/test_normalizacion_telefono.py`

### Implementación para la historia de usuario 1

- [ ] T016 [US1] Implementar el modelo Pydantic de registro con las reglas verbatim de T014, incluida la de `nombre` (FR-017), con los validadores/normalizadores de teléfono (T015), rechazando antes de persistir nada (FR-012), en `app/validation.py`
- [ ] T017 [US1] Implementar el `Protocol` del repositorio + la implementación con `supabase-py` (cliente único `create_client` con la service key del entorno) con `insertar(mensaje)` y `buscar_reciente(dni, texto, ventana_segundos)` (para la ventana de 10 s, FR-016), con los mismos nombres de método que el falso de T009, en `app/repositories/mensajes_repositorio.py`
- [ ] T018 [US1] Implementar `registrar()`: valida con T016 → consulta duplicados (→ `AppError` 409) → asigna `id` uuid y `fecha_hora` del servidor → `clasificacion: "otro"` temporal → persiste, en `app/services/mensajes_servicio.py`
- [ ] T019 [US1] Implementar la ruta `POST /mensajes` y registrarla en la app, en `app/routes/mensajes_ruta.py` (y editar `app/main.py`)
- [ ] T020 [US1] Test de integración: flujo completo con el repositorio falso en memoria — el registro válido queda guardado, el inválido no toca el repositorio, en `tests/integration/test_registrar_mensaje.py`

**Punto de control**: En este punto la historia de usuario 1 debe funcionar y probarse de forma independiente (incremento base).

---

## Fase 4: Historia de usuario 2 - Consultar el historial de un alumno por DNI (Prioridad: P2)

**Objetivo**: `GET /mensajes?dni=` devuelve solo los mensajes de ese DNI, del más reciente al más antiguo (`fecha_hora DESC`, desempate `id DESC`) y lista vacía `[]` sin error si no hay mensajes (FR-007/008).

**Prueba independiente**: Registrar 3 mensajes ficticios del mismo DNI (vía servicio o repositorio falso) y consultar → `200` con los 3 ordenados; DNI sin mensajes → `200 []`; DNI inválido → `400`.

### Pruebas para la historia de usuario 2 (solicitados)

> **NOTA: Escribir estos tests PRIMERO y verificar que FALLAN antes de implementar**

- [ ] T021 [P] [US2] Test de contrato: GET con dni válido → `200` con lista ordenada por `fecha_hora` descendente y sin mensajes de otros DNIs, en `tests/contract/test_mensajes_get.py`
- [ ] T022 [P] [US2] Test de contrato: GET sin `dni` o con `dni` ≠ 8 dígitos → `400` con `campo: "dni"`; dni sin mensajes → `200` con `[]`, en `tests/contract/test_mensajes_get_validacion.py`
- [ ] T023 [P] [US2] Test unitario del orden estable: dos mensajes con la misma `fecha_hora` se devuelven siempre en el mismo orden y sin pérdidas, en `tests/unit/test_orden_historial.py`

### Implementación para la historia de usuario 2

- [ ] T024 [US2] Añadir el modelo/parámetro de consulta `dni: «exactamente 8 dígitos numéricos ^[0-9]{8}$»` (falta o inválido → `400`, no `422`) en `app/validation.py`
- [ ] T025 [US2] Añadir `consultar_por_dni(dni)` con la consulta «WHERE dni = … ORDER BY fecha_hora DESC, id DESC» (FR-007/008) a la implementación `supabase-py`, y ampliar el repositorio falso de `tests/support/repositorio_falso.py` con el mismo método, en `app/repositories/mensajes_repositorio.py`
- [ ] T026 [US2] Añadir `historial(dni)` en el servicio, devolviendo `[]` (sin error) cuando no hay mensajes, en `app/services/mensajes_servicio.py`
- [ ] T027 [US2] Implementar la ruta `GET /mensajes?dni=` en `app/routes/mensajes_ruta.py`
- [ ] T028 [US2] Test de integración: registrar 3 mensajes con repositorio falso → historial ordenado del más reciente al más antiguo, sin mensajes de otros DNIs, en `tests/integration/test_historial_mensajes.py`

**Punto de control**: En este punto las historias de usuario 1 y 2 deben funcionar de forma independiente.

---

## Fase 5: Historia de usuario 3 - Clasificación automática por palabras clave (Prioridad: P3)

**Objetivo**: Clasificar cada mensaje en `informacion_ciclo` | `devolucion` | `interes_inscripcion` | `otro` con prioridad `devolucion > interes_inscripcion > informacion_ciclo > otro` (FR-011), usando las listas del Apéndice A de data-model.md, normalizando mayúsculas/acentos y comparando por palabra o frase con límites de palabra; sustituye el `"otro"` temporal de US1. **Obligatoria para el MVP funcional** (las devoluciones y matrículas deben escalarse a un asesor).

**Prueba independiente**: Registrar textos ficticios con palabras clave de cada categoría → `201` con `clasificacion` esperada; texto mixto → `devolucion`; "devolucionista" → NO clasifica como `devolucion`.

### Pruebas para la historia de usuario 3 (solicitados)

> **NOTA: Escribir estos tests PRIMERO y verificar que FALLAN antes de implementar**

- [ ] T029 [P] [US3] Test unitario de clasificación por categoría con las listas del Apéndice A de data-model.md ("devolución"/"reembolso" → `devolucion`, "ciclo"/"horario"/"turno" → `informacion_ciclo`, "inscribirme"/"matricularme"/"separar vacante" → `interes_inscripcion`, sin palabras clave → `otro`), en `tests/unit/test_clasificacion.py`
- [ ] T030 [P] [US3] Test unitario de prioridad ante texto mixto (FR-011: `devolucion` > `interes_inscripcion` > `informacion_ciclo` > `otro`, p. ej. "anular matrícula" → `devolucion`) y de tolerancia a mayúsculas/acentos ("DEVOLUCIÓN" → `devolucion`), en `tests/unit/test_clasificacion_prioridad.py`
- [ ] T031 [P] [US3] Test unitario de palabra o frase con límites: "devolucionista" NO clasifica como `devolucion`, en `tests/unit/test_clasificacion_palabra_completa.py`
- [ ] T032 [P] [US3] Test de contrato: POST devuelve `clasificacion` correcta según el texto (devoluciones e interés en inscripción quedan marcados para asesor, nunca como `"otro"`), en `tests/contract/test_mensajes_post_clasificacion.py`

### Implementación para la historia de usuario 3

- [ ] T033 [P] [US3] Implementar las listas de palabras clave por categoría del Apéndice A de data-model.md (ampliables sin cambiar la lógica, FR-014), la normalización (minúsculas, sin acentos) y la coincidencia por palabra/frase con límites según research D3, en `app/classification/palabras_clave.py`
- [ ] T034 [US3] Implementar la resolución de prioridad `devolucion > interes_inscripcion > informacion_ciclo > otro` (FR-011) en `app/classification/palabras_clave.py`
- [ ] T035 [US3] Sustituir el `"otro"` temporal por `clasificar(texto)` en `registrar()` en `app/services/mensajes_servicio.py` (depende de T033, T034)
- [ ] T036 [US3] Test de integración: registrar textos ficticios de cada categoría y verificar clasificación y marcado para asesor (escenario 5 del quickstart), en `tests/integration/test_clasificacion_mensajes.py`

**Punto de control**: Todas las historias de usuario deben quedar funcionales de forma independiente.

---

## Fase 6: Pulido y preocupaciones transversales

**Propósito**: Mejoras que afectan a varias historias de usuario

- [ ] T037 [P] Crear el workflow de CI en `.github/workflows/ci.yml` que instala uv (`astral-sh/setup-uv`) y ejecuta `uv run pytest` en cada push y en cada pull request (constitución II: verificación en la canalización de integración)
- [ ] T038 [P] Escribir el `README.md` en español: prerrequisitos (Python 3.12+ y uv), configuración de `.env`, ejecución de `db/schema.sql` en Supabase, `uv run uvicorn app.main:app --reload`, `uv run pytest` y validación manual de los 6 escenarios del quickstart (PowerShell en Windows) en `README.md`
- [ ] T039 Ejecutar la validación completa de `quickstart.md` (los 6 escenarios, incluida la comprobación manual de rendimiento de SC-003, + `uv run pytest` en verde sin base de datos real) y corregir discrepancias en `specs/001-registrar-mensajes-chatbot/quickstart.md`
- [ ] T040 Revisión final en `app/`, `tests/`, `README.md` y `db/`: comentarios y docs en español (constitución VI), cero secretos en el repositorio (constitución IV), códigos HTTP correctos (constitución V), todos los tests en verde (constitución II)

---

## Dependencias y orden de ejecución

### Orden por fases

- **Inicialización (Fase 1)**: Sin dependencias — T001 (eliminación del stack Node.js) va primero por decisión del usuario; T003–T005 en paralelo tras T002
- **Fundacional (Fase 2)**: Depende de la Fase 1 de inicialización — BLOQUEA todas las historias
  - T010 depende de T007 + T008
- **Historias de usuario (Fase 3+)**: Todas dependen de la Fase Fundacional
  - Orden recomendado por prioridad: US1 → US3 (obligatorio para el MVP) → US2
  - US2 y US3 comparten archivos con US1 (`app/validation.py`, `app/services/mensajes_servicio.py`, `app/routes/mensajes_ruta.py`, `app/repositories/mensajes_repositorio.py`), por lo que en la práctica se ejecutan en serie sobre esos archivos; sus tests sí son independientes
- **Pulido (Fase final)**: T037 (CI) puede crearse tras la Fase Fundacional; T038–T040 al final

### Dependencias entre historias

- **Historia de usuario 1 (P1)**: Puede empezar tras la Fase Fundacional — sin dependencias de otras historias
- **Historia de usuario 2 (P2)**: Puede empezar tras la Fase Fundacional — usa `insertar` de US1 solo en su test de integración (repositorio falso); endpoint y consulta independientes
- **Historia de usuario 3 (P3)**: Puede empezar tras la Fase Fundacional — `app/classification/palabras_clave.py` es un módulo nuevo independiente; solo la línea de integración T035 toca US1. **No demorar: sin US3 no hay MVP funcional**

### Dentro de cada historia

- Tests PRIMERO (deben FALLAR antes de implementar)
- Modelo de validación → repositorio → servicio → ruta → integración
- Historia completa antes de pasar a la siguiente prioridad

### Oportunidades de paralelismo

- T003, T004, T005 (inicialización, archivos distintos)
- T006, T007, T008, T009 (Fundacional, archivos distintos)
- T011–T015 (tests US1, archivos distintos)
- T021–T023 (tests US2, archivos distintos)
- T029–T032 (tests US3, archivos distintos); T033 y T034 van en serie (mismo archivo `palabras_clave.py`)
- T037 y T038 (archivos distintos)
- Tras la Fase Fundacional, un desarrollador por historia si hay capacidad

---

## Ejemplo de paralelismo: Historia de usuario 1

```text
# Lanzar juntos todos los tests de la historia de usuario 1:
Tarea T011: Test de contrato POST válido → tests/contract/test_mensajes_post.py
Tarea T012: Test de contrato rechazos 400 → tests/contract/test_mensajes_post_validacion.py
Tarea T013: Test de contrato duplicado 409 → tests/contract/test_mensajes_post_duplicado.py
Tarea T014: Test unitario del modelo Pydantic → tests/unit/test_modelo_registro.py
Tarea T015: Test unitario de la normalización de teléfono → tests/unit/test_normalizacion_telefono.py
```

---

## Estrategia de implementación

### MVP funcional: US1 + US3

> **El MVP mínimo para el objetivo de negocio es US1 + US3**: sin
> clasificación no se escalan las devoluciones ni el interés en inscripción
> a un asesor de ventas, que es la promesa central del feature. US1 aislado
> es solo un incremento técnico (registra y valida), no un MVP desplegable.

1. Completar Fase 1: Inicialización (T001 elimina el stack Node.js)
2. Completar Fase 2: Fundacional (CRÍTICO — bloquea todas las historias)
3. Completar Fase 3: Historia de usuario 1 (incremento base)
4. **Completar Fase 5: Historia de usuario 3 (obligatorio para el MVP)**
5. **PARAR y VALIDAR**: `uv run pytest` en verde — registro, validación, duplicados y clasificación funcionando → MVP funcional listo
6. Desplegar/demostrar si está listo

### Entrega incremental

1. Inicialización + Fundacional → base lista
2. Añadir US1 → probar independientemente → incremento técnico
3. Añadir US3 → probar independientemente → **MVP funcional** (devoluciones e intereses escalados)
4. Añadir US2 → probar independientemente → historial consultable
5. Pulido → CI + README + validación quickstart

### Estrategia de equipo en paralelo

1. El equipo completa la Fase de inicialización y la Fundacional juntos
2. Cuando la Fundacional esté lista:
   - Desarrollador A: US1 (tests T011–T015 en paralelo)
   - Desarrollador B: US3 (`app/classification/palabras_clave.py` es independiente desde el minuto uno)
   - Desarrollador C: US2 (tras US1 por los archivos compartidos, o empezando por sus tests)
3. Las historias se completan e integran de forma independiente

---

## Notas

- Las tareas [P] = archivos distintos, sin dependencias
- La etiqueta [Historia] vincula cada tarea con su historia de usuario (trazabilidad)
- Cada historia debe poder completarse y probarse de forma independiente
- Verificar que los tests fallen antes de implementar (constitución II: tests junto al código)
- Hacer commit tras cada tarea o grupo lógico
- Detenerse en cualquier checkpoint para validar la historia
- Solo datos ficticios en tests (constitución VII); comentarios y docs en español (constitución VI)
- Todos los tests corren sin base de datos real: el repositorio falso en memoria sustituye a `supabase-py` en la frontera del repositorio
- `db/schema.sql` se mantiene tal cual (decisión del usuario) — ninguna tarea lo modifica
- La retención de datos está fuera de alcance (decisión pendiente en spec.md): ninguna tarea implementa purga
