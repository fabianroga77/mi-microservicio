"""
Microservicio básico con FastAPI.
Expone endpoints de salud y versión para ser desplegado en Kubernetes.
"""

from fastapi import FastAPI
import os

app = FastAPI(
    title="Mi Microservicio",
    description="Microservicio de ejemplo para Trabajo K8S - Arquitectura de Software",
    version="1.0.0",
)

# Variable de entorno inyectada por el Helm chart (ver values.yaml → env.APP_ENV)
APP_ENV = os.getenv("APP_ENV", "development")


@app.get("/health")
def health_check():
    """Endpoint de salud requerido por Kubernetes liveness/readiness probes."""
    return {"status": "ok", "env": APP_ENV}


@app.get("/")
def root():
    """Endpoint raíz con información básica del servicio."""
    return {
        "service": "mi-microservicio",
        "version": "1.0.0",
        "env": APP_ENV,
        "message": "Microservicio desplegado con Docker + Helm + K8S + ArgoCD",
    }