"""T028 — Integración: registrar y consultar historial con repositorio falso (US2)."""

from tests.support.cliente import crear_cliente

CUERPO = {"nombre": "Ana Prueba", "dni": "12345678", "telefono": "987654321"}


def test_historial_registra_y_consulta_en_orden_y_sin_otros_dnis() -> None:
    cliente, _ = crear_cliente()
    for texto in ["hola", "quiero devolucion", "horario del ciclo"]:
        assert cliente.post("/mensajes", json={**CUERPO, "texto": texto}).status_code == 201
    assert (
        cliente.post(
            "/mensajes",
            json={"nombre": "Luis Prueba", "dni": "87654321", "telefono": "987654322", "texto": "x"},
        ).status_code
        == 201
    )

    respuesta = cliente.post("/mensajes/consulta", json={"dni": "12345678"})

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert len(datos) == 3
    assert all(m["dni"] == "12345678" for m in datos)
    # Del más reciente al más antiguo (sin pérdida ante marcas iguales)
    fechas = [m["fecha_hora"] for m in datos]
    assert fechas == sorted(fechas, reverse=True)
