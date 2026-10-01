"""T031 — Coincidencia por palabra o frase con límites de palabra (FR-014)."""

from app.classification.palabras_clave import clasificar


def test_devolucionista_no_es_devolucion() -> None:
    assert clasificar("devolucionista") != "devolucion"
    assert clasificar("devolucionista") == "otro"


def test_matriculacion_no_es_inscripcion() -> None:
    """Un substring no debe disparar la categoría (límites de palabra)."""
    assert clasificar("matriculación") == "otro"
