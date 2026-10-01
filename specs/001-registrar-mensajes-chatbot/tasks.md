---

description: "Lista de tareas para la implementación de la feature"
---

# Tareas: Registro e Historial de Mensajes del Chatbot de Ventas

**Entrada**: Documentos de diseño de `/specs/001-registrar-mensajes-chatbot/`

**Prerrequisitos**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/api-mensajes.md](./contracts/api-mensajes.md), [quickstart.md](./quickstart.md)

**Tests**: INCLUIDOS — solicitados explícitamente en la entrada de planificación ("Tests with vitest, mocking Supabase so tests run without a real database") y exigidos por la constitución II. Todos mockean `supabase-js` y usan solo datos ficticios (constitución VII).

**Organización**: Las tareas están agrupadas por historia de usuario para permitir implementación y prueba independientes de cada una.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: ¿Ejecutable en paralelo? (archivos distintos, sin dependencias)
- **[Historia]**: Historia de usuario a la que pertenece (p. ej. US1, US2, US3)
- Cada descripción incluye la ruta exacta del archivo

## Convención de rutas

- **Proyecto único**: `src/`, `tests/`, `db/` en la raíz del repositorio (según plan.md)

## Fase 1: Inicialización (Infraestructura compartida)

**Propósito**: Inicialización del proyecto y estructura básica

- [ ] T001 Crear `package.json` con los scripts `dev` (tsx watch), `build`, `start` y `test` (vitest) según research D10 en `package.json`
- [ ] T002 Instalar dependencias en un solo paso: `express`, `@supabase/supabase-js`, `zod`, `dotenv` + dev: `typescript`, `tsx`, `vitest`, `supertest`, `@types/node`, `@types/express`, `@types/supertest` en `package.json`
- [ ] T003 [P] Crear la configuración estricta de TypeScript en `tsconfig.json`
- [ ] T004 [P] Configurar vitest (entorno node, patrón `tests/**/*.test.ts`) en `vitest.config.ts`
- [ ] T005 [P] Crear `.env.example` con `SUPABASE_URL=` y `SUPABASE_SERVICE_ROLE_KEY=` (valores vacíos, sin secretos reales) y asegurar que `.env` figure en `.gitignore`

**Punto de control**: El proyecto compila y `npm test` se ejecuta (sin tests aún, en verde).

---

## Fase 2: Fundacional (Prerrequisitos bloqueantes)

**Propósito**: Infraestructura base que DEBE estar lista ANTES de cualquier historia de usuario

**?? CRÍTICO**: No puede empezar ninguna historia de usuario hasta completar esta fase

