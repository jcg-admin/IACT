---
id: DOC-DEVOPS-CONTAINERS
estado: activo
propietario: equipo-devops
ultima_actualizacion: 2025-11-02
relacionados: ["DOC-DEVOPS-INDEX", "ADR-2025-001"]
---
# Contenedores y DevContainers - Proyecto IACT

Este documento describe el uso de contenedores Docker y configuración de DevContainers para desarrollo del proyecto IACT.

## Página padre
- [DevOps](readme.md)

## Estado Actual

**Actualmente el proyecto usa Vagrant + VirtualBox** para entorno de desarrollo local (ver [ADR-2025-001](../arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md)).

Este documento prepara la estrategia de migración futura a contenedores Docker y DevContainers.

## DevContainers: Visión General

### ¿Qué son los DevContainers?

DevContainers permiten definir entornos de desarrollo completos usando contenedores Docker, integrados nativamente con VS Code y GitHub Codespaces.

**Ventajas:**
- ✅ Entorno consistente para todo el equipo
- ✅ Onboarding en minutos
- ✅ Integración con VS Code Remote
- ✅ Compatible con GitHub Codespaces
- ✅ Sin instalación de servicios en host

**Desventajas:**
- ❌ Requiere Docker Desktop (licencia para empresas grandes)
- ❌ Limitado a editores compatibles (VS Code principalmente)

## Configuración Propuesta

### Estructura de Archivos

```
.devcontainer/
├── devcontainer.json     # Configuración principal
├── Dockerfile            # Imagen del container de desarrollo
├── docker-compose.yml    # Servicios (PostgreSQL, MariaDB)
└── post-create.sh        # Script post-creación
```

### devcontainer.json

```json
{
  "name": "IACT Development",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",

  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "ms-toolsai.jupyter",
        "mtxr.sqltools",
        "mtxr.sqltools-driver-pg",
        "mtxr.sqltools-driver-mysql"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
          "source.organizeImports": true
        }
      }
    }
  },

  "postCreateCommand": "bash .devcontainer/post-create.sh",

  "forwardPorts": [8000, 15432, 13306],

  "remoteUser": "vscode"
}
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    postgresql-client \
    mariadb-client \
    build-essential \
    libpq-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Instalar dependencias Python
WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Herramientas de desarrollo
RUN pip install --no-cache-dir \
    black \
    pylint \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    ipython

USER $USERNAME
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
    command: sleep infinity
    environment:
      - DATABASE_URL=postgresql://django_user:django_pass@postgres:5432/iact_analytics
      - IVR_DATABASE_URL=mysql://django_user:django_pass@mariadb:3306/iact_ivr
    depends_on:
      - postgres
      - mariadb

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: django_user
      POSTGRES_PASSWORD: django_pass
      POSTGRES_DB: iact_analytics
    ports:
      - "15432:5432"

  mariadb:
    image: mariadb:10.11
    restart: unless-stopped
    volumes:
      - mariadb-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_USER: django_user
      MYSQL_PASSWORD: django_pass
      MYSQL_DATABASE: iact_ivr
    ports:
      - "13306:3306"

volumes:
  postgres-data:
  mariadb-data:
```

### post-create.sh

```bash
#!/bin/bash
set -e

echo "🚀 Iniciando configuración post-creación..."

# Esperar que bases de datos estén listas
echo "⏳ Esperando PostgreSQL..."
until pg_isready -h postgres -U django_user; do
  sleep 1
done

echo "⏳ Esperando MariaDB..."
until mysqladmin ping -h mariadb -u django_user -pdjango_pass --silent; do
  sleep 1
done

# Instalar dependencias Python (si requirements.txt cambió)
echo "📦 Instalando dependencias Python..."
pip install -r requirements.txt

# Ejecutar migraciones
echo "🗄️  Ejecutando migraciones..."
python manage.py migrate

# Crear superuser si no existe
echo "👤 Configurando superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser creado: admin/admin123')
else:
    print('✅ Superuser ya existe')
EOF

# Verificar conexiones a bases de datos
echo "✅ Verificando conexiones..."
python manage.py check --database default
python manage.py check --database ivr

echo "✨ Configuración completada! Entorno listo para desarrollo."
```

## Comparación: Vagrant vs DevContainers

| Aspecto | Vagrant + VirtualBox | DevContainers |
|---------|---------------------|---------------|
| **Boot time** | ~2 min | ~30 seg |
| **Consumo RAM** | ~2 GB | ~500 MB |
| **Compatibilidad OS** | ✅ Todos | ✅ Todos (con Docker) |
| **Integración IDE** | ⚠️ Manual | ✅ Nativa (VS Code) |
| **Curva aprendizaje** | 📊 Baja | 📊 Media |
| **Costo licencia** | ✅ Gratis | ⚠️ Docker Desktop (empresas) |
| **GitHub Codespaces** | ❌ No | ✅ Sí |
| **Snapshot/Restore** | ✅ Sí | ⚠️ Limitado |

## GitHub Codespaces

GitHub Codespaces utiliza automáticamente la configuración de DevContainers:

### Configuración de Codespaces

**.devcontainer/devcontainer.json** ya incluye configuración compatible:

```json
{
  "postCreateCommand": "bash .devcontainer/post-create.sh",
  "forwardPorts": [8000, 15432, 13306]
}
```

### Uso

1. Ir a repositorio en GitHub
2. Click en "Code" → "Codespaces" → "Create codespace on main"
3. Esperar ~2 minutos (primera vez)
4. Entorno completo listo en navegador o VS Code

### Ventajas

- ✅ Cero configuración local
- ✅ Desarrollo desde cualquier máquina
- ✅ Recursos en la nube (potencialmente más potentes)
- ✅ Colaboración en tiempo real

### Limitaciones

- ❌ Requiere conexión a internet
- ❌ Cuota mensual gratuita limitada (60h free tier)
- ❌ Puede tener latencia según ubicación

## Plan de Migración (Futuro)

### Fase 1: Preparación (Q2 2025)

- [ ] Crear configuración DevContainer en rama feature
- [ ] Probar con equipo piloto (2-3 desarrolladores)
- [ ] Documentar diferencias y problemas encontrados
- [ ] Obtener feedback

### Fase 2: Migración Gradual (Q3 2025)

- [ ] Ofrecer DevContainers como opción alternativa
- [ ] Mantener Vagrant como opción principal
- [ ] Capacitar equipo en Docker/DevContainers
- [ ] Migrar CI/CD a Docker

### Fase 3: Transición Completa (Q4 2025)

- [ ] Hacer DevContainers la opción por defecto
- [ ] Deprecar Vagrant (mantener docs)
- [ ] Actualizar README y onboarding
- [ ] Crear nuevo ADR documentando cambio

## Recursos Relacionados

- [Developing inside a Container](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces](https://docs.github.com/en/codespaces)
- [DevContainer Specification](https://containers.dev/)
- [ADR-2025-001: Vagrant](../arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md)

## Notas

Este documento es preparatorio. La configuración actual del proyecto sigue usando Vagrant (ver [README.md](../../readme.md)). La migración a DevContainers se evaluará en 2025 basándose en:

1. Licencias de Docker Desktop disponibles
2. Familiaridad del equipo con containers
3. Necesidad de GitHub Codespaces
4. Feedback de equipo piloto

**Estado**: Planificado, no implementado.
