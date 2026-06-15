from typing import List, Optional

from domain.models.cliente import Cliente
from domain.ports.cliente_repository import ClienteRepository
from infrastructure.persistence.json_store import JsonStore
from infrastructure.persistence.serializers import cliente_from_dict, cliente_to_dict


class JsonClienteRepository(ClienteRepository):
    def __init__(self, store: JsonStore):
        self._store = store

    def save(self, cliente: Cliente) -> Cliente:
        data = cliente_to_dict(cliente)

        def mutator(items):
            updated = [data if i["id"] == cliente.id else i for i in items]
            if not any(i["id"] == cliente.id for i in items):
                updated.append(data)
            return updated

        self._store.update(mutator)
        return cliente

    def find_by_id(self, cliente_id: str) -> Optional[Cliente]:
        for item in self._store.read_all():
            if item["id"] == cliente_id:
                return cliente_from_dict(item)
        return None

    def find_by_documento(self, documento: str) -> Optional[Cliente]:
        for item in self._store.read_all():
            if item["documento"] == documento:
                return cliente_from_dict(item)
        return None

    def list_all(self, skip: int = 0, limit: int = 50) -> List[Cliente]:
        items = sorted(
            self._store.read_all(),
            key=lambda x: x.get("created_at", ""),
        )
        return [cliente_from_dict(i) for i in items[skip : skip + limit]]

    def count(self) -> int:
        return len(self._store.read_all())

    def bulk_insert(self, clientes: List[Cliente]) -> None:
        self._store.write_all([cliente_to_dict(c) for c in clientes])
