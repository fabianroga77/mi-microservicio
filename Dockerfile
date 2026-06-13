# Imagen Docker del microservicio
# Se construye en local con: docker build -t mi-microservicio:local .
# En GitHub Actions el CI hace lo mismo y la sube a ghcr.io

FROM python:3.11-slim

WORKDIR /app

# Copiamos requirements.txt antes que el codigo a proposito:
# si solo cambias main.py, Docker reusa la capa de pip install y el build es mas rapido
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El Dockerfile copia app/ dentro de /app, por eso uvicorn importa "main" y no "app.main"
COPY app/ .

# Mismo puerto que usa FastAPI/Uvicorn y el targetPort del Helm chart
EXPOSE 8000

# 0.0.0.0 para que responda desde afuera del contenedor (no solo localhost)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
