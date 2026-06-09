# Trabajo K8S — Arquitectura de Software (Universidad de La Sabana)

Microservicio desplegado con la cadena completa: **Docker → Helm → Kubernetes → ArgoCD → GitHub Actions**.

## Arquitectura del flujo CI/CD

```
Commit a main
     │
     ▼
GitHub Actions (ci.yml)
  1. Build imagen Docker
  2. Push a ghcr.io (GitHub Container Registry)
  3. Actualiza tag en helm/values.yaml y hace commit
     │
     ▼
ArgoCD detecta el cambio en Git
  - Sincroniza automáticamente el Helm chart
  - Despliega la nueva versión en Kubernetes
```

## Estructura del proyecto

```
mi-microservicio/
├── app/main.py                        FastAPI con endpoints /health y /
├── requirements.txt                   Dependencias Python
├── Dockerfile                         Imagen del contenedor
├── helm/mi-microservicio/
│   ├── Chart.yaml                     Metadatos del chart
│   ├── values.yaml                    Valores por defecto (dev)
│   ├── values-prod.yaml               Override para producción
│   └── templates/
│       ├── _helpers.tpl               Funciones reutilizables
│       ├── deployment.yaml            Deployment de Kubernetes
│       └── service.yaml               Service de Kubernetes
├── argocd/
│   └── application.yaml               Manifiesto ArgoCD Application
└── .github/workflows/
    └── ci.yml                         Pipeline de GitHub Actions
```

## Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)
- Cuenta de GitHub con repositorio creado

---

## Paso 1: Configurar el repositorio

1. Crear un repositorio en GitHub llamado `mi-microservicio`
2. Reemplazar `TU_USUARIO` en los siguientes archivos:
   - `helm/mi-microservicio/values.yaml` → campo `image.repository`
   - `argocd/application.yaml` → campo `source.repoURL`
3. Subir el código al repositorio:

```bash
git init
git add .
git commit -m "feat: microservicio inicial con Docker, Helm y ArgoCD"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/mi-microservicio.git
git push -u origin main
```

---

## Paso 2: Verificar Docker localmente

```bash
# Construir la imagen
docker build -t mi-microservicio:local .

# Ejecutar el contenedor
docker run -p 8000:8000 mi-microservicio:local

# Probar el endpoint de salud
curl http://localhost:8000/health
# Respuesta esperada: {"status":"ok","env":"development"}
```

---

## Paso 3: Iniciar Minikube y desplegar con Helm

```bash
# Iniciar el cluster local
minikube start

# Instalar el chart (primera vez)
helm install mi-microservicio ./helm/mi-microservicio \
  --namespace mi-microservicio \
  --create-namespace

# Verificar que los pods estén corriendo
kubectl get pods -n mi-microservicio

# Acceder al servicio (Minikube crea un tunnel)
kubectl port-forward svc/mi-microservicio-mi-microservicio 8080:80 -n mi-microservicio
# Luego abrir: http://localhost:8080/health
```

### Despliegue con override de producción

```bash
helm upgrade mi-microservicio ./helm/mi-microservicio \
  -f helm/mi-microservicio/values.yaml \
  -f helm/mi-microservicio/values-prod.yaml \
  --namespace mi-microservicio
```

---

## Paso 4: Instalar y configurar ArgoCD

```bash
# Crear namespace e instalar ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Esperar a que todos los pods estén listos
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=120s

# Obtener la contraseña inicial del admin
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d && echo

# Exponer la UI de ArgoCD
kubectl port-forward svc/argocd-server -n argocd 8081:443
# Abrir: https://localhost:8081  (usuario: admin)
```

### Aplicar el manifiesto de ArgoCD

```bash
# ⚠️ Primero editar argocd/application.yaml y reemplazar TU_USUARIO
kubectl apply -f argocd/application.yaml
```

ArgoCD detectará el repositorio, leerá el Helm chart y desplegará el microservicio automáticamente.

---

## Paso 5: Verificar el pipeline CI/CD

1. Realizar un cambio en `app/main.py` (por ejemplo, agregar un mensaje)
2. Hacer commit y push a `main`
3. En GitHub → pestaña **Actions**: ver el pipeline ejecutarse
4. En la UI de ArgoCD: ver la sincronización automática

---

## Endpoints del microservicio

| Método | Ruta      | Descripción                    |
|--------|-----------|--------------------------------|
| GET    | `/`       | Información del servicio       |
| GET    | `/health` | Estado de salud (K8S probes)   |
| GET    | `/docs`   | Documentación automática (Swagger UI) |
