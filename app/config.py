"""Carga y validación del entorno `.env` con pydantic-settings (constitución IV)."""

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Entorno(BaseSettings):
    """Variables de entorno obligatorias del servicio; nunca se versionan."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    SUPABASE_URL: str = Field(min_length=1)
    SUPABASE_SERVICE_ROLE_KEY: str = Field(min_length=1)


def obtener_entorno() -> Entorno:
    """Devuelve el entorno validado o falla con un mensaje claro (constitución IV).

    Indica siempre qué variables faltan o están vacías para que quien arranque
    el servicio sepa exactamente qué completar en `.env`.
    """
    try:
        return Entorno()
    except ValidationError as exc:
        afectadas = ", ".join(str(error["loc"][0]) for error in exc.errors())
        raise RuntimeError(
            "El entorno no es válido: variables ausentes o vacías: "
            f"{afectadas}. Copia `.env.example` a `.env` y rellénalas con los "
            "valores del proyecto de Supabase."
        ) from exc
