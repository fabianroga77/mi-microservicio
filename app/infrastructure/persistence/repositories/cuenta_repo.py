from datetime import datetime, timezone
from typing import List, Optional

from domain.models.cuenta import Cuenta
from domain.ports.cuenta_repository import CuentaRepository
from infrastructure.persistence.json_store import JsonStore
from infrastructure.persistence.serializers import cuenta_from_dict, cuenta_to_dict


class JsonCuentaRepository(CuentaRepository):
    def __init__(self, store: JsonStore):
        self._store = store

    def save(self, cuenta: Cuenta) -> Cuenta:
        data = cuenta_to_dict(cuenta)

        def mutator(items):
            updated = [data if i["id"] == cuenta.id else i for i in items]
            if not any(i["id"] == cuenta.id for i in items):
                updated.append(data)
            return updated

        self._store.update(mutator)
        return cuenta

    def find_by_id(self, cuenta_id: str) -> Optional[Cuenta]:
        for item in self._store.read_all():
            if item["id"] == cuenta_id:
                return cuenta_from_dict(item)
        return None

    def find_by_numero(self, numero_cuenta: str) -> Optional[Cuenta]:
        for item in self._store.read_all():
            if item["numero_cuenta"] == numero_cuenta:
                return cuenta_from_dict(item)
        return None

    def list_all(
        self, cliente_id: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> List[Cuenta]:
        items = self._store.read_all()
        if cliente_id:
            items = [i for i in items if i["cliente_id"] == cliente_id]
        items = sorted(items, key=lambda x: x.get("created_at", ""))
        return [cuenta_from_dict(i) for i in items[skip : skip + limit]]

    def count(self, cliente_id: Optional[str] = None) -> int:
        items = self._store.read_all()
        if cliente_id:
            items = [i for i in items if i["cliente_id"] == cliente_id]
        return len(items)

    def next_numero_cuenta(self) -> str:
        year = datetime.now(timezone.utc).year
        prefix = f"ACC-{year}-"
        numeros = [
            int(i["numero_cuenta"].split("-")[-1])
            for i in self._store.read_all()
            if i["numero_cuenta"].startswith(prefix)
        ]
        siguiente = max(numeros, default=0) + 1
        return f"{prefix}{siguiente:06d}"

    def bulk_insert(self, cuentas: List[Cuenta]) -> None:
        self._store.write_all([cuenta_to_dict(c) for c in cuentas])
