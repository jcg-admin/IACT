FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/callcenter/.npm-global/bin:/home/callcenter/.local/bin:${PATH}"

# Instalar dependencias del sistema de manera idempotente
# - build-essential proporciona gcc/g++/make en un único paquete
# - default-libmysqlclient-dev habilita la compilación de mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    default-libmysqlclient-dev \
    build-essential \
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

# Instalar herramientas base de Python de manera idempotente.
# Las dependencias del proyecto se resuelven durante post-create para evitar duplicar instalaciones.
RUN pip install --user --upgrade \
    pip \
    setuptools \
    wheel \
    poetry

# Crear directorio de configuración de pip de manera idempotente
RUN mkdir -p /home/callcenter/.config/pip \
    && { [ -f /home/callcenter/.config/pip/pip.conf ] || \
    echo -e "[global]\ndisable-pip-version-check = true\nno-cache-dir = false" > /home/callcenter/.config/pip/pip.conf; }

# Volumen para workspace
VOLUME ["/workspaces"]

CMD ["sleep", "infinity"]
