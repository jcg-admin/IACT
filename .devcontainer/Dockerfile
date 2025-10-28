FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    make \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario personalizado sin forzar UID/GID
RUN groupadd callcenter || true \
    && useradd -m -s /bin/bash -g callcenter callcenter || true \
    && mkdir -p /workspaces \
    && chown -R callcenter:callcenter /workspaces

USER callcenter
WORKDIR /workspaces

CMD ["sleep", "infinity"]
