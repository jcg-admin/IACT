# CI/CD - Backend

Este directorio contiene documentacion de pipelines de integracion continua y despliegue continuo especificos del backend.

## Proposito

Documentar:
- Pipelines de CI/CD
- Workflows de GitHub Actions
- Procesos de build y testing
- Estrategias de deployment
- Configuraciones de entornos

## Nomenclatura

```
CI-CD-###-titulo-snake-case.md
```

**Ejemplos:**
- `CI-CD-001-pipeline-tests-backend.md`
- `CI-CD-002-deployment-staging.md`
- `CI-CD-003-pipeline-validacion-restricciones.md`

## Contenido Esperado

### Pipelines de Testing
- Pipeline de ejecucion de pytest
- Validacion de cobertura de tests
- Linting y formateo (black, flake8, mypy)
- Validacion de migraciones

### Pipelines de Deployment
- Deployment a staging
- Deployment a produccion
- Rollback procedures
- Health checks post-deployment

### Validaciones Automatizadas
- Validacion de restricciones criticas (no Redis, no SMTP)
- Verificacion de SessionEngine en settings
- Validacion de configuracion de bases de datos dual

## Estructura de Documento CI/CD

```yaml
---
id: CI-CD-###
tipo: ci_cd
categoria: [pipeline|workflow|deployment]
titulo: Titulo del Pipeline
version: 1.0.0
fecha_creacion: YYYY-MM-DD
---
```

## Workflows de GitHub Actions

```
workflows/
 backend-tests.yml
 backend-linting.yml
 backend-deploy-staging.yml
 backend-validaciones-criticas.yml
```

## Restricciones Validadas en CI/CD

Los pipelines deben validar:
1. **NO Redis:** Verificar que CACHES no usa RedisCache
2. **NO SMTP:** Verificar que EMAIL_BACKEND no es smtp
3. **Sesiones MySQL:** Verificar SESSION_ENGINE = 'django.contrib.sessions.backends.db'
4. **Dual DB:** Verificar configuracion de DATABASES con 'ivr' y 'analytics'

## Metricas de CI/CD

- Tiempo de ejecucion de tests
- Tasa de exito de pipelines
- Cobertura de codigo
- Frecuencia de deployments

---

**Ultima actualizacion:** 2025-11-18
**Responsable:** Equipo Backend + DevOps
