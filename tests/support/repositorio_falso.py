"""Repositorio falso en memoria: misma interfaz que el real, sin base de datos.

Es la frontera de sustitución de `supabase-py` en todos los tests: la app
inyecta este doble en lugar del repositorio real para correr sin red ni
Supabase (constitución VII: solo datos ficticios).
"""

import uuid
from datetime import UTC, datetime, timedelta


def _como_datetime(valor: str | datetime) -> datetime:
    """Interpreta una `fecha_hora` ISO8601 en UTC (admite el sufijo `Z`)."""
    if isinstance(valor, datetime):
        momento = valor
    else:
        momento = datetime.fromisoformat(str(valor))
    if momento.tzinfo is None:
        return momento.replace(tzinfo=UTC)
    return momento


class RepositorioFalso:
    """Guarda los mensajes en una lista; implementa la interfaz del repositorio real."""

    def __init__(self) -> None:
        self.mensajes: list[dict] = []
        # Contador de llamadas a `insertar`: los tests de rechazo comprueban
        # que el repositorio jamás recibe datos inválidos (FR-012)
        self.insertos = 0

    def insertar(self, mensaje: dict) -> dict:
        """Añade el mensaje y devuelve la fila guardada.

        Aplica los mismos defaults que `db/schema.sql` (id y fecha_hora) por si
        el mensaje llega incompleto, igual que haría la tabla real.
        """
        self.insertos += 1
        fila = dict(mensaje)
        fila.setdefault("id", str(uuid.uuid4()))
        fila.setdefault(
            "fecha_hora", datetime.now(UTC).isoformat().replace("+00:00", "Z")
        )
        self.mensajes.append(fila)
        return dict(fila)

    def buscar_reciente(self, dni: str, texto: str, ventana_segundos: int) -> dict | None:
        """Devuelve el mensaje idéntico (mismo DNI y mismo texto recortado) dentro
        de la ventana de segundos indicada, o `None` si no hay coincidencia."""
        limite = datetime.now(UTC) - timedelta(seconds=ventana_segundos)
        for mensaje in reversed(self.mensajes):
            coincide_dni = mensaje["dni"] == dni
            coincide_texto = str(mensaje["texto"]).strip() == texto.strip()
            dentro_de_ventana = _como_datetime(mensaje["fecha_hora"]) > limite
            if coincide_dni and coincide_texto and dentro_de_ventana:
                return dict(mensaje)
        return None

    def consultar_por_dni(self, dni: str) -> list[dict]:
        """Todos los mensajes del DNI: fecha_hora DESC con desempate id DESC
        (orden estable), igual que el repositorio real (FR-007/008)."""
        del_alumno = [m for m in self.mensajes if m["dni"] == dni]
        ordenados = sorted(
            del_alumno,
            key=lambda m: (_como_datetime(m["fecha_hora"]), str(m["id"])),
            reverse=True,
        )
        return [dict(m) for m in ordenados]
