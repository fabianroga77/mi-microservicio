# Trabajo K8S — Arquitectura de Software (Universidad de La Sabana)

Microservicio desplegado con la cadena completa: **Docker → Helm → Kubernetes → ArgoCD → GitHub Actions**.

---

## ¿Qué es todo esto? (explicación simple)

Imagina que tienes una aplicación web pequeña (un API en Python). El objetivo es que cada vez que alguien haga un cambio en el código y lo suba a GitHub, esa nueva versión se despliegue **sola** en un servidor, sin que nadie tenga que hacer nada a mano. Eso es lo que hace este proyecto.

Las herramientas que usamos son:

| Herramienta | ¿Para qué sirve? |
|---|---|
| **FastAPI** | El microservicio en sí: una API en Python con dos endpoints |
| **Docker** | Empaqueta el código en un contenedor (como una caja que tiene todo lo necesario para correr la app) |
| **Kubernetes (Minikube)** | El sistema que corre y gestiona los contenedores en un servidor (o en local con Minikube) |
| **Helm** | Un gestor de paquetes para Kubernetes. En lugar de escribir 5 archivos de config a mano, Helm los organiza como un "chart" reutilizable |
| **ArgoCD** | Vigila el repositorio de GitHub y cada vez que detecta un cambio, actualiza automáticamente lo que corre en Kubernetes |
| **GitHub Actions** | El pipeline de CI/CD: se ejecuta automáticamente cuando hay un push, construye la imagen Docker y la publica |
| **ghcr.io** | GitHub Container Registry: donde se guardan las imágenes Docker (como Docker Hub pero de GitHub) |

---

## El flujo completo (de principio a fin)

```
Desarrollador hace cambio en código y hace git push a main
        │
        ▼
GitHub Actions (ci.yml) se dispara automáticamente
  Paso 1: Construye la imagen Docker con el nuevo código
  Paso 2: Publica la imagen en ghcr.io con tag = SHA del commit (ej: cb4154d)
  Paso 3: Actualiza el archivo values.yaml con ese nuevo tag
  Paso 4: Hace commit y push de ese cambio a GitHub
        │
        ▼
ArgoCD detecta el nuevo commit en el repo
  - Lee el Helm chart actualizado
  - Despliega automáticamente la nueva versión en Kubernetes
        │
        ▼
Kubernetes corre la nueva versión del microservicio
  - El pod viejo se reemplaza por el nuevo sin downtime
```

---

## Estructura del proyecto

```
mi-microservicio/
├── app/
│   └── main.py                    El código de la API (FastAPI)
├── requirements.txt               Librerías Python necesarias
├── Dockerfile                     Instrucciones para construir la imagen Docker
├── helm/
│   └── mi-microservicio/
│       ├── Chart.yaml             Nombre y versión del chart de Helm
│       ├── values.yaml            Configuración por defecto (imagen, recursos, etc.)
│       ├── values-prod.yaml       Configuración para sobreescribir en producción
│       └── templates/
│           ├── _helpers.tpl       Funciones de Helm para no repetir código
│           ├── deployment.yaml    Le dice a K8S cómo correr el contenedor
│           └── service.yaml       Le dice a K8S cómo exponer el contenedor en red
├── argocd/
│   └── application.yaml           Le dice a ArgoCD qué repo vigilar y dónde desplegar
└── .github/
    └── workflows/
        └── ci.yml                 El pipeline de GitHub Actions
```

---

## Paso 1: El microservicio (FastAPI)

El código está en `app/main.py`. Es una API mínima con dos endpoints:

```python
@app.get("/health")
def health_check():
    return {"status": "ok", "env": APP_ENV}

@app.get("/")
def root():
    return {"service": "mi-microservicio", "version": "1.0.0", ...}
```

**¿Por qué `/health`?** Kubernetes necesita saber si el contenedor está vivo y listo para recibir tráfico. Lo hace llamando a este endpoint cada ciertos segundos (configurado en `values.yaml` como `livenessProbe` y `readinessProbe`).

