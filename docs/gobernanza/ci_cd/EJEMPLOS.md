---
title: CI/CD - Ejemplos de Flujos Completos
date: 2025-11-13
domain: gobernanza
status: active
---

# CI/CD - Ejemplos de Flujos Completos

Ejemplos end-to-end de flujos comunes.

---

## Ejemplo 1: Feature Completo (Dark Mode)

### 1. Planning Phase

```bash
python scripts/sdlc_agent.py \
    --phase planning \
    --input "Implementar dark mode toggle en settings para mejorar UX"
```

**Output**: `ISSUE_20251106_150610.md`
- Story points: 5
- Priority: P2
- Labels: feature, frontend, backend

### 2. Development

```bash
# Developer crea branch
git checkout -b feature/IACT-456-dark-mode

# Implementa siguiendo LLD generado
# Escribe tests (TDD)
# Coverage: 85%

# Pre-commit checks
black .
isort .
./scripts/ci/backend_test.sh --mysql
./scripts/ci/frontend_test.sh --unit

# Commit
git add .
git commit -m "feat(ui): implementar dark mode toggle en settings"
git push -u origin feature/IACT-456-dark-mode
```

### 3. CI/CD Automatico

**GitHub Actions ejecuta**:
- backend-ci: PASS (5 min)
- frontend-ci: PASS (7 min)
- test-pyramid: PASS (60/28/12)
- security-scan: PASS (no vulnerabilities)

### 4. Code Review

```bash
# Tech Lead revisa PR
gh pr checkout 456

# Ejecuta tests localmente
./scripts/ci/backend_test.sh --all

# Aprueba PR
# Merge to develop
```

### 5. Deployment Staging (Automatico)

```bash
# Merge to develop activa deploy.yml
# Deploy a staging
# Health checks: PASS
# Smoke tests: PASS
```

### 6. QA Testing

```bash
# QA ejecuta test plan
cat docs/sdlc_outputs/testing/TEST_PLAN_*.md

# Manual testing en staging
# Todos los acceptance criteria: PASS

# Aprueba para production
```

### 7. Production Deployment

```bash
# Tag release
git tag -a v1.5.0 -m "Release: Dark mode feature"
git push origin v1.5.0

# deploy.yml activa con tag
# Blue-green deployment
# Zero downtime
# Health checks: PASS
```

### 8. Monitoring

```bash
# Post-deployment monitoring (5 min intensive)
# Response time: 1.2s (< 2s target)
# Error rate: 0.1% (< 1% target)
# User adoption: 45% in first day
```

**Total time**: Planning to Production = 2 dias

---

## Ejemplo 2: Bugfix Critico (Production Down)

### 1. Incident Detection

```bash
# Alerta: Health check failing
# Error rate: 15% (> 5% threshold)

# Activar incident response
# Go to Actions → Incident Response
# incident_type: production_down
# severity: critical
```

### 2. Incident Response Workflow

**Automatico**:
- Crea issue #789
- Genera diagnostics
- Proporciona playbook

### 3. Diagnostico

```bash
# SSH a production
ssh user@production-server

# Logs
sudo tail -f /var/log/iact/error.log
# Error: OperationalError: MySQL connection lost

# Check MySQL
systemctl status mysql
# Status: failed

# Root cause: MySQL crashed
```

### 4. Resolucion

```bash
# Restart MySQL
sudo systemctl restart mysql

# Verify
mysql -h localhost -u root -p -e "SELECT 1;"

# Restart application
sudo systemctl restart gunicorn-iact-production

# Health check
curl -f https://iact.example.com/api/health
# Status: 200 OK
```

### 5. Post-Incident

```bash
# Update incident issue #789
# Status: Resolved
# Time to resolution: 12 minutos
# Root cause: MySQL OOM, added monitoring

# Schedule post-mortem
# Action items:
# 1. Increase MySQL max_connections
# 2. Add MySQL health alerts
# 3. Implement connection pooling
```

**Total MTTR**: 12 minutos

---

## Ejemplo 3: Database Migration (Risky)

### 1. Feature con Migration

```python
# Feature: Renombrar campo User.email a User.email_address

# RIESGOSO: Migration destructiva
# Requiere multi-step approach
```

### 2. Step 1: Additive Migration

```bash
# Migration 0045: Agregar nuevo campo
python manage.py makemigrations

# Test en staging
python manage.py migrate

# Deploy a staging
# App funciona con ambos campos
```

### 3. Step 2: Data Migration

```bash
# Migration 0046: Copiar data
# En migration file:
def migrate_email_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.update(email_address=F('email'))

# Deploy a staging
# Verify data
```

### 4. Step 3: Code Update

