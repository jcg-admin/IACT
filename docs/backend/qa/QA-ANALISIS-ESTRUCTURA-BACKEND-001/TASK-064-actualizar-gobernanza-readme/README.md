# TASK-064: Actualizar gobernanza/README.md

## Metadatos
- **ID**: TASK-064
- **Fase**: FASE 4 - Validación y Limpieza
- **Prioridad**: BAJA 🔵
- **Estimación**: 10 minutos
- **Estado**: PENDIENTE
- **Metodología**: Auto-CoT + Self-Consistency

## Descripción
Actualizar el README.md de la carpeta gobernanza/ para reflejar los procesos, políticas y estándares aplicados durante la reorganización y documentar las convenciones adoptadas.

## Auto-CoT: Razonamiento Paso a Paso

### Paso 1: Entender Contenido de Gobernanza
**Pensamiento**: ¿Qué es gobernanza en este contexto?

**Gobernanza incluye**:
1. **Políticas**: Reglas y directrices del proyecto
2. **Procesos**: Flujos de trabajo establecidos
3. **Estándares**: Convenciones de código y documentación
4. **Mejores Prácticas**: Guidelines recomendados
5. **Métricas**: KPIs y medición de calidad

**Para Backend**:
- Estándares de código
- Proceso de code review
- Convenciones de nomenclatura
- Estructura de proyectos
- Políticas de documentación
- SLAs y acuerdos

### Paso 2: Identificar Cambios por Reorganización
**Pensamiento**: ¿Qué cambió con la reorganización?

**Nuevos Estándares**:
- Nomenclatura: kebab-case para carpetas (TASK-058)
- Estructura modular: core, packages, components, services
- READMEs obligatorios en carpetas principales
- Metadatos YAML en documentación

**Nuevos Procesos**:
- Validación de enlaces antes de merge (TASK-055)
- Validación de nomenclatura (TASK-058)
- Validación de YAML (TASK-057)

### Paso 3: Estructurar README de Gobernanza
**Pensamiento**: ¿Qué secciones incluir?

**Secciones**:
1. **Descripción**: Qué es gobernanza en este proyecto
2. **Políticas**: Reglas establecidas
3. **Estándares de Código**: Convenciones de código
4. **Estándares de Documentación**: Convenciones de docs
5. **Procesos**: Code review, deployment, etc.
6. **Herramientas**: Linters, validators, etc.
7. **Referencias**: Links a documentos detallados

### Paso 4: Redactar Contenido Actualizado
**Pensamiento**: ¿Cómo hacer el README útil y accionable?
- Conciso pero completo
- Enlaces a documentos detallados
- Ejemplos concretos
- Checklists accionables

## Self-Consistency: Validación Múltiple

### Enfoque 1: README Orientado a Políticas
```markdown
# Gobernanza del Backend

## Políticas

### Estructura de Código
- Usar estructura modular definida
- No crear carpetas fuera de la estructura
- Seguir principio de responsabilidad única

### Documentación
- README obligatorio en carpetas principales
- Metadatos YAML en documentos
- Mantener CHANGELOG actualizado
```

### Enfoque 2: README Orientado a Procesos
```markdown
# Gobernanza del Backend

## Procesos

### Code Review
1. Validar estructura de carpetas
2. Verificar nomenclatura
3. Revisar READMEs
4. Ejecutar linters
5. Aprobar cambios

### Deployment
1. Pasar tests
2. Validar configuración
3. Revisar changelog
4. Deployar a staging
5. Validar en staging
6. Deployar a producción
```

### Enfoque 3: README Como Índice
```markdown
# Gobernanza del Backend

Este directorio contiene todas las políticas, procesos y estándares
del backend.

## Contenido

- [Estándares de Código](./CODE_STANDARDS.md)
- [Estándares de Documentación](./DOC_STANDARDS.md)
- [Proceso de Review](./REVIEW_PROCESS.md)
- [SLAs](./SLA.md)
- [Convenciones de Nomenclatura](./NAMING_CONVENTIONS.md)
```

### Convergencia de Resultados
- Combinar enfoque de índice con resumen de políticas clave
- Enlazar a documentos detallados
- Incluir quick reference de estándares principales

