FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/home/callcenter/.local/bin:${PATH}"

# Instalar dependencias del sistema de manera idempotente
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    make \
    git \
    curl \
    ca-certificates \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario personalizado de manera idempotente
RUN groupadd callcenter 2>/dev/null || true \
    && id -u callcenter 2>/dev/null || useradd -m -s /bin/bash -g callcenter callcenter \
    && mkdir -p /workspaces \
    && chown -R callcenter:callcenter /workspaces

# Cambiar a usuario callcenter
USER callcenter
WORKDIR /workspaces

# Instalar herramientas de Python de manera idempotente
RUN pip install --user --upgrade --no-cache-dir \
    poetry \
    django \
    psycopg2-binary \
    djangorestframework \
    python-dotenv \
    black \
    ruff \
    pytest \
    coverage \
    drf-spectacular

# Crear directorio de configuración de pip de manera idempotente
RUN mkdir -p /home/callcenter/.config/pip \
    && { [ -f /home/callcenter/.config/pip/pip.conf ] || \
    echo -e "[global]\ndisable-pip-version-check = true\nno-cache-dir = false" > /home/callcenter/.config/pip/pip.conf; }

# Volumen para workspace
VOLUME ["/workspaces"]

CMD ["sleep", "infinity"]
