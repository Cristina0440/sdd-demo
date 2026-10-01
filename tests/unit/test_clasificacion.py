"""T029 — Clasificación por categoría con las listas del Apéndice A (US3, FR-009)."""

import pytest

from app.classification.palabras_clave import clasificar


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Quiero una devolución del curso", "devolucion"),
        ("Solicito un reembolso por el pago", "devolucion"),
        ("¿Cuál es el horario del ciclo?", "informacion_ciclo"),
        ("El turno virtual inicia pronto", "informacion_ciclo"),
        ("Quiero inscribirme en el curso", "interes_inscripcion"),
        ("Quiero matricularme en la academia", "interes_inscripcion"),
        ("Vengo a separar vacante", "interes_inscripcion"),
        ("Gracias, ya lo sé", "otro"),
        ("Hola, buenas tardes", "otro"),
    ],
)
def test_clasifica_por_categoria(texto: str, esperado: str) -> None:
    assert clasificar(texto) == esperado
