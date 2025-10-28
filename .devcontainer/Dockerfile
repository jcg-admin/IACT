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

# Crear usuario django
RUN groupadd -g 1000 django 2>/dev/null || true \
    && useradd -u 1000 -g 1000 -m -s /bin/bash django 2>/dev/null || true \
    && mkdir -p /workspaces \
    && chown -R django:django /workspaces

USER django
WORKDIR /workspaces

CMD ["sleep", "infinity"]