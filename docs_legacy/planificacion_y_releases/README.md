---
id: DOC-PLAN-INDEX
estado: borrador
propietario: equipo-producto
ultima_actualizacion: 2025-11-02
relacionados: ["DOC-INDEX-GENERAL", "DOC-GOB-INDEX", "DOC-REQ-INDEX"]
---
# Planificación y Releases - Proyecto IACT

Este espacio documenta la planificación de sprints, roadmap del producto, gestión de releases y cronogramas del proyecto IACT.

## Página padre
- [Índice de espacios documentales](../index.md)

## Páginas hijas
- [Backend - Planificación](../backend/planificacion_y_releases/readme.md)
- [Frontend - Planificación](../frontend/planificacion_y_releases/readme.md)
- [Infrastructure - Planificación](../infrastructure/planificacion_y_releases/readme.md)

## Información clave

### Metodología

El proyecto IACT sigue una metodología ágil adaptada:

- **Sprints**: 2 semanas
- **Planning**: Lunes inicio de sprint
- **Daily standups**: Asíncronos (Slack/Teams)
- **Review**: Viernes fin de sprint
- **Retrospective**: Viernes después de review

### Roadmap 2025

#### Q1 2025 (Enero - Marzo) - Fundación OK EN PROGRESO

**Objetivos:**
- OK Configurar infraestructura local (Vagrant + VirtualBox)
- OK Establecer base documental con MkDocs
- WARNING Implementar ETL básico IVR -> Analytics
- WARNING Desarrollar modelos de datos principales

**Hitos:**
- OK 2025-01-15: Infraestructura local funcional
- OK 2025-02-18: Documentación estructurada
- 🔄 2025-03-31: ETL v1.0 operativo (EN PROGRESO)

#### Q2 2025 (Abril - Junio) - Core Analytics

**Objetivos:**
- Implementar cálculo de KPIs principales (AHT, ASA, FCR)
- Desarrollar agregaciones diarias/mensuales
- Crear comandos Django para procesamiento batch
- Alcanzar 80% cobertura de tests

**Hitos:**
- 2025-04-30: Métricas básicas calculándose
- 2025-05-31: Agregaciones temporales funcionando
- 2025-06-30: Tests y documentación completa

#### Q3 2025 (Julio - Septiembre) - API & Frontend

**Objetivos:**
- Desarrollar API REST con Django REST Framework
- Implementar autenticación y autorización
- Crear dashboard frontend básico
- Documentar APIs con OpenAPI/Swagger

**Hitos:**
- 2025-07-31: API REST v1.0
- 2025-08-31: Frontend básico con visualizaciones
- 2025-09-30: Integración completa API + Frontend

#### Q4 2025 (Octubre - Diciembre) - Optimización

**Objetivos:**
- Optimizar performance de queries
- Implementar caching (Redis)
- Mejorar UX del dashboard
- Preparar para producción

**Hitos:**
- 2025-10-31: Optimizaciones aplicadas
- 2025-11-30: Caching implementado
- 2025-12-15: MVP listo para producción

### Proceso de Release

#### Versionado Semántico

