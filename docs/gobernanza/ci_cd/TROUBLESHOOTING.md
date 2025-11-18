---
title: CI/CD - Troubleshooting
date: 2025-11-13
domain: gobernanza
status: active
---

# CI/CD - Troubleshooting

Problemas comunes y sus soluciones.

---

## Tests Fallando

### Error: Coverage < 80%

**Sintoma**:
```
FAIL Required test coverage of 80% not reached. Total coverage: 75.32%
```

**Causa**: Coverage insuficiente

**Solucion**:
```bash
# Ver que archivos faltan coverage
pytest --cov=callcentersite --cov-report=term-missing

# Agregar tests para archivos con bajo coverage
# Ejemplo: settings.py tiene 45% coverage
# Crear: tests/test_settings.py
```

**Prevencion**:
- Escribir tests mientras desarrollas (TDD)
- Coverage >= 80% antes de PR

---

### Error: Test Pyramid Validation Failed

**Sintoma**:
```
[FAIL] Unit tests are only 35% (should be >= 50%)
```

**Causa**: Demasiados integration/E2E tests, pocos unit tests

**Solucion**:
```bash
# Ver distribucion actual
./scripts/ci/test_pyramid_check.sh

# Agregar mas unit tests
# Unit tests: test models, services, utilities en aislamiento
# NO unit tests: NO deben tocar DB, NO API calls, NO file I/O
```

**Target**:
- Unit: 60% (minimo 50%)
- Integration: 30% (20-40%)
- E2E: 10% (maximo 20%)

---

### Error: Tests Pasan Local, Fallan en CI

**Sintomas Comunes**:

**1. Database differences**
```bash
# CI usa MySQL 8.0, local usa MySQL 5.7
# Solucion: Actualizar MySQL local a 8.0
```

**2. Timezone issues**
```python
# CI usa UTC
# Solucion: Usar timezone-aware datetimes
from django.utils import timezone
now = timezone.now()  # NO: datetime.now()
```

**3. File path issues**
```python
# Solucion: Usar Path objects
from pathlib import Path
base_dir = Path(__file__).parent
```

**4. Environment variables**
```bash
# CI no tiene .env file
# Solucion: Settings con defaults
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
```

---

## Lint Errors

### Error: Flake8 Errors

**Sintoma**:
```
./api/callcentersite/settings.py:152:80: E501 line too long (95 > 79 characters)
```

**Solucion**:
```bash
# Auto-fix con black
cd api/callcentersite
black .

# Manual: Dividir linea larga
# Antes:
SOME_VERY_LONG_VARIABLE_NAME = "This is a very long string that exceeds the character limit"

# Despues:
SOME_VERY_LONG_VARIABLE_NAME = (
    "This is a very long string "
    "that exceeds the character limit"
)
```

---

### Error: Import Order (isort)

**Sintoma**:
```
ERROR: Imports are incorrectly sorted and/or formatted
```

**Solucion**:
```bash
# Auto-fix
cd api/callcentersite
isort .

# Verificar
isort --check-only .
```

**Orden correcto**:
```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from django.conf import settings
import pytest

# 3. Local
from .models import User
from ..services import UserService
```

---

## Security Scan Issues

### Error: Redis Detected (RNF-002)

**Sintoma**:
```
[FAIL] Redis detected in settings. Prohibited by RNF-002
```

**Causa**: Uso de Redis (prohibido)

**Solucion**:
```python
# INCORRECTO:
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# CORRECTO (RNF-002):
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Session backend CORRECTO:
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # MySQL
```

---

### Error: SQL Injection Risk

**Sintoma**:
```
[FAIL] String formatting in SQL queries detected (SQL INJECTION RISK!)
```

**Causa**: String formatting en queries

**Solucion**:
```python
# INCORRECTO (SQL injection!):
User.objects.raw(f"SELECT * FROM users WHERE username = '{username}'")

# CORRECTO (parameterized):
User.objects.raw("SELECT * FROM users WHERE username = %s", [username])

# MEJOR (usar ORM):
User.objects.filter(username=username)
```

