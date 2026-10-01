"""T011 — Contrato de POST /mensajes con datos válidos → 201 (US1, FR-005)."""

from datetime import datetime

from tests.support.cliente import crear_cliente


def test_post_valido_responde_201_con_id_fecha_y_clasificacion() -> None:
    cliente, repositorio = crear_cliente()
    respuesta = cliente.post(
        "/mensajes",
        json={
            "nombre": "Ana Prueba",
            "dni": "12345678",
            "telefono": "987654321",
            # Sin palabras clave: la expectativa "otro" sigue vigente tras US3
            "texto": "Hola, buenas tardes",
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"]
    assert cuerpo["fecha_hora"]
    assert cuerpo["clasificacion"] == "otro"
    # Eco de los datos enviados, según el contrato
    assert cuerpo["nombre"] == "Ana Prueba"
    assert cuerpo["dni"] == "12345678"
    assert cuerpo["telefono"] == "987654321"
    assert cuerpo["texto"] == "Hola, buenas tardes"
    # La fecha es ISO8601 con zona horaria (UTC)
    datetime.fromisoformat(cuerpo["fecha_hora"])
    # El mensaje llegó al repositorio exactamente una vez
    assert repositorio.insertos == 1
    assert len(repositorio.mensajes) == 1
