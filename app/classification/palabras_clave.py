"""Clasificación por palabras clave — listas del Apéndice A de data-model (FR-009).

Las listas son ampliables por el equipo de ventas sin tocar la lógica (FR-014):
basta añadir o quitar frases en `PALABRAS_CLAVE`. La prioridad ante texto
mixto es `devolucion` > `interes_inscripcion` > `informacion_ciclo` > `otro`
(FR-011), la normalización baja y quita acentos (research D3) y la
coincidencia es por palabra o frase con límites de palabra.
"""

import re
import unicodedata

# Orden de evaluación = prioridad cuando el texto contiene varias categorías
PRIORIDAD = ("devolucion", "interes_inscripcion", "informacion_ciclo")

PALABRAS_CLAVE: dict[str, tuple[str, ...]] = {
    "devolucion": (
        "devolución",
        "devolver",
        "devuelvan",
        "reembolso",
        "reembolsar",
        "anular matrícula",
        "retirarme",
        "me quiero retirar",
    ),
    "interes_inscripcion": (
        "matrícula",
        "matricular",
        "matricularme",
        "quiero matricularme",
        "inscribir",
        "inscribirme",
        "inscripción",
        "separar vacante",
        "separar mi vacante",
        "vacante",
        "cómo me inscribo",
        "quiero inscribirme",
    ),
    "informacion_ciclo": (
        "ciclo",
        "ciclos",
        "horario",
        "horarios",
        "turno",
        "turnos",
        "fecha de inicio",
        "cuándo empieza",
        "cursos",
        "modalidad",
        "virtual",
        "presencial",
        "precio",
        "costo",
        "cuánto cuesta",
        "mensualidad",
        "simulacro",
    ),
}


def _normalizar(texto: str) -> str:
    """Minúsculas, sin acentos (remoción de marcas diacríticas) y un solo
    espacio entre palabras (research D3)."""
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(caracter) != "Mn"
    )
    return re.sub(r"\s+", " ", sin_acentos).strip()


def _compilar(categoria: str) -> tuple[re.Pattern[str], ...]:
    """Un patrón por palabra o frase con límites de palabra `\\b`."""
    patrones = []
    for frase in PALABRAS_CLAVE[categoria]:
        patrones.append(re.compile(rf"\b{re.escape(_normalizar(frase))}\b"))
    return tuple(patrones)


# Precompilado una vez por módulo, en orden de prioridad de categoría
_COINCIDENCIAS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (categoria, patron)
    for categoria in PRIORIDAD
    for patron in _compilar(categoria)
)


def clasificar(texto: str) -> str:
    """Categoría del mensaje: `devolucion` | `interes_inscripcion` |
    `informacion_ciclo` | `otro` (nunca vacío; FR-009, FR-011, FR-015)."""
    normalizado = _normalizar(texto)
    for categoria, patron in _COINCIDENCIAS:
        if patron.search(normalizado):
            return categoria
    return "otro"
