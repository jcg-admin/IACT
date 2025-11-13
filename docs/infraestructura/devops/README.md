---
id: DOC-DEVOPS-INDEX
estado: activo
propietario: equipo-devops
ultima_actualizacion: 2025-11-02
relacionados: ["DOC-INDEX-GENERAL", "DOC-ARQ-INDEX", "ADR-2025-001"]
---
# DevOps - Proyecto IACT

Este espacio documenta la infraestructura, pipelines de CI/CD, runbooks operativos, y procedimientos de deployment del proyecto IACT.

## Página padre
- [Índice de espacios documentales](../index.md)

## Páginas hijas
- [Contenedores y DevContainer](contenedores_devcontainer.md)
- [Runbooks Operativos](runbooks/)
  - [Claude Code](runbooks/claude_code.md)
  - [Post-create Vagrant](runbooks/post_create.md)
  - [Codespaces con GitHub Copilot](runbooks/github_copilot_codespaces.md)
  - [Verificar Servicios](runbooks/verificar_servicios.md)
  - [Reprocesar ETL Fallido](runbooks/reprocesar_etl_fallido.md)
- [Backend - DevOps](../backend/devops/readme.md)
- [Frontend - DevOps](../frontend/devops/readme.md)
- [Infrastructure - DevOps](../infrastructure/devops/readme.md)

## Información clave

### Filosofía DevOps

El proyecto IACT adopta principios DevOps core:

1. **Infraestructura como Código (IaC)**
   - Configuración versionada en Git
   - Reproducible y auditable
   - Automatizada mediante scripts

2. **CI/CD Automatizado**
   - Tests automáticos en cada PR
   - Deployment automático a staging
   - Deployment manual a producción (por ahora)

3. **Observabilidad**
   - Logging centralizado
   - Métricas de sistema y aplicación
   - Alertas proactivas

4. **Cultura de Colaboración**
   - Desarrolladores participan en operaciones
   - Runbooks documentados y accesibles
   - Post-mortems sin culpa

### Entornos

#### Desarrollo Local

**Stack:**
- Vagrant 2.3+
- VirtualBox 7+
- Python 3.11+ (venv)

**Servicios:**
```
PostgreSQL: 127.0.0.1:15432
MariaDB:    127.0.0.1:13306
```

**Comandos:**
```bash
# Levantar infraestructura
vagrant up

# Verificar servicios
./scripts/verificar_servicios.sh

# Activar entorno Python
source .venv/bin/activate

# Ejecutar tests
pytest

# Runserver
python manage.py runserver
```

#### Staging (Futuro)

**Stack:**
- Docker + Docker Compose
- Servidor dedicado o cloud VM
- Base de datos gestionada

**URL:** `https://staging.iact.example.com`

#### Producción (Futuro)

**Stack:**
- Kubernetes (k8s)
- PostgreSQL RDS/managed
- Redis cluster
- Load balancer

**URL:** `https://iact.example.com`

### Pipeline CI/CD

#### Actual (Manual)

```
Developer -> Git Push -> Manual Review -> Manual Tests -> Manual Deploy
```

#### Objetivo Q2 2025

```
Developer
   ↓
Git Push
   ↓
GitHub Actions
   ├-> Lint (Pylint, Flake8, Black)
   ├-> Type Check (mypy)
   ├-> Unit Tests (pytest)
   ├-> Integration Tests
   └-> Security Scan (bandit)
   ↓
Build Docker Image
   ↓
Push to Registry
   ↓
Deploy to Staging (auto)
   ↓
Smoke Tests
   ↓
Deploy to Prod (manual approval)
   ↓
Post-deployment Tests
```

### Infraestructura como Código

#### Vagrant

**Archivo:** `vagrantfile`

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.network "forwarded_port", guest: 5432, host: 15432
  config.vm.network "forwarded_port", guest: 3306, host: 13306

  config.vm.provision "shell", path: "provisioning/bootstrap.sh"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 2
  end
end
```

**Script de Aprovisionamiento:** `provisioning/bootstrap.sh`
- Instala PostgreSQL 15
- Instala MariaDB 10
- Crea usuarios y bases de datos
- Configura acceso remoto
- Ejecuta scripts de inicialización

#### Docker (Futuro)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    ports:
      - "15432:5432"
    environment:
      POSTGRES_USER: django_user
      POSTGRES_PASSWORD: django_pass
      POSTGRES_DB: iact_analytics
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mariadb:
    image: mariadb:10.11
    ports:
      - "13306:3306"
    environment:
      MYSQL_USER: django_user
      MYSQL_PASSWORD: django_pass
      MYSQL_DATABASE: iact_ivr
    volumes:
      - mariadb_data:/var/lib/mysql

  django:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - mariadb

volumes:
  postgres_data:
  mariadb_data:
```

