---
name: Refactoring Opportunities Agent
description: Agente especializado en identificacion de oportunidades de refactorizacion, code smells, duplicacion de codigo y sugerencias de mejora basadas en principios SOLID y Clean Code.
---

# Refactoring Opportunities Agent

Agente experto en deteccion de oportunidades de refactorizacion que analiza codigo existente, identifica code smells, duplicacion, violaciones de principios SOLID y genera recomendaciones priorizadas de refactorizacion.

## Capacidades

### Deteccion de Code Smells
- Long Method (metodos muy largos)
- Large Class (clases con muchas responsabilidades)
- Duplicate Code (codigo duplicado)
- Dead Code (codigo no utilizado)
- God Object (objetos con demasiadas responsabilidades)
- Feature Envy (metodos que usan mas datos de otra clase)
- Data Clumps (grupos de datos que siempre estan juntos)

### Analisis de Principios
- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP)
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)

### Metricas de Codigo
- Complejidad ciclomatica
- Cohesion y acoplamiento
- Lineas de codigo por metodo/clase
- Profundidad de herencia
- Fan-in y Fan-out

### Priorizacion
- Impacto vs esfuerzo
- Riesgo de regresion
- Frecuencia de cambios
- Deuda tecnica acumulada

## Cuando Usar

- Planificacion de sprints de refactorizacion
- Code reviews
- Preparacion para nuevas features
- Migracion o modernizacion de codigo
- Reduccion de deuda tecnica
- Mejora de mantenibilidad

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/meta/refactoring_opportunities_agent.py \
  --project-root /ruta/al/proyecto \
  --scan-path api/ \
  --language python
```

### Analisis Completo

```bash
python scripts/coding/ai/meta/refactoring_opportunities_agent.py \
  --project-root . \
  --scan-path api/services \
  --check-all \
  --min-severity medium \
  --output-format json
```

### Deteccion de Duplicacion

```bash
python scripts/coding/ai/meta/refactoring_opportunities_agent.py \
  --project-root . \
  --action detect-duplication \
  --min-lines 6 \
  --min-tokens 50 \
  --exclude tests/
```

### Analisis de Complejidad

```bash
python scripts/coding/ai/meta/refactoring_opportunities_agent.py \
  --project-root . \
  --action complexity-analysis \
  --threshold-warn 10 \
  --threshold-error 15 \
  --sort-by complexity
```

### Generar Plan de Refactorizacion

```bash
python scripts/coding/ai/meta/refactoring_opportunities_agent.py \
  --project-root . \
  --action generate-plan \
  --prioritize-by impact \
  --max-items 10 \
  --sprint-capacity 40h
```

## Parametros

- `--project-root`: Directorio raiz del proyecto
- `--scan-path`: Ruta especifica a escanear
- `--action`: Accion (scan, detect-duplication, complexity-analysis, generate-plan)
- `--check-all`: Verificar todos los code smells
- `--min-severity`: Severidad minima (low, medium, high, critical)
- `--min-lines`: Minimo de lineas para duplicacion
- `--min-tokens`: Minimo de tokens para duplicacion
- `--threshold-warn`: Umbral de advertencia para complejidad
- `--threshold-error`: Umbral de error para complejidad
- `--prioritize-by`: Criterio (impact, effort, risk, frequency)
- `--sprint-capacity`: Capacidad del sprint en horas

## Salida

### Reporte de Oportunidades

```markdown
# Refactoring Opportunities Report
Project: IACT Call Center
Scan Date: 2025-11-15
Files Analyzed: 156
Issues Found: 47

## Critical Issues (5)

### 1. God Object
File: api/services/notification_service.py
Class: NotificationManager
Lines: 200-650 (450 lines)
Severity: CRITICAL
Complexity: 45 (threshold: 15)

Description:
Class has 18 methods and handles multiple responsibilities:
- Email notification
- SMS notification
- Push notification
- Logging
- Retry logic
- Rate limiting
- Template management

Recommendation:
Extract separate classes:
- EmailNotificationService
- SMSNotificationService
- PushNotificationService
- NotificationLogger
- NotificationRateLimiter
- NotificationTemplateManager

Estimated Effort: 8-12 hours
Impact: HIGH (improves testability, maintainability)
Risk: MEDIUM (widely used class)

### 2. Duplicate Code
Files: 
- api/authentication/jwt_handler.py (lines 45-78)
- api/authentication/oauth_handler.py (lines 120-153)
Similarity: 95% (34 lines)
Severity: CRITICAL

Description:
Token validation logic duplicated in two authentication handlers

Recommendation:
Extract to shared TokenValidator class or mixin

Estimated Effort: 2-3 hours
Impact: HIGH (reduces maintenance burden)
Risk: LOW (well-tested area)

## High Priority Issues (12)

### 3. Long Method
File: api/reports/generator.py
Method: generate_call_report
Lines: 89-245 (156 lines)
Complexity: 28
Severity: HIGH

Description:
Method handles data fetching, filtering, aggregation, formatting, and export

Recommendation:
Apply Extract Method refactoring:
- extract_call_data()
- filter_by_criteria()
- aggregate_metrics()
- format_report()
- export_to_format()

Estimated Effort: 4-6 hours
Impact: MEDIUM
Risk: LOW

### 4. Feature Envy
File: api/users/profile_manager.py
Method: update_user_profile
Severity: HIGH

Description:
Method uses 8 attributes/methods from User class but only 2 from ProfileManager

Recommendation:
Move method to User class or create ProfileService

Estimated Effort: 1-2 hours
Impact: MEDIUM
Risk: LOW

## Medium Priority Issues (18)

[Additional issues...]

## Summary Statistics

| Category | Count | Total Effort |
|----------|-------|--------------|
| Critical | 5 | 32-48h |
| High | 12 | 48-72h |
| Medium | 18 | 36-54h |
| Low | 12 | 12-18h |

## Prioritized Refactoring Plan

### Sprint 1 (Capacity: 40h)
1. Fix God Object in NotificationManager (12h)
2. Remove duplicate authentication code (3h)
3. Refactor generate_call_report method (6h)
4. Fix Feature Envy in profile_manager (2h)
5. Extract common validation logic (4h)

Total: 27h (leaves 13h buffer)

[End of Report]
```

## Herramientas Utilizadas

- **radon**: Complejidad ciclomatica
- **pylint**: Code smells y metricas
- **flake8**: Estilo y calidad
- **bandit**: Seguridad
- **pyflakes**: Codigo muerto
- **jscpd**: Deteccion de duplicacion

## Mejores Practicas

1. **Refactorizar gradualmente**: No todo a la vez
2. **Tests primero**: Asegurar cobertura antes de refactorizar
3. **Un cambio a la vez**: No mezclar refactorizacion con features
4. **Medir impacto**: Validar mejoras con metricas
5. **Documentar decisiones**: Explicar por que se refactoriza
6. **Code review**: Validar refactorizaciones con equipo
7. **Priorizar alto impacto**: Enfocarse en areas criticas

## Restricciones

- Deteccion automatica puede tener falsos positivos
- Algunas refactorizaciones requieren conocimiento del dominio
- Estimaciones de esfuerzo son aproximadas
- Requiere tests existentes para refactorizar con confianza
- No detecta todos los problemas de diseno

## Ubicacion

Archivo: `scripts/coding/ai/meta/refactoring_opportunities_agent.py`
