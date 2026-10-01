"""Ruta POST /mensajes: registro de mensajes del chatbot de ventas."""

from typing import Annotated

from fastapi import APIRouter, Body, Request
from pydantic import ValidationError

from app.errors import AppError, registrar_error_interno
from app.services.mensajes_servicio import ServicioMensajes
from app.validation import ConsultaHistorial

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


@router.post("/mensajes/consulta")
def consultar_historial(request: Request, datos: Annotated[dict, Body()]) -> list:
    """Historial ordenado del alumno (contrato: 200 / 400 / 500).

    El DNI va en el cuerpo JSON (principio VIII: nunca en la URL ni en los
    logs de acceso). Falta o formato inválido → 400 con `campo: "dni"`.
    """
    if not isinstance(datos, dict) or not isinstance(datos.get("dni"), str):
        raise AppError(400, "El DNI debe tener exactamente 8 dígitos", campo="dni")
    try:
        entrada = ConsultaHistorial.model_validate(datos)
        servicio = ServicioMensajes(request.app.state.repositorio)
        return servicio.historial(entrada.dni)
    except (AppError, ValidationError):
        # Validación (400): el manejador ya responde con campo y motivo
        raise
    except Exception as exc:  # noqa: BLE001 — contrato: cualquier fallo inesperado → 500
        registrar_error_interno(
            f"Error interno en {request.method} {request.url.path} (consulta)", exc
        )
        raise AppError(500, "Error interno al consultar el historial") from None
