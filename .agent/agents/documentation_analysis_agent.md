---
name: Documentation Analysis Agent
description: Agente especializado en analisis de calidad de documentacion, deteccion de gaps, links rotos, contenido desactualizado y sugerencias de mejora.
---

# Documentation Analysis Agent

Agente experto en analisis de documentacion que evalua calidad, completitud, precision y mantenibilidad de documentacion tecnica, identificando gaps, enlaces rotos, contenido obsoleto y generando recomendaciones de mejora.

## Capacidades

### Analisis de Calidad
- Evaluacion de legibilidad (Flesch Reading Ease)
- Deteccion de contenido desactualizado
- Verificacion de consistencia terminologica
- Analisis de estructura y organizacion
- Medicion de cobertura de documentacion

### Deteccion de Problemas
- Enlaces rotos (internos y externos)
- Imagenes faltantes
- Code snippets invalidos
- Ejemplos no funcionales
- Referencias sin resolver

### Analisis de Contenido
- Identificacion de gaps de documentacion
- Deteccion de redundancia
- Evaluacion de profundidad de temas
- Analisis de relevancia
- Verificacion de versionado

### Metricas
- Documentation Coverage Score
- Freshness Index
- Quality Score
- Completeness Percentage
- Link Health Ratio

## Cuando Usar

- Auditoria de documentacion
- Preparacion para releases
- Onboarding de equipo
- Migracion de documentacion
- Mejora continua de docs
- Compliance y certificaciones

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/documentation/documentation_analysis_agent.py \
  --docs-dir /ruta/a/docs \
  --analysis-type full
```

### Analisis Completo

```bash
python scripts/coding/ai/documentation/documentation_analysis_agent.py \
  --docs-dir docs/ \
  --analysis-type full \
  --check-links \
  --validate-code-snippets \
  --output-format html
```

### Deteccion de Enlaces Rotos

```bash
python scripts/coding/ai/documentation/documentation_analysis_agent.py \
  --docs-dir docs/ \
  --analysis-type links \
  --check-external \
  --parallel-requests 10
```

### Analisis de Cobertura

```bash
python scripts/coding/ai/documentation/documentation_analysis_agent.py \
  --docs-dir docs/ \
  --analysis-type coverage \
  --compare-with-code api/ \
  --min-coverage 80
```

### Validacion de Code Snippets

```bash
python scripts/coding/ai/documentation/documentation_analysis_agent.py \
  --docs-dir docs/ \
  --analysis-type snippets \
  --execute-python \
  --validate-syntax
```

## Parametros

- `--docs-dir`: Directorio de documentacion
- `--analysis-type`: Tipo (full, links, coverage, snippets, freshness)
- `--check-links`: Verificar enlaces
- `--check-external`: Incluir enlaces externos
- `--validate-code-snippets`: Validar sintaxis de codigo
- `--execute-python`: Ejecutar snippets Python
- `--compare-with-code`: Comparar con codigo fuente
- `--min-coverage`: Cobertura minima requerida
- `--output-format`: Formato (text, html, json)
- `--parallel-requests`: Requests paralelos para links

## Salida

### Reporte de Analisis

```markdown
# Documentation Analysis Report
Project: IACT Call Center
Analysis Date: 2025-11-15
Docs Directory: docs/
Files Analyzed: 127

## Executive Summary

| Metric | Score | Status |
|--------|-------|--------|
| Overall Quality | 72/100 | PASS |
| Documentation Coverage | 68% | NEEDS IMPROVEMENT |
| Link Health | 89% | GOOD |
| Freshness | 65% | NEEDS IMPROVEMENT |
| Code Snippet Validity | 91% | GOOD |

## Quality Analysis

### Readability
Average Flesch Reading Ease: 62.4 (Standard)
- Technical docs: 58.2 (Fairly Difficult) ✓
- User guides: 71.5 (Fairly Easy) ✓
- API docs: 55.1 (Fairly Difficult) ⚠️ Too complex

Recommendation: Simplify API documentation language

### Structure
- Clear hierarchy: YES
- Table of contents: 78% of docs have TOC
- Navigation: Good (breadcrumbs present)
- Search functionality: Available

### Consistency
- Terminology: 23 inconsistent terms found
  - "API endpoint" vs "API route" (use "API endpoint")
  - "database" vs "DB" (use "database")
  - "authentication" vs "auth" (use "authentication" in formal docs)

## Coverage Analysis

### Documented vs Undocumented

| Component | Documented | Undocumented | Coverage |
|-----------|------------|--------------|----------|
| API Endpoints | 45 | 12 | 79% |
| Models | 38 | 7 | 84% |
| Services | 22 | 15 | 59% ⚠️ |
| Utilities | 15 | 28 | 35% ❌ |

### Critical Gaps

1. **Authentication Flow** (Priority: HIGH)
   - Current: Partial documentation
   - Missing: OAuth integration, token refresh, MFA setup
   - Impact: New developers struggle with auth implementation