## Criterios de Aceptación
- [ ] README.md de gobernanza actualizado
- [ ] Políticas de estructura documentadas
- [ ] Estándares de nomenclatura incluidos
- [ ] Procesos de validación documentados
- [ ] Referencias a herramientas (linters, validators)
- [ ] Enlaces a documentos detallados
- [ ] Markdown válido

## Entregables
1. **docs/backend/gobernanza/README.md** (Actualizado)
   - Políticas y estándares actualizados
   - Referencias a nueva estructura
   - Procesos documentados

2. **NAMING_CONVENTIONS.md** (Opcional, si no existe)
   - Detalle de convenciones de nomenclatura
   - Basado en TASK-058

3. **STRUCTURE_STANDARDS.md** (Opcional, si no existe)
   - Estándares de estructura de carpetas
   - Guía "dónde agregar código"

## Template README Gobernanza

```markdown
# Gobernanza del Backend

> Políticas, procesos y estándares para el desarrollo del backend del Sistema IACT.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Políticas](#políticas)
- [Estándares](#estándares)
- [Procesos](#procesos)
- [Herramientas](#herramientas)
- [Documentos](#documentos)

---

## Descripción

Este directorio contiene la gobernanza técnica del backend, incluyendo:

- **Políticas**: Reglas y directrices obligatorias
- **Estándares**: Convenciones de código y documentación
- **Procesos**: Flujos de trabajo establecidos
- **Herramientas**: Tools para cumplimiento automático

### Propósito

Garantizar:
- ✅ Consistencia en código y documentación
- ✅ Calidad mantenible en el tiempo
- ✅ Onboarding eficiente de nuevos desarrolladores
- ✅ Escalabilidad de la base de código

---

## Políticas

### Estructura de Código

#### Organización Modular
- **DEBE** seguir estructura definida: core, packages, components, services
- **NO DEBE** crear carpetas fuera de la estructura sin aprobación
- **DEBE** colocar código en la ubicación semánticamente correcta

Ver: [Guía de Navegación](../docs/GUIA_NAVEGACION_BACKEND.md)

#### Responsabilidad Única
- Cada módulo/componente debe tener una responsabilidad clara
- Evitar módulos "god" que hacen de todo
- Preferir composición sobre herencia

### Documentación

#### READMEs Obligatorios
- **DEBE** tener README.md en:
  - Carpetas principales (core, packages, components, etc.)
  - Cada módulo/servicio nuevo
  - Carpetas con múltiples archivos

#### Metadatos YAML
- **DEBE** incluir frontmatter YAML en:
  - Documentación técnica
  - Guías y tutoriales
  - Documentos de arquitectura

**Campos obligatorios**:
```yaml
---
title: "Título del Documento"
description: "Descripción breve"
status: draft|review|published
---
```

Ver: [TASK-057: Validación de Metadatos YAML](../qa/QA-ANALISIS-ESTRUCTURA-BACKEND-001/TASK-057-validar-metadatos-yaml/)

#### CHANGELOG
- **DEBE** actualizar CHANGELOG.md para cambios significativos
- **DEBE** seguir formato Keep a Changelog
- **DEBE** incluir categorías: Added, Changed, Deprecated, Removed, Fixed

Ver: [CHANGELOG.md](../CHANGELOG.md)

---

## Estándares

### Nomenclatura

#### Carpetas
- **Formato**: `kebab-case`
- **Ejemplos**: `user-management`, `api-gateway`
- ❌ **Evitar**: Espacios, mayúsculas, underscores, camelCase

#### Archivos

**JavaScript/TypeScript**:
- Servicios: `[nombre]Service.js` (camelCase)
- Controllers: `[nombre]Controller.js` (camelCase)
- Clases: `PascalCase.js`

**Python**:
- Todo: `snake_case.py`

**Documentación**:
- READMEs: `README.md` (uppercase)
- Docs importantes: `CHANGELOG.md`, `CONTRIBUTING.md`
- Guías: `kebab-case.md` o `SCREAMING_CASE.md`

Ver: [TASK-058: Validación de Nomenclatura](../qa/QA-ANALISIS-ESTRUCTURA-BACKEND-001/TASK-058-validar-nomenclatura/)

### Código

#### JavaScript/TypeScript
```javascript
// Usar ESLint con configuración del proyecto
// .eslintrc.json en raíz

