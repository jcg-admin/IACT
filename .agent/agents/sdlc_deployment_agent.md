---
name: SDLCDeploymentAgent
description: Agente especializado en planificación de despliegues, generación de runbooks, checklists de deployment, estrategias de rollback y documentación de procedimientos de producción.
---

# SDLC Deployment Agent

SDLCDeploymentAgent es un agente Python especializado en la fase de Deployment del ciclo SDLC. Su función principal es generar planes de despliegue detallados, runbooks operacionales, checklists de deployment, estrategias de rollback y documentación completa de procedimientos para despliegues a producción.

## Capacidades

### Planificación de Deployment

- Generación de deployment plans detallados
- Identificación de dependencias de deployment
- Definición de secuencia de pasos
- Estimación de downtime y ventanas de mantenimiento
- Planificación de recursos necesarios

### Runbooks Operacionales

- Creación de runbooks paso a paso
- Comandos específicos para ejecución
- Validaciones entre pasos
- Procedimientos de verificación
- Documentación de troubleshooting

### Estrategias de Rollback

- Definición de criterios de rollback
- Procedimientos de rollback automático
- Backup de configuraciones previas
- Plan de recuperación de datos
- Comunicación de rollback

### Checklists y Validaciones

- Checklists pre-deployment
- Validaciones post-deployment
- Health checks automatizados
- Smoke tests de producción
- Métricas de éxito de deployment

## Cuándo Usarlo

### Antes de Releases

- Planificación de deployment a producción
- Generación de runbooks para equipo DevOps
- Definición de strategy de deployment
- Preparación de comunicaciones

### Deployments Complejos

- Migraciones de base de datos
- Actualizaciones de infraestructura
- Cambios con múltiples dependencias
- Deployments con downtime

### Post-Mortems

- Documentación de deployments fallidos
- Mejora de procedimientos existentes
- Actualización de runbooks
- Refinamiento de checklists

## Cómo Usarlo

### Ejecución Básica

```bash
python scripts/coding/ai/sdlc/deployment_agent.py \
  --feature-description "Deploy v2.0 con nuevas APIs" \
  --environment production \
  --generate-runbook
```

### Deployment Plan Completo

```bash
python scripts/coding/ai/sdlc/deployment_agent.py \
  --deployment-spec specs/release_v2.0.md \
  --environment production \
  --include-migrations \
  --generate-runbook \
  --generate-rollback \
  --estimate-downtime \
  --output-dir deployment_plans/
```

### Parámetros Principales

- `--feature-description`: Descripción de lo que se deployea
- `--deployment-spec`: Archivo con especificación de deployment
- `--environment`: Entorno target (staging, production)
- `--include-migrations`: Incluir pasos de migración DB
- `--generate-runbook`: Generar runbook operacional
- `--generate-rollback`: Generar plan de rollback
- `--estimate-downtime`: Estimar tiempo de downtime
- `--deployment-strategy`: Strategy (blue-green, canary, rolling)

## Ejemplos de Uso

### Ejemplo 1: Deployment Estándar

```bash
python scripts/coding/ai/sdlc/deployment_agent.py \
  --feature-description "Deploy hotfix de seguridad" \
  --environment production \
  --deployment-strategy rolling \
  --generate-runbook
```

Genera:
- Runbook con pasos específicos
- Validaciones entre pasos
- Health checks post-deployment
- Comunicaciones requeridas

### Ejemplo 2: Deployment con Migraciones

```bash
python scripts/coding/ai/sdlc/deployment_agent.py \
  --deployment-spec specs/database_migration.md \
  --environment production \
  --include-migrations \
  --generate-rollback \
  --estimate-downtime
```

Genera:
- Plan de migración de base de datos
- Backup procedures
- Rollback de migrations
- Estimación de downtime (ej: 15 minutos)
- Scripts de validación post-migración

### Ejemplo 3: Blue-Green Deployment

```bash
python scripts/coding/ai/sdlc/deployment_agent.py \
  --feature-description "Deploy v3.0 con arquitectura nueva" \
  --environment production \
  --deployment-strategy blue-green \
  --generate-runbook \
  --generate-rollback
```

## Outputs Generados

### Deployment Runbook

