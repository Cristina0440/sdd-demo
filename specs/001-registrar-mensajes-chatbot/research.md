# Investigación Técnica: Registro e Historial de Mensajes del Chatbot de Ventas

**Branch**: `001-registrar-mensajes-chatbot` | **Date**: 2026-10-01

Todos los puntos abiertos del contexto técnico quedan resueltos aquí; no
quedan `NEEDS CLARIFICATION` en `plan.md`.

## Decisiones

### D1. Ventana de detección de duplicados: 10 segundos

- **Decisión**: rechazar como duplicado un registro con el mismo DNI y el
  mismo texto (tras `trim`) llegado dentro de los 10 segundos desde la
  fecha/hora del mensaje previo; fuera de esa ventana, registrar como nuevo.
- **Razón**: el usuario fijó explícitamente 10 segundos en la entrada de
  planificación; sustituye a los 60 segundos que asumía el spec, que se
  sincronizó (spec.md actualizado en Clarifications, US1, FR-016, Edge Cases,
  SC-008 y Assumptions).
- **Alternativas consideradas**: ventana de 60 s (descartada: decisión
  explícita del usuario); sin ventana, rechazar todo texto repetido (descartada:
  un alumno puede escribir "hola" legítimamente más tarde).

### D2. Mecanismo anti-duplicados: comprobación previa → HTTP 409

- **Decisión**: antes de insertar, el repositorio busca un mensaje con el
  mismo `dni` y `texto` con `fecha_hora > ahora - 10s`; si existe, se responde
  409 con mensaje claro y no se guarda nada.
- **Razón**: es la solución directa para el caso de uso real (reintentos del
  chatbot), fácil de leer y de testear con el repositorio mockeado
  (constitución I).
- **Alternativas consideradas**: restricción única en la base de datos
  (imposible: una ventana temporal no se expresa como `UNIQUE` estándar);
  bloqueo distribuido/lock (complejidad injustificada para reintentos
  esporádicos); caché en memoria del servicio (pierde estado al reiniciar y
  añade piezas). La ventana de carrera entre dos peticiones idénticas
  simultáneas se acepta como riesgo residual documentado: el objetivo es
  filtrar reintentos, no consensuar escrituras.

### D3. Clasificación por palabras clave con normalización y prioridad fija

- **Decisión**: listas de palabras clave por categoría en un módulo propio
  (`src/clasificacion/palabras-clave.ts`), ampliables sin tocar la lógica
  (FR-014). El texto se normaliza a minúsculas y sin acentos y se compara por
  palabra completa (evita "devolucionista" → "devolucion"). Prioridad:
  `devolucion` > `interes_inscripcion` > `informacion_ciclo` > `otro`
  (FR-011). La clasificación se calcula una sola vez, al registrar.
- **Razón**: es lo que exige el spec y es testeable en unit tests puros con
  vitest.
- **Alternativas consideradas**: clasificador NLP/LLM (coste, respuestas no
  deterministas, complejidad innecesaria para listas cortas de palabras clave);
  expresiones regulares libres por usuario (frágiles y difíciles de revisar).

### D4. Retención: fuera de alcance (decisión pendiente)

- **Decisión**: no se define plazo de conservación ni purga de mensajes en
  esta fase; el diseño de retención a 24 meses se retiró de spec.md,
  data-model.md, contracts/, quickstart.md y tasks.md.
- **Razón**: decisión de alcance tomada en la remediación posterior al
  análisis; queda registrada como decisión pendiente en Assumptions del
  spec y deberá resolverse antes de usar datos personales reales.
- **Alternativas consideradas** (registradas por si se retoma): purga
  periódica desde el servicio, `pg_cron` en Supabase, solo filtro en
  lectura, anonimización in situ.

### D5. Acceso a Supabase: `supabase-js` con service role, solo servidor

- **Decisión**: un único cliente `createClient(url, serviceRoleKey)` creado
  detrás de la interfaz del repositorio; las claves viven en `.env`
  (git-ignored) con `.env.example` sin valores; el arranque valida las
  variables con zod y falla con mensaje claro si faltan.
