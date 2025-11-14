# Agentes DevOps

Agentes especializados en operaciones DevOps, gestión de releases, dependencias y seguridad.

## Ubicación

**Archivos de definición**: `.agent/agents/` y `.github/agents/`
**Scripts**: `scripts/coding/ai/` (cuando aplique)

## Agentes Disponibles

### 1. GitOpsAgent

**Archivo**: `.agent/agents/gitops_agent.md`

**Propósito**: Operaciones Git y gestión de repositorio.

**Capacidades**:
- Sincronización de ramas principales
- Limpieza de ramas obsoletas
- Auditoría de estructura de repositorio
- Gestión de workflows Git
- Detección de conflictos
- Análisis de historial de commits

**Cuándo usar**:
- Después de múltiples PRs mergeados
- Limpieza periódica de ramas
- Sincronización antes de release
- Auditoría de estructura del repositorio
- Resolución de conflictos complejos

**Ejemplo**:
```
GitOpsAgent: Sincroniza todas las ramas principales con develop
y genera reporte completo de cambios.
```

**Comandos comunes**:
```bash
# Sincronizar ramas
GitOpsAgent: Sync all main branches with develop and generate changelog

# Limpiar ramas
GitOpsAgent: Delete merged branches older than 30 days

# Auditar repositorio
GitOpsAgent: Audit repository structure and generate compliance report
```

**Output esperado**:
- Reporte en `docs/qa/registros/YYYY_MM_DD_gitops_[operacion].md`
- Lista de cambios realizados
- Conflictos detectados (si hay)

---

### 2. ReleaseAgent

**Archivo**: `.agent/agents/release_agent.md`

**Propósito**: Gestión de releases y versionado semántico.

**Capacidades**:
- Cálculo automático de versión según commits (Conventional Commits)
- Generación de changelogs
- Creación de tags Git
- Actualización de archivos de versión
- Preparación de release notes
- Validación de pre-release

**Cuándo usar**:
- Crear nuevo release (major, minor, patch)
- Generar changelog
- Crear release candidate
- Hotfix urgente
- Preparar release notes para stakeholders

**Ejemplo**:
```
ReleaseAgent: Crear nuevo release minor.
Analiza commits desde último tag, genera changelog,
actualiza versiones y crea tag.
```

**Versionado Semántico**:
- **MAJOR** (1.0.0 -> 2.0.0): Breaking changes
- **MINOR** (1.0.0 -> 1.1.0): New features (backward compatible)
- **PATCH** (1.0.0 -> 1.0.1): Bug fixes

**Conventional Commits**:
```
feat: nueva funcionalidad -> MINOR
fix: corrección de bug -> PATCH
BREAKING CHANGE: cambio incompatible -> MAJOR
```

**Comandos comunes**:
```bash
# Release automático
ReleaseAgent: Create release based on commits since last tag

# Release específico
ReleaseAgent: Create patch release v1.2.3 with changelog

# Hotfix
ReleaseAgent: Create hotfix release for CVE-2023-xxxxx
```

**Output esperado**:
- Tag Git creado
- CHANGELOG.md actualizado
- Archivos de versión actualizados
- Release notes en `docs/releases/v*.md`

---

### 3. DependencyAgent

**Archivo**: `.agent/agents/dependency_agent.md`

**Propósito**: Gestión de dependencias y vulnerabilidades.

**Capacidades**:
- Actualización de dependencias (conservadora/moderada/agresiva)
- Escaneo de vulnerabilidades (CVEs)
- Auditoría de licencias
- Limpieza de dependencias no usadas
- Gestión de lockfiles
- Análisis de impacto de actualizaciones

**Estrategias de actualización**:
- **Conservadora**: Solo patches (1.2.3 -> 1.2.4)
- **Moderada**: Patches y minors (1.2.3 -> 1.3.0)
- **Agresiva**: Todas incluyendo majors (1.2.3 -> 2.0.0)

