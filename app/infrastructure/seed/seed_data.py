from decimal import Decimal

from domain.enums import TipoCuenta
from domain.models.cliente import Cliente
from domain.models.cuenta import Cuenta
from infrastructure.persistence.repositories.cliente_repo import JsonClienteRepository
from infrastructure.persistence.repositories.cuenta_repo import JsonCuentaRepository
from infrastructure.persistence.repositories.transaccion_repo import JsonTransaccionRepository


def seed_if_empty(
    cliente_repo: JsonClienteRepository,
    cuenta_repo: JsonCuentaRepository,
    transaccion_repo: JsonTransaccionRepository,
) -> None:
    """Carga datos de ejemplo la primera vez que arranca (util para probar Swagger)."""
    if not cliente_repo._store.is_empty():
        return

    c1 = Cliente(
        id="seed-cliente-001",
        nombre="Ana Maria Lopez",
        documento="1010101010",
        email="ana.lopez@email.com",
    )
    c2 = Cliente(
        id="seed-cliente-002",
        nombre="Carlos Ruiz",
        documento="2020202020",
        email="carlos.ruiz@email.com",
    )
    cliente_repo.bulk_insert([c1, c2])

    cuentas = [
        Cuenta(
            id="seed-cuenta-001",
            numero_cuenta="ACC-2026-000001",
            cliente_id=c1.id,
            tipo=TipoCuenta.AHORROS,
            saldo=Decimal("1500000.00"),
        ),
        Cuenta(
            id="seed-cuenta-002",
            numero_cuenta="ACC-2026-000002",
            cliente_id=c1.id,
            tipo=TipoCuenta.CORRIENTE,
            saldo=Decimal("500000.00"),
        ),
        Cuenta(
            id="seed-cuenta-003",
            numero_cuenta="ACC-2026-000003",
            cliente_id=c2.id,
            tipo=TipoCuenta.AHORROS,
            saldo=Decimal("250000.00"),
        ),
    ]
    cuenta_repo.bulk_insert(cuentas)
    transaccion_repo.bulk_insert([])