- [ ] T006 [P] Crear la tabla `mensajes` en `db/schema.sql` con columnas `id uuid PK`, `nombre text`, `dni char(8)`, `telefono char(9)`, `texto text`, `fecha_hora timestamptz`, `clasificacion text`, con los CHECK verbatim de data-model.md — `dni ~ '^[0-9]{8}$'`, `telefono ~ '^[0-9]{9}$'`, `length(btrim(texto)) > 0`, `clasificacion IN ('informacion_ciclo','devolucion','interes_inscripcion','otro')` — e índice `(dni, fecha_hora DESC)` en `db/schema.sql`
- [ ] T007 [P] Implementar la carga de `.env` y su validación con zod, fallando el arranque con un mensaje claro que indique la variable que falta (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`), en `src/config/entorno.ts`
- [ ] T008 [P] Implementar `AppError` (código HTTP + mensaje + campo opcional) y el middleware de errores de Express: 400 validación, 409 duplicado, 500 genérico con el detalle solo en el log del servidor, sin stack traces al cliente, en `src/errores.ts`
- [ ] T009 Crear la app Express (parser de JSON, middleware de errores de T008, sin rutas aún) en `src/app.ts` y el punto de entrada que lee el entorno y escucha en `src/index.ts` (depende de T007, T008)

**Punto de control**: Base lista — las historias de usuario ya pueden empezar en paralelo.

---

## Fase 3: Historia de usuario 1 - Registrar un mensaje nuevo con validación (Prioridad: P1)

**Objetivo**: El chatbot envía un mensaje; el servicio valida (`nombre` no vacío, DNI 8 dígitos, teléfono 9 dígitos, texto no vacío), rechaza duplicados dentro de 10 s y guarda con `id`, `fecha_hora` y `clasificacion` (valor temporal `"otro"` hasta que US3 instale el clasificador — FR-009).

> Nota: este incremento es la base técnica; el **MVP funcional (objetivo de negocio) es US1 + US3** — ver *Estrategia de implementación* al final.

**Prueba independiente**: `POST /mensajes` con datos válidos → `201` con id/fecha_hora; datos inválidos → `400` sin persistir; mismo body dentro de 10 s → `409`. Todo con repositorio mockeado y `npm test` sin base de datos.

### Pruebas para la historia de usuario 1 (solicitados)

> **NOTA: Escribir estos tests PRIMERO y verificar que FALLAN antes de implementar**

- [ ] T010 [P] [US1] Test de contrato: POST `/mensajes` con body válido cuyo texto sea "Hola, buenas tardes" (sin palabras clave, para que la expectativa `clasificacion: "otro"` siga siendo válida tras US3) → `201` con `id`, `fecha_hora`, `clasificacion: "otro"`, en `tests/contract/mensajes-post.test.ts`
- [ ] T011 [P] [US1] Test de contrato: POST rechaza `nombre` vacío («no vacío»), `dni` "12345" («exactamente 8 dígitos»), `telefono` "61234567X" («exactamente 9 dígitos») y `texto` "   " («no vacío ni solo espacios») con `400` + `campo`, y el repositorio NUNCA recibe `insertar`, en `tests/contract/mensajes-post-validacion.test.ts`
- [ ] T012 [P] [US1] Test de contrato: POST idéntico (mismo dni + mismo texto tras `trim`) dentro de la ventana de 10 segundos → `409`, sin guardar; fuera de la ventana → `201`, en `tests/contract/mensajes-post-duplicado.test.ts`
- [ ] T013 [P] [US1] Test unitario del esquema zod de registro: `«nombre: obligatorio, no vacío (tras trim)»`, `«dni: exactamente 8 dígitos numéricos ^[0-9]{8}$»`, `«telefono: exactamente 9 dígitos numéricos ^[0-9]{9}$»` tras normalizar, `«texto: no vacío ni solo espacios en blanco»`, en `tests/unit/mensaje-esquema.test.ts`
- [ ] T014 [P] [US1] Test unitario de normalización de teléfono: `+34 612 345 678` → `612345678` válido; `+35161234567` → rechazado, en `tests/unit/normalizacion-telefono.test.ts`

### Implementación para la historia de usuario 1

- [ ] T015 [US1] Implementar el esquema zod de registro con las reglas verbatim de T013, incluida la de `nombre` (FR-017), rechazando antes de persistir nada (FR-012), en `src/validacion/mensaje-esquema.ts`
- [ ] T016 [US1] Implementar la interfaz del repositorio + el cliente `supabase-js` (cliente único, service key del entorno) con `insertar(mensaje)` y `buscarReciente(dni, texto, ventanaSegundos)` (para la ventana de 10 s, FR-016), en `src/repositorios/mensajes-repositorio.ts`
- [ ] T017 [US1] Implementar `registrar()`: valida con T015 → consulta duplicados (→ `AppError` 409) → asigna `id` uuid y `fecha_hora` del servidor → `clasificacion: "otro"` temporal → persiste, en `src/servicios/mensajes-servicio.ts`
- [ ] T018 [US1] Implementar la ruta `POST /mensajes` y registrarla en la app, en `src/rutas/mensajes-ruta.ts` (y editar `src/app.ts`)
- [ ] T019 [US1] Test de integración: flujo completo con repositorio falso en memoria — el registro válido queda guardado, el inválido no toca el repositorio, en `tests/integration/registrar-mensaje.test.ts`

**Punto de control**: En este punto la historia de usuario 1 debe funcionar y probarse de forma independiente (incremento base).

---

## Fase 4: Historia de usuario 2 - Consultar el historial de un alumno por DNI (Prioridad: P2)

**Objetivo**: `GET /mensajes?dni=` devuelve solo los mensajes de ese DNI, del más reciente al más antiguo (`fecha_hora DESC`, desempate `id DESC`) y lista vacía `[]` sin error si no hay mensajes (FR-007/008).

**Prueba independiente**: Registrar 3 mensajes ficticios del mismo DNI (vía servicio o repo falso) y consultar → `200` con los 3 ordenados; DNI sin mensajes → `200 []`; DNI inválido → `400`.

### Pruebas para la historia de usuario 2 (solicitados)

> **NOTA: Escribir estos tests PRIMERO y verificar que FALLAN antes de implementar**

- [ ] T020 [P] [US2] Test de contrato: GET con dni válido → `200` con lista ordenada por `fecha_hora` descendente y sin mensajes de otros DNIs, en `tests/contract/mensajes-get.test.ts`
- [ ] T021 [P] [US2] Test de contrato: GET sin `dni` o con `dni` ≠ 8 dígitos → `400` con `campo: "dni"`; dni sin mensajes → `200` con `[]`, en `tests/contract/mensajes-get-validacion.test.ts`
- [ ] T022 [P] [US2] Test unitario del orden estable: dos mensajes con la misma `fecha_hora` se devuelven siempre en el mismo orden y sin pérdidas, en `tests/unit/orden-historial.test.ts`

### Implementación para la historia de usuario 2

- [ ] T023 [US2] Añadir el esquema de consulta `dni: «exactamente 8 dígitos numéricos ^[0-9]{8}$»` (falta o inválido → `400`) en `src/validacion/mensaje-esquema.ts`
- [ ] T024 [US2] Añadir `consultarPorDni(dni)` con la consulta «WHERE dni = … ORDER BY fecha_hora DESC, id DESC» (FR-007/008) en `src/repositorios/mensajes-repositorio.ts`
- [ ] T025 [US2] Añadir `historial(dni)` en el servicio, devolviendo `[]` (sin error) cuando no hay mensajes, en `src/servicios/mensajes-servicio.ts`
- [ ] T026 [US2] Implementar la ruta `GET /mensajes?dni=` en `src/rutas/mensajes-ruta.ts`
- [ ] T027 [US2] Test de integración: registrar 3 mensajes con repositorio falso → historial ordenado del más reciente al más antiguo, sin mensajes de otros DNIs, en `tests/integration/historial-mensajes.test.ts`

**Punto de control**: En este punto las historias de usuario 1 y 2 deben funcionar de forma independiente.

---

## Fase 5: Historia de usuario 3 - Clasificación automática por palabras clave (Prioridad: P3)

**Objetivo**: Clasificar cada mensaje en `informacion_ciclo` | `devolucion` | `interes_inscripcion` | `otro` con prioridad `devolucion > interes_inscripcion > informacion_ciclo > otro` (FR-011), usando las listas del Apéndice A de data-model.md, normalizando mayúsculas/acentos y comparando por palabra o frase con límites de palabra; sustituye el `"otro"` temporal de US1. **Obligatoria para el MVP funcional** (las devoluciones y matrículas deben escalarse a un asesor).

**Prueba independiente**: Registrar textos ficticios con palabras clave de cada categoría → `201` con `clasificacion` esperada; texto mixto → `devolucion`; "devolucionista" → NO clasifica como `devolucion`.

### Pruebas para la historia de usuario 3 (solicitados)

> **NOTA: Escribir estos tests PRIMERO y verificar que FALLAN antes de implementar**

- [ ] T028 [P] [US3] Test unitario de clasificación por categoría con las listas del Apéndice A de data-model.md ("devolución"/"reembolso" → `devolucion`, "ciclo"/"horario"/"turno" → `informacion_ciclo`, "inscribirme"/"matricularme"/"separar vacante" → `interes_inscripcion`, sin palabras clave → `otro`), en `tests/unit/clasificacion.test.ts`
- [ ] T029 [P] [US3] Test unitario de prioridad ante texto mixto (FR-011: `devolucion` > `interes_inscripcion` > `informacion_ciclo` > `otro`, p. ej. "anular matrícula" → `devolucion`) y de tolerancia a mayúsculas/acentos ("DEVOLUCIÓN" → `devolucion`), en `tests/unit/clasificacion-prioridad.test.ts`
- [ ] T030 [P] [US3] Test unitario de palabra o frase con límites: "devolucionista" NO clasifica como `devolucion`, en `tests/unit/clasificacion-palabra-completa.test.ts`
- [ ] T031 [P] [US3] Test de contrato: POST devuelve `clasificacion` correcta según el texto (devoluciones e interés en inscripción quedan marcados para asesor, nunca como `"otro"`), en `tests/contract/mensajes-post-clasificacion.test.ts`

### Implementación para la historia de usuario 3

- [ ] T032 [P] [US3] Implementar las listas de palabras clave por categoría del Apéndice A de data-model.md (ampliables sin cambiar la lógica, FR-014), la normalización (minúsculas, sin acentos) y la coincidencia por palabra/frase con límites según research D3, en `src/clasificacion/palabras-clave.ts`
- [ ] T033 [US3] Implementar la resolución de prioridad `devolucion > interes_inscripcion > informacion_ciclo > otro` (FR-011) en `src/clasificacion/palabras-clave.ts`
- [ ] T034 [US3] Sustituir el `"otro"` temporal por `clasificar(texto)` en `registrar()` en `src/servicios/mensajes-servicio.ts` (depende de T032, T033)
- [ ] T035 [US3] Test de integración: registrar textos ficticios de cada categoría y verificar clasificación y marcado para asesor (escenario 5 del quickstart), en `tests/integration/clasificacion-mensajes.test.ts`

**Punto de control**: Todas las historias de usuario deben quedar funcionales de forma independiente.

---

## Fase 6: Pulido y preocupaciones transversales

**Propósito**: Mejoras que afectan a varias historias de usuario

- [ ] T036 [P] Crear el workflow de CI en `.github/workflows/ci.yml` que ejecuta `npm test` en cada push y en cada pull request (constitución II: verificación en la canalización de integración)
- [ ] T037 [P] Escribir el `README.md` en español: prerrequisitos, configuración de `.env`, ejecución de `db/schema.sql` en Supabase, `npm run dev`, `npm test` y validación manual de los 6 escenarios del quickstart (PowerShell en Windows) en `README.md`
- [ ] T038 Ejecutar la validación completa de `quickstart.md` (los 6 escenarios, incluida la comprobación manual de rendimiento de SC-003, + `npm test` en verde sin base de datos real) y corregir discrepancias en `specs/001-registrar-mensajes-chatbot/quickstart.md`
- [ ] T039 Revisión final en `src/`, `tests/`, `README.md` y `db/`: comentarios y docs en español (constitución VI), cero secretos en el repositorio (constitución IV), códigos HTTP correctos (constitución V), todos los tests en verde (constitución II)

---

## Dependencias y orden de ejecución

### Orden por fases

- **Inicialización (Fase 1)**: Sin dependencias — puede empezar de inmediato
- **Fundacional (Fase 2)**: Depende de la Fase 1 de inicialización — BLOQUEA todas las historias
  - T009 depende de T007 + T008
- **Historias de usuario (Fase 3+)**: Todas dependen de la Fase Fundacional
  - Orden recomendado por prioridad: US1 → US3 (obligatorio para el MVP) → US2
  - US2 y US3 comparten archivos con US1 (`mensajes-servicio.ts`, `mensajes-ruta.ts`, `mensajes-repositorio.ts`), por lo que en la práctica se ejecutan en serie sobre esos archivos; sus tests sí son independientes
- **Pulido (Fase final)**: T036 (CI) puede crearse tras la Fase Fundacional; T037–T039 al final

### Dependencias entre historias

- **Historia de usuario 1 (P1)**: Puede empezar tras la Fase Fundacional — sin dependencias de otras historias
- **Historia de usuario 2 (P2)**: Puede empezar tras la Fase Fundacional — usa `insertar` de US1 solo en su test de integración (repositorio falso); endpoint y consulta independientes
- **Historia de usuario 3 (P3)**: Puede empezar tras la Fase Fundacional — `clasificacion/palabras-clave.ts` es un módulo nuevo independiente; solo la línea de integración T034 toca US1. **No demorar: sin US3 no hay MVP funcional**

### Dentro de cada historia

- Tests PRIMERO (deben FALLAR antes de implementar)
- Esquema de validación → repositorio → servicio → ruta → integración
- Historia completa antes de pasar a la siguiente prioridad

### Oportunidades de paralelismo

- T003, T004, T005 (inicialización, archivos distintos)
- T006, T007, T008 (Fundacional, archivos distintos)
- T010–T014 (tests US1, archivos distintos)
- T020–T022 (tests US2, archivos distintos)
- T028–T031 (tests US3, archivos distintos); T032 y T033 van en serie (mismo archivo `palabras-clave.ts`)
- T036 y T037 (archivos distintos)
- Tras la Fase Fundacional, un desarrollador por historia si hay capacidad

---

## Ejemplo de paralelismo: Historia de usuario 1

```text
# Lanzar juntos todos los tests de la historia de usuario 1:
Tarea T010: Test de contrato POST válido → tests/contract/mensajes-post.test.ts
Tarea T011: Test de contrato rechazos 400 → tests/contract/mensajes-post-validacion.test.ts
Tarea T012: Test de contrato duplicado 409 → tests/contract/mensajes-post-duplicado.test.ts
Tarea T013: Test unitario del esquema zod → tests/unit/mensaje-esquema.test.ts
Tarea T014: Test unitario de la normalización de teléfono → tests/unit/normalizacion-telefono.test.ts
```

---

## Estrategia de implementación

### MVP funcional: US1 + US3

> **El MVP mínimo para el objetivo de negocio es US1 + US3**: sin
> clasificación no se escalan las devoluciones ni el interés en inscripción
> a un asesor de ventas, que es la promesa central del feature. US1 aislado
> es solo un incremento técnico (registra y valida), no un MVP desplegable.

1. Completar Fase 1: Inicialización
2. Completar Fase 2: Fundacional (CRÍTICO — bloquea todas las historias)
3. Completar Fase 3: Historia de usuario 1 (incremento base)
4. **Completar Fase 5: Historia de usuario 3 (obligatorio para el MVP)**
5. **PARAR y VALIDAR**: `npm test` en verde — registro, validación, duplicados y clasificación funcionando → MVP funcional listo
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
   - Desarrollador A: US1 (tests T010–T014 en paralelo)
   - Desarrollador B: US3 (`palabras-clave.ts` es independiente desde el minuto uno)
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
- La retención de datos está fuera de alcance (decisión pendiente en spec.md): ninguna tarea implementa purga