**Cuándo usar**:
- Actualización mensual de dependencias
- Respuesta a alerta de CVE
- Auditoría de licencias antes de release
- Limpieza de dependencias obsoletas
- Preparación para upgrade de framework

**Ejemplo**:
```
DependencyAgent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors. Genera reporte de cambios.
```

**Comandos comunes**:
```bash
# Actualizar dependencias
DependencyAgent: Update dependencies with conservative strategy

# Escanear vulnerabilidades
DependencyAgent: Scan for CVEs and generate report with severities

# Auditar licencias
DependencyAgent: Audit licenses and flag GPL/AGPL packages

# Limpiar no usadas
DependencyAgent: Remove unused dependencies and update lockfile
```

**Output esperado**:
- Reporte de actualizaciones en `docs/qa/registros/`
- Lista de CVEs encontrados con severidad
- Licencias incompatibles detectadas
- PRs automáticos (opcional)

---

### 4. SecurityAgent

**Archivo**: `.agent/agents/security_agent.md`

**Propósito**: Auditorías de seguridad y compliance.

**Capacidades**:
- Escaneo de código con Bandit (Python)
- Detección de secrets con gitleaks
- Análisis de amenazas STRIDE
- Validación de restricciones del proyecto
- Auditoría de configuración de seguridad
- SAST (Static Application Security Testing)

**STRIDE Model**:
- **S**poofing (Suplantación)
- **T**ampering (Manipulación)
- **R**epudiation (Repudio)
- **I**nformation Disclosure (Divulgación de información)
- **D**enial of Service (Denegación de servicio)
- **E**levation of Privilege (Elevación de privilegios)

**Cuándo usar**:
- Antes de cada release
- Auditoría mensual de seguridad
- Después de cambios en autenticación
- Respuesta a incidente de seguridad
- Validación de cumplimiento (SOC2, ISO27001)

**Ejemplo**:
```
SecurityAgent: Ejecuta auditoría completa de seguridad.
Incluye: código, dependencias, secrets, configuración.
Genera reporte priorizado por severidad.
```

**Comandos comunes**:
```bash
# Auditoría completa
SecurityAgent: Run full security audit and generate compliance report

# Escanear secrets
SecurityAgent: Scan for exposed secrets in codebase and git history

# Análisis STRIDE
SecurityAgent: Perform STRIDE threat analysis on authentication module

# Validar configuración
SecurityAgent: Validate security configuration against best practices
```

**Severidades**:
- **CRITICAL**: Requiere acción inmediata
- **HIGH**: Requiere acción pronto
- **MEDIUM**: Planificar corrección
- **LOW**: Considerar mejora
- **INFO**: Informativo

**Output esperado**:
- Reporte de seguridad en `docs/qa/registros/`
- Lista de vulnerabilidades por severidad
- Secrets detectados (si hay)
- Recomendaciones de corrección

---

### 5. CodeTasker (my_agent)

**Archivo**: `.agent/agents/my_agent.md`

**Propósito**: Tareas de programación asíncronas y delegables.

**Capacidades**:
- Escribir funciones en múltiples lenguajes
- Depurar errores
- Refactorizar módulos
- Generar documentación
- Ejecutar pruebas de código
- Análisis de código

**Cuándo usar**:
- Tareas de programación delegables
- Trabajo en segundo plano
- Refactorización de código legacy
- Generación de boilerplate
- Análisis de código complejo

**Ejemplo**:
```
CodeTasker: Refactoriza módulo authentication.py siguiendo principios SOLID.
Mantén funcionalidad existente y genera tests.
```

**Comandos comunes**:
```bash
# Refactorizar
CodeTasker: Refactor function extract_data() to use generators instead of lists

# Generar función
CodeTasker: Write function to validate email with regex and tests

# Debugear
CodeTasker: Debug why test_login() is failing intermittently

# Documentar
CodeTasker: Generate docstrings for all functions in utils.py
```

---

### 6. CodexMCPWorkflow Orchestrator

**Archivo**: `.agent/agents/codex_mcp_workflow.md`

