---
id: PROCED-DEVOPS-001
tipo: procedimiento
categoria: devops
subcategoria: deployment
version: 1.0.0
fecha_creacion: 2025-11-17
autor: Claude Code (Sonnet 4.5)
estado: activo
relacionados: ["PROC-DEVOPS-001", "ADR-DEVOPS-001"]
---

# PROCED-DEVOPS-001: Deploy a Staging

## Objetivo

Proporcionar pasos detallados para realizar un deployment seguro y verificable al ambiente de staging del proyecto IACT.

## Alcance

Este procedimiento cubre:
- Pre-deployment checks
- Proceso de deployment
- Verificación post-deployment
- Rollback en caso de problemas

NO cubre:
- Deployment a producción (requiere procedimiento separado)
- Configuración inicial de infraestructura
- Cambios de configuración de servidores

## Pre-requisitos

- Acceso a CI/CD pipeline (GitHub Actions / Jenkins)
- Credenciales para ambiente staging
- Branch aprobado y merged a `develop` o rama correspondiente
- Tests pasando en CI

## Roles y Responsabilidades

- **DevOps Engineer**: Ejecuta deployment y monitorea
- **Tech Lead**: Aprueba deployment de cambios mayores
- **Developer**: Verifica funcionalidad post-deployment

## Procedimiento Detallado

### PASO 1: Pre-Deployment Checks

#### 1.1 Verificar estado de staging actual

```bash
# Verificar que staging esté operacional
curl -f https://staging.iact-project.com/api/health
# Esperado: HTTP 200 OK
```

#### 1.2 Verificar tests en CI

Ir a GitHub Actions / Jenkins y confirmar:
- ✅ Tests unitarios: PASSED
- ✅ Tests de integración: PASSED
- ✅ Linters: PASSED
- ✅ Security scans: PASSED
- ✅ Build: SUCCESSFUL

**Si algún check falla**: NO proceder con deployment.

---

#### 1.3 Revisar changelog

```bash
# Ver commits desde último deploy
git log staging..develop --oneline

# O usar GitHub compare
# https://github.com/org/repo/compare/staging...develop
```

Verificar:
- ¿Hay cambios de BD (migrations)?
- ¿Hay cambios en variables de entorno?
- ¿Hay cambios que requieren downtime?
- ¿Hay cambios que pueden romper integraciones?

---

#### 1.4 Notificar inicio de deployment

Enviar mensaje en canal de equipo:

```
🚀 Starting deployment to staging

Branch: develop
Commit: abc1234 - "feat(auth): implement JWT authentication"
ETA: 15 minutos
Expected downtime: 0 minutos

Status updates: 🧵
```

---

### PASO 2: Backup Pre-Deployment

#### 2.1 Backup de base de datos

```bash
# Conectar a servidor de staging
ssh user@staging.iact-project.com

# Crear backup de BD
pg_dump -U postgres iact_staging > /backups/iact_staging_$(date +%Y%m%d_%H%M%S).sql

# Verificar backup creado
ls -lh /backups/iact_staging_*.sql | tail -1
```

**Criterio de éxito**: Archivo de backup creado con tamaño > 0

---

#### 2.2 Backup de configuración

```bash
# Backup de variables de entorno
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Backup de archivos de configuración
tar -czf /backups/config_$(date +%Y%m%d_%H%M%S).tar.gz /etc/nginx /etc/systemd
```

---

### PASO 3: Ejecutar Deployment

#### 3.1 Opción A: Deployment Automático (CI/CD)

**Usando GitHub Actions**:

```bash
# Trigger deployment workflow
gh workflow run deploy-staging.yml --ref develop
```

**Verificar progreso**:

```bash
# Ver status del workflow
gh run list --workflow=deploy-staging.yml --limit 1
```

---

#### 3.2 Opción B: Deployment Manual

**Paso 1: Pull latest code**

```bash
ssh user@staging.iact-project.com

cd /var/www/iact-project
git fetch origin
git checkout develop
git pull origin develop
```

**Paso 2: Instalar dependencias**

```bash
# Python
source venv/bin/activate
pip install -r requirements.txt

# Node.js (si aplica)
npm install
```

**Paso 3: Ejecutar migrations**

```bash
# Django
python manage.py migrate --noinput

# Verificar migrations aplicadas
python manage.py showmigrations
```

**Paso 4: Collectstatic (Django)**

```bash
python manage.py collectstatic --noinput
```

**Paso 5: Build frontend (si aplica)**

```bash
npm run build
```

**Paso 6: Restart services**

```bash
# Reload application server
sudo systemctl restart iact-gunicorn

# Reload nginx
sudo systemctl reload nginx

# Restart workers (Celery, etc.)
sudo systemctl restart iact-celery-worker
```

---

### PASO 4: Verificación Post-Deployment

#### 4.1 Health checks

```bash
# API health check
curl -f https://staging.iact-project.com/api/health
# Esperado: {"status": "healthy", "version": "1.2.3"}

# Database connection
curl -f https://staging.iact-project.com/api/db-check
# Esperado: {"database": "connected"}

# Cache connection
curl -f https://staging.iact-project.com/api/cache-check
# Esperado: {"cache": "connected"}
```

---

#### 4.2 Smoke tests

Ejecutar tests críticos:

```bash
# Test de autenticación
curl -X POST https://staging.iact-project.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
# Esperado: HTTP 200 + token

# Test de endpoint protegido
curl -H "Authorization: Bearer $TOKEN" \
  https://staging.iact-project.com/api/users/me
# Esperado: HTTP 200 + user data
```

---

#### 4.3 Verificar logs

