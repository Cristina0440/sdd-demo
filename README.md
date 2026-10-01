# Registro e Historial de Mensajes - Chatbot de Ventas

## Descripción
Sistema de registro y consulta de mensajes para un chatbot de ventas, construido con Python 3.12+, FastAPI y Supabase. Gestionado con `uv`.

## Requisitos previos

- **Python 3.12 o superior**
- **uv** (gestor de paquetes y entornos)

## Configuración del entorno

1. Clonar el repositorio
2. Ejecutar `uv sync` para instalar las dependencias y crear el entorno `.venv`
3. Copiar `.env.example` a `.env` y completar las variables:
   - `SUPABASE_URL=` — URL de tu instancia Supabase
   - `SUPABASE_SERVICE_ROLE_KEY=` — Service role key de Supabase
4. Verificar que `.env` está en `.gitignore` (hecho automáticamente por `.gitignore`)

## Base de datos

Ejecutar el esquema de Supabase:

```powershell
# En la raíz del proyecto
sqlcmd -S <tu-servidor> -i db/schema.sql
```

O mediante la consola de Supabase Dashboard.

## Ejecutar la aplicación

```powershell
uv run uvicorn app.main:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

## Ejecutar tests

```powershell
uv run pytest
```

Todos los tests usan un repositorio falso en memoria, por lo que **no requieren base de datos real**.

## Escenarios del quickstart (validación manual)

Los 6 escenarios del `quickstart.md` pueden validarse manualmente con PowerShell:

1. **Registro válido** — POST `/mensajes` con datos completos → `201`
2. **Nombre vacío** — debe devolver `400` con `campo: "nombre"`
3. **DNI inválido** — distinto de 8 dígitos → `400` con `campo: "dni"`
4. **Teléfono inválido** — no cumple patrón peruano → `400` con `campo: "telefono"`
5. **Texto vacío** — debe devolver `400` con `campo: "texto"`
6. **Duplicado dentro de 10 s** — mismo DNI + mismo texto (tras recortar espacios) → `409`

También validar que `POST /mensajes/consulta` devuelve el historial ordenado por DNI.

## Workflow de CI

El repositorio incluye un workflow de CI en `.github/workflows/ci.yml` que, en cada push y pull request:

- Instala `uv` y las dependencias
- Ejecuta `ruff check .` (análisis estático)
- Ejecuta `pytest` (tests unitarios y de contrato con repositorio falso)

## Licencia

Ver `LICENSE` o contactar al equipo de desarrollo.