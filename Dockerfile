# Usa la misma versión de Python que tu entorno local si vas a cargar el .joblib
FROM python:3.8-slim

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=180 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Herramientas mínimas por si pip necesita compilar algo
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# 👇 tiempo de espera más alto + preferir binarios (wheels)
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary --default-timeout=180 \
        -i https://pypi.org/simple \
        --trusted-host pypi.org --trusted-host files.pythonhosted.org \
        -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]

