# Implementation Plan: Registro e Historial de Mensajes del Chatbot de Ventas

**Branch**: `001-registrar-mensajes-chatbot` | **Date**: 2026-10-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-registrar-mensajes-chatbot/spec.md`

## Summary

Servicio REST que registra los mensajes que los alumnos envían al chatbot de
ventas de una academia (validando DNI de 8 dígitos, celular peruano de 9
dígitos y texto no vacío, con anti-duplicados de 10 segundos), consulta el
historial por DNI ordenado del más reciente al más antiguo, y clasifica cada
mensaje en `informacion_ciclo`, `devolucion`, `interes_inscripcion` u `otro`
para que el chatbot decida qué responde él y qué escala a un asesor de ventas
humano. Enfoque técnico: **Python + FastAPI**, persistencia en Supabase
(PostgreSQL) con `supabase-py`, validación de entrada con **Pydantic**,
configuración del entorno con **pydantic-settings** (`.env` con `.env.example`
sin valores reales), tests con **pytest + FastAPI TestClient** usando un
repositorio falso en memoria (sin base de datos real), proyecto gestionado con
**uv**, SQL de creación de tabla incluido (`db/schema.sql`, sin cambios) y
README en español con pasos para ejecutar en local en Windows.

## Technical Context

**Language/Version**: Python 3.12 o superior (gestionado con uv; compatible con Windows)

**Primary Dependencies**: fastapi (servidor HTTP/ASGI), uvicorn (arranque y recarga en desarrollo), `supabase` (supabase-py, cliente de Supabase), pydantic (validación de entrada), pydantic-settings (carga y validación de `.env`); dev: pytest, httpx (backend del `TestClient` de FastAPI), ruff (análisis estático)

**Storage**: Supabase (PostgreSQL gestionado) mediante `supabase-py`; una única tabla `mensajes` (DDL en `db/schema.sql`, **se mantiene tal cual** — decisión del usuario); credenciales en `.env` con `.env.example` sin valores reales

**Testing**: pytest con FastAPI `TestClient` y un repositorio falso inyectado en la app: tests unitarios (clasificación, modelos Pydantic, normalización de teléfono), de contrato (endpoints contra la app) e integración del servicio — todo sin base de datos real y con solo datos ficticios

**Target Platform**: Servidor web Python ejecutándose en local en Windows para desarrollo (`uv run uvicorn`); desplegable en cualquier entorno Python

**Project Type**: web-service (API REST: `POST /mensajes` y `GET /mensajes?dni=`)

**Performance Goals**: consulta de historial en menos de 2 segundos con hasta 10.000 mensajes almacenados (SC-003)

**Constraints**: validación Pydantic en la capa de entrada única (constitución III); credenciales solo en variables de entorno cargadas con pydantic-settings, nunca en el repositorio (constitución IV); códigos HTTP correctos con mensajes claros (constitución V); documentación y comentarios en español (constitución VI); tests exclusivamente con datos ficticios (constitución VII); ventana anti-duplicados de 10 segundos (decisión del usuario); canalización de CI en Python (`uv run ruff check` + `uv run pytest`)

**Scale/Scope**: hasta 10.000 mensajes; 2 endpoints REST; 1 tabla; listas de palabras clave ampliables sin cambiar la lógica de clasificación (FR-014)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principio (constitución) | Estado | Evidencia en el diseño |
|---|--------------------------|--------|------------------------|
| I | Simplicidad y Legibilidad (NO NEGOCIABLE) | PASS | FastAPI + Pydantic + capas finas (rutas → servicio → repositorio); un solo paquete `app/`; sin ORM (cliente `supabase-py` plano tras un Protocolo de repositorio); nombres de dominio en español coherentes con el spec |
| II | Cobertura de Tests Automatizados (NO NEGOCIABLE) | PASS | pytest cubre validación, clasificación, duplicados, orden del historial y endpoints (TestClient); repositorio falso en memoria para correr sin BD; CI con `uv run pytest` en cada push/PR; los tests se entregan junto al código |
| III | Validación de Entrada | PASS | Pydantic valida body y query en la capa de entrada, una sola vez; dato inválido → rechazo con mensaje claro (400) sin persistir nada |
| IV | Credenciales en Variables de Entorno (NO NEGOCIABLE) | PASS | Claves de Supabase solo en `.env` (git-ignored) con `.env.example` sin valores; pydantic-settings valida las variables y el arranque falla con mensaje claro si falta alguna |
| V | Manejo de Errores con Códigos HTTP Correctos | PASS | 400 entrada inválida (Pydantic), 409 duplicado, 500 error interno con detalle solo en el servidor; mensajes claros sin stack traces, vía exception handlers de FastAPI |
| VI | Documentación y Comentarios en Español | PASS | README en español con pasos para Windows (PowerShell), comentarios en español que expliquen el porqué |
| VII | Solo Datos Ficticios en Pruebas (NO NEGOCIABLE) | PASS | DNIs/teléfonos de prueba ficticios y deterministas (p. ej. `987654321`); repositorio falso en memoria; cero datos reales |

**Gate result**: PASS — sin violaciones; `Complexity Tracking` queda vacío.

**Re-evaluación post-diseño (fase 1)**: PASS — `data-model.md`,
`contracts/api-mensajes.md` y `quickstart.md` no introducen nuevas piezas
(comprobado: repositorio plano con un Protocolo, sin ORM ni abstracciones;
sin purga de retención — fuera de alcance, decisión pendiente; tests sin
datos reales; `db/schema.sql` sin cambios).
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
app/
├── main.py                  # Crea la app FastAPI, registra handlers de error y rutas
├── config.py                # pydantic-settings: carga y valida .env (falla si falta alguna variable)
├── errors.py                # AppError + exception handlers de FastAPI (400/409/500)
├── validation.py            # Modelos Pydantic: registro (body) y consulta (query `dni`)
├── classification/
│   └── palabras_clave.py    # Listas de palabras clave por categoría y prioridad (Apéndice A)
├── services/
│   └── mensajes_servicio.py # Registrar, consultar historial, clasificar
├── repositories/
│   └── mensajes_repositorio.py # Protocolo + implementación supabase-py
└── routes/
    └── mensajes_ruta.py     # POST /mensajes y GET /mensajes?dni=

db/
└── schema.sql               # SQL para crear la tabla en Supabase (sin cambios)

tests/
├── unit/                    # Clasificación, modelos Pydantic, normalización
├── contract/                # Endpoints con TestClient y repositorio falso
├── integration/             # Flujo completo con repositorio falso
└── support/
    └── repositorio_falso.py # Repositorio falso en memoria (inyectado en la app)

pyproject.toml + uv.lock     # Proyecto uv: dependencias, scripts y config de pytest
.env.example                 # Variables sin valores reales
README.md                    # Instrucciones en español (Windows)
.github/workflows/ci.yml     # CI: uv + `uv run ruff check` + `uv run pytest` en push/PR
```

**Structure Decision**: Proyecto único (web-service) — no hay frontend ni móvil:
un solo paquete `app/` con capas finas (rutas → validación Pydantic → servicio →
repositoritorio), `db/schema.sql` para el DDL de Supabase (tal cual) y `tests/`
dividido en unit/contract/integration con un repositorio falso reutilizable en
`tests/support/`. La app se construye con una función `crear_app(repositorio=None)`
para que los tests inyecten el repositorio falso sin tocar la configuración real.
Gestión con uv (`uv sync`, `uv run ...`); el archivo `uv.lock` se versiona y
`.venv/` va en `.gitignore` (constitución I: simplicidad).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| *(sin violaciones — Constitution Check en PASS)* | — | — |
