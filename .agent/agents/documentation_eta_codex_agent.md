---
name: ETA CODEX Agent
description: Agente especializado en generacion de documentacion tecnica estilo CODEX (Code Documentation Excellence), incluyendo arquitectura, APIs, guias de desarrollo y runbooks.
---

# ETA CODEX Agent

Agente experto en generacion de documentacion tecnica de alta calidad siguiendo el estandar ETA CODEX, produciendo documentacion completa, estructurada y mantenible para arquitectura, APIs, procesos y operaciones.

## Capacidades

### Documentacion de Arquitectura
- Documentos de decision arquitectonica (ADRs)
- Diagramas C4 con descripciones
- Documentacion de patrones utilizados
- Mapas de dependencias
- Analisis de trade-offs

### Documentacion de APIs
- Especificaciones OpenAPI/Swagger
- Ejemplos de requests/responses
- Guias de autenticacion
- Rate limiting y quotas
- Versionado de APIs

### Guias de Desarrollo
- Setup y configuracion
- Estandares de codigo
- Workflows de desarrollo
- Guias de testing
- Troubleshooting comun

### Runbooks Operacionales
- Procedimientos de deployment
- Guias de incident response
- Playbooks de troubleshooting
- Monitoring y alertas
- Disaster recovery

## Cuando Usar

- Onboarding de nuevos desarrolladores
- Documentacion de arquitectura nueva
- Preparacion para auditorias
- Transferencia de conocimiento
- Mejora de procesos operacionales
- Preparacion de releases

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/documentation/eta_codex_agent.py \
  --project-root /ruta/al/proyecto \
  --doc-type architecture \
  --output-dir docs/
```

### Generar ADR

```bash
python scripts/coding/ai/documentation/eta_codex_agent.py \
  --project-root . \
  --doc-type adr \
  --decision "Adopt microservices architecture" \
  --output-file docs/adr/001-microservices.md
```

### Documentar API

```bash
python scripts/coding/ai/documentation/eta_codex_agent.py \
  --project-root . \
  --doc-type api \
  --api-spec api/openapi.yaml \
  --generate-examples \
  --output-dir docs/api/
```

### Generar Developer Guide

```bash
python scripts/coding/ai/documentation/eta_codex_agent.py \
  --project-root . \
  --doc-type dev-guide \
  --include-setup \
  --include-standards \
  --output-file docs/DEVELOPER_GUIDE.md
```

### Crear Runbook

```bash
python scripts/coding/ai/documentation/eta_codex_agent.py \
  --project-root . \
  --doc-type runbook \
  --scenario "Database migration failure" \
  --output-file docs/runbooks/database-migration-failure.md
```

## Parametros

- `--project-root`: Directorio raiz del proyecto
- `--doc-type`: Tipo (architecture, adr, api, dev-guide, runbook)
- `--decision`: Decision para ADR
- `--api-spec`: Archivo de especificacion API
- `--scenario`: Escenario para runbook
- `--include-setup`: Incluir instrucciones de setup
- `--include-standards`: Incluir estandares de codigo
- `--generate-examples`: Generar ejemplos de uso
- `--output-dir`: Directorio de salida
- `--output-file`: Archivo de salida especifico

## Salida

### ADR Generado

```markdown
# ADR 001: Adopt Microservices Architecture

## Status
Proposed

## Context
The current monolithic architecture faces scalability challenges:
- Deployment requires full system downtime
- Teams cannot work independently on features
- Technology stack is locked to Django
- Scaling requires scaling entire application

## Decision
Migrate to microservices architecture with the following services:
- User Service (authentication, profiles)
- Order Service (order management)
- Payment Service (payment processing)
- Notification Service (emails, SMS, push)

## Rationale

### Benefits
- Independent deployment of services
- Technology diversity (use best tool for each service)
- Team autonomy
- Horizontal scaling of individual services
- Fault isolation

### Trade-offs
- Increased complexity in distributed systems
- Network latency between services
- Data consistency challenges
- Monitoring and debugging more complex
- Higher operational overhead

## Consequences

### Positive
- Faster feature delivery
- Better scalability
- Improved fault tolerance
- Team velocity increases

### Negative
- Learning curve for team
- Infrastructure costs increase
- Need for service mesh/API gateway
- Distributed tracing required

### Neutral
- Need to establish service communication patterns
- API versioning strategy required
- Data migration complexity

## Implementation Plan

### Phase 1: Extract User Service (2 weeks)
- Set up Kubernetes cluster
- Implement API gateway
- Extract authentication logic
- Migrate user database

### Phase 2: Extract Payment Service (2 weeks)
- Implement event bus (Kafka/RabbitMQ)
- Extract payment processing
- Implement saga pattern for distributed transactions

### Phase 3: Extract remaining services (4 weeks)
- Order Service
- Notification Service
- Gradual migration of remaining logic

## Alternatives Considered

### Alternative 1: Stay with Monolith
Rejected: Does not address scalability and team velocity issues

### Alternative 2: Modular Monolith
Rejected: Still requires full deployment, limited scaling

