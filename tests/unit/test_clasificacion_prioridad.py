"""T030 — Prioridad ante texto mixto y tolerancia a mayúsculas/acentos (FR-011)."""

import pytest

from app.classification.palabras_clave import clasificar


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        # "anular matrícula" (devolución) gana a "matrícula" (interés)
        ("Quiero anular matrícula", "devolucion"),
        # interés (matrícula) gana a información (horario)
        ("Quiero matrícula y saber el horario", "interes_inscripcion"),
        # devolución gana a información (ciclo)
        ("Quiero devolver el curso y saber el horario", "devolucion"),
    ],
)
def test_prioridad_de_categoria(texto: str, esperado: str) -> None:
    assert clasificar(texto) == esperado


@pytest.mark.parametrize(
    "texto",
    [
        "DEVOLUCIÓN",
        "Devolución del curso",
        "DEVUELVAN el dinero",
    ],
)
def test_tolerancia_a_mayusculas_y_acentos(texto: str) -> None:
    assert clasificar(texto) == "devolucion"