```bash
# Update codigo para usar email_address
# Deploy a staging
# Test extensivamente
# Both fields still exist (safe)
```

### 5. Step 4: Remove Old Field

```bash
# Migration 0047: Remove email field
# AHORA es seguro (data en email_address)
# Reversible (podemos restore email_address → email)

# Deploy a production
```

**Total time**: 4 deployments en 1 semana (safely)

---

## Ejemplo 4: Security Vulnerability Fix

### 1. Detection

```bash
# npm audit alerta: Critical vulnerability en react-scripts
# CRITICAL: Prototype Pollution

# security-scan.yml falla
```

### 2. Fix

```bash
# Developer
git checkout -b fix/CVE-2024-XXXX-react-scripts

# Update package
cd frontend
npm update react-scripts@latest

# Verify
npm audit
# 0 vulnerabilities

# Test
./scripts/ci/frontend_test.sh --all
# PASS

# Commit
git commit -m "fix(security): actualizar react-scripts (CVE-2024-XXXX)"
git push
```

### 3. Fast-Track Deployment

```bash
# PR approved (security priority)
# Merge to main

# Deploy a staging (automatico)
# Quick smoke test
# Deploy a production (same day)
```

**Total time**: Detection to Production = 4 horas

---

## Ejemplo 5: Performance Optimization

### 1. Problem Detection

```bash
# Monitoring alerta: Response time 4.5s (> 2s target)
# Endpoint: /api/users/list/
```

### 2. Diagnostico

```bash
# Django debug toolbar
# Identifica: N+1 query problem

# Slow query log
mysql -e "SELECT * FROM mysql.slow_log LIMIT 10;"
# Query: SELECT * FROM user_profile WHERE user_id = X
# Executed 1000 times!
```

### 3. Fix

```python
# ANTES (N+1):
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # 1000 queries!

# DESPUES:
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.bio)  # 1 query!
```

### 4. Validation

```bash
# Local test
time curl http://localhost:8000/api/users/list/
# Before: 4.5s
# After: 0.8s

# Load test
ab -n 1000 -c 10 http://localhost:8000/api/users/list/
# All requests < 2s
```

### 5. Deploy

```bash
# Normal deployment flow
# Monitoring post-deployment
# Response time: 0.8s (target met!)
```

---

## Ejemplo 6: Test Pyramid Violation Fix

### 1. Detection

```bash
# test-pyramid.yml falla
# [FAIL] Unit tests are only 35% (should be >= 50%)
# Too many integration tests (55%)
```

### 2. Analysis

```bash
./scripts/ci/test_pyramid_check.sh

# Current:
# Unit: 35% (21 tests)
# Integration: 55% (33 tests)
# E2E: 10% (6 tests)

# Need 24 more unit tests to reach 60%
```

### 3. Refactor

```bash
# Convert integration tests to unit tests
# Example:

# ANTES (integration test):
def test_user_creation():
    response = client.post('/api/users/', data)
    assert response.status_code == 201
    assert User.objects.count() == 1

# DESPUES (unit test):
def test_user_creation_service():
    user = UserService.create_user(data)
    assert user.email == data['email']
    assert user.is_active == True

# Integration test permanece, pero mas simple:
def test_user_api_endpoint():
    response = client.post('/api/users/', data)
    assert response.status_code == 201
```

### 4. Validation

```bash
./scripts/ci/test_pyramid_check.sh

# New:
# Unit: 62% (45 tests)  [PASS]
# Integration: 28% (21 tests)  [PASS]
# E2E: 10% (6 tests)  [PASS]
```

---

## Checklist General

### Pre-Development
- [ ] SDLC Planning phase ejecutada
- [ ] Story points estimados
- [ ] Acceptance criteria claros

### Development
- [ ] Feature branch creada
- [ ] TDD: Tests escritos primero
- [ ] Codigo implementado
- [ ] Coverage >= 80%
- [ ] Pre-commit checks: PASS

### Code Review
- [ ] PR creado
- [ ] CI/CD: All checks PASS
- [ ] Code review aprobado
- [ ] Merge to develop

### QA
- [ ] Deploy a staging: SUCCESS
- [ ] Test plan ejecutado
- [ ] Acceptance criteria verificados
- [ ] QA sign-off

### Production
- [ ] Tag release creado
- [ ] Deploy a production: SUCCESS
- [ ] Health checks: PASS
- [ ] Monitoring: Normal

### Post-Deployment
- [ ] 5 min monitoring: OK
- [ ] 24h monitoring: OK
- [ ] User feedback: Positive
- [ ] Close issue

---

**Version**: 1.0
**Fecha**: 2025-11-06
