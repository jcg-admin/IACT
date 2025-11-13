---
title: CI/CD - Guia de Uso por Rol
date: 2025-11-13
domain: gobernanza
status: active
---

# CI/CD - Guia de Uso por Rol

Guias especificas para Developer, QA, DevOps y Tech Lead.

---

## Developer

### Workflow Diario

#### 1. Antes de empezar a trabajar

```bash
# Actualizar codigo
git pull origin develop

# Crear feature branch
git checkout -b feature/IACT-123-dark-mode
```

#### 2. Durante desarrollo

```bash
# Ejecutar tests relevantes frecuentemente
cd api/callcentersite
python manage.py test callcentersite.tests.test_settings

# O usar script completo (mas lento)
./scripts/ci/backend_test.sh --mysql
```

#### 3. Antes de hacer commit

```bash
# Lint automatico
cd api/callcentersite
black .
isort .
flake8 .

# Tests rapidos
python manage.py test --parallel --keepdb

# Validar restricciones IACT
./scripts/ci/security_scan.sh
```

#### 4. Antes de push

```bash
# Suite completa (recomendado antes de PR)
./scripts/ci/backend_test.sh --mysql
./scripts/ci/frontend_test.sh --unit
./scripts/ci/test_pyramid_check.sh
```

**Tiempo estimado**: 5-10 minutos

#### 5. Crear Pull Request

```bash
# Push a feature branch
git push -u origin feature/IACT-123-dark-mode

# Crear PR via GitHub
# Los workflows CI/CD se ejecutaran automaticamente
```

### Checklist Pre-Push

- [ ] Codigo linted (black, isort, flake8, ESLint)
- [ ] Tests unitarios pasando
- [ ] Coverage > 80%
- [ ] NO emojis en codigo/docs
- [ ] NO uso de Redis (RNF-002)
- [ ] NO uso de Email/SMTP
- [ ] Commit message formato: `tipo(scope): mensaje`

### Comandos Utiles

```bash
# Tests rapidos (solo cambios)
pytest -x --ff

# Coverage especifico
pytest --cov=callcentersite.settings --cov-report=term-missing

# Lint solo archivos modificados
git diff --name-only | grep '\.py$' | xargs flake8

# Ver diferencias antes de commit
git diff --staged
```

### Cuando falla CI

1. **Revisar logs en GitHub Actions**
   - Click en el check fallido
   - Leer output completo

2. **Reproducir localmente**
   ```bash
   # Mismo comando que CI
   ./scripts/ci/backend_test.sh --all
   ```

3. **Corregir y re-push**
   ```bash
   # Fix codigo
   # Re-run tests
   git add .
   git commit --amend --no-edit
   git push --force-with-lease
   ```

---

## QA

### Workflow de Testing

#### 1. Testing en Feature Branch

```bash
# Checkout feature branch
git checkout feature/IACT-123-dark-mode

# Ejecutar suite completa
./scripts/ci/backend_test.sh --all
./scripts/ci/frontend_test.sh --all
./scripts/ci/test_pyramid_check.sh
./scripts/ci/security_scan.sh
```

**Tiempo estimado**: 15-20 minutos

#### 2. Validar Test Pyramid

```bash
# Generar reporte
REPORT_FILE=test-pyramid-report.md ./scripts/ci/test_pyramid_check.sh

# Revisar reporte
cat test-pyramid-report.md
```

**Criterios aceptacion**:
- Unit tests >= 50%
- Integration tests 20-40%
- E2E tests <= 20%

#### 3. Ejecutar Tests Manuales

Seguir test plan generado por SDLCTestingAgent:
```bash
# Ver test plan
cat docs/sdlc_outputs/testing/TEST_PLAN_*.md

# Ver test cases
cat docs/sdlc_outputs/testing/TEST_CASES_*.md
```

#### 4. Reportar Issues

Si falla:
```bash
# Crear issue con detalles
# Usar template de bug report
# Incluir:
# - Pasos para reproducir
# - Comportamiento esperado vs actual
# - Screenshots (si aplica)
# - Logs relevantes
```

### Checklist QA

