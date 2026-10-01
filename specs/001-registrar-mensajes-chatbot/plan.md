# Implementation Plan: Registro e Historial de Mensajes del Chatbot de Ventas

**Branch**: `001-registrar-mensajes-chatbot` | **Date**: 2026-10-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-registrar-mensajes-chatbot/spec.md`

## Summary

Servicio REST que registra los mensajes que los alumnos envían al chatbot de
ventas de una academia (validando DNI de 8 dígitos, teléfono de 9 dígitos y
texto no vacío, con anti-duplicados de 10 segundos), consulta el historial por
DNI ordenado del más reciente al más antiguo, y clasifica cada mensaje en
`informacion_ciclo`, `devolucion`, `interes_inscripcion` u `otro` para que el
chatbot decida qué responde él y qué escala a un asesor de ventas humano.
Enfoque técnico: Node.js + TypeScript + Express, persistencia en Supabase
(Supabase/PostgreSQL) con `supabase-js`, validación de entrada con `zod`,
tests con `vitest` supabase mockeado (sin base de datos real), SQL de creación
de tabla incluido y README en español con pasos para ejecutar en local en
Windows.

## Technical Context

**Language/Version**: TypeScript 5.x sobre Node.js 20 LTS o superior (LTS activa en Windows)

**Primary Dependencies**: express (servidor HTTP), `@supabase/supabase-js` (cliente de Supabase), zod (validación de entrada y de variables de entorno), dotenv (carga de `.env`); dev: vitest, supertest (tests HTTP), typescript, tsx (arranque en desarrollo)

**Storage**: Supabase (PostgreSQL gestionado) mediante `supabase-js`; una única tabla `mensajes`; credenciales en `.env` con `.env.example` sin valores reales

**Testing**: vitest con `supabase-js` mockeado en la frontera del repositorio: tests unitarios (clasificación, validación), de contrato (endpoints vía supertest) e integración del servicio con repositorio falso — todo sin base de datos real y con solo datos ficticios

**Target Platform**: Servidor web Node.js ejecutándose en local en Windows para desarrollo; desplegable en cualquier entorno Node (p. ej. Supabase-adjacente en la nube)

**Project Type**: web-service (API REST: `POST /mensajes` y `GET /mensajes?dni=`)

**Performance Goals**: consulta de historial en menos de 2 segundos con hasta 10.000 mensajes almacenados (SC-003)

**Constraints**: validación `zod` en la capa de entrada única (constitución III); credenciales solo en variables de entorno, nunca en el repositorio (constitución IV); códigos HTTP correctos con mensajes claros (constitución V); documentación y comentarios en español (constitución VI); tests exclusivamente con datos ficticios (constitución VII); ventana anti-duplicados de 10 segundos (decisión del usuario, sincronizada en spec.md)

**Scale/Scope**: hasta 10.000 mensajes; 2 endpoints REST; 1 tabla; listas de palabras clave ampliables sin cambiar la lógica de clasificación (FR-014)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principio (constitución) | Estado | Evidencia en el diseño |
|---|--------------------------|--------|------------------------|
| I | Simplicidad y Legibilidad (NO NEGOCIABLE) | PASS | Express + zod + una capa de servicio y una de repositorio; sin abstracciones prematuras ni patrones innecesarios; nombres de dominio en español coherentes con el spec |
| II | Cobertura de Tests Automatizados (NO NEGOCIABLE) | PASS | vitest cubre validación, clasificación, duplicados, orden del historial y endpoints (supertest); repositorio mockeado para correr sin BD; los tests se entregan junto al código |
| III | Validación de Entrada | PASS | `zod` valida body y query en la capa de entrada, una sola vez; dato inválido → rechazo con mensaje claro (400) sin persistir nada |
| IV | Credenciales en Variables de Entorno (NO NEGOCIABLE) | PASS | Claves de Supabase solo en `.env` (git-ignored) con `.env.example` sin valores; el arranque falla con mensaje claro si falta alguna variable |
| V | Manejo de Errores con Códigos HTTP Correctos | PASS | 400 entrada inválida (zod), 409 duplicado, 422 regla semántica si aplica, 500 error interno con detalle solo en servidor; mensajes claros sin stack traces |
| VI | Documentación y Comentarios en Español | PASS | README en español con pasos para Windows, comentarios en español que expliquen el porqué |
| VII | Solo Datos Ficticios en Pruebas (NO NEGOCIABLE) | PASS | DNIs/teléfonos de prueba ficticios y deterministas; `supabase-js` mockeado; cero datos reales |

**Gate result**: PASS — sin violaciones; `Complexity Tracking` queda vacío.

**Re-evaluación post-diseño (fase 1)**: PASS — `data-model.md`,
`contracts/api-mensajes.md` y `quickstart.md` no introducen nuevas piezas
(comprobado: repositorio plano con una interfaz, sin ORM ni abstracciones;
sin purga de retención — fuera de alcance, decisión pendiente; tests sin
datos reales).
Los gates siguen en PASS y `Complexity Tracking` permanece vacío.

## Project Structure

### Documentation (this feature)

```text
specs/001-registrar-mensajes-chatbot/
├── plan.md              # Este archivo (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (contrato REST de la API)
│   └── api-mensajes.md
├── checklists/
│   └── requirements.md
├── spec.md
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── index.ts                 # Arranque del servidor (lee env, crea app, escucha)
├── app.ts                   # Configuración de Express y registro de rutas
├── config/
│   └── entorno.ts           # Lectura y validación zod de las variables de .env
├── errores.ts               # Manejo de errores y mapeo a códigos HTTP
├── validacion/
│   └── mensaje-esquema.ts   # Esquemas zod de registro (body) y consulta (query)
├── clasificacion/
│   └── palabras-clave.ts    # Listas de palabras clave por categoría y prioridad
├── servicios/
│   └── mensajes-servicio.ts # Registrar, consultar historial, clasificar, purgar
├── repositorios/
│   └── mensajes-repositorio.ts # Interfaz + implementación supabase-js
└── rutas/
    └── mensajes-ruta.ts     # POST /mensajes y GET /mensajes?dni=

db/
└── schema.sql               # SQL para crear la tabla en Supabase

tests/
├── unit/                    # Clasificación, validación, normalización
├── contract/                # Endpoints con supertest y repositorio mockeado
└── integration/             # Flujo completo con repositorio falso

.env.example                 # Variables sin valores reales
README.md                    # Instrucciones en español (Windows)
```

**Structure Decision**: Proyecto único (web-service) — no hay frontend ni móvil:
un solo árbol `src/` con capas finas (rutas → validación → servicio →
repositorio), `db/schema.sql` para el DDL de Supabase y `tests/` dividido en
unit/contract/integration. Elegimos la estructura de un solo proyecto porque el
alcance es una API con dos endpoints (constitución I: simplicidad).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| *(sin violaciones — Constitution Check en PASS)* | — | — |
