"""T022 — Contrato: POST /mensajes/consulta sin dni o inválido → 400 (US2)."""

from tests.support.cliente import crear_cliente


def test_consulta_sin_dni_responde_400_con_campo_dni() -> None:
    cliente, _ = crear_cliente()

    respuesta = cliente.post("/mensajes/consulta", json={})

    assert respuesta.status_code == 400
    datos = respuesta.json()
    assert datos["campo"] == "dni"
    assert datos["mensaje"] == "El DNI debe tener exactamente 8 dígitos"


def test_consulta_dni_invalido_responde_400_con_campo_dni() -> None:
    cliente, _ = crear_cliente()

    respuesta = cliente.post("/mensajes/consulta", json={"dni": "123"})

    assert respuesta.status_code == 400
    datos = respuesta.json()
    assert datos["campo"] == "dni"
    assert datos["mensaje"] == "El DNI debe tener exactamente 8 dígitos"


def test_consulta_dni_sin_mensajes_responde_200_con_lista_vacia() -> None:
    cliente, _ = crear_cliente()

    respuesta = cliente.post("/mensajes/consulta", json={"dni": "87654321"})

    assert respuesta.status_code == 200
    assert respuesta.json() == []
