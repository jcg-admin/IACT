---
id: DOC-PROCEDIMIENTOS-INDEX
estado: activo
propietario: equipo-qa
ultima_actualizacion: 2025-11-04
relacionados: ["DOC-INDEX-GENERAL", "DOC-CHECKLISTS-INDEX"]
---
# Procedimientos - Proyecto IACT

Este directorio contiene todos los procedimientos operativos del proyecto IACT, centralizados para fácil acceso y referencia.

## Página padre
- [Documentación General](../readme.md)

## Propósito

Los procedimientos definen **cómo** hacer las cosas en el proyecto:
- Paso a paso detallado
- Comandos específicos
- Checklists integrados
- Troubleshooting incluido
- Ejemplos prácticos

## Procedimientos Disponibles

### START Desarrollo

#### [Procedimiento: Instalación de Entorno](../gobernanza/procesos/procedimiento_instalacion_entorno.md)
**Cuándo usar**: Primera vez configurando tu entorno de desarrollo

**Cubre**:
- Instalación de herramientas (Git, Python, Vagrant, VirtualBox)
- Configuración de SSH y GitHub
- Setup del entorno virtual
- Configuración de IDE

**Tiempo estimado**: 1-1.5 horas
**Propietario**: equipo-devops

---

#### [Procedimiento: Desarrollo Local](../gobernanza/procesos/procedimiento_desarrollo_local.md)
**Cuándo usar**: Cada día que trabajes en el proyecto

**Cubre**:
- Iniciar entorno de desarrollo
- Ejecutar tests
- Trabajar con Git (branches, commits, PR)
- Tareas comunes (migraciones, shell Django)
- Troubleshooting frecuente

**Tiempo estimado**: Referencia rápida
**Propietario**: equipo-desarrollo

---

#### [Procedimiento: Gestión de Cambios](../gobernanza/procesos/procedimiento_gestion_cambios.md)
**Cuándo usar**: Al proponer cualquier cambio al código

**Cubre**:
- Tipos de cambios (feat, fix, refactor, etc.)
- Flujo completo de Git (branch -> PR -> merge)
- Conventional Commits
- Code review guidelines
- Cambios de emergencia (hotfix)

**Tiempo estimado**: Seguir en cada PR
**Propietario**: equipo-desarrollo

---

### BUSCAR Quality Assurance

#### [Procedimiento: QA](../gobernanza/procesos/procedimiento_qa.md)
**Cuándo usar**: Testing de features antes de release

**Cubre**:
- Niveles de testing (unitario, integración, E2E)
- Crear test plans
- Ejecutar tests automatizados
- Tests manuales
- Reportar bugs
- Sign-off de QA

**Tiempo estimado**: Por feature
**Propietario**: equipo-qa

---

### NOTA Documentación

#### [Procedimiento: Revisión Documental](../gobernanza/procesos/procedimiento_revision_documental.md)
**Cuándo usar**: Al crear o modificar documentación

**Cubre**:
- Tipos de cambios documentales
- Estándares de formato
- Proceso de review
- ADRs (Architecture Decision Records)
- Métricas de documentación

**Tiempo estimado**: Por documento
**Propietario**: equipo-qa

---

### 🚢 Release y Deployment

#### [Procedimiento: Release](../gobernanza/procesos/procedimiento_release.md)
**Cuándo usar**: Al crear una nueva versión oficial

**Cubre**:
- Semantic versioning
- Crear release branch
- Deployment a staging
- Smoke tests
- Deployment a producción
- Hotfix releases
- Rollback

**Tiempo estimado**: 2-4 horas
**Propietario**: equipo-devops

---

## Guía Rápida por Rol

### Para Nuevos Desarrolladores

1. **Día 1**: [Instalación de Entorno](../gobernanza/procesos/procedimiento_instalacion_entorno.md)
2. **Día 2+**: [Desarrollo Local](../gobernanza/procesos/procedimiento_desarrollo_local.md)
3. **Primera feature**: [Gestión de Cambios](../gobernanza/procesos/procedimiento_gestion_cambios.md)

### Para Desarrolladores Existentes

**Diariamente**:
- [Desarrollo Local](../gobernanza/procesos/procedimiento_desarrollo_local.md) (referencia)

**Por feature/fix**:
- [Gestión de Cambios](../gobernanza/procesos/procedimiento_gestion_cambios.md)

**Documentación**:
- [Revisión Documental](../gobernanza/procesos/procedimiento_revision_documental.md)

### Para QA

**Por feature**:
- [Procedimiento QA](../gobernanza/procesos/procedimiento_qa.md)

**Por release**:
- [Procedimiento QA](../gobernanza/procesos/procedimiento_qa.md) -> [Procedure Release](../gobernanza/procesos/procedimiento_release.md)

### Para DevOps

**Configuración inicial**:
- [Instalación de Entorno](../gobernanza/procesos/procedimiento_instalacion_entorno.md)

**Releases**:
- [Procedimiento Release](../gobernanza/procesos/procedimiento_release.md)

**Operaciones**:
- Ver [Runbooks DevOps](../devops/runbooks/)

---

## Relación con Otros Documentos

### Checklists
Los procedimientos **usan** checklists como herramientas:

- [Checklist de Desarrollo](../checklists/checklist_desarrollo.md)
- [Checklist de Testing](../checklists/checklist_testing.md)
- [Checklist de Cambios Documentales](../checklists/checklist_cambios_documentales.md)

### Runbooks
Los procedimientos son workflows completos; los runbooks son operaciones específicas:

- [Runbook: Reprocesar ETL Fallido](../devops/runbooks/reprocesar_etl_fallido.md)
- [Runbook: Verificar Servicios](../devops/runbooks/verificar_servicios.md)
- [Runbook: Post-Create Setup](../devops/runbooks/post_create.md)