### Monitoring y Observabilidad

#### Logging

**Stack Objetivo:**
- **Agregación**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **Formato**: JSON estructurado
- **Niveles**: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Configuración Django:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

#### Métricas

**Stack Objetivo:**
- **Recolección**: Prometheus
- **Visualización**: Grafana
- **Alertas**: Prometheus Alertmanager

**Métricas Clave:**
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (%)
- Database connection pool usage
- ETL job duration
- Queue depth

#### Alertas

| Alerta | Condición | Severidad | Acción |
|--------|-----------|-----------|--------|
| High Error Rate | Error rate > 5% | Critical | Page on-call |
| Slow Response | p95 > 2s | Warning | Investigate |
| DB Connection Pool Full | Usage > 90% | Warning | Review queries |
| ETL Job Failed | Job exit != 0 | Critical | Run runbook |
| Disk Space Low | Usage > 85% | Warning | Clean logs |

### Deployment

#### Proceso Actual (Manual)

1. Merge PR a `develop`
2. Crear tag de release: `git tag v0.1.0`
3. Push tag: `git push origin v0.1.0`
4. SSH a servidor
5. `git pull origin main`
6. `python manage.py migrate`
7. `systemctl restart iact-django`
8. Verificar servicios

#### Proceso Objetivo (Automatizado)

```bash
# Deployment automático vía GitHub Actions
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions:
# 1. Run tests
# 2. Build Docker image
# 3. Push to registry
# 4. Deploy to staging
# 5. Run smoke tests
# 6. Wait for manual approval
# 7. Deploy to production
# 8. Run post-deployment tests
# 9. Notify Slack
```

### Runbooks

Los runbooks documentan procedimientos operativos comunes:

- [Claude Code](runbooks/claude_code.md) - Desarrollo con Claude Code, limitaciones y alternativas
- [Verificar Servicios](runbooks/verificar_servicios.md) - Validar que DB estén operativas
- [Reprocesar ETL Fallido](runbooks/reprocesar_etl_fallido.md) - Recuperar de fallas ETL
- [Post-create Vagrant](runbooks/post_create.md) - Setup después de `vagrant up`
- [GitHub Copilot Codespaces](runbooks/github_copilot_codespaces.md) - Configurar Codespaces

### Seguridad

#### Gestión de Secrets

**Actual:**
- Variables de entorno en `.env`
- `.env` en `.gitignore`
- Secrets no committeados

**Objetivo:**
- Vault (HashiCorp Vault) o AWS Secrets Manager
- Rotación automática de credenciales
- Audit log de accesos

#### Security Scanning

- **SAST**: Bandit (Python)
- **Dependency Check**: Safety, pip-audit
- **Container Scanning**: Trivy
- **Frequency**: En cada PR + nightly

### Backup y Disaster Recovery

#### Estrategia de Backup

**Base de Datos:**
- Backups automáticos diarios
- Retención: 30 días
- Testing de restore: Mensual

**Código:**
- Git como source of truth
- GitHub como backup remoto
- Mirrors en GitLab (futuro)

#### RTO/RPO

- **RTO** (Recovery Time Objective): 4 horas
- **RPO** (Recovery Point Objective): 24 horas

## Estado de cumplimiento

| Elemento | Estado | Observaciones |
|----------|--------|---------------|
| Infraestructura local documentada | OK Sí | Vagrant + VirtualBox |
| Pipeline CI/CD | NO No | Planeado para Q2 2025 |
| Monitoring configurado | NO No | Planeado para Q3 2025 |
| Runbooks creados | WARNING Parcial | 5 runbooks existentes |
| Backup strategy | WARNING Parcial | Solo Git, falta DB backups |

## Acciones prioritarias
- [ ] Implementar GitHub Actions para CI/CD
- [ ] Configurar pre-commit hooks (Black, Pylint, etc.)
- [ ] Crear Dockerfile y docker-compose.yml
- [ ] Establecer strategy de branching (Gitflow)
- [ ] Documentar proceso de rollback
- [ ] Configurar Prometheus + Grafana

## Recursos relacionados
- [Arquitectura](../arquitectura/readme.md)
- [ADR-2025-001: Vagrant](../arquitectura/adr/ADR-2025-001-vagrant-mod-wsgi.md)
- [Script verificar_servicios.sh](../../scripts/verificar_servicios.sh)
- [Vagrantfile](../../vagrantfile)
- [Bootstrap.sh](../../provisioning/bootstrap.sh)