2. **Database Schema** (Priority: HIGH)
   - Current: ERD diagram outdated (2024-08-15)
   - Missing: Recent table additions (audit_log, notification_queue)
   - Impact: Confusion about data relationships

3. **Deployment Process** (Priority: MEDIUM)
   - Current: Basic deployment steps
   - Missing: Rollback procedure, zero-downtime deployment
   - Impact: Risky deployments

## Link Analysis

### Broken Links (14 found)

#### Internal Links (8)
1. docs/api/authentication.md:45
   - Link: [User API](../reference/user-api.md)
   - Error: File not found
   - Fix: Update to ../api-reference/users.md

2. docs/guides/setup.md:112
   - Link: [Database Setup](database.md)
   - Error: Anchor #postgresql not found
   - Fix: Update anchor to #postgresql-configuration

[Additional broken links...]

#### External Links (6)
1. docs/integrations/stripe.md:23
   - Link: https://stripe.com/docs/api/v1
   - Error: 404 Not Found
   - Fix: Update to https://stripe.com/docs/api (v1 deprecated)

2. docs/references/django.md:67
   - Link: https://docs.djangoproject.com/en/3.2/
   - Error: DNS resolution timeout
   - Status: Temporary issue, recheck later

### Link Health: 89% (114/128 links working)

## Freshness Analysis

### Outdated Documentation (23 files)

| File | Last Updated | Age | Status |
|------|--------------|-----|--------|
| docs/architecture/overview.md | 2024-03-15 | 8 months | ⚠️ STALE |
| docs/api/v1/orders.md | 2024-01-20 | 10 months | ❌ OUTDATED |
| docs/deployment/aws.md | 2023-11-10 | 12 months | ❌ CRITICAL |

Recommendation: Update docs older than 6 months

### Recently Updated (Good) (45 files)
- docs/getting-started.md (2025-11-10)
- docs/api/users.md (2025-11-05)
- docs/guides/testing.md (2025-10-28)

## Code Snippet Validation

### Syntax Errors (4 found)

1. docs/examples/authentication.md:89
```python
# Error: Missing import
user = User.objects.get(id=user_id)  # NameError: User not defined
```
Fix: Add `from api.models import User`

2. docs/api/webhooks.md:45
```python
# Error: Invalid syntax
def handle_webhook(request)
    data = request.body  # SyntaxError: missing ':'
```

### Execution Errors (3 found)

1. docs/guides/database.md:120
```python
# Error: ImportError
from obsolete_module import Helper  # Module removed in v2.0
```

### Outdated Examples (7 found)

1. docs/api/authentication.md:34
   - Uses deprecated `authenticate_user()` function
   - Should use `AuthService.authenticate()` (since v2.1)

## Improvement Recommendations

### High Priority
1. Fix 14 broken links (Est. 2 hours)
2. Update 23 outdated documents (Est. 16 hours)
3. Document 15 undocumented services (Est. 20 hours)
4. Fix 4 code snippet syntax errors (Est. 1 hour)

### Medium Priority
5. Improve consistency (use terminology guide) (Est. 4 hours)
6. Add missing API endpoint docs (12 endpoints) (Est. 8 hours)
7. Update ERD diagram (Est. 3 hours)

### Low Priority
8. Improve readability of complex API docs (Est. 6 hours)
9. Add more examples to user guides (Est. 10 hours)
10. Implement automated freshness checks (Est. 8 hours)

## Action Plan

### Sprint 1 (40 hours)
- Fix broken links
- Update critical outdated docs
- Fix code snippet errors
- Document high-priority undocumented components

### Sprint 2 (40 hours)
- Improve consistency
- Add missing API docs
- Update diagrams
- Add more examples

### Maintenance
- Implement CI checks for broken links
- Add documentation coverage to PR checks
- Schedule quarterly documentation reviews
- Set up automated staleness warnings

[End of Report]
```

## Herramientas Utilizadas

- **markdown-link-check**: Verificacion de enlaces
- **textstat**: Metricas de legibilidad
- **pygments**: Validacion de sintaxis de codigo
- **requests**: Verificacion de enlaces externos
- **beautifulsoup4**: Parseo de HTML
- **mkdocs**: Integracion con sistema de docs

## Mejores Practicas

1. **Ejecutar regularmente**: Mensual o antes de releases
2. **Automatizar**: Integrar en CI para detectar problemas temprano
3. **Priorizar**: Enfocarse en gaps criticos primero
4. **Colaborar**: Asignar ownership de documentos
5. **Medir progreso**: Trackear metricas en el tiempo
6. **Feedback loop**: Incorporar feedback de usuarios
7. **Mantener actualizados**: Actualizar docs con codigo

## Restricciones

- Validacion de code snippets limitada a lenguajes soportados
- Enlaces externos pueden dar falsos positivos (timeouts)
- Deteccion de contenido desactualizado es heuristica
- No detecta problemas de exactitud tecnica
- Metricas de legibilidad son estimadas

## Ubicacion

Archivo: `scripts/coding/ai/documentation/documentation_analysis_agent.py`
