"""Ruta POST /mensajes: registro de mensajes del chatbot de ventas."""

from typing import Annotated

from fastapi import APIRouter, Body, Request
from pydantic import ValidationError

from app.errors import AppError, registrar_error_interno
from app.services.mensajes_servicio import ServicioMensajes

router = APIRouter()


@router.post("/mensajes", status_code=201)
def registrar_mensaje(request: Request, datos: Annotated[dict, Body()]) -> dict:
    """Registra un mensaje validado (contrato: 201 / 400 / 409 / 500)."""
    servicio = ServicioMensajes(request.app.state.repositorio)
    try:
        return servicio.registrar(datos)
    except (AppError, ValidationError):
        # Negocio (409) y validación (400): sus manejadores ya responden
        raise
    except Exception as exc:  # noqa: BLE001 — contrato: cualquier fallo inesperado → 500
        # Log técnico sin el mensaje de la excepción (puede contener datos
        # personales, T041); el cliente solo ve el mensaje del contrato
        registrar_error_interno(
            f"Error interno en {request.method} {request.url.path} (registrar)", exc
        )
        raise AppError(500, "Error interno al registrar el mensaje") from None
