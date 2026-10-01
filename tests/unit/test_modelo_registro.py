"""T014 — Reglas verbatim del modelo de registro (data-model, US1)."""

import pytest
from pydantic import ValidationError

from app.validation import MensajeRegistro

VALIDO = {
    "nombre": "Ana Prueba",
    "dni": "12345678",
    "telefono": "987654321",
    "texto": "Quiero información del ciclo",
}


def _mensaje(**cambios) -> MensajeRegistro:
    return MensajeRegistro.model_validate({**VALIDO, **cambios})


def _primero(exc: ValidationError) -> dict:
    return exc.errors()[0]


def _motivo(exc: ValidationError) -> str:
    primero = _primero(exc)
    causa = (primero.get("ctx") or {}).get("error")
    return str(causa) if causa is not None else primero["msg"]


def test_campos_obligatorios() -> None:
    with pytest.raises(ValidationError) as info:
        MensajeRegistro.model_validate({"dni": "12345678", "telefono": "987654321"})
    assert _primero(info.value)["type"] == "missing"
    assert "nombre" in _primero(info.value)["loc"]


@pytest.mark.parametrize(
    ("campo", "valor", "esperado"),
    [
        ("nombre", "", "El nombre es obligatorio y no puede estar vacío"),
        ("nombre", "   ", "El nombre es obligatorio y no puede estar vacío"),
        ("dni", "12345", "El DNI debe tener exactamente 8 dígitos"),
        ("dni", "123456789", "El DNI debe tener exactamente 8 dígitos"),
        ("dni", "1234567a", "El DNI debe tener exactamente 8 dígitos"),
        (
            "telefono",
            "98765432X",
            "El teléfono debe tener exactamente 9 dígitos y empezar por 9",
        ),
        (
            "telefono",
            "876543210",
            "El teléfono debe tener exactamente 9 dígitos y empezar por 9",
        ),
        ("texto", "", "El texto no puede estar vacío ni solo espacios en blanco"),
        ("texto", "   ", "El texto no puede estar vacío ni solo espacios en blanco"),
    ],
)
def test_reglas_de_validacion(campo: str, valor: str, esperado: str) -> None:
    with pytest.raises(ValidationError) as info:
        _mensaje(**{campo: valor})
    assert campo in _primero(info.value)["loc"]
    assert _motivo(info.value) == esperado


def test_nombre_se_recorta_al_inicio_y_al_final() -> None:
    assert _mensaje(nombre="  Ana  ").nombre == "Ana"


def test_dni_se_recorta_antes_de_validar() -> None:
    assert _mensaje(dni=" 12345678 ").dni == "12345678"


def test_telefono_se_normaliza_a_nueve_digitos() -> None:
    assert _mensaje(telefono="+51 987 654 321").telefono == "987654321"


def test_texto_se_conserva_tal_cual() -> None:
    """Solo se valida recortando; el texto guardado llega intacto (data-model)."""
    assert _mensaje(texto="  Hola  ").texto == "  Hola  "