**Propósito**: Normalizar flujos Codex MCP single-agent y multi-agent en todos los proveedores LLM.

**Capacidades**:
- Genera briefs declarativos vía `CodexMCPWorkflowBuilder`
- Configuración del servidor MCP (`npx -y codex mcp`)
- Políticas de escritura (`approval-policy`, `sandbox`)
- Gating de artefactos (design specs, frontend, etc.)
- Observabilidad con Traces
- Multi-agent coordination

**Script principal**:
```python
scripts/coding/ai/orchestrators/codex_mcp_workflow.py
```

**Cuándo usar**:
- Ejecutar flujos multi-agente complejos
- Coordinar Project Manager + especialistas
- Validar artefactos antes de cada handoff
- Establecer instrumentación de Traces
- Flujos que requieren múltiples LLM providers

**Ejemplo**:
```
CodexMCPWorkflow Orchestrator: Genera brief multi-agente para "Bug Busters" usando proveedor Anthropic.
Adjunta artefactos generados y traza resultante.
```

**Configuración**:
```yaml
name: "Multi-Agent Workflow"
provider: "anthropic"  # o "openai", "huggingface"
agents:
  - role: "Project Manager"
    responsibilities: ["Planning", "Coordination"]
  - role: "Backend Developer"
    responsibilities: ["API Development"]
  - role: "Frontend Developer"
    responsibilities: ["UI Development"]
  - role: "QA Engineer"
    responsibilities: ["Testing", "Validation"]

gates:
  - artifact: "design/design_spec.md"
    required: true
    validator: "DesignValidator"
  - artifact: "frontend/index.html"
    required: true
    validator: "UIValidator"

observability:
  enable_traces: true
  trace_provider: "datadog"  # o "honeycomb", "jaeger"
```

**Comandos comunes**:
```bash
# Ejecutar workflow
python scripts/coding/ai/orchestrators/codex_mcp_workflow.py \
  --workflow "workflows/feature-development.yaml" \
  --provider "anthropic"

# Con trazas
python scripts/coding/ai/orchestrators/codex_mcp_workflow.py \
  --workflow "workflows/bug-fix.yaml" \
  --provider "openai" \
  --enable-traces
```

**Output esperado**:
- Artefactos generados por cada agente
- Reporte de validación de gates
- Trazas de ejecución
- Métricas de coordinación

---

## Integración CI/CD

Los agentes DevOps se integran en pipelines:

```yaml
# .github/workflows/release.yml
name: Release Pipeline

on:
  push:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Security Audit
        run: |
          SecurityAgent: Run full security scan

  dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check Dependencies
        run: |
          DependencyAgent: Scan for vulnerabilities

  release:
    needs: [security, dependencies]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        run: |
          ReleaseAgent: Create release based on commits
```

## Estructura de Reportes

Ubicación: `docs/qa/registros/YYYY_MM_DD_[agente]_[operacion].md`

Formato estándar:
```markdown
---
id: QA-REG-YYYYMMDD-AGENTE
tipo: registro_actividad
categoria: devops|security|release
fecha: YYYY-MM-DD
responsable: [NombreAgente]
estado: completado|pendiente|fallido
---

# Registro: [Operación] - YYYY-MM-DD

## Información General
- Agente: [Nombre]
- Operación: [Descripción]
- Duración: [Tiempo]

## Trabajo Realizado
[Lista de tareas ejecutadas]

## Resultados
[Métricas y outputs]

## Issues Detectados
[Problemas encontrados]

## Próximos Pasos
[Acciones recomendadas]
```

## Referencias

- [Agentes de Automatización](../../../docs/gobernanza/metodologias/agentes_automatizacion.md)
- [Runbooks DevOps](../../../docs/devops/runbooks/)
- [CODEX MCP Multi-Agent Guide](../../../docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md)

---

**Última actualización**: 2025-11-14
**Total de agentes DevOps**: 6
**Integración CI/CD**: GitHub Actions, GitLab CI