// Imports ordenados
const fs = require('fs'); // Node built-ins
const express = require('express'); // External
const { auth } = require('@core/auth'); // Internal core
const userService = require('./userService'); // Local

// Naming
const camelCase = 'para variables y funciones';
const PascalCase = 'para clases y constructores';
const SCREAMING_CASE = 'para constantes';
```

#### Python
```python
# Usar Black + Flake8
# pyproject.toml en raíz

# Naming
snake_case = "para variables y funciones"
PascalCase = "para clases"
SCREAMING_CASE = "para constantes"
```

### Documentación

#### Estructura de README
```markdown
# Título

## Descripción
¿Qué es esto?

## Contenido
¿Qué hay aquí?

## Uso
¿Cómo se usa?

## Referencias
Enlaces relacionados
```

#### Comentarios en Código
- JSDoc para JavaScript/TypeScript
- Docstrings para Python
- Comentarios para lógica compleja, no obviedades

---

## Procesos

### Code Review

#### Checklist de Review
- [ ] Código en ubicación correcta según estructura
- [ ] Nomenclatura sigue convenciones
- [ ] README actualizado/creado si necesario
- [ ] Tests incluidos (si aplica)
- [ ] Documentación actualizada
- [ ] Linters pasados sin errores
- [ ] No hay secretos hardcodeados

#### Proceso
1. Crear feature branch desde develop
2. Desarrollar y commitear cambios
3. Ejecutar linters y tests localmente
4. Crear Pull Request
5. Review por al menos 1 desarrollador
6. Aprobar y merge a develop

### Validación Pre-Commit

#### Hooks Automáticos
```bash
# Pre-commit hooks ejecutan:
- Linters (ESLint, Black)
- Formatters (Prettier, Black)
- Validación de nomenclatura
- Validación de YAML
- Tests unitarios (opcional)
```

### Deployment

#### Ambientes
- **Development**: Deploy automático desde develop
- **Staging**: Deploy manual desde release branch
- **Production**: Deploy manual con aprobación

#### Checklist de Deployment
- [ ] Tests pasados en CI/CD
- [ ] Code review aprobado
- [ ] CHANGELOG actualizado
- [ ] Configuración validada
- [ ] Documentación actualizada
- [ ] Stakeholders notificados

---

## Herramientas

### Linters y Formatters

#### JavaScript/TypeScript
- **ESLint**: Linting
- **Prettier**: Formatting
- Configuración: `.eslintrc.json`, `.prettierrc`

#### Python
- **Black**: Formatting
- **Flake8**: Linting
- **mypy**: Type checking (opcional)
- Configuración: `pyproject.toml`

### Validadores Personalizados

Scripts en `utils/scripts/`:
- `validate-structure.sh` - Validar estructura de carpetas
- `validate-naming.sh` - Validar nomenclatura
- `validate-yaml.sh` - Validar metadatos YAML
- `validate-links.sh` - Validar enlaces en Markdown

Ver: [TASK-055 a TASK-058](../qa/QA-ANALISIS-ESTRUCTURA-BACKEND-001/)

### CI/CD

- **GitHub Actions** / **GitLab CI**
- Ejecuta en cada PR:
  - Linters
  - Tests
  - Validaciones personalizadas
  - Build

---

## Documentos

### Estándares Detallados
- [Estándares de Código](./CODE_STANDARDS.md) - Convenciones de código
- [Estándares de Documentación](./DOC_STANDARDS.md) - Convenciones de docs
- [Convenciones de Nomenclatura](./NAMING_CONVENTIONS.md) - Naming detallado

### Procesos
- [Proceso de Code Review](./REVIEW_PROCESS.md) - Flujo de review
- [Proceso de Deployment](./DEPLOYMENT_PROCESS.md) - Flujo de deploy
- [Proceso de Onboarding](./ONBOARDING_PROCESS.md) - Para nuevos devs

### Políticas
- [SLA](./SLA.md) - Acuerdos de nivel de servicio
- [Política de Seguridad](./SECURITY_POLICY.md) - Seguridad
- [Política de Versionamiento](./VERSIONING_POLICY.md) - Semver

### Guías
- [Guía de Contribución](../CONTRIBUTING.md)
- [Guía de Navegación](../docs/GUIA_NAVEGACION_BACKEND.md)
- [Guía de Testing](../docs/guias/TESTING.md)

---

## Quick Reference

### ¿Dónde va mi código?
```
¿Core del sistema? → core/
¿Paquete reutilizable? → packages/
¿Componente modular? → components/
¿Servicio/API? → services/
¿Utilidad del dominio? → utils/
```

### ¿Cómo nombro carpetas?
```
kebab-case siempre
user-management ✅
UserManagement ❌
user_management ❌
```

### ¿Qué validar antes de PR?
```bash
npm run lint        # Linters
npm test            # Tests
npm run validate    # Validaciones personalizadas
```

---

## Cumplimiento

### Métricas de Calidad

Monitoreamos:
- 📊 Cobertura de tests (objetivo: >80%)
- 📝 Cobertura de documentación (READMEs presentes)
- 🔗 Enlaces rotos (objetivo: 0)
- 📐 Conformidad de nomenclatura (objetivo: 100%)
- ✅ Linters sin warnings

### Revisiones

- **Semanal**: Métricas de calidad
- **Mensual**: Revisión de procesos
- **Trimestral**: Revisión de estándares

---

## Contacto

¿Preguntas sobre gobernanza?
- 💬 Slack: #backend-governance
- 📧 Email: governance@team.com
- 📝 Issues: Etiquetar con `governance`

---

**Última actualización**: 2025-11-18
**Versión**: 2.0.0 (actualizado con reorganización)
**Mantenida por**: Equipo de Arquitectura Backend
```

