"""
mi-microservicio

Autores:
- Jorge Eliecer Rojas
- Juan Esteban Gomez
- Fabian Andres Rojas
- Juan Velez
- David Panesso

Arquitectura de Software - Universidad de La Sabana
Trabajo K8S (Docker, Helm, Kubernetes, ArgoCD)

Esta es la API que corre dentro del contenedor. Kubernetes la consulta
por /health para saber si el pod esta bien. El resto de endpoints son
para probar que el despliegue quedo con la version y el entorno correctos.
"""

from fastapi import FastAPI, HTTPException
import os
import platform
import time

# Variables de entorno. APP_ENV la inyecta Helm desde values.yaml.
# APP_VERSION no la pasamos desde Helm todavia, queda en 1.0.0 por defecto.
APP_ENV = os.getenv("APP_ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_NAME = "mi-microservicio"

# Guardamos cuando arranco el server para calcular uptime en /info
START_TIME = time.time()

app = FastAPI(
    title="Mi Microservicio",
    description="API del trabajo K8S - Arquitectura de Software",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
def root():
    """
    Respuesta rapida para ver que el servicio esta arriba.
    Devuelve nombre, version y entorno (development/production).
    """
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "env": APP_ENV,
        "message": "Servicio activo",
    }


@app.get("/health")
def health_check():
    """
    Lo usa Kubernetes en los probes (liveness y readiness).
    Si esto deja de responder, K8S puede reiniciar el pod o dejar de mandarle trafico.
    Tiene que ser liviano y no depender de bases de datos ni nada externo.
    """
    return {"status": "ok", "env": APP_ENV}


@app.get("/info")
def info():
    """
    Info extra del contenedor: version de Python, OS, cuanto lleva corriendo.
    Nos sirve para debuggear cuando algo se ve raro en el cluster.
    """
    uptime_seconds = round(time.time() - START_TIME, 1)

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "env": APP_ENV,
        "python_version": platform.python_version(),
        "os": platform.system(),
        "uptime_seconds": uptime_seconds,
    }


@app.get("/env/{variable}")
def get_env_variable(variable: str):
    """
    Permite leer algunas variables de entorno desde afuera (para pruebas).
    Solo dejamos APP_ENV y APP_VERSION — no exponemos secretos ni tokens.
    """
    allowed = {"APP_ENV", "APP_VERSION"}

    if variable not in allowed:
        raise HTTPException(
            status_code=403,
            detail=f"Variable '{variable}' no esta disponible. Permitidas: {sorted(allowed)}",
        )

    value = os.getenv(variable)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Variable '{variable}' no definida.")

    return {"variable": variable, "value": value}
