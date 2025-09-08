# ==========================
# 1. Build stage
# ==========================
FROM python:3.9-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalamos compiladores y dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Creamos un directorio con las dependencias ya instaladas
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# ==========================
# 2. Final stage
# ==========================
FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalamos solo curl (para healthcheck en producción)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos las dependencias desde el builder
COPY --from=builder /install /usr/local

# Copiamos la app
COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "Principal.py", "--server.port=8501", "--server.address=0.0.0.0"]
