"""
Core Banking Lite — microservicio bancario (trabajo K8S)

Autores:
- Jorge Eliecer Rojas
- Juan Esteban Gomez
- Fabian Andres Rojas
- Juan Velez
- David Panesso

Arquitectura hexagonal:
  domain/       entidades y reglas de negocio
  application/  casos de uso
  infrastructure/  FastAPI + persistencia JSON

Persistencia en archivos JSON (DATA_DIR). Sin base de datos.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from infrastructure.config import get_settings
from infrastructure.web.dependencies import init_app
from infrastructure.web.exception_handlers import register_exception_handlers
from infrastructure.web.routers import clientes, cuentas, sistema, transacciones


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_app()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Core Banking Lite",
        description=(
            "API de banco simulado para el trabajo de Arquitectura de Software. "
            "Gestiona clientes, cuentas (ahorros/corriente) y transacciones en COP. "
            "Los datos se guardan en JSON local (PVC en Kubernetes)."
        ),
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    register_exception_handlers(app)

    app.include_router(sistema.router)
    app.include_router(clientes.router)
    app.include_router(cuentas.router)
    app.include_router(transacciones.router)

    return app


app = create_app()