Seguimos [SemVer 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

Ejemplo: 1.2.3
- MAJOR (1): Cambios incompatibles en API
- MINOR (2): Nueva funcionalidad compatible
- PATCH (3): Bug fixes compatibles
```

#### Tipos de Release

**1. Patch Release (1.0.X)**
- Bug fixes menores
- Mejoras de documentación
- Sin nuevas features
- Frequency: Según necesidad

**2. Minor Release (1.X.0)**
- Nuevas features
- Mejoras de performance
- Cambios compatibles
- Frequency: Cada 4-6 semanas

**3. Major Release (X.0.0)**
- Breaking changes en API
- Arquitectura refactorizada
- Migración de datos
- Frequency: Cada 6-12 meses

#### Checklist de Release

**Pre-Release:**
- [ ] Todos los tests pasan (coverage >= 80%)
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado
- [ ] Migraciones de DB testeadas
- [ ] Security audit pasado
- [ ] Performance benchmarks aceptables

**Release:**
- [ ] Tag en Git: `v1.2.3`
- [ ] Build de producción generado
- [ ] Deployment a staging
- [ ] Smoke tests en staging
- [ ] Deployment a producción
- [ ] Post-deployment verification

**Post-Release:**
- [ ] Anuncio a stakeholders
- [ ] Actualizar documentación de usuario
- [ ] Monitoring de métricas clave
- [ ] Retrospectiva de release

### Gestión de Sprints

#### Sprint Actual: Sprint 5 (2025-11-01 -> 2025-11-14)

**Objetivo del Sprint:**
Completar correcciones en estructura documental y establecer base sólida para ETL.

**User Stories Comprometidas:**
1. Corregir errores en estructura de `docs/` (#TBD)
2. Crear archivos faltantes en mkdocs.yml (#TBD)
3. Implementar extractor IVR básico (#TBD)
4. Crear tests para modelos de Call (#TBD)

**Capacidad del Sprint:** 40 story points

**Burndown:**
```
Story Points
40 |-
35 |  -
30 |    -
25 |      -
20 |        -
15 |
10 |
 5 |
 0 |______________
   L M M J V L M J V
```

#### Sprints Planificados

**Sprint 6 (2025-11-15 -> 2025-11-28):**
- Implementar transformer para datos de llamadas
- Crear loader para PostgreSQL
- Tests de integración ETL

**Sprint 7 (2025-11-29 -> 2025-12-12):**
- Calculadora de AHT
- Calculadora de ASA
- Agregador diario

### Dependencias y Riesgos

#### Dependencias Críticas

| Dependencia | Tipo | Impacto | Mitigación |
|-------------|------|---------|------------|
| Acceso a DB IVR producción | Externa | Alto | Usar datos de muestra mientras |
| Especificación completa de KPIs | Interna | Medio | Workshops con negocio |
| Recursos de infraestructura | Externa | Alto | Solicitar anticipadamente |

#### Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Plan de Mitigación |
|--------|--------------|---------|-------------------|
| Cambios en esquema IVR | Media | Alto | Abstraer con capa de mapeo |
| Performance insuficiente | Baja | Alto | Benchmarks tempranos + optimización |
| Falta de recursos DevOps | Media | Medio | Capacitar equipo desarrollo |

### Métricas de Proyecto

#### Velocidad del Equipo

```
Sprint | Story Points Completados
----------------------------------
SP 1   | 28
SP 2   | 32
SP 3   | 35
SP 4   | 38
SP 5   | TBD (objetivo: 40)

Velocidad promedio: 33 SP/sprint
```

#### Burndown de Release

**Release 0.1.0 (MVP):**
- Total story points: 280
- Completados: 133 (47%)
- Restantes: 147 (53%)
- Sprints restantes: 5
- Estado: WARNING En riesgo (velocity necesaria: 29 SP)

## Estado de cumplimiento

| Elemento | Estado | Observaciones |
|----------|--------|---------------|
| Roadmap documentado | OK Sí | Q1-Q4 2025 definido |
| Proceso de release establecido | OK Sí | SemVer + checklist |
| Sprints planificados | OK Sí | 3 sprints adelante |
| Métricas de velocidad | WARNING Parcial | Falta automatizar tracking |
| Registro de riesgos | OK Sí | Documentado arriba |

## Acciones prioritarias
- [ ] Automatizar tracking de burndown charts
- [ ] Establecer SLAs para cada tipo de issue
- [ ] Crear plantilla de planning de sprint
- [ ] Definir criterios de aceptación estándar
- [ ] Implementar release notes automáticas

## Recursos relacionados
- [Requisitos](../requisitos/readme.md)
- [Gobernanza](../gobernanza/readme.md)
- [QA - Estrategia](../qa/estrategia_qa.md)
- [Solicitudes](../solicitudes/readme.md)