### Lineamientos
Los procedimientos siguen lineamientos establecidos:

- [Lineamientos de Código](../arquitectura/lineamientos_codigo.md)
- [Lineamientos de Gobernanza](../gobernanza/lineamientos_gobernanza.md)
- [Documentación Corporativa](../gobernanza/documentacion_corporativa.md)

---

## Cómo Usar Este Directorio

### Buscar un Procedimiento

**Por situación**:
- "Necesito configurar mi máquina" -> [Instalación de Entorno](../gobernanza/procesos/procedimiento_instalacion_entorno.md)
- "Voy a hacer un cambio" -> [Gestión de Cambios](../gobernanza/procesos/procedimiento_gestion_cambios.md)
- "Debo probar una feature" -> [QA](../gobernanza/procesos/procedimiento_qa.md)
- "Vamos a hacer release" -> [Release](../gobernanza/procesos/procedimiento_release.md)

**Por rol**:
- Ver sección "Guía Rápida por Rol" arriba

**Por tema**:
- Desarrollo: procedimientos 1-3
- QA: procedimiento 4-5
- Release: procedimiento 6

### Contribuir

Para agregar un nuevo procedimiento:

1. Usar plantilla base:
   ```yaml
   ---
   id: PROC-NOMBRE
   tipo: procedimiento
   categoria: desarrollo|qa|devops
   version: 1.0.0
   fecha_creacion: YYYY-MM-DD
   propietario: equipo-nombre
   relacionados: []
   ---
   ```

2. Incluir secciones:
   - Propósito
   - Alcance
   - Pre-requisitos
   - Procedimiento (paso a paso)
   - Troubleshooting
   - Recursos relacionados
   - Changelog

3. Crear PR siguiendo [Procedimiento de Revisión Documental](../gobernanza/procesos/procedimiento_revision_documental.md)

4. Actualizar este índice

---

## Estructura de Procedimientos

Todos los procedimientos siguen esta estructura:

```markdown
# Procedimiento: Nombre

## Propósito
¿Qué problema resuelve?

## Alcance
¿A quién aplica?

## Pre-requisitos
¿Qué se necesita antes de empezar?

## Procedimiento
### Paso 1: ...
### Paso 2: ...

## Troubleshooting
Problemas comunes y soluciones

## Recursos Relacionados
Links a otros documentos

## Changelog
Historial de cambios
```

---

## Índice Alfabético

| Procedimiento | ID | Propietario | Categoría |
|---------------|-----|-------------|-----------|
| [Desarrollo Local](../gobernanza/procesos/procedimiento_desarrollo_local.md) | PROC-DEV-LOCAL | desarrollo | desarrollo |
| [Gestión de Cambios](../gobernanza/procesos/procedimiento_gestion_cambios.md) | PROC-CAMBIOS | desarrollo | desarrollo |
| [Instalación de Entorno](../gobernanza/procesos/procedimiento_instalacion_entorno.md) | PROC-INSTALL | devops | infrastructure |
| [QA](../gobernanza/procesos/procedimiento_qa.md) | PROC-QA | qa | qa |
| [Release](../gobernanza/procesos/procedimiento_release.md) | PROC-RELEASE | devops | devops |
| [Revisión Documental](../gobernanza/procesos/procedimiento_revision_documental.md) | PROC-REV-DOC | qa | qa |

---

## Métricas de Procedimientos

Medir efectividad:
- **Tiempo de onboarding**: Nuevo dev productivo en < 1 semana
- **Adherencia**: % de equipo que sigue procedimientos
- **Claridad**: % de procedimientos que requieren soporte adicional
- **Actualización**: % de procedimientos actualizados en último mes

---

## Estado de Procedimientos

| Procedimiento | Estado | Última Actualización | Próxima Revisión |
|---------------|--------|----------------------|------------------|
| Instalación Entorno | OK Activo | 2025-11-04 | 2025-12-04 |
| Desarrollo Local | OK Activo | 2025-11-04 | 2025-12-04 |
| Gestión Cambios | OK Activo | 2025-11-04 | 2025-12-04 |
| QA | OK Activo | 2025-11-04 | 2025-12-04 |
| Revisión Documental | OK Activo | 2025-11-04 | 2025-12-04 |
| Release | OK Activo | 2025-11-04 | 2025-12-04 |

---

## Backlog de Procedimientos

Procedimientos futuros a crear:

- [ ] Procedimiento: Disaster Recovery
- [ ] Procedimiento: Backup y Restore
- [ ] Procedimiento: Security Incident Response
- [ ] Procedimiento: Performance Monitoring
- [ ] Procedimiento: Database Migrations
- [ ] Procedimiento: API Versioning
- [ ] Procedimiento: Dependency Updates
- [ ] Procedimiento: Tech Debt Management

---

## Recursos Relacionados

- [Checklists](../checklists/readme.md)
- [Runbooks DevOps](../devops/runbooks/)
- [Gobernanza](../gobernanza/readme.md)
- [Arquitectura](../arquitectura/readme.md)
- [QA](../qa/readme.md)

---

## Soporte

¿No encuentras el procedimiento que necesitas?

1. Buscar en este índice
2. Revisar [Runbooks](../devops/runbooks/) por si es operación específica
3. Revisar [Checklists](../checklists/) por si es lista de verificación
4. Crear issue solicitando nuevo procedimiento

---

## Changelog

- 2025-11-04: Creación inicial de directorio de procedimientos
  - 6 procedimientos principales creados
  - Índice maestro creado
  - Estructura estandarizada definida