---

## Paso 2: Docker — empaquetar la aplicación

El `Dockerfile` convierte el código Python en una imagen que puede correr en cualquier máquina o servidor.

Para probar localmente (desde la carpeta `mi-microservicio/`):

```bash
# Construir la imagen
docker build -t mi-microservicio:local .

# Correr el contenedor en el puerto 8000
docker run -p 8000:8000 mi-microservicio:local

# Probar que responde
curl http://localhost:8000/health
# Respuesta: {"status":"ok","env":"development"}
```

**¿Qué hace cada cosa?**
- `docker build`: lee el Dockerfile y construye la imagen
- `-t mi-microservicio:local`: le da un nombre a la imagen
- `docker run -p 8000:8000`: corre el contenedor y mapea el puerto 8000 del contenedor al 8000 de tu máquina

---

## Paso 3: Kubernetes con Minikube — correr en un cluster local

Minikube crea un cluster de Kubernetes en tu máquina. Es como tener un servidor real pero en tu PC.

### Iniciar Minikube

```powershell
minikube start
```

Esto levanta una máquina virtual con Kubernetes adentro. Puede tardar 1-2 minutos la primera vez.

### Instalar el microservicio con Helm

En lugar de aplicar los archivos YAML de Kubernetes uno por uno, Helm los agrupa en un "chart" y los instala todos juntos:

```powershell
helm install mi-microservicio C:\Users\User\PycharmProjects\trabajoarqui\mi-microservicio\helm\mi-microservicio --namespace mi-microservicio --create-namespace
```

**¿Qué hace cada parte?**
- `helm install`: instala el chart por primera vez
- `mi-microservicio`: el nombre que le damos a esta instalación
- `C:\...\helm\mi-microservicio`: la ruta al chart
- `--namespace mi-microservicio`: crea todo dentro de un espacio aislado llamado `mi-microservicio`
- `--create-namespace`: si el namespace no existe, lo crea automáticamente

**Verificar que el pod está corriendo:**

```powershell
kubectl get pods -n mi-microservicio
```

Resultado esperado:
```
NAME                                                 READY   STATUS    RESTARTS   AGE
mi-microservicio-mi-microservicio-6b48bbcf9c-fxh9s   1/1     Running   0          1m
```

- `1/1`: significa que el pod tiene 1 contenedor y los 1 están listos
- `Running`: el pod está corriendo correctamente

### Acceder al microservicio desde el navegador

Kubernetes no expone los servicios directamente hacia tu máquina. Para acceder localmente usamos `port-forward`:

```powershell
kubectl port-forward svc/mi-microservicio-mi-microservicio 8080:80 -n mi-microservicio
```

Esto crea un túnel: `localhost:8080` → `servicio en Kubernetes:80` → `contenedor:8000`.

Abrir en el navegador: `http://localhost:8080/health`

Respuesta esperada:
```json
{"status": "ok", "env": "development"}
```

---

## Paso 4: ArgoCD — despliegue automático desde Git

ArgoCD es el sistema GitOps: vigila el repositorio de GitHub y cuando detecta un cambio en los archivos del Helm chart, actualiza automáticamente lo que corre en Kubernetes.

### Instalar ArgoCD en el cluster

```powershell
# Crear el namespace donde vivirá ArgoCD
kubectl create namespace argocd

# Instalar todos los componentes de ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Verificar que todos los pods están corriendo (puede tardar 2-3 minutos)
kubectl get pods -n argocd
```

Cuando todo está listo se ven estos pods en estado `Running`:
```
argocd-application-controller-0        1/1   Running
argocd-applicationset-controller-...   1/1   Running
argocd-dex-server-...                  1/1   Running
argocd-notifications-controller-...    1/1   Running
argocd-redis-...                       1/1   Running
argocd-repo-server-...                 1/1   Running
argocd-server-...                      1/1   Running
```

