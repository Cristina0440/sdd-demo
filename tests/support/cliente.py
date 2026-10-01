"""Fábrica de clientes de prueba: app con repositorio falso, sin base de datos."""

from fastapi.testclient import TestClient

from app.main import crear_app
from tests.support.repositorio_falso import RepositorioFalso


def crear_cliente() -> tuple[TestClient, RepositorioFalso]:
    """Devuelve un cliente de prueba y su repositorio en memoria para asertarlo."""
    repositorio = RepositorioFalso()
    cliente = TestClient(crear_app(repositorio=repositorio))
    return cliente, repositorio
