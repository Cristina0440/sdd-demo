"""T041 — Los logs de una petición rechazada nunca contienen datos personales.

Regla (decisión del usuario): los registros de validación y de error anotan el
campo, el tipo de error y el endpoint, pero jamás el valor enviado (DNI,
teléfono, nombre o texto del mensaje).
"""

import logging

import pytest

from tests.support.cliente import crear_cliente

# Datos personales ficticios pero deliberadamente distintivos
NOMBRE = "María Ejemplo Quiñones"
DNI_VALIDO = "12345678"
DNI_INVALIDO = "12X45678"
TELEFONO_ENVIADO = "987 654 321"
TELEFONO_NORMALIZADO = "987654321"
TELEFONO_INVALIDO = "+34 612 345 678"
TELEFONO_INVALIDO_DIGITOS = "612345678"
TEXTO = "Confidencial 42"

CUERPO_BASE = {
    "nombre": NOMBRE,
    "dni": DNI_VALIDO,
    "telefono": TELEFONO_ENVIADO,
    "texto": TEXTO,
}

# Ningún valor enviado debe aparecer nunca en el log, en ningún caso
VALORES_PROHIBIDOS = (
    NOMBRE,
    "María",
    "Quiñones",
    DNI_VALIDO,
    DNI_INVALIDO,
    TELEFONO_ENVIADO,
    TELEFONO_NORMALIZADO,
    TELEFONO_INVALIDO,
    TELEFONO_INVALIDO_DIGITOS,
    TEXTO,
)


@pytest.mark.parametrize(
    ("campo", "valor_invalido"),
    [
        ("dni", DNI_INVALIDO),
        ("telefono", TELEFONO_INVALIDO),
    ],
)
def test_peticion_rechazada_no_registra_el_valor_enviado(
    caplog, campo: str, valor_invalido: str
) -> None:
    cliente, repositorio = crear_cliente()

    with caplog.at_level(logging.DEBUG):
        respuesta = cliente.post("/mensajes", json={**CUERPO_BASE, campo: valor_invalido})

    assert respuesta.status_code == 400
    assert repositorio.insertos == 0

    texto_log = caplog.text
    # El registro SÍ anota campo, tipo de error y endpoint...
    assert f"campo={campo}" in texto_log
    assert "tipo=" in texto_log
    assert "POST /mensajes" in texto_log
    # ...pero NUNCA los valores enviados (datos personales)
    for valor_prohibido in VALORES_PROHIBIDOS:
        assert valor_prohibido not in texto_log
