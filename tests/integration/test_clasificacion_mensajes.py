"""T036 — Integración: clasificación y destino bot/asesor (escenario 5 del quickstart)."""

import pytest

from tests.support.cliente import crear_cliente

CUERPO_BASE = {"nombre": "Ana Prueba", "dni": "12345678", "telefono": "987654321"}

ASESOR = {"devolucion", "interes_inscripcion"}


@pytest.mark.parametrize(
    ("texto", "esperado", "va_a_asesor"),
    [
        ("Quiero una devolución del curso", "devolucion", True),
        ("Me quiero inscribir en el ciclo", "interes_inscripcion", True),
        ("¿Cuál es el horario del ciclo?", "informacion_ciclo", False),
        ("Gracias, ya lo sé", "otro", False),
        # Texto mixto con devolución y ciclo → devolución (prioridad FR-011)
        ("Quiero devolver el curso y saber el horario", "devolucion", True),
    ],
)
def test_clasificacion_y_destino(texto: str, esperado: str, va_a_asesor: bool) -> None:
    cliente, repositorio = crear_cliente()

    respuesta = cliente.post("/mensajes", json={**CUERPO_BASE, "texto": texto})

    assert respuesta.status_code == 201
    clasificacion = respuesta.json()["clasificacion"]
    assert clasificacion == esperado
    assert (clasificacion in ASESOR) is va_a_asesor
    # Quedó persistida con esa clasificación
    assert repositorio.mensajes[-1]["clasificacion"] == esperado
