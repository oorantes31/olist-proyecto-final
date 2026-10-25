# Dockerfile para Microservicio de Riesgo de Pedidos Olist
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar artefactos de la API (código, pipeline entrenado, umbral)
COPY main.py .
COPY preparacion.py .
COPY modelo_riesgo.joblib .
COPY modelo_olist.joblib .
COPY umbral.json .

# Puerto de servicio
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Comando de inicio del servidor ASGI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
