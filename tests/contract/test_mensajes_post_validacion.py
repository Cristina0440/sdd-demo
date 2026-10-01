"""T012 — Contrato de POST con datos inválidos → 400 + campo, sin persistir (FR-012)."""

import pytest

from tests.support.cliente import crear_cliente

CUERPO_VALIDO = {
    "nombre": "Ana Prueba",
    "dni": "12345678",
    "telefono": "987654321",
    "texto": "Quiero información del ciclo",
}


@pytest.mark.parametrize(
    ("campo", "valor_invalido"),
    [
        ("nombre", ""),
        ("nombre", "   "),
        ("dni", "12345"),
        ("telefono", "98765432X"),
        ("texto", "   "),
    ],
)
def test_post_invalido_responde_400_con_campo_y_no_persiste(
    campo: str, valor_invalido: str
) -> None:
    cliente, repositorio = crear_cliente()
    cuerpo = {**CUERPO_VALIDO, campo: valor_invalido}

    respuesta = cliente.post("/mensajes", json=cuerpo)

    assert respuesta.status_code == 400
    datos = respuesta.json()
    assert datos["campo"] == campo
    assert isinstance(datos["mensaje"], str) and datos["mensaje"]
    # El repositorio falso NUNCA recibe insertar con datos inválidos
    assert repositorio.insertos == 0
    assert repositorio.mensajes == []


def test_post_sin_cuerpo_responde_400() -> None:
    cliente, repositorio = crear_cliente()

    respuesta = cliente.post("/mensajes", json={})

    assert respuesta.status_code == 400
    assert repositorio.insertos == 0
