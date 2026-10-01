"""T020 — Integración del registro completo con repositorio falso (US1)."""

from tests.support.cliente import crear_cliente

CUERPO = {
    "nombre": "Ana Prueba",
    "dni": "12345678",
    "telefono": "987654321",
    "texto": "Quiero información del ciclo",
}


def test_registro_valido_queda_guardado_en_el_repositorio() -> None:
    cliente, repositorio = crear_cliente()

    respuesta = cliente.post("/mensajes", json=CUERPO)

    assert respuesta.status_code == 201
    assert repositorio.insertos == 1
    guardado = repositorio.mensajes[0]
    assert guardado["id"]
    assert guardado["fecha_hora"]
    assert guardado["dni"] == "12345678"
    assert guardado["telefono"] == "987654321"
    # US3 (T035) sustituyó el "otro" temporal por la clasificación real
    assert guardado["clasificacion"] == "informacion_ciclo"


def test_registro_invalido_no_toca_el_repositorio() -> None:
    cliente, repositorio = crear_cliente()

    respuesta = cliente.post("/mensajes", json={**CUERPO, "dni": "12345"})

    assert respuesta.status_code == 400
    assert respuesta.json()["campo"] == "dni"
    assert repositorio.insertos == 0
    assert repositorio.mensajes == []


def test_registro_duplicado_no_guarda_una_segunda_fila() -> None:
    cliente, repositorio = crear_cliente()

    assert cliente.post("/mensajes", json=CUERPO).status_code == 201
    assert cliente.post("/mensajes", json=CUERPO).status_code == 409

    assert repositorio.insertos == 1
    assert len(repositorio.mensajes) == 1
