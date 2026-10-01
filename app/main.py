"""Composición de la aplicación FastAPI: fábrica `crear_app` (constitución III)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import obtener_entorno
from app.errors import instalar_manejadores
from app.routes.mensajes_ruta import router as router_mensajes


def _crear_repositorio_por_defecto():
    """Repositorio real de Supabase con las credenciales del entorno (.env)."""
    # Import diferido: solo hace falta al servir con el repositorio por defecto;
    # los tests inyectan el repositorio falso y no lo necesitan nunca
    from app.repositories.mensajes_repositorio import RepositorioMensajesSupabase

    entorno = obtener_entorno()  # si falta una variable, lanza con mensaje claro
    return RepositorioMensajesSupabase(
        supabase_url=entorno.SUPABASE_URL,
        service_role_key=entorno.SUPABASE_SERVICE_ROLE_KEY,
    )


@asynccontextmanager
async def _arranque(aplicacion: FastAPI) -> AsyncIterator[None]:
    """Al arrancar el servidor, conecta el repositorio por defecto si no hay uno inyectado."""
    if aplicacion.state.repositorio is None:
        aplicacion.state.repositorio = _crear_repositorio_por_defecto()
    yield


def crear_app(repositorio=None) -> FastAPI:
    """Crea la app con los manejadores de error; los tests inyectan el falso.

    Con `repositorio=None` (servidor real) el entorno se valida **al arrancar**
    el servidor y no al importar el módulo: así los tests pueden construir la app
    sin tener `.env` configurado (constitución IV).
    """
    aplicacion = FastAPI(
        title="Registro e Historial de Mensajes del Chatbot de Ventas",
        version="0.1.0",
        lifespan=_arranque,
    )
    aplicacion.state.repositorio = repositorio
    instalar_manejadores(aplicacion)
    aplicacion.include_router(router_mensajes)
    return aplicacion


app = crear_app()  # entrada del servidor: `uv run uvicorn app.main:app --reload`
