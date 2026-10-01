"""Errores de aplicación y manejadores de excepciones de FastAPI (constitución V).

Al cliente solo se le envían mensajes claros y en español; el detalle completo
de los fallos inesperados queda en el log del servidor, nunca en la respuesta.
"""

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

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


def _campo_del_error(error: dict) -> str | None:
    """Campo implicado; `None` si el problema es el cuerpo completo de la petición."""
    localizacion = error.get("loc") or ()
    if not localizacion:
        return None
    # `("body",)` o `("query",)` sin nombre: el error no es de un campo concreto
    if len(localizacion) == 1 and localizacion[0] in {"body", "query"}:
        return None
    # Los modelos Pydantic informan `("dni",)` y FastAPI añade el prefijo
    # `("body", "dni")`: en ambos casos el campo es el último tramo
    return str(localizacion[-1])


def _respuesta_validacion(request: Request, errores: list) -> JSONResponse:
    """400 con el campo y el motivo del primer error (FR-012, contrato de la API)."""
    if not errores:
        logger.warning("Validación fallida sin detalle en %s", request.url.path)
        return JSONResponse(status_code=400, content=_cuerpo("Datos inválidos"))
    primero = errores[0]
    # El modelo declara los campos en orden `nombre, dni, telefono, texto` y
    # pydantic los informa en ese mismo orden: el primero informado es el correcto.
    # Solo se registran campo, tipo y endpoint: el dict de pydantic incluye la
    # clave `input` con el valor enviado (datos personales) y NUNCA debe llegar
    # al log (T041 — privacidad: ni DNI, ni teléfono, ni nombre, ni texto)
    logger.warning(
        "Validación rechazada en %s %s: campo=%s tipo=%s",
        request.method,
        request.url.path,
        _campo_del_error(primero) or "(cuerpo)",
        primero.get("type", "desconocido"),
    )
    return JSONResponse(
        status_code=400,
        content=_cuerpo(_motivo_del_error(primero), _campo_del_error(primero)),
    )


def _traza_tecnica(exc: Exception) -> str:
    """Traza de pila SIN el mensaje de la excepción.

    El mensaje de un fallo inesperado puede reproducir datos personales
    (p. ej. un error de PostgreSQL que repita el valor que chocó), así que en
    los logs solo se registra dónde falló, nunca qué contenía la petición.
    """
    return "".join(traceback.format_tb(exc.__traceback__)).rstrip()


def registrar_error_interno(contexto: str, exc: Exception) -> None:
    """Error interno sin datos personales: contexto/endpoint, tipo del fallo y traza."""
    traza = _traza_tecnica(exc)
    if traza:
        logger.error("%s: %s\n%s", contexto, type(exc).__name__, traza)
    else:
        logger.error("%s: %s", contexto, type(exc).__name__)


def instalar_manejadores(app: FastAPI) -> None:
    """Registra los manejadores de error de la app: 400 / 409 / 500 (constitución V)."""

    async def _validacion(request: Request, exc) -> JSONResponse:
        return _respuesta_validacion(request, exc.errors())

    # Entrada validada por FastAPI al parsear la petición y por nuestros modelos
    # Pydantic dentro del servicio: ambas rutas responden 400 con campo y motivo
    app.add_exception_handler(RequestValidationError, _validacion)
    app.add_exception_handler(ValidationError, _validacion)

    @app.exception_handler(AppError)
    async def _error_de_negocio(request: Request, exc: AppError) -> JSONResponse:
        # Los mensajes de `AppError` son siempre constantes de la plantilla del
        # contrato (nunca datos de la petición), por eso sí pueden registrarse
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
        # Red de seguridad: detalle técnico en el log (sin mensajes que puedan
        # contener datos personales, T041); el cliente recibe un genérico sin
        # stack traces (constitución V)
        registrar_error_interno(
            f"Error interno en {request.method} {request.url.path}", exc
        )
        return JSONResponse(
            status_code=500, content=_cuerpo("Error interno del servidor")
        )
