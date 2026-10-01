"""T013 — Contrato de duplicados: dentro de la ventana → 409; fuera → 201 (FR-016)."""

from datetime import UTC, datetime, timedelta

from tests.support.cliente import crear_cliente

CUERPO = {
    "nombre": "Ana Prueba",
    "dni": "12345678",
    "telefono": "987654321",
    "texto": "Quiero información del ciclo",
}


def test_duplicado_dentro_de_la_ventana_responde_409_y_no_guarda() -> None:
    cliente, repositorio = crear_cliente()
    primera = cliente.post("/mensajes", json=CUERPO)
    assert primera.status_code == 201

    repetida = cliente.post("/mensajes", json=CUERPO)

    assert repetida.status_code == 409
    assert "duplicado" in repetida.json()["mensaje"].lower()
    assert repositorio.insertos == 1
    assert len(repositorio.mensajes) == 1


def test_duplicado_con_texto_recortado_responde_409() -> None:
    """La comparación recorta espacios al inicio y al final (data-model)."""
    cliente, repositorio = crear_cliente()
    assert cliente.post("/mensajes", json=CUERPO).status_code == 201

    espaciado = {**CUERPO, "texto": f"  {CUERPO['texto']}  "}
    respuesta = cliente.post("/mensajes", json=espaciado)

    assert respuesta.status_code == 409
    assert repositorio.insertos == 1


def test_mismo_mensaje_fuera_de_la_ventana_se_registra() -> None:
    cliente, repositorio = crear_cliente()
    assert cliente.post("/mensajes", json=CUERPO).status_code == 201

    # Envejecemos el guardado 11 s para salir de la ventana de 10 s
    guardado = repositorio.mensajes[0]
    guardado["fecha_hora"] = (
        datetime.now(UTC) - timedelta(seconds=11)
    ).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    respuesta = cliente.post("/mensajes", json=CUERPO)

    assert respuesta.status_code == 201
    assert repositorio.insertos == 2
    assert len(repositorio.mensajes) == 2