### Alternative 3: Serverless
Rejected: Too radical change, limited control over infrastructure

## References
- [Microservices Patterns](https://microservices.io/patterns/)
- [Building Microservices by Sam Newman](https://samnewman.io/books/building_microservices/)
- [12 Factor App](https://12factor.net/)

## Authors
- John Doe (john@example.com)
- Jane Smith (jane@example.com)

## Last Updated
2025-11-15
```

### Runbook Generado

```markdown
# Runbook: Database Migration Failure

## Overview
This runbook provides step-by-step procedures for handling database migration failures.

## Symptoms
- Migration command fails with error
- Application cannot connect to database
- Database schema is inconsistent
- Data integrity issues reported

## Severity
**HIGH** - Can cause application downtime

## Prerequisites
- Access to production database
- Database backup available
- Application deployment paused

## Diagnosis Steps

### Step 1: Identify Failed Migration
```bash
python manage.py showmigrations
```

Look for migrations marked with `[ ]` (not applied).

### Step 2: Check Migration Error
```bash
python manage.py migrate --verbosity 3
```

Review error message for:
- Syntax errors in migration
- Constraint violations
- Missing tables or columns

### Step 3: Verify Database State
```bash
psql -h localhost -U postgres -d mydb
\dt  # List tables
\d table_name  # Describe table
```

## Resolution Procedures

### Procedure A: Rollback Migration

**When to use:** Migration partially applied

1. Identify last successful migration:
```bash
python manage.py showmigrations app_name
```

2. Rollback to last successful:
```bash
python manage.py migrate app_name 0042_previous_migration
```

3. Verify database state consistent

4. Fix migration file

5. Re-apply migration:
```bash
python manage.py migrate
```

### Procedure B: Manual Database Fix

**When to use:** Database in inconsistent state

1. Connect to database:
```bash
psql -h localhost -U postgres -d mydb
```

2. Manually apply missing changes:
```sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
CREATE INDEX idx_users_email ON users(email);
```

3. Mark migration as applied:
```bash
python manage.py migrate --fake app_name 0043_add_phone_field
```

4. Verify application works

### Procedure C: Restore from Backup

**When to use:** Cannot recover, data corruption

⚠️ **CRITICAL**: Only use as last resort

1. Stop application:
```bash
kubectl scale deployment myapp --replicas=0
```

2. Restore database backup:
```bash
pg_restore -h localhost -U postgres -d mydb backup_file.dump
```

3. Verify data integrity

4. Re-apply migrations from clean state

5. Start application

## Verification

After resolution, verify:

✓ All migrations applied successfully
```bash
python manage.py showmigrations
```

✓ Application starts without errors
```bash
python manage.py runserver
```

✓ Database queries work
```bash
python manage.py shell
>>> from app.models import User
>>> User.objects.count()
```

✓ Tests pass
```bash
pytest tests/
```

## Prevention

- Always test migrations in staging first
- Use migration linting (django-migration-linter)
- Implement zero-downtime migrations
- Maintain recent database backups
- Monitor migration execution time
- Document complex migrations

## Escalation

If issue persists after 30 minutes:
1. Notify: devops-oncall@example.com
2. Create incident: https://incident.example.com
3. Join war room: #incident-response

## Related Runbooks
- [Database Backup and Restore](./database-backup-restore.md)
- [Application Deployment Rollback](./deployment-rollback.md)
- [Zero-Downtime Migration](./zero-downtime-migration.md)

## Change Log
| Date | Author | Change |
|------|--------|--------|
| 2025-11-15 | John Doe | Initial version |

## Feedback
Improve this runbook: https://github.com/example/docs/issues
```

## Estandares CODEX

### Estructura
- Titulo claro y descriptivo
- Table of contents para docs >2 paginas
- Secciones claramente delimitadas
- Ejemplos practicos
- Referencias a recursos adicionales

### Calidad
- Informacion precisa y actualizada
- Ejemplos funcionales
- Formato consistente
- Lenguaje claro y conciso
- Screenshots cuando sea util

### Mantenibilidad
- Fecha de ultima actualizacion
- Historial de cambios
- Autores y contactos
- Enlaces a documentacion relacionada
- Versionado de documentos

## Mejores Practicas

1. **Actualizar regularmente**: Docs desactualizados son peor que no tener docs
2. **Audience-specific**: Adaptar nivel tecnico a audiencia
3. **Ejemplos reales**: Usar ejemplos del proyecto
4. **Validar ejemplos**: Asegurar que ejemplos funcionan
5. **Vincular documentos**: Cross-reference entre docs relacionados
6. **Versionado**: Documentar para cada version de software
7. **Feedback loop**: Recoger feedback y mejorar

## Restricciones

- Documentacion generada requiere revision y validacion
- Ejemplos pueden necesitar ajustes segun entorno
- ADRs requieren input de decisiones arquitectonicas
- Runbooks requieren conocimiento de operaciones reales
- Calidad depende de informacion disponible en codigo

## Ubicacion

Archivo: `scripts/coding/ai/documentation/eta_codex_agent.py`
