from dataclasses import dataclass
from pathlib import Path

from application.use_cases.clientes import ClienteUseCases
from application.use_cases.cuentas import CuentaUseCases
from application.use_cases.transacciones import TransaccionUseCases
from infrastructure.config import get_settings
from infrastructure.persistence.json_store import JsonStore
from infrastructure.persistence.repositories.cliente_repo import JsonClienteRepository
from infrastructure.persistence.repositories.cuenta_repo import JsonCuentaRepository
from infrastructure.persistence.repositories.transaccion_repo import JsonTransaccionRepository
from infrastructure.seed.seed_data import seed_if_empty


@dataclass
class AppContainer:
    cliente_uc: ClienteUseCases
    cuenta_uc: CuentaUseCases
    transaccion_uc: TransaccionUseCases


_container: AppContainer | None = None


def build_container(data_dir: Path | None = None) -> AppContainer:
    settings = get_settings()
    base = data_dir or settings.data_dir
    base.mkdir(parents=True, exist_ok=True)

    cliente_repo = JsonClienteRepository(JsonStore(base / "clientes.json"))
    cuenta_repo = JsonCuentaRepository(JsonStore(base / "cuentas.json"))
    transaccion_repo = JsonTransaccionRepository(JsonStore(base / "transacciones.json"))

    seed_if_empty(cliente_repo, cuenta_repo, transaccion_repo)

    cuenta_uc = CuentaUseCases(cliente_repo, cuenta_repo)
    return AppContainer(
        cliente_uc=ClienteUseCases(cliente_repo),
        cuenta_uc=cuenta_uc,
        transaccion_uc=TransaccionUseCases(cuenta_uc, cuenta_repo, transaccion_repo),
    )


def get_container() -> AppContainer:
    global _container
    if _container is None:
        _container = build_container()
    return _container


def init_app() -> AppContainer:
    global _container
    _container = build_container()
    return _container
