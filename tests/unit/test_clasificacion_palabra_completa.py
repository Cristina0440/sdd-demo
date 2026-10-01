"""T031 — Coincidencia por palabra o frase con límites de palabra (FR-014)."""

from app.classification.palabras_clave import clasificar


def test_devolucionista_no_es_devolucion() -> None:
    assert clasificar("devolucionista") == "otro"


def test_matriculaciones_no_es_matriculacion() -> None:
    """Solo la palabra o frase listada exacta cuenta; la derivación no listada,
    no: `matriculaciones` no es la palabra clave `matriculación` (límite de
    palabra tras la normalización)."""
    assert clasificar("matriculaciones") == "otro"