```markdown
# Deployment Runbook: Release v2.0

## Pre-Deployment Checklist
- [ ] Backup de base de datos completado
- [ ] Comunicación enviada a stakeholders
- [ ] Monitoring dashboards preparados
- [ ] Equipo de guardia notificado
- [ ] Rollback plan revisado

## Deployment Steps

### Step 1: Pre-Deployment Validation
```bash
# Verificar estado de servicios
kubectl get pods -n production
curl https://api.example.com/health

# Expected: All pods running, health check OK
```

### Step 2: Database Migrations
```bash
# Backup actual
pg_dump production_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Ejecutar migrations
python manage.py migrate --database=production

# Validar
python manage.py showmigrations | grep -v "\\[X\\]"
# Expected: No pending migrations
```

### Step 3: Deploy Application
```bash
# Pull nueva imagen
docker pull registry.example.com/app:v2.0

# Rolling update
kubectl set image deployment/app app=registry.example.com/app:v2.0

# Monitorear rollout
kubectl rollout status deployment/app
# Expected: deployment "app" successfully rolled out
```

### Step 4: Post-Deployment Validation
```bash
# Health check
curl https://api.example.com/health
# Expected: {"status": "healthy", "version": "2.0"}

# Smoke tests
pytest tests/smoke/production_smoke_tests.py
# Expected: All tests pass

# Check error rates
# Monitor for 15 minutes, error rate should be < 1%
```

## Rollback Procedure

### Trigger Criteria
- Error rate > 5% for 5 minutes
- Critical functionality broken
- Database corruption detected

### Rollback Steps
```bash
# Step 1: Rollback deployment
kubectl rollout undo deployment/app

# Step 2: Rollback migrations (if needed)
python manage.py migrate api 0042_previous_migration

# Step 3: Verify rollback
curl https://api.example.com/health
# Expected: {"status": "healthy", "version": "1.9"}
```

## Communication Plan
- T-60min: Notify stakeholders of upcoming deployment
- T-0: Start deployment, post in #ops-channel
- T+15min: Completion notification or rollback decision
- T+60min: Post-deployment report

## Success Metrics
- Deployment time < 30 minutes
- Zero downtime (rolling update)
- Error rate < 1%
- Response time < 500ms p95
```

### Deployment Checklist

```markdown
# Pre-Deployment Checklist

## Infrastructure
- [ ] Production environment accessible
- [ ] Load balancers configured
- [ ] SSL certificates valid
- [ ] DNS records updated
- [ ] CDN cache cleared (if needed)

## Application
- [ ] Code review completed
- [ ] Tests passing (100%)
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] Documentation updated

## Database
- [ ] Migrations tested in staging
- [ ] Backup completed and verified
- [ ] Rollback scripts prepared
- [ ] Index creation planned (if large tables)

## Monitoring
- [ ] Dashboards configured
- [ ] Alerts configured
- [ ] Logs aggregation working
- [ ] APM tools enabled

## Team
- [ ] On-call engineer identified
- [ ] Stakeholders notified
- [ ] Rollback plan reviewed
- [ ] Communication channels ready
```

## Herramientas y Dependencias

- **Container Orchestration**: Kubernetes, Docker Swarm
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **Infrastructure**: Terraform, Ansible, CloudFormation
- **Monitoring**: Prometheus, Grafana, Datadog
- **Database**: Django migrations, Liquibase, Flyway
- **LLM**: Claude, GPT-4 para generación de runbooks

## Mejores Prácticas

### Planificación

- Siempre tener plan de rollback preparado
- Estimar downtime de manera conservadora
- Incluir buffer time en plan
- Comunicar proactivamente
- Documentar cada paso

### Ejecución

- Seguir runbook al pie de la letra
- Validar después de cada paso
- Monitorear métricas clave continuamente
- Tener criterios claros de go/no-go
- Documentar desviaciones del plan

### Post-Deployment

- Ejecutar smoke tests inmediatamente
- Monitorear por 24 horas
- Documentar lecciones aprendidas
- Actualizar runbooks con mejoras
- Celebrar éxitos, aprender de fallos

## Restricciones

- Runbooks generados requieren revisión DevOps
- Comandos deben validarse en staging primero
- Estimaciones son aproximadas
- No reemplaza testing exhaustivo pre-producción
- Requiere conocimiento del entorno específico

## Archivo de Implementación

Ubicación: `scripts/coding/ai/sdlc/deployment_agent.py`
