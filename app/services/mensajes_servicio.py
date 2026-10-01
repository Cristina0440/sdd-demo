"""Servicio de mensajes: registro con validación, anti-duplicados y clasificación."""

import uuid
from datetime import UTC, datetime

from app.classification.palabras_clave import clasificar
from app.errors import AppError
from app.validation import MensajeRegistro

# Ventana anti-duplicados de 10 segundos, decisión del usuario (FR-016)
VENTANA_DUPLICADOS_SEGUNDOS = 10
MENSAJE_DUPLICADO = (
    "Mensaje duplicado: idéntico a uno registrado en los últimos 10 segundos"
)


class ServicioMensajes:
    """Casos de uso de mensajes sobre el repositorio inyectado en la app."""

    def __init__(self, repositorio) -> None:
        self._repositorio = repositorio

    def registrar(self, datos: dict) -> dict:
        """Valida, descarta duplicados y persiste el mensaje (FR-012, FR-016).

        El orden importa: primero se valida (400 sin tocar el repositorio),
        luego se consulta la ventana de duplicados (409) y solo entonces se
        persiste con id, fecha_hora y clasificación.
        """
        entrada = MensajeRegistro.model_validate(datos)
        duplicado = self._repositorio.buscar_reciente(
            entrada.dni, entrada.texto, VENTANA_DUPLICADOS_SEGUNDOS
        )
        if duplicado is not None:
            raise AppError(409, MENSAJE_DUPLICADO)
        mensaje = {
            "id": str(uuid.uuid4()),
            "nombre": entrada.nombre,
            "dni": entrada.dni,
            "telefono": entrada.telefono,
            "texto": entrada.texto,
            "fecha_hora": datetime.now(UTC)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "clasificacion": clasificar(entrada.texto),
        }
        return self._repositorio.insertar(mensaje)

    def historial(self, dni: str) -> list[dict]:
        """Historial del alumno ordenado; `[]` sin error si no hay mensajes (FR-008)."""
        return self._repositorio.consultar_por_dni(dni)
