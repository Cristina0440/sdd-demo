"""Errores de aplicación y manejadores de excepciones de FastAPI (constitución V).

Al cliente solo se le envían mensajes claros y en español; el detalle completo
de los fallos inesperados queda en el log del servidor, nunca en la respuesta.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Error de negocio: código HTTP, mensaje claro y campo opcional (constitución V)."""

    def __init__(self, status_code: int, mensaje: str, campo: str | None = None) -> None:
        super().__init__(mensaje)
        self.status_code = status_code
        self.mensaje = mensaje
        self.campo = campo


def _cuerpo(mensaje: str, campo: str | None = None) -> dict[str, str]:
    """Cuerpo de error según el contrato: `mensaje` y `campo` solo cuando aplica."""
    if campo is None:
        return {"mensaje": mensaje}
    return {"campo": campo, "mensaje": mensaje}


def _motivo_del_error(error: dict) -> str:
    """Redacta en español el motivo de un error de validación (contrato de la API)."""
    tipo = error.get("type", "")
    if tipo == "missing":
        return "El campo es obligatorio"
    if tipo == "json_invalid":
        return "El cuerpo de la petición debe ser JSON válido"
    if tipo == "string_type":
        return "El campo debe ser texto"
    # Validadores propios: lanzan `ValueError` con el motivo ya redactado en español
    causa = (error.get("ctx") or {}).get("error")
    if causa is not None:
        return str(causa)
    return str(error.get("msg") or "El valor enviado no es válido")


def instalar_manejadores(app: FastAPI) -> None:
    """Registra los manejadores de error de la app: 400 / 409 / 500 (constitución V)."""

    @app.exception_handler(RequestValidationError)
    async def _validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
        errores = exc.errors()
        if not errores:
            logger.warning("Validación fallida sin detalle en %s", request.url.path)
            return JSONResponse(status_code=400, content=_cuerpo("Datos inválidos"))
        primero = errores[0]
        # El modelo declara los campos en orden `nombre, dni, telefono, texto`:
        # pydantic respeta ese orden, así que el primero informado es el correcto
        localizacion = primero.get("loc") or ()
        campo = str(localizacion[-1]) if len(localizacion) > 1 else None
        logger.warning(
            "Entrada inválida en %s %s: %s", request.method, request.url.path, primero
        )
        return JSONResponse(
            status_code=400, content=_cuerpo(_motivo_del_error(primero), campo)
        )

    @app.exception_handler(AppError)
    async def _error_de_negocio(request: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error(
                "AppError %s en %s %s: %s",
                exc.status_code,
                request.method,
                request.url.path,
                exc.mensaje,
            )
        return JSONResponse(
            status_code=exc.status_code, content=_cuerpo(exc.mensaje, exc.campo)
        )

    @app.exception_handler(Exception)
    async def _error_interno(request: Request, exc: Exception) -> JSONResponse:
        # Red de seguridad: el detalle completo solo en el log del servidor;
        # el cliente recibe un mensaje genérico sin stack traces (constitución V)
        logger.exception("Error interno en %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500, content=_cuerpo("Error interno del servidor")
        )
