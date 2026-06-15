from typing import List, Optional

from domain.enums import TipoTransaccion
from domain.models.transaccion import Transaccion
from domain.ports.transaccion_repository import TransaccionRepository
from infrastructure.persistence.json_store import JsonStore
from infrastructure.persistence.serializers import (
    transaccion_from_dict,
    transaccion_to_dict,
)


class JsonTransaccionRepository(TransaccionRepository):
    def __init__(self, store: JsonStore):
        self._store = store

    def save(self, transaccion: Transaccion) -> Transaccion:
        data = transaccion_to_dict(transaccion)

        def mutator(items):
            updated = [data if i["id"] == transaccion.id else i for i in items]
            if not any(i["id"] == transaccion.id for i in items):
                updated.append(data)
            return updated

        self._store.update(mutator)
        return transaccion

    def find_by_id(self, transaccion_id: str) -> Optional[Transaccion]:
        for item in self._store.read_all():
            if item["id"] == transaccion_id:
                return transaccion_from_dict(item)
        return None

    def find_by_idempotency_key(self, key: str) -> Optional[Transaccion]:
        for item in self._store.read_all():
            if item.get("idempotency_key") == key:
                return transaccion_from_dict(item)
        return None

    def list_all(
        self,
        cuenta_id: Optional[str] = None,
        tipo: Optional[TipoTransaccion] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Transaccion]:
        items = self._store.read_all()
        if cuenta_id:
            items = [
                i
                for i in items
                if i["cuenta_id"] == cuenta_id
                or i.get("cuenta_destino_id") == cuenta_id
            ]
        if tipo:
            items = [i for i in items if i["tipo"] == tipo.value]
        items = sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)
        return [transaccion_from_dict(i) for i in items[skip : skip + limit]]

    def count(
        self,
        cuenta_id: Optional[str] = None,
        tipo: Optional[TipoTransaccion] = None,
    ) -> int:
        items = self._store.read_all()
        if cuenta_id:
            items = [
                i
                for i in items
                if i["cuenta_id"] == cuenta_id
                or i.get("cuenta_destino_id") == cuenta_id
            ]
        if tipo:
            items = [i for i in items if i["tipo"] == tipo.value]
        return len(items)

    def bulk_insert(self, transacciones: List[Transaccion]) -> None:
        self._store.write_all([transaccion_to_dict(t) for t in transacciones])
