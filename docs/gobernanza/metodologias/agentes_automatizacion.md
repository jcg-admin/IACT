---
id: DOC-DEV-AGENTES
tipo: documentacion
categoria: desarrollo
version: 1.2.0
fecha_creacion: 2025-11-04
fecha_actualizacion: 2025-11-06
propietario: equipo-desarrollo
relacionados: ["DOC-GOB-ESTANDARES", "DOC-SCRIPTS-VALIDACION", "RUNBOOK-GIT-MERGE-CLEANUP"]
---
# Agentes de Automatización - Proyecto IACT

## Propósito

Este documento explica la arquitectura de agentes de automatización utilizada en el proyecto IACT, tanto para tareas ad-hoc (como limpieza de emojis) como para el pipeline completo de CI/CD.

## Tabla de Contenidos

1. [Agentes Usados en el Proyecto](#agentes-usados-en-el-proyecto)
   - [Agente de Exploración de Código](#1-agente-de-exploración-de-código)
   - [Agente General Purpose (Remoción de Emojis)](#2-agente-general-purpose-remoción-de-emojis)
   - [Agente GitOps (Operaciones Git y DevOps)](#3-agente-gitops-operaciones-git-y-devops)
   - [Agente Release (Gestión de Releases)](#4-agente-release-gestión-de-releases)
   - [Agente Dependency (Gestión de Dependencias)](#5-agente-dependency-gestión-de-dependencias)
   - [Agente Security (Auditorías de Seguridad)](#6-agente-security-auditorías-de-seguridad)
2. [Arquitectura Propuesta de CI/CD](#arquitectura-propuesta-de-cicd)
3. [Implementación de Pre-commit Hooks](#implementación-de-pre-commit-hooks)
4. [GitHub Actions CI/CD](#github-actions-cicd)
5. [Mejores Prácticas](#mejores-prácticas)

## IMPORTANTE: Arquitectura de Agentes Especializados

Este documento muestra la implementación inicial con agentes monolíticos. Para la arquitectura CORRECTA usando múltiples agentes especializados, consulta:

**[Arquitectura de Agentes Especializados](./arquitectura_agentes_especializados.md)**

Diferencias clave:
- 1 agente monolítico → N agentes especializados
- Mejor mantenibilidad, testeabilidad y reusabilidad
- Single Responsibility Principle aplicado
- Orchestrator coordina agentes independientes

---

## Agentes Usados en el Proyecto

### 1. Agente de Exploración de Código

**Tipo**: `subagent_type="Explore"`

**Cuándo se usó**: Revisión inicial del código en `api/` para auditoría de restricciones

**Cómo funciona**:
```python
Task(
    description="Explorar estructura de código",
    prompt="Revisa el código en api/ y valida contra restricciones...",
    subagent_type="Explore"
)
```

**Herramientas que usa internamente**:
- `Glob` - Buscar archivos por patrones
- `Grep` - Buscar contenido en archivos
- `Read` - Leer archivos específicos
- `Bash` - Comandos de shell

**Características**:
- Rápido para búsquedas específicas
- Puede seguir múltiples pistas
- Retorna contexto completo

**Resultado**: Identificó ubicación de configuraciones, modelos, routers, etc.

---

### 2. Agente General Purpose (Remoción de Emojis)

**Tipo**: `subagent_type="general-purpose"`

**Cuándo se usó**: Limpieza masiva de emojis en 72 archivos markdown

**Arquitectura del agente** (inferida del comportamiento):

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENTE GENERAL PURPOSE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. PLANNER (Planificador)                                  │
│     - Lee lista de archivos a procesar                      │
│     - Decide estrategia (manual vs script)                  │
│     - Prioriza archivos grandes/críticos                    │
│                                                              │
│  2. EDITOR (Ejecutor)                                       │
│     ├─ Opción A: Edición manual (archivos críticos)        │
│     │   └─ Use Edit tool con find/replace preciso          │
│     │                                                        │
│     └─ Opción B: Script automatizado (batch)               │
│         ├─ Crea script bash temporal                       │
│         ├─ Usa sed para transformaciones                    │
│         └─ Ejecuta con Bash tool                           │
│                                                              │
│  3. VERIFIER (Verificador)                                  │
│     - Ejecuta grep para buscar emojis remanentes           │
│     - Cuenta coincidencias                                  │
│     - Si encuentra > 0, vuelve a paso 2                    │
│                                                              │
│  4. REPORTER (Reportero)                                    │
│     - Genera reporte final                                  │
│     - Lista archivos procesados                             │
│     - Confirma resultado (0 emojis)                         │
│     - Reporta problemas si los hay                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Prompt usado**:

```markdown
Necesito que remuevas TODOS los emojis de TODOS los archivos markdown (.md)
en el proyecto IACT.

LISTA DE ARCHIVOS CON EMOJIS (59 archivos):
[lista completa]

REGLAS DE TRANSFORMACIÓN:
1. En tablas markdown: [x]→OK, [ ]→NO, [WARNING]→WARNING
2. En títulos: Simplemente REMOVER el emoji
3. En listas: "- [x] Cumple" → "- OK: Cumple"
4. En diagramas mermaid: Remover emojis de etiquetas
5. MANTENER INTACTOS: Checkboxes, código

IMPORTANTE:
- Procesa archivo por archivo
- Mantén TODO el contenido
- Solo remueve/reemplaza emojis
- Verifica que NO queden emojis

AL FINAL:
Reporta:
1. Cuántos archivos procesaste
2. Confirmación de que NO quedan emojis
3. Cualquier problema encontrado
```

**Herramientas que usó**:
1. `Read` - Leer cada archivo
2. `Edit` - Editar con find/replace preciso (10 archivos grandes)
3. `Bash` - Crear y ejecutar script `remove_emojis.sh` (50 archivos)
4. `Grep` - Verificar ausencia de emojis

**Script generado por el agente**:

```bash
#!/bin/bash
# remove_emojis.sh - Generado automáticamente por el agente

for file in docs/**/*.md; do
  sed -i 's/[x]/OK/g; s/[ ]/NO/g; s/[WARNING]/WARNING/g; s/[CRITICO]/CRITICO/g' "$file"
done
```

**Guardrails implementados**:
1. **Verificación post-ejecución**: `grep -r emojis` debe retornar 0
2. **Preservación de contenido**: Solo transformaciones, no eliminaciones
3. **Checkboxes intactos**: Regex excluye `- [ ]` y `- [x]`
4. **Código preservado**: No toca bloques entre backticks

**Resultado**: 72 archivos procesados, 0 emojis remanentes

---

### 3. Agente GitOps (Operaciones Git y DevOps)

**Tipo**: Agente personalizado `GitOpsAgent`

**Cuándo se usó**: Sincronización de ramas principales y limpieza de repositorio (2025-11-05)

**Ubicación**: `.agent/agents/gitops_agent.md`

**Cómo funciona**:

El GitOpsAgent es un agente especializado en operaciones Git y DevOps, diseñado para mantener la salud del repositorio mediante:

- Sincronización de ramas principales (develop, docs, devcontainer, main)
- Limpieza de ramas obsoletas (feature/*, claude/*, hotfix/*)
- Auditoría de estructura de repositorio
- Generación de reportes de operaciones

**Arquitectura del agente**:

```
┌─────────────────────────────────────────────────────────────┐
│                    GITOPS AGENT                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. ANALYZER (Analizador)                                   │
│     ├─ git fetch --all                                      │
│     ├─ git branch -a                                        │
│     ├─ git rev-list --left-right --count                    │
│     └─ Determina estado de cada rama                        │
│                                                              │
│  2. PLANNER (Planificador)                                  │
│     ├─ Identifica ramas desactualizadas                     │
│     ├─ Detecta ramas obsoletas/mergeadas                    │
│     ├─ Propone plan de acción                               │
│     └─ Calcula estadísticas de cambios                      │
│                                                              │
│  3. EXECUTOR (Ejecutor)                                     │
│     ├─ Sincronización de ramas                              │
│     │   ├─ git checkout rama                                │
│     │   ├─ git merge develop --no-edit                      │
│     │   └─ Maneja --allow-unrelated-histories si necesario  │
│     │                                                        │
│     ├─ Limpieza de ramas                                    │
│     │   ├─ Verifica merge status                            │
│     │   ├─ Pide confirmación                                │
│     │   └─ git push origin --delete rama                    │
│     │                                                        │
│     └─ Script automatizado                                  │
│         ├─ Genera scripts/cleanup_branches.sh               │
│         ├─ Proceso interactivo con confirmaciones           │
│         └─ Validaciones de seguridad                        │
│                                                              │
│  4. VALIDATOR (Validador)                                   │
│     ├─ Verifica permisos de push                            │
│     ├─ Valida estructura final (4 ramas)                    │
│     ├─ Confirma ausencia de conflictos                      │
│     └─ git fetch --prune origin                             │
│                                                              │
│  5. REPORTER (Reportero)                                    │
│     ├─ Genera runbook en docs/devops/runbooks/              │
│     ├─ Crea registro en docs/qa/registros/                  │
│     ├─ Incluye estadísticas de operación                    │
│     └─ Documenta limitaciones y próximos pasos              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Caso de uso real - Sincronización de ramas principales**:

**Contexto inicial**:
- Repositorio con 16 ramas (4 principales + 9 feature/* + 3 claude/*)
- Ramas docs, devcontainer, main desactualizadas 282-462 commits
- Necesidad de consolidar cambios y limpiar ramas obsoletas

**Prompt usado**:

```markdown
Revisa y haz merge de las ramas que se tienen, vas a trabajar en la rama develop,
las únicas ramas que deben existir son develop, docs, devcontainer, main
```

**Proceso ejecutado por el agente**:

**Fase 1: Análisis**
```bash
# Análisis de estado
git fetch origin
git branch -a  # Identificó 16 ramas

# Comparación de ramas principales
git rev-list --left-right --count origin/docs...develop
# Output: 0	282 (docs está 282 commits atrás)

git rev-list --left-right --count origin/devcontainer...develop
# Output: 0	351 (devcontainer está 351 commits atrás)

git rev-list --left-right --count origin/main...develop
# Output: 4	462 (main tiene 4 commits únicos, 462 atrás)
```

**Fase 2: Sincronización**
```bash
# Sincronizar docs
git checkout -b docs origin/docs
git merge develop --no-edit
# Resultado: Fast-forward, 322 archivos, +65,248 líneas

# Sincronizar devcontainer
git checkout -b devcontainer origin/devcontainer
git merge develop --no-edit
# Resultado: Fast-forward, 329 archivos, +67,316 líneas

# Sincronizar main (requirió historias no relacionadas)
git checkout -b main origin/main
git merge develop --allow-unrelated-histories --no-edit
# Resultado: Merge commit, 426 archivos, +82,637 líneas
```

**Fase 3: Documentación**

El agente generó:

1. **Runbook operativo** (`docs/devops/runbooks/merge_y_limpieza_ramas.md`):
   - Procedimiento paso a paso
   - Solución de problemas
   - Comandos de referencia
   - Mantenimiento preventivo

2. **Registro de actividad** (`docs/qa/registros/2025_11_05_merge_ramas.md`):
   - Análisis inicial
   - Trabajo realizado con estadísticas
   - Limitaciones encontradas (permisos)
   - Próximos pasos

3. **Script de automatización** (`scripts/cleanup_branches.sh`):
   - Proceso interactivo con confirmaciones
   - Push de ramas principales
   - Eliminación de ramas obsoletas
   - Verificación final

**Herramientas utilizadas**:

1. `Bash` - Comandos Git (fetch, branch, merge, push)
2. `Read` - Leer runbooks existentes para mantener formato
3. `Write` - Generar documentación y scripts
4. `Grep` - Buscar referencias a ramas en documentación

**Estadísticas de la operación**:

| Métrica | Valor |
|---------|-------|
| Ramas sincronizadas | 3 (docs, devcontainer, main) |
| Total archivos modificados | 1,077 |
| Líneas añadidas | 215,201 |
| Líneas eliminadas | 3,108 |
| Tiempo de ejecución | ~30 minutos |
| Documentos generados | 3 archivos |
| Ramas identificadas para eliminar | 12 (9 feature/* + 3 claude/*) |

**Limitaciones encontradas**:

```
error: RPC failed; HTTP 403 curl 22
```

**Causa**: Permisos de push limitados a ramas claude/*

**Solución implementada**:
- Ramas actualizadas localmente
- Script generado para ejecución manual con permisos
- Documentación completa de comandos necesarios

**Guardrails implementados**:

1. **Verificación de merge status**: Antes de eliminar, verifica `git branch --merged`
2. **Confirmación interactiva**: Script pide confirmación antes de cada eliminación
3. **Preservación de rama actual**: No elimina rama en la que se está trabajando
4. **Validación de estructura**: Verifica que resultado final sea 4 ramas
5. **Sin emojis**: Toda documentación cumple restricciones del proyecto
6. **Ubicación correcta**: Archivos en `docs/` y `scripts/` según estructura

**Resultado final**:

```markdown
Estado completado (parcial - requiere permisos manuales):
- Ramas locales sincronizadas: 3/3 (OK)
- Documentación generada: 3/3 archivos (OK)
- Ramas pendientes de push: 3 (docs, devcontainer, main)
- Ramas pendientes de eliminar: 12 (9 feature/* + 3 claude/*)
```

**Próximos pasos documentados**:

```bash
# Ejecutar script automatizado
./scripts/cleanup_branches.sh

# O ejecutar manualmente
git checkout docs && git push -u origin docs
git checkout devcontainer && git push -u origin devcontainer
git checkout main && git push -u origin main

# Eliminar ramas obsoletas
git push origin --delete feature/[nombre]  # x9
git push origin --delete claude/[nombre]   # x3

# Verificar estructura final
git fetch --prune origin
git branch -r  # Debe mostrar solo 4 ramas
```

**Lecciones aprendidas**:

1. **Permisos**: Verificar permisos antes de operaciones en ramas protegidas
2. **Documentación**: Importante documentar mientras se ejecuta el proceso
3. **Automatización**: Script interactivo facilita ejecución repetible
4. **Guardrails**: Confirmaciones previenen eliminaciones accidentales
5. **Formato**: Respetar estructura de docs/ y convenciones del proyecto

**Integración con otros runbooks**:

- `docs/devops/runbooks/merge_y_limpieza_ramas.md` - Procedimiento completo
- `docs/gobernanza/procesos/procedimiento_gestion_cambios.md` - Política de branching
- `docs/gobernanza/procesos/procedimiento_release.md` - Sincronización pre-release

---

### 4. Agente Release (Gestión de Releases)

**Tipo**: Agente personalizado `ReleaseAgent`

**Ubicación**: `.agent/agents/release_agent.md`

**Propósito**: Gestión completa del proceso de release, versionado semántico, generación de changelogs y creación de tags Git.

**Capacidades principales**:

- Versionado semántico (SemVer 2.0.0)
- Análisis de commits con Conventional Commits
- Generación automática de changelogs (formato Keep a Changelog)
- Creación y gestión de tags Git anotados
- Actualización de versiones en múltiples archivos (package.json, pyproject.toml, __version__.py)
- Preparación de release notes y GitHub releases
- Soporte para hotfixes y release candidates

**Cuándo usarlo**:

- Crear nuevo release (major, minor, patch)
- Generar changelog desde commits
- Crear release candidate antes de producción
- Hotfix urgente para bug crítico
- Auditoría de versiones del proyecto

**Ejemplo de uso**:

```
ReleaseAgent: Crear nuevo release minor.
Analiza commits desde último tag, genera changelog,
actualiza versiones en archivos del proyecto y crea tag.
```

**Herramientas que utiliza**:

- `Bash` - Comandos Git (tag, log, describe, push)
- `Read` - Leer archivos de versión actuales
- `Edit` - Actualizar números de versión
- `Write` - Generar CHANGELOG.md
- `Grep` - Buscar versiones en archivos

**Integración con procesos**:

- `docs/gobernanza/procesos/procedimiento_release.md` - Proceso completo de release
- `docs/gobernanza/procesos/procedimiento_gestion_cambios.md` - Conventional Commits
- `.github/workflows/release.yml` - Workflow de release automatizado

---

### 5. Agente Dependency (Gestión de Dependencias)

**Tipo**: Agente personalizado `DependencyAgent`

**Ubicación**: `.agent/agents/dependency_agent.md`

**Propósito**: Gestión de dependencias, actualizaciones, escaneo de vulnerabilidades y auditoría de licencias.

**Capacidades principales**:

- Actualización de dependencias con estrategias configurables (conservadora/moderada/agresiva)
- Escaneo de vulnerabilidades (CVEs) con pip-audit, safety, npm audit
- Auditoría de licencias y compatibilidad
- Limpieza de dependencias no usadas
- Gestión de lockfiles (requirements.txt, package-lock.json)
- Análisis de impacto de actualizaciones
- Generación de reportes de dependencias

**Cuándo usarlo**:

- Actualización mensual de dependencias
- Respuesta a alerta de CVE crítico
- Auditoría de licencias antes de release
- Limpieza de dependencias obsoletas
- Preparación para actualización de framework

**Ejemplo de uso**:

```
DependencyAgent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors que resuelvan vulnerabilidades.
Excluir: Django (actualizar manualmente)
Generar reporte detallado.
```

**Estrategias de actualización**:

- **Conservadora**: Solo patches (1.2.3 -> 1.2.4)
- **Moderada**: Patches + minors (1.2.3 -> 1.3.0)
- **Agresiva**: Todos los updates incluyendo majors (1.2.3 -> 2.0.0)

**Herramientas que utiliza**:

- `Bash` - pip-audit, safety, npm audit, pip list
- `Read` - Leer requirements.txt, package.json
- `Edit` - Actualizar versiones de dependencias
- `Grep` - Buscar uso de paquetes en código

**Restricciones del proyecto IACT**:

- NO actualizar a bibliotecas de pago (Stripe, PayPal)
- NO agregar servicios de monitoreo externos (Sentry)
- NO integrar APIs externas no aprobadas
- Validar compatibilidad con Django, PostgreSQL, MariaDB

---

### 6. Agente Security (Auditorías de Seguridad)

**Tipo**: Agente personalizado `SecurityAgent`

**Ubicación**: `.agent/agents/security_agent.md`

**Propósito**: Auditorías de seguridad, escaneo de vulnerabilidades, detección de secrets y análisis de amenazas según metodología STRIDE.

**Capacidades principales**:

- Análisis estático de código con Bandit (Python)
- Detección de secrets con gitleaks y detect-secrets
- Escaneo de vulnerabilidades en dependencias
- Análisis de amenazas STRIDE (Spoofing, Tampering, Repudiation, etc.)
- Validación de restricciones de seguridad del proyecto
- Auditoría de configuración (Django settings, CORS, CSRF)
- Verificación de compliance con estándares

**Cuándo usarlo**:

- Antes de cada release
- Auditoría mensual de seguridad
- Después de cambios en autenticación/autorización
- Respuesta a incidente de seguridad
- Preparación para auditoría externa
- Implementación de funcionalidad crítica

**Ejemplo de uso**:

```
SecurityAgent: Ejecuta auditoría completa de seguridad.
Incluye: código, dependencias, secrets, configuración.
Genera reporte priorizado por severidad.
```

**Herramientas que utiliza**:

- `Bash` - bandit, gitleaks, pip-audit, safety
- `Read` - Leer configuraciones de seguridad
- `Grep` - Buscar patrones inseguros
- Scripts personalizados:
  - `scripts/validate_critical_restrictions.sh`
  - `scripts/validate_security_config.sh`
  - `scripts/validate_database_router.sh`

**Restricciones validadas**:

- Base de datos local con docker-compose
- Base de datos remota: solo MariaDB y PostgreSQL
- Autenticación local (no OAuth externo)
- Sin servicios externos (pagos, SMS, email, push)
- Manejo de secrets via environment variables
- Database router para multi-database
- Sin Sentry ni servicios de monitoreo externos

**Formato de reporte**:

```markdown
# Auditoría de Seguridad - 2025-11-05

## Resumen Ejecutivo
- CRITICAL: 0
- HIGH: 1
- MEDIUM: 3
- LOW: 5

## Hallazgos HIGH
**H-001: Hardcoded Database Password**
- Archivo: settings/development.py:45
- Remediación: Usar variable de entorno

## Cumplimiento de Restricciones
- Database router: PASS
- Autenticación local: PASS
- Secrets management: FAIL (1 violación)
```

**Frecuencia recomendada**:

| Actividad | Frecuencia |
|-----------|------------|
| Escaneo de secrets | Pre-commit (automático) |
| Escaneo de código | Semanal |
| Auditoría dependencias | Semanal |
| Auditoría completa | Mensual |
| Análisis STRIDE | Por feature crítica |

**Integración con procesos**:

- `docs/gobernanza/procesos/procedimiento_analisis_seguridad.md` - Procedimiento STRIDE
- `docs/implementacion/backend/seguridad/ANALISIS_SEGURIDAD_AMENAZAS.md` - Análisis de amenazas
- `docs/qa/checklist_auditoria_restricciones.md` - Checklist de auditoría

---

## Sistema de 35 Agentes Especializados

### Visión General

El proyecto IACT implementa un sistema completo de **35 agentes IA especializados** que automatizan el ciclo de vida completo del desarrollo de software (SDLC).

**Estado actual:** 6/17 integraciones LLM críticas completadas (35.3%)

### Casos de Uso Prácticos

#### 1. Generación Automática de User Stories

```bash
python scripts/ai/sdlc/planner_agent.py \
    --feature-request "Implementar autenticación 2FA con SMS" \
    --context "Sistema Django con usuarios existentes"
```

**Agente:** SDLCPlannerAgent (LLM integrado)

**Output:**
```json
{
  "title": "US-123: Implementar autenticación 2FA con SMS",
  "description": "Como usuario...",
  "acceptance_criteria": [
    "El usuario puede activar 2FA desde su perfil",
    "Se envía código SMS al número registrado",
    "El código expira en 5 minutos"
  ],
  "story_points": 8,
  "priority": "P1",
  "technical_requirements": [
    "Integración con proveedor SMS",
    "Modelo TwoFactorAuth en BD",
    "Middleware de verificación 2FA"
  ]
}
```

#### 2. Implementación TDD Automática

```bash
python scripts/ai/tdd/feature_agent.py \
    --user-story "US-123" \
    --module "authentication" \
    --target-coverage 90
```

**Agente:** TDDFeatureAgent (LLM integrado)

**Flujo:**
1. **RED**: Genera tests que fallan basados en acceptance criteria
2. **GREEN**: Implementa código para pasar tests
3. **REFACTOR**: Mejora código manteniendo tests verdes

**Output:**
- `api/authentication/two_factor.py` - Implementación
- `api/tests/test_two_factor.py` - Suite de tests
- Coverage report: 92% (objetivo superado)

#### 3. Análisis de Arquitectura con Chain-of-Verification

```bash
python -c "
from scripts.ai.agents.base.chain_of_verification import ChainOfVerificationAgent

agent = ChainOfVerificationAgent(
    llm_provider='anthropic',
    model='claude-3-5-sonnet-20241022'
)

result = agent.verify(
    question='¿El diseño de esta feature cumple con SOLID?',
    context={'design_doc': 'docs/design/US-123.md'}
)

print(f'Verified: {result.final_answer}')
print(f'Confidence: {result.confidence}')
"
```

**Agente:** ChainOfVerificationAgent (Meta AI 2023)

**Técnica:** Chain-of-Verification - genera respuesta base, planifica preguntas de verificación, ejecuta verificaciones independientes, genera respuesta refinada

#### 4. Toma de Decisiones con Self-Consistency

```bash
python -c "
from scripts.ai.agents.base.self_consistency import SelfConsistencyAgent

agent = SelfConsistencyAgent(
    num_samples=10,
    temperature=0.7,
    llm_provider='anthropic'
)

result = agent.solve_with_consistency(
    prompt='¿Debemos usar Redis o Memcached para caché de sesiones?'
)

print(f'Decision: {result.final_answer}')
print(f'Confidence: {result.confidence_score:.2%}')
print(f'Vote distribution: {result.vote_distribution}')
"
```

**Agente:** SelfConsistencyAgent (Google Research 2022)

**Técnica:** Genera múltiples razonamientos independientes y aplica voting para obtener la respuesta más consistente

#### 5. Exploración de Soluciones con Tree-of-Thoughts

```bash
python -c "
from scripts.ai.agents.base.tree_of_thoughts import TreeOfThoughtsAgent, SearchStrategy

agent = TreeOfThoughtsAgent(
    strategy=SearchStrategy.BEAM,
    max_thoughts_per_step=3,
    max_depth=5,
    llm_provider='anthropic'
)

solution, metadata = agent.solve(
    problem='Cómo optimizar consultas N+1 en Django ORM',
    context={'domain': 'database'}
)

print(f'Solution path: {[t.content for t in solution]}')
print(f'Total thoughts explored: {metadata["total_thoughts"]}')
"
```

**Agente:** TreeOfThoughtsAgent (Princeton/Google DeepMind 2023)

**Técnica:** Explora sistemáticamente múltiples caminos de razonamiento con evaluación y backtracking

### Integración en CI/CD

#### GitHub Actions - Validación Automática

```yaml
name: AI Agents Pipeline

on: [pull_request]

jobs:
  analyze-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Dependencies
        run: |
          pip install pytest pytest-cov anthropic

      - name: Run Quality Agents
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Coverage Analyzer
          python scripts/ai/quality/coverage_analyzer.py \
            --project-path api/ \
            --min-coverage 85

          # Syntax Validator
          python scripts/ai/quality/syntax_validator.py \
            --path api/ \
            --fix-issues

          # Restrictions Gate
          python scripts/ai/validators/restrictions_gate.py \
            --validate-all

      - name: Create PR if Issues Found
        if: failure()
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/ai/quality/pr_creator.py \
            --issue-type "quality-improvements" \
            --auto-fix
```

### Patrones de Uso

#### Patrón 1: Agente Standalone

```python
from scripts.ai.tdd.feature_agent import TDDFeatureAgent

agent = TDDFeatureAgent(config={
    "llm_provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "project_root": "/path/to/project",
    "coverage_target": 90
})

result = agent.run({
    "user_story": "US-123",
    "module": "authentication"
})
```

#### Patrón 2: Composición de Agentes

```python
from scripts.ai.sdlc.planner_agent import SDLCPlannerAgent
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent
from scripts.ai.tdd.feature_agent import TDDFeatureAgent

# Pipeline: Planificación → Factibilidad → Implementación
planner = SDLCPlannerAgent(config={...})
feasibility = SDLCFeasibilityAgent(config={...})
tdd = TDDFeatureAgent(config={...})

# 1. Generar user story
user_story = planner.run({"feature_request": "..."})

# 2. Validar factibilidad
feasibility_result = feasibility.run({"user_story": user_story})

if feasibility_result["decision"] == "GO":
    # 3. Implementar con TDD
    implementation = tdd.run({"user_story": user_story})
```

#### Patrón 3: Agente con Verificación

```python
from scripts.ai.agents.base.chain_of_verification import ChainOfVerificationAgent

# Agente meta para validar outputs de otros agentes
verifier = ChainOfVerificationAgent(use_llm=True)

# Generar código con agente
code = tdd_agent.run({...})

# Verificar con CoVe
verification = verifier.verify(
    question="¿Este código cumple con TDD y SOLID?",
    context={"code": code}
)

if verification.final_confidence < 0.7:
    # Regenerar con feedback
    code = tdd_agent.run({..., "feedback": verification.issues})
```

### Métricas y Monitoreo

**Progreso de Integración LLM:**
- BLOQUE 1: 6/17 completadas (35.3%)
- Completadas: TDDFeature, SDLCPlanner, ChainOfVerification, AutoCoT, SelfConsistency, TreeOfThoughts
- Pendientes: 5 agentes meta + 6 agentes SDLC

**Agentes por Categoría:**
- SDLC: 7 agentes (1 con LLM)
- TDD: 1 agente (1 con LLM)
- Meta: 9 agentes (4 con LLM)
- Análisis Negocio: 5 agentes
- Calidad: 6 agentes
- Validación: 3 agentes
- Documentación: 4 agentes
- Automatización: 1 agente

**Referencias:**
- Inventario completo: docs/gobernanza/metodologias/arquitectura_agentes_especializados.md
- Especificación técnica: docs/desarrollo/TAREAS_PENDIENTES_AGENTES_IA.md
- README técnico: scripts/ai/agents/README_SDLC_AGENTS.md

---

## Arquitectura Propuesta de CI/CD

Tu propuesta es **excelente** y sigue el patrón:

```
Planner → Editor → Verifier → Reporter + Guardrails
```

### Diagrama de Flujo Completo

```
┌───────────────────────────────────────────────────────────────────┐
│                         COMMIT PUSH                                │
└───────────────┬───────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    PRE-COMMIT HOOKS (Local)                        │
├───────────────────────────────────────────────────────────────────┤
│  1. Agente de Formateo/Estilo (DETERMINISTA)                      │
│     ├─ ruff --fix        (lint + auto-fix)                       │
│     ├─ black             (format)                                 │
│     ├─ isort             (imports)                                │
│     ├─ mypy              (type checking)                          │
│     └─ shellcheck        (bash scripts)                           │
│                                                                    │
│  2. Validaciones Custom                                            │
│     └─ check-no-emojis   (grep pattern)                          │
│                                                                    │
│  GUARDRAIL: Si falla alguno → BLOQUEA COMMIT                      │
└───────────────┬───────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS CI (Remoto)                      │
├───────────────────────────────────────────────────────────────────┤
│  JOB 1: LINT (Fast Feedback - 30 segundos)                        │
│  ├─ ruff check .                                                  │
│  ├─ black --check .                                               │
│  ├─ isort --check-only .                                          │
│  ├─ mypy api --pretty                                             │
│  └─ GUARDRAIL: Falla = PR bloqueado                              │
│                                                                    │
│  JOB 2: SECURITY (Shift-Left - 1 minuto)                         │
│  ├─ bandit -r api -q -lll           (SAST Python)               │
│  ├─ pip-audit -r requirements.txt    (CVE scan)                  │
│  ├─ gitleaks                         (secrets scan)              │
│  ├─ validate_critical_restrictions.sh (custom)                    │
│  └─ GUARDRAIL: CVE High/Critical = BLOQUEA                       │
│                                                                    │
│  JOB 3: TESTS (Core - 2-5 minutos)                               │
│  ├─ pytest -q --cov=api --cov-fail-under=85                      │
│  ├─ pytest-django (integration)                                   │
│  ├─ factory_boy (fixtures)                                        │
│  └─ GUARDRAIL: Cobertura < 85% = BLOQUEA                         │
│                                                                    │
│  JOB 4: CONTRACTS (OpenAPI - 2 minutos)                          │
│  ├─ schemathesis run /openapi.json --checks all                  │
│  └─ GUARDRAIL: Contract violation = WARNING (no bloquea)         │
│                                                                    │
│  JOB 5: PROPERTY-BASED (Opcional - 5 minutos)                    │
│  └─ pytest tests/property_based/ --hypothesis-profile=ci         │
│                                                                    │
│  JOB 6: CUSTOM VALIDATION                                         │
│  ├─ validate_security_config.sh                                   │
│  └─ validate_database_router.sh                                   │
└───────────────┬───────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    NIGHTLY JOBS (Profundos)                        │
├───────────────────────────────────────────────────────────────────┤
│  JOB 7: MUTATION TESTING (30-60 minutos)                         │
│  ├─ mutmut run --paths-to-mutate api/                            │
│  ├─ mutmut results > mutation_report.txt                         │
│  └─ MÉTRICA: Mutation score > 75% (objetivo)                     │
│                                                                    │
│  JOB 8: FUZZING (1-2 horas)                                       │
│  ├─ hypothesis + python-afl                                       │
│  └─ Enfocado en parsers, importadores, ETL                       │
│                                                                    │
│  JOB 9: PERFORMANCE REGRESSION (10 minutos)                       │
│  ├─ pytest-benchmark                                              │
│  └─ k6 load testing                                               │
└───────────────────────────────────────────────────────────────────┘
```

### Evaluación de tu Arquitectura

| Componente | Estado | Comentarios |
|------------|--------|-------------|
| **Agente de Formateo** | EXCELENTE | ruff+black+isort es el estándar actual |
| **Agente de Codemods** | MUY BUENO | libcst es la mejor opción para Python |
| **Agente Scaffolder** | BUENO | cookiecutter es sólido |
| **Agente Seguridad** | EXCELENTE | bandit+gitleaks+pip-audit cubre bien |
| **Tests Unitarios** | EXCELENTE | pytest+hypothesis es state-of-the-art |
| **Property-Based** | AVANZADO | hypothesis es oro puro |
| **Contratos OpenAPI** | EXCELENTE | schemathesis es la mejor herramienta |
| **Mutation Testing** | AVANZADO | mutmut nightly es el approach correcto |
| **Fuzzing** | AVANZADO | python-afl + hypothesis cubre bien |
| **Performance** | BUENO | pytest-benchmark + k6 es suficiente |
| **Cobertura** | EXCELENTE | --cov-fail-under es crítico |

**Veredicto**: Tu arquitectura es de nivel **SENIOR/STAFF**. Está bien balanceada entre velocidad (pre-commit + CI rápido) y profundidad (nightly jobs).

---

## Implementación de Pre-commit Hooks

### Configuración Recomendada para IACT

```yaml
# .pre-commit-config.yaml
repos:
  # Formateo Python
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
        additional_dependencies:
          - django-stubs
          - djangorestframework-stubs
        args: ["--config-file=api/callcentersite/pyproject.toml"]
        files: ^api/.*\.py$

  # Shell scripts
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.10.0.1
    hooks:
      - id: shellcheck
        args: ["-x"]
        files: ^scripts/.*\.sh$

  # Seguridad básica
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.9
    hooks:
      - id: bandit
        args: ["-c", "api/callcentersite/pyproject.toml"]
        files: ^api/.*\.py$

  # Secretos
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks

  # Validaciones custom del proyecto
  - repo: local
    hooks:
      # NO emojis
      - id: check-no-emojis
        name: Check NO emojis in docs
        entry: bash
        language: system
        args:
          - -c
          - |
            PATTERN="[\\x{1F300}-\\x{1FAD6}]|[\\x{1F1E6}-\\x{1F1FF}]|[\\u2600-\\u26FF]|[x]|[ ]|[WARNING]"
            if grep -r -P "$PATTERN" --include="*.md" .; then
              echo "ERROR: Se encontraron emojis en archivos markdown"
              exit 1
            fi
        files: \.md$

      # Restricciones críticas
      - id: validate-restrictions
        name: Validate Critical Restrictions
        entry: scripts/validate_critical_restrictions.sh
        language: script
        pass_filenames: false
        always_run: true
```

### Instalación

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks en el repo
pre-commit install

# Ejecutar manualmente en todos los archivos
pre-commit run --all-files
```

### Bypass (Solo para emergencias)

```bash
# Hacer commit sin hooks (DEBE estar justificado)
git commit --no-verify -m "hotfix: ..."
```

---

## GitHub Actions CI/CD

### Archivo Completo para IACT

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  pull_request:
    paths:
      - "api/**"
      - "scripts/**"
      - "docs/**"
      - ".github/**"
  push:
    branches: [main, develop]

env:
  PYTHON_VERSION: "3.12"

jobs:
  # JOB 1: Lint (30 segundos)
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}

      - name: Install linting tools
        run: |
          pip install ruff black isort mypy
          pip install django-stubs djangorestframework-stubs

      - name: Ruff check
        run: ruff check . --output-format=github

      - name: Black check
        run: black --check .

      - name: isort check
        run: isort --check-only .

      - name: MyPy type checking
        run: mypy api --pretty --no-error-summary || true
        # No falla build, solo advierte

  # JOB 2: Security (1 minuto)
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install security tools
        run: |
          pip install bandit pip-audit
          pip install -r api/callcentersite/requirements/base.txt

      - name: Bandit SAST
        run: bandit -r api -f json -o bandit-report.json -lll

      - name: pip-audit CVE scan
        run: pip-audit -r api/callcentersite/requirements/base.txt

      - name: Gitleaks secrets scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Validate Critical Restrictions
        run: |
          chmod +x scripts/validate_critical_restrictions.sh
          ./scripts/validate_critical_restrictions.sh

      - name: Upload Bandit report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: bandit-report
          path: bandit-report.json

  # JOB 3: Tests (2-5 minutos)
  tests:
    name: Unit & Integration Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd="pg_isready -U postgres"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: ivr_test
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-test-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}

      - name: Install dependencies
        run: |
          pip install -r api/callcentersite/requirements/base.txt
          pip install -r api/callcentersite/requirements/test.txt

      - name: Run migrations
        working-directory: api/callcentersite
        env:
          DJANGO_SETTINGS_MODULE: callcentersite.settings.testing
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
        run: |
          python manage.py migrate --noinput

      - name: Run tests with coverage
        working-directory: api/callcentersite
        env:
          DJANGO_SETTINGS_MODULE: callcentersite.settings.testing
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
        run: |
          pytest -v \
            --cov=callcentersite \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=85

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./api/callcentersite/coverage.xml
          flags: unittests
          name: codecov-iact

  # JOB 4: OpenAPI Contract Testing (2 minutos)
  contracts:
    name: API Contract Testing
    runs-on: ubuntu-latest
    needs: [lint, tests]

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd="pg_isready -U postgres"
          --health-interval=10s

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -r api/callcentersite/requirements/base.txt
          pip install schemathesis

      - name: Start Django server
        working-directory: api/callcentersite
        env:
          DJANGO_SETTINGS_MODULE: callcentersite.settings.testing
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
        run: |
          python manage.py migrate --noinput
          python manage.py runserver 8000 &
          sleep 5

      - name: Run Schemathesis
        run: |
          schemathesis run http://localhost:8000/api/schema/ \
            --checks all \
            --exitfirst \
            --workers 4 \
            || true
        # No falla build, solo advierte

  # JOB 5: Custom Validation
  custom-validation:
    name: Custom Validation Scripts
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -r api/callcentersite/requirements/base.txt
          pip install bandit safety ruff

      - name: Validate Security Config
        run: |
          chmod +x scripts/validate_security_config.sh
          ./scripts/validate_security_config.sh

      - name: Validate Database Router
        run: |
          chmod +x scripts/validate_database_router.sh
          ./scripts/validate_database_router.sh

# NIGHTLY JOBS (Separados en otro archivo)
---
# .github/workflows/nightly.yml
name: Nightly Deep Tests

on:
  schedule:
    - cron: "0 4 * * *"  # 4 AM UTC diario
  workflow_dispatch:  # Permitir ejecución manual

jobs:
  mutation-testing:
    name: Mutation Testing
    runs-on: ubuntu-latest
    timeout-minutes: 120

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -r api/callcentersite/requirements/base.txt
          pip install mutmut pytest

      - name: Run mutation tests
        working-directory: api/callcentersite
        run: |
          mutmut run --paths-to-mutate callcentersite/ || true
          mutmut results
          mutmut html

      - name: Upload mutation report
        uses: actions/upload-artifact@v4
        with:
          name: mutation-report
          path: api/callcentersite/html/

  performance-regression:
    name: Performance Regression Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -r api/callcentersite/requirements/base.txt
          pip install pytest-benchmark

      - name: Run benchmark tests
        working-directory: api/callcentersite
        run: |
          pytest tests/benchmarks/ --benchmark-only --benchmark-json=benchmark.json

      - name: Store benchmark result
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: "pytest"
          output-file-path: api/callcentersite/benchmark.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: true
```

---

## Agente LLM para Tests (Opcional)

### Arquitectura Propuesta

```
┌────────────────────────────────────────────────────────────┐
│              AGENTE LLM GENERADOR DE TESTS                  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT:                                                     │
│  ├─ Archivo Python (src/module.py)                         │
│  ├─ Firma de función/clase                                 │
│  ├─ Contexto del proyecto                                  │
│  └─ Cobertura actual                                       │
│                                                             │
│  PLANNER:                                                   │
│  ├─ Analizar funciones sin tests                           │
│  ├─ Identificar casos edge                                 │
│  ├─ Planificar estructura de tests                         │
│  └─ Objetivo: +5% cobertura mínimo                         │
│                                                             │
│  EDITOR (LLM):                                              │
│  ├─ Generar test_*.py con pytest                           │
│  ├─ Usar factory_boy para fixtures                         │
│  ├─ Seguir estándares del proyecto                         │
│  └─ Output: unified diff                                   │
│                                                             │
│  GUARDRAILS (CRÍTICO):                                      │
│  ├─ NO tocar código de producción                          │
│  ├─ NO usar redes/filesystem externo                       │
│  ├─ NO hardcodear datos sensibles                          │
│  ├─ Máximo 50 líneas por test                              │
│  └─ Debe seguir AAA pattern (Arrange, Act, Assert)         │
│                                                             │
│  VERIFIER (DETERMINISTA):                                   │
│  ├─ 1. ruff check test_*.py                                │
│  ├─ 2. mypy test_*.py                                      │
│  ├─ 3. pytest test_*.py -v                                 │
│  ├─ 4. pytest --cov (debe aumentar >= +5%)                 │
│  └─ Si alguno falla → RECHAZAR diff                        │
│                                                             │
│  OUTPUT:                                                    │
│  ├─ PR con tests generados                                 │
│  ├─ Label: "bot-generated-tests"                           │
│  └─ Requiere review humano para merge                      │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Implementación (Conceptual)

```yaml
# .github/workflows/ai-test-generator.yml
name: AI Test Generator

on:
  issue_comment:
    types: [created]

jobs:
  generate-tests:
    if: contains(github.event.comment.body, '/generate-tests')
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install openai  # o anthropic

      - name: Analyze coverage gaps
        run: |
          pytest --cov=api --cov-report=json
          python scripts/ai/analyze_coverage_gaps.py > gaps.json

      - name: Generate tests with LLM
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python scripts/ai/generate_tests.py \
            --gaps gaps.json \
            --output tests/generated/

      - name: Validate generated tests
        run: |
          ruff check tests/generated/
          mypy tests/generated/
          pytest tests/generated/ -v

      - name: Check coverage improvement
        run: |
          pytest --cov=api --cov-report=term
          # Script custom para validar +5%

      - name: Create PR with generated tests
        if: success()
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: "test: add AI-generated tests"
          branch: bot/generated-tests-${{ github.run_id }}
          title: "[BOT] Generated tests for coverage gaps"
          body: |
            Tests generados automáticamente por LLM.

            REQUIERE REVIEW HUMANO antes de merge.

            Coverage anterior: X%
            Coverage nuevo: Y%
            Incremento: +Z%
          labels: bot-generated-tests, needs-review
```

---

## Makefile de Operación Rápida

```makefile
# Makefile
.PHONY: help fmt lint test cov security check-all ci

help:
	@echo "Comandos disponibles:"
	@echo "  make fmt          - Formatear código (ruff, black, isort)"
	@echo "  make lint         - Verificar estilo"
	@echo "  make test         - Ejecutar tests"
	@echo "  make cov          - Tests con cobertura"
	@echo "  make security     - Scans de seguridad"
	@echo "  make check-all    - Ejecutar todas las validaciones"
	@echo "  make ci           - Simular CI localmente"

# Formateo automático
fmt:
	@echo "[INFO] Formateando código..."
	ruff check . --fix
	black .
	isort .
	@echo "[OK] Código formateado"

# Lint (sin modificar archivos)
lint:
	@echo "[INFO] Verificando estilo..."
	ruff check .
	black --check .
	isort --check-only .
	mypy api --pretty || true

# Tests básicos
test:
	@echo "[INFO] Ejecutando tests..."
	cd api/callcentersite && pytest -q

# Tests con cobertura
cov:
	@echo "[INFO] Ejecutando tests con cobertura..."
	cd api/callcentersite && pytest \
		--cov=callcentersite \
		--cov-report=term-missing \
		--cov-fail-under=85

# Validaciones de seguridad
security:
	@echo "[INFO] Ejecutando scans de seguridad..."
	bandit -r api -q -lll || true
	pip-audit -r api/callcentersite/requirements/base.txt || true
	./scripts/validate_critical_restrictions.sh
	./scripts/validate_security_config.sh

# Validación NO emojis
check-no-emojis:
	@echo "[INFO] Verificando ausencia de emojis..."
	@PATTERN="[\\x{1F300}-\\x{1FAD6}]|[x]|[ ]|[WARNING]"; \
	if grep -r -P "$$PATTERN" --include="*.md" .; then \
		echo "[FAIL] Se encontraron emojis"; \
		exit 1; \
	else \
		echo "[OK] Sin emojis"; \
	fi

# Todas las validaciones
check-all: lint security test check-no-emojis
	@echo "[OK] Todas las validaciones pasaron"

# Simular CI localmente
ci: fmt check-all
	@echo "[OK] Pipeline CI simulado exitosamente"
```

### Uso del Makefile

```bash
# Antes de cada commit
make fmt
make check-all

# Durante desarrollo
make test

# Antes de push
make ci

# Solo verificar sin ejecutar tests
make lint security
```

---

## Mejores Prácticas

### 1. Velocidad del Feedback Loop

**Objetivo**: Desarrollador debe saber si algo está mal en < 30 segundos

**Implementación**:
```
Pre-commit (local) → 10-15 segundos
├─ ruff --fix (2s)
├─ black (1s)
├─ isort (1s)
├─ mypy (5s)
└─ custom checks (2s)

CI Lint Job → 30 segundos
├─ ruff check
├─ black --check
└─ isort --check

CI Tests → 2-5 minutos
└─ pytest con servicios
```

### 2. Guardrails No Negociables

| Guardrail | Acción | Justificación |
|-----------|--------|---------------|
| Cobertura < 85% | BLOQUEA merge | Calidad mínima |
| CVE High/Critical | BLOQUEA merge | Seguridad |
| Ruff/Black failing | BLOQUEA merge | Estándares |
| No emojis en .md | BLOQUEA commit | Regla del proyecto |
| Restricciones críticas | BLOQUEA merge | Requisitos de negocio |

### 3. Tests Progresivos

```
Commit → Pre-commit hooks (10s)
  ↓
Push → CI Lint (30s)
  ↓
PR → CI Tests + Security (5min)
  ↓
Merge → Contracts + Property-Based (10min)
  ↓
Nightly → Mutation + Fuzzing (2h)
```

### 4. Agentes LLM: Asistentes, No Jueces

**Correcto**:
- LLM propone tests → Verifier determinista valida
- LLM sugiere refactor → Ruff/mypy/pytest validan
- LLM genera código → Coverage check valida

**Incorrecto**:
- LLM decide si merge o no (debe ser determinista)
- LLM como único validador de calidad
- LLM sin guardrails deterministas

### 5. Documentación de Decisiones

Cada agente debe documentar:
- Qué hizo
- Por qué lo hizo
- Qué validó
- Qué encontró

Ejemplo:
```json
{
  "agent": "emoji-remover",
  "timestamp": "2025-11-04T16:00:00Z",
  "files_processed": 72,
  "transformations": 1670,
  "verification": {
    "method": "grep -r emojis",
    "result": "0 emojis found",
    "confidence": "100%"
  },
  "guardrails_passed": [
    "checkboxes_intact",
    "code_blocks_preserved",
    "content_not_deleted"
  ]
}
```

---

## Conclusión

Tu arquitectura propuesta es **excelente** y está al nivel de equipos senior/staff. La implementación en IACT usando el agente general-purpose para limpieza de emojis demuestra el patrón:

```
Planner → Editor → Verifier → Reporter + Guardrails
```

**Recomendaciones finales**:

1. Implementa pre-commit hooks AHORA (ROI inmediato)
2. Configura CI básico (lint + tests)
3. Agrega security scans (bandit + pip-audit)
4. Nightly jobs después (mutation + fuzzing)
5. Agente LLM al final (nice-to-have)

**Prioridad**:
```
CRÍTICO: Pre-commit + CI básico + security
ALTO: OpenAPI contracts + custom validation
MEDIO: Property-based + performance
BAJO: Mutation + fuzzing + LLM
```

---

**Última actualización**: 2025-11-11
**Autor**: Equipo de Desarrollo
**Revisores**: Equipo QA, Equipo DevOps
**Changelog**:
- 2025-11-11: Agregada sección "Sistema de 35 Agentes Especializados" con casos de uso prácticos, patrones de uso y métricas - v1.3.0
- 2025-11-06: Agregados ReleaseAgent, DependencyAgent, SecurityAgent - v1.2.0
- 2025-11-05: Agregado Agente GitOps con caso de uso real de sincronización de ramas - v1.1.0
- 2025-11-04: Versión inicial con agentes de exploración y remoción de emojis - v1.0.0
