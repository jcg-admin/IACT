# Configuracion de Ambientes (Dev, Staging, Prod)

Guia completa para manejar diferentes configuraciones en desarrollo, staging y produccion.

## Indice

1. [Introduccion](#introduccion)
2. [Estructura de Ambientes](#estructura-de-ambientes)
3. [Setup Inicial](#setup-inicial)
4. [Backend (Python/Django)](#backend-pythondjango)
5. [Frontend (React/JavaScript)](#frontend-reactjavascript)
6. [Infraestructura (Docker/CI-CD)](#infraestructura-dockerci-cd)
7. [Agentes AI](#agentes-ai)
8. [Casos de Uso](#casos-de-uso)
9. [Troubleshooting](#troubleshooting)

---

## Introduccion

El sistema soporta 3 ambientes:

| Ambiente | Proposito | Infraestructura |
|----------|-----------|-----------------|
| **development** | Desarrollo local | VM, localhost, mocks |
| **staging** | Testing pre-produccion | Servidores staging |
| **production** | Produccion real | Servidores produccion |

### Diferencias Clave

```
DESARROLLO:
- Base de datos: Maquina virtual (VM)
- APIs: localhost:8000
- LLM: Ollama local (gratis)
- Cache: Memoria
- Emails: Deshabilitados
- Debug: Habilitado

STAGING:
- Base de datos: staging-db.internal
- APIs: staging-api.example.com
- LLM: Claude Haiku (barato)
- Cache: Redis staging
- Emails: Solo a emails de test
- Debug: Deshabilitado

PRODUCCION:
- Base de datos: Credenciales directas
- APIs: api.example.com
- LLM: Claude Sonnet (mejor)
- Cache: Redis produccion
- Emails: Habilitados
- Debug: Deshabilitado
```

---

## Estructura de Ambientes

### Archivo `.env`

Copia el template y configura segun tu ambiente:

```bash
cp .env.example .env
```

Edita `.env` y configura:

```bash
# Cambia esto segun donde estes trabajando
ENVIRONMENT=development  # o "staging" o "production"

# Development usa VM
DB_VM_HOST=localhost
DB_VM_PORT=5432

# Production usa credenciales directas
DB_PROD_HOST=prod-db.example.com
DB_PROD_USER=prod_user
DB_PROD_PASSWORD=tu_password_segura
```

### Deteccion Automatica

El sistema detecta el ambiente en este orden:

1. Variable `ENVIRONMENT` en `.env`
2. Variable `APP_ENV`
3. Variable `DJANGO_ENV`
4. Default: `development`

---

## Setup Inicial

### 1. Instalar Dependencias

```bash
# Crear virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar `.env`

```bash
# Copiar template
cp .env.example .env

# Editar con tus valores
nano .env
```

### 3. Verificar Configuracion

```bash
# Script de verificacion
python3 examples/verify_environment.py
```

---

## Backend (Python/Django)

### Uso en Codigo Python

```python
from scripts.ai.shared.environment_config import get_environment_config

# Obtener configuracion
config = get_environment_config()

# Verificar ambiente actual
if config.is_dev:
    print("Estamos en desarrollo")
elif config.is_prod:
    print("Estamos en produccion")

# Obtener config de base de datos
db_config = config.get_database_config()

if db_config["use_vm"]:
    # Desarrollo: Conectar a VM
    host = db_config["host"]
    port = db_config["port"]

    if db_config["ssh_tunnel"]["enabled"]:
        # Crear SSH tunnel
        tunnel = create_ssh_tunnel(db_config["ssh_tunnel"])
else:
    # Produccion: Conexion directa
    host = db_config["host"]
    port = db_config["port"]
    ssl_mode = db_config["ssl_mode"]

# Conectar
connection = psycopg2.connect(
    host=host,
    port=port,
    database=db_config["database"],
    user=db_config["user"],
    password=db_config["password"]
)
```

### Ejemplo: Django settings.py

```python
# settings.py
from scripts.ai.shared.environment_config import get_environment_config

config = get_environment_config()
db_config = config.get_database_config()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_config['database'],
        'USER': db_config['user'],
        'PASSWORD': db_config['password'],
        'HOST': db_config['host'],
        'PORT': db_config['port'],
    }
}

# Debug solo en desarrollo
DEBUG = config.is_dev

# Allowed hosts segun ambiente
if config.is_dev:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
elif config.is_staging:
    ALLOWED_HOSTS = ['staging.example.com']
else:
    ALLOWED_HOSTS = ['www.example.com', 'api.example.com']

# Cache
cache_config = config.get_cache_config()
if cache_config['backend'] == 'redis':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': f"redis://{cache_config['host']}:{cache_config['port']}",
        }
    }
else:
    # Memory cache para desarrollo
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
```

### Ejemplo: Agente AI con Configuracion

```python
from scripts.ai.shared.environment_config import get_environment_config
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

# Obtener config del ambiente
env_config = get_environment_config()
llm_config = env_config.get_llm_config()

# Crear agente con config apropiada
agent = SDLCFeasibilityAgent(config=llm_config)

# En desarrollo: usara Ollama local
# En produccion: usara Claude Sonnet
result = agent.run({"issue": {...}})
```

---

## Frontend (React/JavaScript)

### Archivo de Configuracion

Crear `frontend/src/config/environment.js`:

```javascript
// environment.js
const environments = {
  development: {
    apiUrl: 'http://localhost:8000',
    enableAnalytics: false,
    enableLogging: true,
    mockAPIs: true
  },

  staging: {
    apiUrl: 'https://staging-api.example.com',
    enableAnalytics: true,
    enableLogging: true,
    mockAPIs: false
  },

  production: {
    apiUrl: 'https://api.example.com',
    enableAnalytics: true,
    enableLogging: false,
    mockAPIs: false
  }
};

// Detectar ambiente
const env = process.env.REACT_APP_ENV ||
            process.env.NODE_ENV ||
            'development';

export const config = environments[env];
export const isDev = env === 'development';
export const isStaging = env === 'staging';
export const isProd = env === 'production';
```

### Uso en Componentes React

```javascript
// api.js
import { config } from './config/environment';

export async function fetchData(endpoint) {
  // URL segun ambiente
  const url = `${config.apiUrl}${endpoint}`;

  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    if (config.enableLogging) {
      console.error('API Error:', error);
    }
    throw error;
  }
}

// Analytics (solo en produccion)
export function trackEvent(eventName, data) {
  if (config.enableAnalytics) {
    window.gtag('event', eventName, data);
  }
}
```

### Build Scripts

```json
{
  "scripts": {
    "start": "REACT_APP_ENV=development react-scripts start",
    "build:staging": "REACT_APP_ENV=staging react-scripts build",
    "build:prod": "REACT_APP_ENV=production react-scripts build"
  }
}
```

---

## Infraestructura (Docker/CI-CD)

### Dockerfile Multistage

```dockerfile
# Dockerfile
FROM python:3.11-slim as base

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Development stage
FROM base as development
ENV ENVIRONMENT=development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Staging stage
FROM base as staging
ENV ENVIRONMENT=staging
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

# Production stage
FROM base as production
ENV ENVIRONMENT=production
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### Docker Compose para Desarrollo

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: iact_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build:
      context: .
      target: development
    environment:
      - ENVIRONMENT=development
      - DB_VM_HOST=db
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - db

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  ollama_data:
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches:
      - main          # Deploy a produccion
      - staging       # Deploy a staging
      - develop       # Deploy a development

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Detect environment
        id: env
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == "refs/heads/staging" ]]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
          else
            echo "environment=development" >> $GITHUB_OUTPUT
          fi

      - name: Build Docker image
        run: |
          docker build --target ${{ steps.env.outputs.environment }} \
            -t myapp:${{ steps.env.outputs.environment }} .

      - name: Run tests
        run: |
          docker run myapp:${{ steps.env.outputs.environment }} \
            python -m pytest

      - name: Deploy to ${{ steps.env.outputs.environment }}
        run: |
          # Deploy logic aqui
          echo "Deploying to ${{ steps.env.outputs.environment }}"
```

### Kubernetes (si aplica)

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iact-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: registry.example.com/iact:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DB_PROD_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
        - name: DB_PROD_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
```

---

## Agentes AI

### Como Usan los Agentes la Configuracion

Todos los agentes SDLC detectan automaticamente el ambiente:

```python
# scripts/ai/sdlc/feasibility_agent.py

class SDLCFeasibilityAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__("SDLCFeasibilityAgent")

        # Si no hay config, obtener del ambiente
        if config is None:
            env_config = get_environment_config()
            config = env_config.get_llm_config()

        # En desarrollo: usara Ollama o heuristicas
        # En produccion: usara Claude Sonnet
        if config.get("use_llm"):
            self.llm_generator = LLMGenerator(
                provider=config["llm_provider"],
                model=config["model"]
            )
```

### Ejemplo Completo

```python
#!/usr/bin/env python3
"""
Script que se adapta automaticamente al ambiente.
"""
from scripts.ai.shared.environment_config import get_environment_config
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

# Obtener configuracion del ambiente
config = get_environment_config()

print(f"Ambiente actual: {config.environment}")
print(f"Es desarrollo: {config.is_dev}")
print(f"Es produccion: {config.is_prod}")

# Obtener config de LLM apropiada
llm_config = config.get_llm_config()

if config.is_dev:
    print("Modo desarrollo:")
    print(f"  - LLM Provider: {llm_config['llm_provider']}")
    print(f"  - Model: {llm_config['model']}")
    print(f"  - Max tokens: {llm_config['max_tokens']}")
elif config.is_prod:
    print("Modo produccion:")
    print(f"  - LLM Provider: {llm_config['llm_provider']}")
    print(f"  - Model: {llm_config['model']}")
    print(f"  - Monthly budget: ${llm_config['monthly_budget']}")

# Crear agente (usara config automatica)
agent = SDLCFeasibilityAgent(config=llm_config)

# Analizar feature
result = agent.run({
    "issue": {
        "title": "Add dark mode",
        "description": "Toggle between light and dark themes",
        "requirements": ["CSS variables", "localStorage"],
        "estimated_story_points": 2
    }
})

print(f"\nResultado: {result['phase_result'].decision}")
```

---

## Casos de Uso

### Caso 1: Desarrollador Local

```bash
# 1. Setup inicial
cp .env.example .env
nano .env  # Set ENVIRONMENT=development

# 2. Levantar servicios locales
docker-compose -f docker-compose.dev.yml up -d

# 3. Ejecutar agentes (usaran Ollama local)
python3 test_case1_viabilidad.py

# Resultado: Usa VM + Ollama (gratis, local)
```

### Caso 2: Testing en Staging

```bash
# 1. Configurar staging
export ENVIRONMENT=staging
export DB_STAGING_HOST=staging-db.internal
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Deploy a staging
git push origin staging

# 3. CI/CD automaticamente:
#    - Detecta ambiente = staging
#    - Usa Claude Haiku (barato)
#    - Conecta a staging-db.internal
```

### Caso 3: Deploy a Produccion

```bash
# 1. Configurar produccion en servidor
cat > /etc/iact/.env << EOF
ENVIRONMENT=production
DB_PROD_HOST=prod-db.example.com
DB_PROD_USER=prod_user
DB_PROD_PASSWORD=strong_password_here
ANTHROPIC_API_KEY=sk-ant-prod-key
EOF

# 2. Deploy
git push origin main

# 3. Sistema automaticamente:
#    - Detecta ambiente = production
#    - Usa Claude Sonnet (mejor)
#    - Conecta directamente a prod-db
#    - Habilita SSL
#    - Habilita monitoring
```

### Caso 4: Switch Rapido entre Ambientes

```bash
# Desarrollo
export ENVIRONMENT=development
python3 test_case1_viabilidad.py
# Usa: VM + Ollama

# Staging
export ENVIRONMENT=staging
python3 test_case1_viabilidad.py
# Usa: Staging DB + Claude Haiku

# Produccion
export ENVIRONMENT=production
python3 test_case1_viabilidad.py
# Usa: Prod DB + Claude Sonnet
```

---

## Troubleshooting

### Error: "Produccion requiere variables"

```
ValueError: Produccion requiere variables: DB_PROD_HOST, DB_PROD_USER
```

**Solucion**: En produccion, debes configurar todas las variables criticas:

```bash
# .env
DB_PROD_HOST=your-prod-db.com
DB_PROD_USER=your_user
DB_PROD_PASSWORD=your_password
API_PROD_URL=https://api.example.com
```

### Error: "Cannot connect to database"

**Desarrollo**:
```bash
# Verificar que VM esta corriendo
docker ps | grep postgres

# O levantarla
docker-compose -f docker-compose.dev.yml up -d db
```

**Produccion**:
```bash
# Verificar credenciales
psql -h $DB_PROD_HOST -U $DB_PROD_USER -d $DB_PROD_NAME
```

### Error: "LLM API 404"

**Desarrollo**: Instalar Ollama
```bash
# Mac
brew install ollama
ollama serve

# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

**Produccion**: Agregar API key
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY
```

### Verificar Configuracion Actual

```python
#!/usr/bin/env python3
from scripts.ai.shared.environment_config import get_environment_config

config = get_environment_config()

print(f"Environment: {config.environment}")
print(f"Database: {config.get_database_config()['host']}")
print(f"API: {config.get_api_config()['base_url']}")
print(f"LLM: {config.get_llm_config()['llm_provider']}")
print(f"Cache: {config.get_cache_config()['backend']}")

# Validar
try:
    config.validate_config()
    print("\n[OK] Configuracion valida")
except ValueError as e:
    print(f"\n[ERROR] {e}")
```

---

## Resumen

| Aspecto | Development | Staging | Production |
|---------|-------------|---------|------------|
| **Database** | VM/localhost | staging-db | prod-db (directo) |
| **API** | localhost:8000 | staging-api | api.example.com |
| **LLM** | Ollama (gratis) | Haiku (barato) | Sonnet (mejor) |
| **Cache** | Memoria | Redis | Redis |
| **Debug** | Habilitado | Deshabilitado | Deshabilitado |
| **Emails** | Deshabilitados | Solo test | Habilitados |
| **Monitoring** | Logs console | Logs + Sentry | Sentry + APM |

El sistema detecta automaticamente el ambiente y aplica la configuracion correcta.

No necesitas cambiar codigo, solo configurar `.env` correctamente.
