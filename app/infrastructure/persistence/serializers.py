from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

from domain.enums import EstadoCuenta, TipoCuenta, TipoTransaccion
from domain.models.cliente import Cliente
from domain.models.cuenta import Cuenta
from domain.models.transaccion import Transaccion


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def cliente_to_dict(c: Cliente) -> Dict[str, Any]:
    return {
        "id": c.id,
        "nombre": c.nombre,
        "documento": c.documento,
        "email": c.email,
        "activo": c.activo,
        "created_at": c.created_at.isoformat(),
    }


def cliente_from_dict(d: Dict[str, Any]) -> Cliente:
    return Cliente(
        id=d["id"],
        nombre=d["nombre"],
        documento=d["documento"],
        email=d["email"],
        activo=d.get("activo", True),
        created_at=_parse_dt(d["created_at"]),
    )


def cuenta_to_dict(c: Cuenta) -> Dict[str, Any]:
    return {
        "id": c.id,
        "numero_cuenta": c.numero_cuenta,
        "cliente_id": c.cliente_id,
        "tipo": c.tipo.value,
        "saldo": str(c.saldo),
        "estado": c.estado.value,
        "created_at": c.created_at.isoformat(),
    }


def cuenta_from_dict(d: Dict[str, Any]) -> Cuenta:
    return Cuenta(
        id=d["id"],
        numero_cuenta=d["numero_cuenta"],
        cliente_id=d["cliente_id"],
        tipo=TipoCuenta(d["tipo"]),
        saldo=Decimal(d["saldo"]),
        estado=EstadoCuenta(d["estado"]),
        created_at=_parse_dt(d["created_at"]),
    )


def transaccion_to_dict(t: Transaccion) -> Dict[str, Any]:
    return {
        "id": t.id,
        "tipo": t.tipo.value,
        "monto": str(t.monto),
        "cuenta_id": t.cuenta_id,
        "cuenta_destino_id": t.cuenta_destino_id,
        "referencia": t.referencia,
        "descripcion": t.descripcion,
        "idempotency_key": t.idempotency_key,
        "created_at": t.created_at.isoformat(),
    }


def transaccion_from_dict(d: Dict[str, Any]) -> Transaccion:
    return Transaccion(
        id=d["id"],
        tipo=TipoTransaccion(d["tipo"]),
        monto=Decimal(d["monto"]),
        cuenta_id=d["cuenta_id"],
        cuenta_destino_id=d.get("cuenta_destino_id"),
        referencia=d.get("referencia", ""),
        descripcion=d.get("descripcion", ""),
        idempotency_key=d.get("idempotency_key"),
        created_at=_parse_dt(d["created_at"]),
    )
