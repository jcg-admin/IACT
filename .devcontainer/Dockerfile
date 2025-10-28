FROM python:3.12-alpine3.19

# Metadata de la imagen
LABEL maintainer="CallCenter Team"
LABEL description="Dev container for Django CallCenter application with PostgreSQL and MariaDB support"
LABEL version="1.0"
LABEL org.opencontainers.image.source="https://github.com/NestorMonroy/"

# Build arguments (pueden sobreescribirse en build time)
ARG PYTHON_VERSION=3.12
ARG USER_UID=1000
ARG USER_GID=1000

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONIOENCODING=UTF-8 \
    LANG=C.UTF-8

# Instalar dependencias del sistema
# Se agrupan en una sola capa RUN para optimizar el tamaño de la imagen
RUN apk add --no-cache \
    # PostgreSQL
    postgresql-dev \
    postgresql-client \
    # MariaDB/MySQL
    mariadb-dev \
    mariadb-client \
    mariadb-connector-c \
    # Herramientas de compilación (necesarias para psycopg2, mysqlclient)
    gcc \
    musl-dev \
    linux-headers \
    # Utilidades de desarrollo
    git \
    bash \
    curl \
    make \
    # Timezone data (útil para Django)
    tzdata \
    && rm -rf /var/cache/apk/*

# Actualizar pip a la última versión
RUN pip install --upgrade pip setuptools wheel

# Pre-instalar dependencias Python base en la imagen
# Esto acelera el inicio del Codespace ya que están en el prebuild
# Nota: requirements está en api/requirements/base.txt
COPY callcentersite/requirements/base.txt /tmp/base.txt

RUN pip install --no-cache-dir -r /tmp/base.txt \
    && rm /tmp/base.txt \
    # Verificar instalaciones críticas
    && python -c "import django; print(f'Django {django.get_version()} instalado correctamente')" \
    && python -c "import psycopg2; print('psycopg2 instalado correctamente')" \
    && python -c "import MySQLdb; print('mysqlclient instalado correctamente')"

# Crear grupo y usuario no-root para seguridad
# El UID/GID 1000 es estándar y evita problemas de permisos con archivos del host
RUN addgroup -g ${USER_GID} django \
    && adduser -D -u ${USER_UID} -G django -s /bin/bash django \
    && mkdir -p /home/django/.cache \
    && chown -R django:django /home/django

# Configurar directorio de trabajo
WORKDIR /workspace/callcentersite

# Cambiar a usuario no-root
# Todos los comandos posteriores se ejecutarán como 'django'
USER django

# Verificación de salud (opcional, para debugging)
# Este comando no se ejecuta automáticamente, pero está disponible
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# El comando por defecto es 'sleep infinity'
# Esto mantiene el contenedor vivo para que Codespaces pueda usarlo
CMD ["sleep", "infinity"]