## Comandos Útiles

### Validar cumplimiento
```bash
# Ejecutar todas las validaciones
npm run validate:all

# Validar solo nomenclatura
npm run validate:naming

# Validar solo estructura
npm run validate:structure

# Generar reporte de métricas
npm run metrics:generate
```

### Encontrar violaciones
```bash
# Carpetas que no siguen convenciones
find docs/backend -type d -name "*_*"  # Tiene underscore
find docs/backend -type d -name "* *"  # Tiene espacio

# READMEs faltantes
for dir in docs/backend/*/; do
  [ ! -f "$dir/README.md" ] && echo "Missing: $dir"
done
```

## Checklist de Revisión

### Contenido
- [ ] Políticas claramente definidas
- [ ] Estándares documentados con ejemplos
- [ ] Procesos paso a paso
- [ ] Herramientas listadas
- [ ] Quick reference útil

### Actualización
- [ ] Refleja nueva estructura modular
- [ ] Incluye convenciones de nomenclatura
- [ ] Referencia a validaciones (TASK-055-058)
- [ ] Enlaces a guías actualizadas

### Formato
- [ ] Markdown válido
- [ ] Enlaces funcionan
- [ ] Ejemplos correctos
- [ ] Tablas bien formateadas

## Prioridades

### P1 - Actualizar
- Referencia a nueva estructura
- Convenciones de nomenclatura
- Procesos de validación

### P2 - Agregar
- Quick reference
- Métricas de calidad
- Enlaces a herramientas

### P3 - Mejorar
- Ejemplos más detallados
- Diagramas de procesos
- FAQs

## Dependencias
- TASK-002: Estructura de carpetas definida
- TASK-058: Convenciones de nomenclatura
- TASK-055-057: Procesos de validación
- TASK-063: Guía de navegación

## Notas
- Gobernanza debe ser enforcement con empatía
- Estándares deben facilitar, no obstaculizar
- Automatizar cumplimiento donde sea posible
- Revisar y actualizar periódicamente

## Referencias
- [Engineering Standards](https://github.com/github/engineering)
- [Google Engineering Practices](https://google.github.io/eng-practices/)
- Auto-CoT: Wei et al. (2022)
- Self-Consistency: Wang et al. (2022)
