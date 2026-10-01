"""T023 — Orden estable del historial con marcas de fecha iguales (US2, FR-007)."""

from tests.support.repositorio_falso import RepositorioFalso


def test_orden_estable_con_la_misma_fecha_hora() -> None:
    repo = RepositorioFalso()
    marca = "2026-10-01T12:00:00.000Z"
    repo.insertar(
        {"id": "bbbb2222-2222-4222-8222-222222222222", "dni": "12345678", "texto": "u1", "fecha_hora": marca}
    )
    repo.insertar(
        {"id": "aaaa1111-1111-4111-8111-111111111111", "dni": "12345678", "texto": "u2", "fecha_hora": marca}
    )

    primero = repo.consultar_por_dni("12345678")
    segundo = repo.consultar_por_dni("12345678")

    # Desempate por id DESC y resultado idéntico al repetir (orden estable)
    assert [m["id"] for m in primero] == [
        "bbbb2222-2222-4222-8222-222222222222",
        "aaaa1111-1111-4111-8111-111111111111",
    ]
    assert [m["id"] for m in primero] == [m["id"] for m in segundo]
    assert len(primero) == 2  # sin pérdidas
