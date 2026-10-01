"""Validación y normalización de la entrada (capa Pydantic — constitución III).

Rechaza cualquier dato inválido **antes** de persistir nada (FR-012) con un
mensaje claro que indica campo y motivo, tal como exige el contrato de la API.
"""

import re

from pydantic import BaseModel, field_validator


def normalizar_telefono(valor: str) -> str:
    """Celular peruano a 9 dígitos, o error.

    Aplica las normalizaciones del data-model, en orden: recortar espacios al
    inicio y al final → eliminar espacios y guiones → eliminar el prefijo
    peruano `+51` o `51` si existe → deben quedar exactamente 9 dígitos
    empezando por 9. Cualquier otro código de país (incluido `+34`) se rechaza.
    """
    limpio = re.sub(r"[\s\-]", "", valor.strip())
    limpio = re.sub(r"^\+?51", "", limpio)
    if re.fullmatch(r"9[0-9]{8}", limpio) is None:
        raise ValueError("El teléfono debe tener exactamente 9 dígitos y empezar por 9")
    return limpio


class MensajeRegistro(BaseModel):
    """Mensaje entrante del chatbot: valida y normaliza cada campo (FR-002/003/004/017)."""

    nombre: str
    dni: str
    telefono: str
    texto: str

    @field_validator("nombre")
    @classmethod
    def _nombre_no_vacio(cls, valor: str) -> str:
        recortado = valor.strip()
        if not recortado:
            raise ValueError("El nombre es obligatorio y no puede estar vacío")
        return recortado

    @field_validator("dni")
    @classmethod
    def _dni_ocho_digitos(cls, valor: str) -> str:
        recortado = valor.strip()
        if re.fullmatch(r"[0-9]{8}", recortado) is None:
            raise ValueError("El DNI debe tener exactamente 8 dígitos")
        return recortado

    @field_validator("telefono")
    @classmethod
    def _telefono_celular_peruano(cls, valor: str) -> str:
        return normalizar_telefono(valor)

    @field_validator("texto")
    @classmethod
    def _texto_no_vacio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El texto no puede estar vacío ni solo espacios en blanco")
        # Se valida recortando pero se conserva tal cual (data-model)
        return valor


class ConsultaHistorial(BaseModel):
    """Cuerpo de `POST /mensajes/consulta`: el DNI a consultar (FR-006)."""

    dni: str

    @field_validator("dni")
    @classmethod
    def _dni_ocho_digitos(cls, valor: str) -> str:
        recortado = valor.strip()
        if re.fullmatch(r"[0-9]{8}", recortado) is None:
            raise ValueError("El DNI debe tener exactamente 8 dígitos")
        return recortado
