"""Repositorio real de mensajes con supabase-py (frontera de datos, constitución III)."""

from datetime import UTC, datetime, timedelta
from typing import Protocol

from supabase import Client, create_client


class RepositorioMensajes(Protocol):
    """Interfaz común: el servicio solo conoce estos métodos (el tests usa el doble)."""

    def insertar(self, mensaje: dict) -> dict:
        """Persiste el mensaje y devuelve la fila guardada."""
        ...

    def buscar_reciente(self, dni: str, texto: str, ventana_segundos: int) -> dict | None:
        """Mensaje idéntico (mismo DNI y mismo texto recortado) dentro de la ventana."""
        ...


class RepositorioMensajesSupabase:
    """Implementación con Supabase (PostgreSQL) usando la service role key."""

    def __init__(self, supabase_url: str, service_role_key: str) -> None:
        # Un único cliente por repositorio; el repositorio es singleton de la app
        self._cliente: Client = create_client(supabase_url, service_role_key)

    def insertar(self, mensaje: dict) -> dict:
        respuesta = self._cliente.table("mensajes").insert(mensaje).execute()
        return respuesta.data[0]

    def buscar_reciente(self, dni: str, texto: str, ventana_segundos: int) -> dict | None:
        limite = datetime.now(UTC) - timedelta(seconds=ventana_segundos)
        respuesta = (
            self._cliente.table("mensajes")
            .select("*")
            .eq("dni", dni)
            .gte(
                "fecha_hora",
                limite.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            )
            .order("fecha_hora", desc=True)
            .execute()
        )
        # El filtro por ventana se hace en SQL; la comparación del texto recortando
        # espacios al inicio y al final se hace aquí, en Python (data-model)
        for fila in respuesta.data:
            if str(fila["texto"]).strip() == texto.strip():
                return fila
        return None