- **Razón**: la API es de uso interno (chatbot y equipo de ventas), no hay
  navegador de por medio, así que la service key no sale del servidor
  (constitución IV).
- **Alternativas consideradas**: exponer la anon key con RLS (innecesario sin
  cliente web); inyectar claves por otro mecanismo de secretos (fuera de
  alcance para desarrollo local en Windows).

### D6. Mapeo de errores: 400 / 409 / 500 con mensajes claros

- **Decisión**: fallo de validación zod → **400** con el campo y el motivo
  (DNI ≠ 8 dígitos, teléfono ≠ 9 dígitos, texto vacío, duplicado → **409**);
  error inesperado → **500** con mensaje genérico y detalle solo en el log
  del servidor (constitución V). Nunca se guarda nada si la validación falla.
- **Razón**: sigue la constitución y los escenarios de aceptación del spec.
- **Alternativas consideradas**: 422 para reglas semánticas (posible, pero
  todas las reglas de este servicio son de formato en la entrada → 400 es
  suficiente y más simple; se deja documentado por si crece).

### D7. Estrategia de tests: mock en la frontera del repositorio

- **Decisión**: los tests mockean el repositorio (o `supabase-js`) para que
  `npm test` funcione sin base de datos real: unit (clasificación,
  esquemas zod, normalización de teléfono), contract (supertest contra la app
  Express con repositorio falso) e integration (flujo registro → consulta con
  repositorio en memoria). Solo datos ficticios (constitución VII).
- **Razón**: requisito explícito del usuario y permite cubrir los casos
  límite (orden estable, ventana de duplicados, purga) de forma determinista.
- **Alternativas consideradas**: tests contra una base Supabase real
  (incumple el requisito y es frágil en local); contenedor PostgreSQL local
  (añade dependencia pesada para un mock ya suficiente).

### D8. Esquema de la tabla: restricciones en la base + validación en la entrada

- **Decisión**: tabla `mensajes` con `id uuid` PK, `nombre text`,
  `dni char(8)`, `telefono char(9)`, `texto text`, `fecha_hora timestamptz`,
  `clasificacion text` con `CHECK` para cada regla (ver `data-model.md`);
  índice en `(dni, fecha_hora DESC)`. El SQL de creación se entregará en
  `db/schema.sql` (fase de implementación).
- **Razón**: la validación zod es la puerta de entrada (constitución III) y
  los `CHECK` son la red de seguridad que garantiza el invariant aunque
  alguien escriba directamente en la base.
- **Alternativas consideradas**: tipos ENUM de PostgreSQL (más rígidos al
  ampliar categorías, FR-014); tabla `alumnos` separada (el DNI basta como
  identidad derivada; no hay más atributos de alumno — evita joins
  innecesarios).

### D9. Fecha/hora y orden del historial

- **Decisión**: `fecha_hora` la asigna el servidor en el momento del
  registro; el historial ordena por `fecha_hora DESC` y desempata por
  `id DESC` para que el orden sea estable con marcas iguales (escenario US2-2).
- **Razón**: el spec exige "la fecha/hora la asigna el sistema" y un orden
  estable sin perder mensajes.
- **Alternativas consideradas**: usar solo `fecha_hora` (orden no estable
  con empates); contador secuencial (complejidad añadida sin necesidad).

### D10. Ejecución local en Windows

- **Decisión**: `package.json` con scripts `dev` (tsx watch), `build`,
  `start` y `test` (vitest); dotenv carga `.env`; comandos documentados en
  PowerShell en el README (constitución VI).
- **Razón**: requisito explícito del usuario; `tsx` evita pasos manuales de
  compilación en desarrollo.
- **Alternativas consideradas**: `nodemon` + `ts-node` (más piezas); solo
  build compilado en cada cambio (lento en desarrollo).

## Puntos que quedan para fases posteriores

- Contrato de autenticación/autorización de la API: diferido a la
  planificación/seguridad según Assumptions del spec (no bloquea este plan).
- Señales de observabilidad (logs estructurados/métricas): fuera del alcance
  de este plan; el log de errores del servidor (D6) es el mínimo exigido por
  la constitución V.