```bash
# Logs de aplicación (últimos 5 minutos)
sudo journalctl -u iact-gunicorn --since "5 minutes ago" --no-pager

# Verificar que NO haya errores críticos
sudo journalctl -u iact-gunicorn --since "5 minutes ago" | grep -i error
# Esperado: Sin resultados o solo warnings menores
```

---

#### 4.4 Verificar UI manualmente

Abrir en navegador:
- ✅ https://staging.iact-project.com
- ✅ Login exitoso
- ✅ Navegar páginas principales
- ✅ Verificar nueva funcionalidad deployada

---

#### 4.5 Verificar metrics

Revisar dashboard de monitoreo (Datadog, Grafana, etc.):
- ✅ Response times < threshold
- ✅ Error rate < 1%
- ✅ CPU usage normal
- ✅ Memory usage normal
- ✅ No picos de latencia

---

### PASO 5: Documentar Deployment

#### 5.1 Actualizar CHANGELOG

Editar `CHANGELOG.md`:

```markdown
## [Unreleased]

## [1.2.3] - 2025-11-17 (Staging)

### Added
- JWT authentication system
- Refresh token mechanism

### Changed
- Updated user permissions model

### Fixed
- Bug in permission validation
- Token expiration timing

### Deployment Notes
- Requires new env var: JWT_SECRET_KEY
- Database migrations: 0042_add_refresh_token_field
```

---

#### 5.2 Notificar éxito

Mensaje en canal de equipo:

```
✅ Deployment to staging SUCCESSFUL

Version: 1.2.3
Duration: 12 minutos
Downtime: 0 minutos

Health checks: ✅ All passing
Smoke tests: ✅ All passing

Staging ready for testing!
```

---

### PASO 6: Rollback (Si hay Problemas)

#### 6.1 Identificar problema

Síntomas que requieren rollback:
- 🔴 Health checks failing
- 🔴 Error rate > 5%
- 🔴 Critical functionality broken
- 🔴 Database corruption

---

#### 6.2 Ejecutar rollback inmediato

**Opción 1: Revert a commit anterior**

```bash
ssh user@staging.iact-project.com
cd /var/www/iact-project

# Encontrar último commit funcional
git log --oneline | head -5

# Revert a ese commit
git checkout abc1234  # commit anterior

# Restart services
sudo systemctl restart iact-gunicorn
sudo systemctl restart iact-celery-worker
```

**Opción 2: Rollback de migrations**

```bash
# Si migrations causan el problema
python manage.py migrate app_name 0041  # migration anterior

# Restart services
sudo systemctl restart iact-gunicorn
```

**Opción 3: Restaurar backup de BD**

```bash
# SOLO si corruption de BD
psql -U postgres iact_staging < /backups/iact_staging_20251117_140000.sql
```

---

#### 6.3 Verificar rollback exitoso

Repetir health checks y smoke tests del PASO 4.

---

#### 6.4 Notificar rollback

```
⚠️ ROLLBACK executed on staging

Reason: Critical error in JWT authentication
Rolled back to: version 1.2.2 (commit abc1234)
Status: ✅ Staging stable

Investigation ongoing.
```

---

#### 6.5 Investigar causa raíz

1. Revisar logs del deployment fallido
2. Reproducir problema localmente
3. Crear issue con detalles
4. Corregir problema
5. Re-ejecutar deployment con fix

---

## Métricas de Deployment

Monitorear:
- **Deployment frequency**: Cuántos deploys/semana
- **Lead time**: Tiempo desde commit hasta staging
- **Change failure rate**: % de deploys que requieren rollback
- **Mean time to recovery**: Tiempo promedio de rollback

**Targets**:
- Deployment frequency: >= 5/semana
- Change failure rate: < 10%
- MTTR: < 10 minutos

---

## Problemas Comunes y Soluciones

### Problema 1: Migrations fail

**Error**: `django.db.utils.OperationalError: relation does not exist`

**Solución**:
```bash
# Verificar estado de migrations
python manage.py showmigrations

# Aplicar migrations faltantes
python manage.py migrate --fake-initial
python manage.py migrate
```

---

### Problema 2: Static files not loading

**Error**: CSS/JS returning 404

**Solución**:
```bash
# Re-run collectstatic
python manage.py collectstatic --clear --noinput

# Verify nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

---

### Problema 3: Environment variables missing

**Error**: `KeyError: 'JWT_SECRET_KEY'`

**Solución**:
```bash
# Add missing variable to .env
echo "JWT_SECRET_KEY=your_secret_key_here" >> .env

# Reload service
sudo systemctl restart iact-gunicorn
```

---

## Checklist de Deployment

```markdown
Pre-Deployment:
- [ ] CI tests passing
- [ ] Changelog reviewed
- [ ] Team notified
- [ ] Backup de BD creado
- [ ] Backup de config creado

Deployment:
- [ ] Code pulled/deployed
- [ ] Dependencies installed
- [ ] Migrations executed
- [ ] Static files collected
- [ ] Services restarted

Post-Deployment:
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Logs sin errores críticos
- [ ] UI verificada manualmente
- [ ] Metrics normales
- [ ] CHANGELOG actualizado
- [ ] Team notificado éxito
```

---

## Referencias

- [PROC-DEVOPS-001: DevOps Automation](../procesos/PROC-DEVOPS-001-devops_automation.md)
- [ADR-DEVOPS-001: Vagrant mod_wsgi](../adr/ADR-DEVOPS-001-vagrant-mod-wsgi.md)
- [Twelve-Factor App: Deployment](https://12factor.net/)

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0.0 | 2025-11-17 | Claude Code | Versión inicial |

## Aprobación

- **Autor**: Claude Code (Sonnet 4.5)
- **Revisado por**: Pendiente
- **Aprobado por**: Pendiente
- **Fecha de próxima revisión**: 2026-02-17