- [ ] Todos los tests automatizados pasando
- [ ] Test pyramid cumple criterios
- [ ] Coverage > 80%
- [ ] Tests manuales completados
- [ ] Security scan pasando
- [ ] Performance aceptable (< 2s response time)
- [ ] Validacion RNF-002 (NO Redis)

### Comandos Utiles

```bash
# Ver coverage detallado
cd api/callcentersite
pytest --cov=callcentersite --cov-report=html
# Abrir htmlcov/index.html

# Ejecutar solo tests de integracion
pytest -m integration

# Ejecutar solo tests E2E
pytest -m e2e

# Ver tests mas lentos
pytest --durations=10
```

### Tipos de Testing

**1. Unit Tests**
```bash
./scripts/ci/backend_test.sh --mysql
# Solo tests de modelos/servicios aislados
```

**2. Integration Tests**
```bash
cd api/callcentersite
pytest -m integration
# Tests de API endpoints end-to-end
```

**3. E2E Tests**
```bash
./scripts/ci/frontend_test.sh --e2e
# Tests de flujos completos de usuario
```

**4. Performance Tests**
```bash
# Medir response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health
```

**5. Security Tests**
```bash
./scripts/ci/security_scan.sh
# Bandit, npm audit, SQL injection, XSS, CSRF
```

---

## DevOps

### Deployment Workflow

#### 1. Pre-Deployment

```bash
# Validar que CI esta GREEN
# Revisar GitHub Actions - todos los checks pasando

# Ejecutar validaciones locales
./scripts/ci/security_scan.sh
./scripts/validate_critical_restrictions.sh

# Backup base de datos
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD iact_staging > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 2. Deployment a Staging

**Manual via GitHub Actions**:
1. Go to Actions tab
2. Select "Deploy" workflow
3. Run workflow:
   - Branch: main
   - Environment: staging
   - Skip tests: false

**O via git tag**:
```bash
# Push a main activa deployment automatico a staging
git checkout main
git pull origin main
git push origin main
```

#### 3. Validar Staging

```bash
# Health check
curl -f https://staging.iact.example.com/api/health

# Smoke tests
./scripts/smoke_test_staging.sh

# Monitorear logs
ssh user@staging-server "tail -f /var/log/iact/gunicorn.log"
```

#### 4. Deployment a Production

**Solo con tag**:
```bash
# Tag version
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3

# Workflow deploy.yml se activa automaticamente
# Blue-green deployment se ejecuta
```

#### 5. Post-Deployment Monitoring

```bash
# Monitorear primeros 5 minutos
watch -n 10 'curl -s https://iact.example.com/api/health'

# Revisar metricas
# - Response time
# - Error rate
# - CPU/Memory usage

# Revisar session table size
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM django_session;" iact_production
```

#### 6. Rollback (si necesario)

```bash
# Ejecutar rollback plan
# Ver: docs/sdlc_outputs/deployment/ROLLBACK_PLAN_production_*.md

# Rollback automatico via GitHub Actions
# Go to Actions → Deploy workflow → Re-run con version anterior
```

### Checklist Pre-Deployment

- [ ] CI GREEN (todos los workflows pasando)
- [ ] Security scan pasando
- [ ] RNF-002 validado (NO Redis)
- [ ] Database backup creado
- [ ] Rollback plan revisado
- [ ] Team notificado
- [ ] On-call engineer disponible
- [ ] Deployment window programado (low traffic)

### Incident Response

#### 1. Detectar Incidente

```bash
# Via monitoreo automatico
# O via reporte manual

# Activar incident response workflow
# Go to Actions → Incident Response → Run workflow
# Seleccionar:
# - incident_type: production_down, performance_degradation, etc.
# - severity: critical, high, medium, low
# - description
```

#### 2. Ejecutar Playbook

```bash
# Workflow crea issue automatico
# Genera diagnostics
# Proporciona playbook especifico

# Seguir steps del playbook
# Ejemplo para production_down:
# 1. Verify health endpoint
# 2. Check application server status
# 3. Check database connectivity
# 4. Review logs
# 5. Consider rollback
```

#### 3. Comunicacion

```bash
# Notificar via InternalMessage (NO email - RNF-002)
# Actualizar incident issue
# Alertar equipo
```

### Comandos Utiles

```bash
# Ver status de servicios
systemctl status gunicorn-iact-production
systemctl status nginx