> **Nota:** Si algún pod queda en estado `Error` por condición de carrera, se reinicia con:
> ```powershell
> kubectl rollout restart deployment argocd-applicationset-controller -n argocd
> ```
> Si un pod queda colgado en `Init:0/1` por mucho tiempo, se elimina para que Kubernetes lo recree:
> ```powershell
> kubectl delete pod <nombre-del-pod> -n argocd
> ```

### Acceder a la UI de ArgoCD

```powershell
# Crear un túnel hacia la UI de ArgoCD
kubectl port-forward svc/argocd-server -n argocd 8081:443
```

Abrir en el navegador: `https://localhost:8081`

**Obtener la contraseña del usuario `admin`:**

```powershell
$p = kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}"; [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($p))
```

La contraseña viene guardada en base64 dentro de un Secret de Kubernetes. El comando la decodifica a texto plano.

### Conectar el repositorio de GitHub

En la UI de ArgoCD:
1. **Settings → Repositories → Connect Repo**
2. Connection method: `HTTPS`
3. Repository URL: `https://github.com/fabianroga77/mi-microservicio.git`
4. Clic en **Connect** → debe mostrar `Successful`

### Registrar la aplicación en ArgoCD

El archivo `argocd/application.yaml` le dice a ArgoCD:
- Qué repositorio vigilar
- En qué rama (`main`)
- Dónde está el Helm chart dentro del repo (`helm/mi-microservicio`)
- En qué namespace de Kubernetes desplegar

```powershell
kubectl apply -f C:\Users\User\PycharmProjects\trabajoarqui\mi-microservicio\argocd\application.yaml
```

Después de esto, en la UI de ArgoCD → **Applications**, aparece `mi-microservicio` con estado:
- `Synced`: el cluster coincide con lo que hay en Git
- `Healthy`: los pods están corriendo correctamente

---

## Paso 5: GitHub Actions — el pipeline de CI/CD

El archivo `.github/workflows/ci.yml` se ejecuta automáticamente cada vez que hay un `push` a la rama `main`. Hace dos trabajos en secuencia:

### Job 1: Build & Push

1. Descarga el código del repo
2. Calcula el SHA corto del commit (ej: `cb4154d`) para usarlo como tag de la imagen
3. Se autentica en `ghcr.io` usando el token automático de GitHub
4. Construye la imagen Docker
5. La publica en `ghcr.io/fabianroga77/mi-microservicio:cb4154d` y también como `:latest`

### Job 2: Update Helm Tag

1. Modifica `helm/mi-microservicio/values.yaml` reemplazando el campo `tag` con el SHA nuevo
2. Hace commit y push de ese cambio con el mensaje `ci: actualizar imagen a cb4154d [skip ci]`
3. El `[skip ci]` evita que ese commit dispare otro pipeline (bucle infinito)

Cuando ArgoCD detecta ese nuevo commit, sincroniza automáticamente y Kubernetes descarga y corre la nueva imagen.

---

## Comandos de referencia rápida

```powershell
# Ver pods del microservicio
kubectl get pods -n mi-microservicio

# Ver pods de ArgoCD
kubectl get pods -n argocd

# Acceder al microservicio
kubectl port-forward svc/mi-microservicio-mi-microservicio 8080:80 -n mi-microservicio

# Acceder a la UI de ArgoCD
kubectl port-forward svc/argocd-server -n argocd 8081:443

# Ver logs del microservicio
kubectl logs -n mi-microservicio <nombre-del-pod>

# Forzar sincronización en ArgoCD (normalmente es automático)
kubectl rollout restart deployment mi-microservicio-mi-microservicio -n mi-microservicio

# Actualizar el chart después de cambios en values.yaml
helm upgrade mi-microservicio C:\Users\User\PycharmProjects\trabajoarqui\mi-microservicio\helm\mi-microservicio --namespace mi-microservicio
```

---

## Endpoints del microservicio

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Información del servicio |
| GET | `/health` | Estado de salud (usado por K8S para saber si el pod está vivo) |
| GET | `/docs` | Documentación automática generada por FastAPI (Swagger UI) |