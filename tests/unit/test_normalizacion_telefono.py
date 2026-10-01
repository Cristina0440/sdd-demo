"""T015 — Normalización de teléfono a celular peruano de 9 dígitos (FR-003)."""

import pytest

from app.validation import normalizar_telefono

MENSAJE_INVALIDO = "El teléfono debe tener exactamente 9 dígitos y empezar por 9"


@pytest.mark.parametrize(
    "entrada",
    [
        "+51 987 654 321",
        "51 987654321",
        "987-654-321",
        "987654321",
    ],
)
def test_normaliza_a_celular_peruano(entrada: str) -> None:
    assert normalizar_telefono(entrada) == "987654321"


@pytest.mark.parametrize(
    "entrada",
    [
        "+34 612 345 678",  # código de país distinto (España)
        "+35161234567",  # otro código de país
        "876543210",  # 9 dígitos pero no empieza por 9
    ],
)
def test_rechaza_telefonos_invalidos(entrada: str) -> None:
    with pytest.raises(ValueError) as info:
        normalizar_telefono(entrada)
    assert str(info.value) == MENSAJE_INVALIDO
