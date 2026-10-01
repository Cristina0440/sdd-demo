"""T032 — Contrato: POST devuelve la clasificación según el texto (US3, FR-009/015)."""

import pytest

from tests.support.cliente import crear_cliente

CUERPO_BASE = {
    "nombre": "Ana Prueba",
    "dni": "12345678",
    "telefono": "987654321",
}

ASESOR = {"devolucion", "interes_inscripcion"}


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Quiero una devolución del curso", "devolucion"),
        ("Me quiero inscribir en el ciclo", "interes_inscripcion"),
        ("¿Cuál es el horario del ciclo?", "informacion_ciclo"),
        ("Gracias, ya lo sé", "otro"),
    ],
)
def test_post_clasifica_segun_el_texto(texto: str, esperado: str) -> None:
    cliente, _ = crear_cliente()

    respuesta = cliente.post("/mensajes", json={**CUERPO_BASE, "texto": texto})

    assert respuesta.status_code == 201
    clasificacion = respuesta.json()["clasificacion"]
    assert clasificacion == esperado
    # Devoluciones e interés quedan marcados para asesor, nunca como "otro":
    # el valor de `clasificacion` es la señal que usa el chatbot (FR-015)
    assert (clasificacion in ASESOR) is (esperado in ASESOR)