---

### Error: Critical npm Vulnerabilities

**Sintoma**:
```
[FAIL] CRITICAL vulnerabilities found in npm packages
```

**Solucion**:
```bash
cd frontend

# Ver detalles
npm audit

# Fix automatico (si disponible)
npm audit fix

# Fix manual
npm update <package-name>

# Si no hay fix, considerar alternativa
npm uninstall <vulnerable-package>
npm install <alternative-package>
```

---

## Deployment Issues

### Error: Health Check Failed

**Sintoma**:
```
Health check failed after deployment
curl: (22) The requested URL returned error: 500
```

**Diagnostico**:
```bash
# SSH al servidor
ssh user@production-server

# Ver logs
sudo tail -f /var/log/iact/gunicorn.log
sudo tail -f /var/log/iact/error.log

# Check service status
sudo systemctl status gunicorn-iact-production
```

**Causas comunes**:

**1. Migraciones no aplicadas**
```bash
cd /var/www/iact/api/callcentersite
python manage.py migrate --no-input
sudo systemctl restart gunicorn-iact-production
```

**2. Static files no generados**
```bash
python manage.py collectstatic --no-input
```

**3. Permisos incorrectos**
```bash
sudo chown -R www-data:www-data /var/www/iact
```

**4. Environment variables faltantes**
```bash
# Verificar .env
cat /var/www/iact/.env

# Debe tener: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY
```

---

### Error: Database Connection Failed

**Sintoma**:
```
django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")
```

**Diagnostico**:
```bash
# Test conexion MySQL
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT 1;"

# Check MySQL running
sudo systemctl status mysql

# Check network
telnet $DB_HOST 3306
```

**Solucion**:
```bash
# Restart MySQL
sudo systemctl restart mysql

# Verificar firewall
sudo ufw status
sudo ufw allow from <app-server-ip> to any port 3306

# Verificar MySQL users
mysql -u root -p
> SELECT user, host FROM mysql.user;
> GRANT ALL ON iact_production.* TO 'iact_user'@'%';
> FLUSH PRIVILEGES;
```

---

### Error: Rollback Failed

**Sintoma**:
```
Rollback failed: Database restore error
```

**Causa**: Backup corrupto o incompatible

**Solucion**:
```bash
# Verificar backup
mysqldump --version
file backup_20251106_150000.sql

# Test restore en ambiente temporal
mysql -u root -p test_restore < backup_20251106_150000.sql

# Si backup corrupto, usar backup anterior
ls -lh /backup/*.sql
mysql -u root -p iact_production < backup_20251106_140000.sql  # 1 hour earlier
```

**Prevencion**:
- Backups automaticos cada hora
- Test restore mensualmente
- Mantener ultimos 7 dias de backups

---

## Performance Issues

### Error: Slow Response Time (> 2s)

**Diagnostico**:
```bash
# Medir response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/endpoint

# Ver slow queries
mysql -e "SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;"

# Django debug toolbar (solo development)
# Instalar: pip install django-debug-toolbar
```

**Causas comunes**:

**1. N+1 Queries**
```python
# INCORRECTO (N+1):
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # Query por cada user!

# CORRECTO:
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.bio)  # 1 query total
```

**2. Session Table Grande**
```bash
# Ver size
mysql -e "SELECT COUNT(*) FROM django_session;"

# Limpiar sesiones expiradas
python manage.py clearsessions

# Automatizar (cron):
# 0 2 * * * cd /var/www/iact/api/callcentersite && python manage.py clearsessions
```

**3. Missing Indexes**
```sql
-- Identificar queries sin index
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- Si "type: ALL" = full table scan (MALO)
-- Agregar index
CREATE INDEX idx_users_email ON users(email);
```

---

### Error: High Memory Usage