# Ver logs en tiempo real
journalctl -u gunicorn-iact-production -f

# Restart services
systemctl restart gunicorn-iact-production
systemctl reload nginx

# Limpiar sesiones MySQL
python manage.py clearsessions

# Ver conexiones activas
mysql -e "SHOW PROCESSLIST;"

# Disk space
df -h

# Memory usage
free -h

# Running processes
ps aux | grep python
```

### Monitoring

**Metricas clave**:
- Response time: < 2s
- Error rate: < 1%
- CPU usage: < 70%
- Memory usage: < 80%
- Disk usage: < 80%
- Session table size: < 100k records

**Alerting thresholds**:
- CRITICAL: Response time > 5s, Error rate > 5%
- WARNING: Response time > 3s, Error rate > 2%

---

## Tech Lead

### Code Review Workflow

#### 1. Revisar PR

**Checklist automatico** (CI/CD):
- [ ] backend-ci: PASS
- [ ] frontend-ci: PASS
- [ ] test-pyramid: PASS
- [ ] security-scan: PASS

**Review manual**:
- [ ] Codigo sigue convencion del proyecto
- [ ] No hay complejidad innecesaria
- [ ] Tests cubren casos edge
- [ ] Documentacion actualizada
- [ ] NO emojis en codigo/docs
- [ ] RNF-002 respetado

#### 2. Ejecutar Tests Localmente

```bash
# Checkout PR branch
gh pr checkout 123

# Ejecutar validaciones
./scripts/ci/backend_test.sh --all
./scripts/ci/security_scan.sh
./scripts/ci/test_pyramid_check.sh
```

#### 3. Aprobar y Merge

```bash
# Si todo OK
# Aprobar PR en GitHub
# Merge to develop

# Auto-deploy a staging se activa
```

### Architecture Review

Para cambios arquitectonicos:
```bash
# Revisar ADRs generados
cat docs/sdlc_outputs/design/ADR_*.md

# Revisar HLD
cat docs/sdlc_outputs/design/HLD_*.md

# Revisar diagramas
cat docs/sdlc_outputs/design/DIAGRAMS_*.md
```

**Criterios**:
- [ ] Cumple restricciones IACT (RNF-002)
- [ ] Escalable y mantenible
- [ ] Seguro (CSRF, XSS, SQL injection protegido)
- [ ] Performance aceptable
- [ ] Documentado adecuadamente

### Metricas y KPIs

**Revisar semanalmente**:

```bash
# Test pyramid
./scripts/ci/test_pyramid_check.sh

# Coverage trend
pytest --cov=callcentersite --cov-report=term

# Security scan
./scripts/ci/security_scan.sh

# DORA metrics
python scripts/dora_metrics.py --start-date 2025-10-01 --end-date 2025-11-01
```

**Targets**:
- Coverage: > 80%
- Test pyramid: 60/30/10
- Security: 0 critical vulnerabilities
- Deployment frequency: Daily (staging)
- Lead time: < 1 day

### Team Management

**Capacity planning**:
```bash
# Revisar velocity
# Story points completados por sprint

# Analizar blockers
# Issues con label "blocked"

# Review WIP
# PRs abiertas > 3 dias
```

---

## Recursos Adicionales

### Documentacion

- [README.md](README.md) - Vista general CI/CD
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problemas comunes
- [EJEMPLOS.md](EJEMPLOS.md) - Flujos completos
- [workflows/](workflows/) - Docs workflows individuales
- [scripts/](scripts/) - Docs scripts individuales

### Scripts Utiles

```bash
# Pre-push hook (agregar a .git/hooks/pre-push)
#!/bin/bash
./scripts/ci/backend_test.sh --mysql || exit 1
./scripts/ci/security_scan.sh || exit 1
```

### Contactos

- **DevOps Lead**: [contact info]
- **Tech Lead**: [contact info]
- **Security Team**: [contact info]

---

**Version**: 1.0
**Fecha**: 2025-11-06
**Mantenido por**: DevOps Team
