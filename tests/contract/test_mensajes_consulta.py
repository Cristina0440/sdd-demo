"""T021 — Contrato: POST /mensajes/consulta con dni válido → 200 ordenado (US2)."""

from tests.support.cliente import crear_cliente


def _fila(id: str, dni: str, texto: str, fecha_hora: str) -> dict:
    return {
        "id": id,
        "nombre": "Ana Prueba",
        "dni": dni,
        "telefono": "987654321",
        "texto": texto,
        "fecha_hora": fecha_hora,
        "clasificacion": "otro",
    }


def test_consulta_devuelve_historial_ordenado_y_filtrado_por_dni() -> None:
    cliente, repositorio = crear_cliente()
    repositorio.insertar(
        _fila("11111111-1111-4111-8111-111111111111", "12345678", "Antiguo", "2026-10-01T10:00:00.000Z")
    )
    repositorio.insertar(
        _fila("22222222-2222-4222-8222-222222222222", "12345678", "Del medio", "2026-10-01T10:05:00.000Z")
    )
    repositorio.insertar(
        _fila("33333333-3333-4333-8333-333333333333", "12345678", "Reciente", "2026-10-01T10:10:00.000Z")
    )
    repositorio.insertar(
        _fila("44444444-4444-4444-8444-444444444444", "87654321", "Otro alumno", "2026-10-01T10:07:00.000Z")
    )

    respuesta = cliente.post("/mensajes/consulta", json={"dni": "12345678"})

    assert respuesta.status_code == 200
    datos = respuesta.json()
    # Del más reciente al más antiguo y solo los del DNI consultado
    assert [m["texto"] for m in datos] == ["Reciente", "Del medio", "Antiguo"]
    assert all(m["dni"] == "12345678" for m in datos)