**Diagnostico**:
```bash
# Ver memoria
free -h

# Ver procesos Python
ps aux | grep python | awk '{print $6, $11}'

# Memory profiler
pip install memory_profiler
python -m memory_profiler manage.py runserver
```

**Solucion**:
```bash
# Restart workers (libera memoria)
sudo systemctl restart gunicorn-iact-production

# Ajustar workers (en gunicorn.conf):
# workers = 2 * CPU_CORES + 1
# max_requests = 1000  # Reciclar workers cada 1000 requests
```

---

## Workflow Failures

### Error: Workflow Timeout

**Sintoma**:
```
Error: The operation was canceled.
```

**Causa**: Job excede 2 horas (default timeout)

**Solucion**:
```yaml
# En .github/workflows/backend-ci.yml
jobs:
  test-mysql:
    timeout-minutes: 30  # Agregar timeout especifico
```

---

### Error: Artifact Upload Failed

**Sintoma**:
```
Error: Unable to upload artifact. Max size 5GB exceeded
```

**Solucion**:
```yaml
# Reducir size de artifact
- name: Upload logs
  uses: actions/upload-artifact@v4
  with:
    name: test-logs
    path: |
      logs/*.log
      !logs/debug*.log  # Excluir archivos grandes
    retention-days: 7  # Reducir retention
```

---

## Migration Issues

### Error: Migration Conflict

**Sintoma**:
```
CommandError: Conflicting migrations detected
```

**Causa**: Dos branches crearon migraciones simultaneas

**Solucion**:
```bash
# Opcion 1: Rebase y recrear migracion
git checkout feature/my-feature
git rebase develop
rm -rf */migrations/0012_*.py  # Eliminar migracion conflictiva
python manage.py makemigrations

# Opcion 2: Merge migration
python manage.py makemigrations --merge
```

---

### Error: Migration No Reversible

**Sintoma**:
```
Cannot reverse this migration (data loss)
```

**Causa**: Migration destructiva (DROP COLUMN, DELETE MODEL)

**Solucion**:
```python
# Hacer migration reversible con multi-step approach

# Step 1 migration: Agregar nueva column (reversible)
class Migration(migrations.Migration):
    operations = [
        migrations.AddField('User', 'new_email', models.EmailField(null=True)),
    ]

# Deploy, migrate data manualmente
# UPDATE users SET new_email = old_email;

# Step 2 migration: Remover old column (ahora reversible con data en new_email)
class Migration(migrations.Migration):
    operations = [
        migrations.RemoveField('User', 'old_email'),
    ]
```

---

## General Debugging

### Logs Locations

```bash
# Application logs
/var/log/iact/gunicorn.log
/var/log/iact/error.log

# System logs
journalctl -u gunicorn-iact-production
journalctl -u nginx

# Database logs
/var/log/mysql/error.log
/var/log/mysql/slow-query.log
```

### Verbose Mode

```bash
# Django manage.py con verbosity
python manage.py migrate --verbosity=2

# pytest con output
pytest -v -s

# Script con debug
bash -x ./scripts/ci/backend_test.sh
```

### Remote Debugging

```bash
# SSH tunel para debugging
ssh -L 8000:localhost:8000 user@server

# Django shell remoto
ssh user@server "cd /var/www/iact/api/callcentersite && python manage.py shell"
```

---

## Escalation

Si problema persiste:

1. **Revisar documentacion**: [INDICE.md](INDICE.md)
2. **Buscar en issues**: GitHub Issues del proyecto
3. **Consultar equipo**: Slack #devops-help
4. **Crear incident**: Si afecta produccion, usar [incident-response workflow](workflows/incident-response.md)

### Contactos

- **DevOps Lead**: [contact]
- **Backend Lead**: [contact]
- **Security Team**: [contact]
- **On-Call**: [PagerDuty/on-call system]

---

**Version**: 1.0
**Fecha**: 2025-11-06
**Mantenido por**: DevOps Team
