---
id: PROCED-GOB-009
tipo: procedimiento
categoria: calidad-codigo
titulo: Procedimiento para Refactorizaciones de Codigo con TDD
version: 1.0.0
fecha_creacion: 2025-11-17
autor: Claude Code Agent
frecuencia_uso: ad-hoc (cuando se requiera refactorización)
alcance: Refactorizaciones de calidad en codebase Python/JavaScript
---

# PROCED-GOB-009: Procedimiento para Refactorizaciones de Codigo con TDD

## 1. Proposito

Establecer un proceso estandarizado para ejecutar refactorizaciones de codigo usando metodologia Test-Driven Development (TDD), garantizando zero regresiones funcionales y manteniendo calidad del codigo.

## 2. Alcance

**Aplica a:**
- Refactorizaciones de calidad (mejoras sin cambio funcional)
- Modernizacion de sintaxis (PEP 585, ES6+, etc.)
- Extraccion de constantes y eliminacion de magic numbers
- Reorganizacion de codigo sin cambio de comportamiento

**NO aplica a:**
- Nuevas funcionalidades (usar proceso de desarrollo normal)
- Cambios breaking que modifican APIs publicas
- Hotfixes urgentes de produccion

## 3. Roles y Responsabilidades

**Desarrollador/Agente:**
- Ejecutar el procedimiento completo
- Generar evidencias en cada fase
- Ejecutar rollback si es necesario

**Tech Lead:**
- Aprobar refactorizaciones propuestas
- Revisar analisis de impacto

**QA:**
- Validar que tests pasan
- Verificar evidencias completas

## 4. Prerequisitos

Antes de iniciar refactorizacion:
- [ ] Tests automatizados existen (o crear smoke tests basicos)
- [ ] Rama de desarrollo limpia y actualizada
- [ ] Version de runtime compatible (Python 3.9+, Node 16+, etc.)
- [ ] Backup strategy definida (tag o branch)
- [ ] Commits identificados con cambios a aplicar

## 5. Fases del Procedimiento

### FASE 1: ANALISIS (30-60 min)

**Objetivo:** Entender cambios y crear plan ejecutable

**Pasos:**
1. Identificar commits con refactorizaciones deseadas
2. Analizar impacto:
   - Archivos afectados
   - Lineas modificadas
   - Tipo de cambios (imports, tipos, valores)
   - Riesgos potenciales
3. Crear documento ANALISIS-REFACTORIZACIONES-YYYY-MM-DD.md con:
   - Estado actual del codigo
   - Refactorizaciones pendientes (detalle por commit)
   - Analisis de compatibilidad
   - Matriz de riesgos
   - Metricas (lineas, archivos, tiempo estimado)
4. Ubicar en: docs/ai/refactorizaciones/QA-REFACTOR-XXX-NNN/

**Salidas:**
- Documento de analisis completo
- Identificacion clara de cambios
- Matriz de riesgos documentada

### FASE 2: PLANIFICACION (30-45 min)

**Objetivo:** Crear plan ejecutable con metodologia TDD

**Pasos:**
1. Definir fases del plan (tipicamente 5):
   - Preparacion
   - Refactorizacion(es) con TDD
   - Validacion final
   - Commit y push
2. Crear PLAN-INTEGRACION-REFACTORIZACIONES-YYYY-MM-DD.md con:
   - Metodologia TDD explicita
   - Fases y tareas detalladas
   - Matriz RACI
   - Dependencias entre tareas
   - Estrategia de rollback
   - Criterios de exito
3. Desglosar en tareas individuales (formato TASK-NNN)
4. Cada tarea debe incluir:
   - Tipo TDD: preparacion|red|refactor|green|validate|commit
   - Prerequisitos
   - Pasos de ejecucion con comandos bash exactos
   - Criterios de exito medibles
   - Validaciones especificas
   - Rollback documentado
   - Evidencias requeridas

**Salidas:**
- Plan completo con 10-20 tareas
- Todas las tareas en carpetas individuales con evidencias/
- Tiempo estimado total

### FASE 3: PREPARACION (10-20 min)

**Objetivo:** Crear backup y validar estado inicial

**Tareas tipicas:**
1. TASK-001: Crear backup de seguridad (tag o branch local)
2. TASK-002: Verificar tests existentes y documentar baseline
3. TASK-003: Validar entorno (version runtime, dependencias)

**Criterios de exito:**
- Backup creado exitosamente
- Tests baseline documentados (N tests passing)
- Entorno compatible validado

### FASE 4: REFACTORIZACION CON TDD (40-60 min)

**Objetivo:** Aplicar refactorizaciones usando ciclo TDD estricto

Para CADA refactorizacion:

**TASK-NNN: [TDD-RED] Ejecutar Tests Pre-Refactorizacion**
```bash
pytest <modulo> -v > evidencias/baseline-pre-refactor.log
```
- Establecer baseline de tests (cuantos pasan)
- Documentar estado actual del codigo
- Guardar snapshot del archivo si es necesario

**TASK-NNN+1: [TDD-REFACTOR] Aplicar Refactorizacion**
```bash
git cherry-pick <commit-hash>
# o aplicacion manual si hay conflictos
```
- Aplicar cambios de refactorizacion
- Resolver conflictos si existen
- Validar sintaxis basica

**TASK-NNN+2: [TDD-GREEN] Validar Tests Post-Refactorizacion**
```bash
pytest <modulo> -v > evidencias/tests-post-refactor.log
diff evidencias/baseline-pre-refactor.log evidencias/tests-post-refactor.log
```
- CRITERIO CRITICO: Mismo numero de tests pasando
- Si tests fallan: ROLLBACK INMEDIATO
- Comparar con baseline

**TASK-NNN+3: [TDD-VALIDATE] Validaciones Adicionales**
- Type checking (mypy, pyright, tsc)
- Smoke tests funcionales
- Import checks
- Validaciones especificas del cambio

**Criterios para continuar:**
- Tests: 100% passing (mismo que baseline)
- Validaciones: PASS
- Sin regresiones detectadas

**Criterios para ROLLBACK:**
- Cualquier test que fallo
- Errores de sintaxis o imports
- Regresion funcional detectada

### FASE 5: VALIDACION FINAL (15-25 min)

**Objetivo:** Validacion integral del sistema

**Tareas tipicas:**
1. TASK-NNN: Ejecutar suite COMPLETA de tests (no solo modulo)
2. TASK-NNN+1: Validar imports y sintaxis de todos archivos
3. TASK-NNN+2: Documentar cambios en evidencias consolidadas

**Criterios de exito:**
- Suite completa: 100% passing
- 0 errores sintaxis
- Evidencias consolidadas creadas

### FASE 6: COMMIT Y PUSH (5-10 min)

**Objetivo:** Persistir cambios en repositorio

**Tareas:**
1. TASK-NNN: Commit con mensaje descriptivo
   ```bash
   git commit -m "refactor: <descripcion>

   - Cambio 1 (commit original: abc1234)
   - Cambio 2 (commit original: def5678)
   - Validado con TDD (N tests passing)
   - Zero regresiones funcionales"
   ```
2. TASK-NNN+1: Push a rama remota con retry logic

**Criterios de exito:**
- Commit creado con mensaje convencional
- Push exitoso
- Rama remota actualizada

## 6. Metodologia TDD

### Ciclo TDD para Refactorizaciones:

```
1. RED (Baseline)
   ├── Ejecutar tests existentes
   ├── Documentar cuantos pasan (N tests)
   └── Guardar estado actual

2. REFACTOR (Cambio)
   ├── Aplicar refactorizacion
   ├── Resolver conflictos
   └── Validar sintaxis basica

3. GREEN (Validacion)
   ├── Ejecutar tests nuevamente
   ├── Comparar con baseline
   └── MISMO numero de tests pasando (CRITICO)

4. VALIDATE (Adicional)
   ├── Type checking
   ├── Smoke tests
   └── Validaciones especificas

5. Decision
   ├── Si TODO OK → Continuar
   └── Si FALLO → ROLLBACK INMEDIATO
```

### Principios TDD Aplicados:

1. **Tests primero:** Siempre verificar baseline antes de cambiar
2. **Cambios incrementales:** Una refactorizacion a la vez
3. **Validacion continua:** Tests despues de cada cambio
4. **Rollback rapido:** No continuar si tests fallan
5. **Evidencias obligatorias:** Cada paso documentado

## 7. Gestion de Evidencias

### Estructura de Evidencias:

```
QA-REFACTOR-XXX-NNN/
├── ANALISIS-REFACTORIZACIONES-YYYY-MM-DD.md
├── PLAN-INTEGRACION-REFACTORIZACIONES-YYYY-MM-DD.md
├── INDICE.md
├── TASK-001-nombre/
│   ├── TASK-001-nombre.md
│   └── evidencias/
│       ├── backup-tag-created.log
│       └── commit-hash.txt
├── TASK-002-nombre/
│   └── evidencias/
│       ├── baseline-tests.log
│       └── test-count.txt
└── ...
```

### Evidencias Requeridas por Fase:

**Preparacion:**
- backup-tag-created.log
- baseline-tests.log
- python-version.txt

**Refactorizacion (por cada una):**
- baseline-pre-refactor.log
- refactor-applied.log
- tests-post-refactor.log
- validation-results.log

**Validacion Final:**
- suite-completa-tests.log
- import-validation.log
- CONSOLIDADO-EVIDENCIAS.md

**Commit/Push:**
- commit-message.txt
- commit-hash.txt
- push-result.log

## 8. Estrategia de Rollback

### Rollback por Fase:

**Si falla PREPARACION:**
```bash
# Eliminar tag/branch de backup si existe
git tag -d backup-refactor-YYYY-MM-DD
# o
git branch -d backup-refactor-YYYY-MM-DD
```

**Si falla REFACTORIZACION:**
```bash
# Opcion 1: Revert del commit
git revert <commit-hash>

# Opcion 2: Reset hard a backup
git reset --hard backup-refactor-YYYY-MM-DD

# Opcion 3: Cherry-pick inverso
git cherry-pick --abort  # si en progreso
```

**Si falla VALIDACION FINAL:**
```bash
# Reset a backup completo
git reset --hard backup-refactor-YYYY-MM-DD

# Limpiar working directory
git clean -fd
```

### Criterios para Ejecutar Rollback:

- **INMEDIATO:** Tests fallan despues de refactorizacion
- **INMEDIATO:** Errores de sintaxis o imports
- **INMEDIATO:** Regresion funcional detectada
- **EVALUACION:** Type checker reporta nuevos errores (puede ser falso positivo)

## 9. Riesgos Comunes y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion Primaria | Mitigacion Secundaria |
|--------|-------------|---------|-------------------|---------------------|
| Tests no existen | MEDIA | MEDIO | Crear smoke tests basicos | Validacion manual exhaustiva |
| Runtime incompatible | BAJA | ALTO | Validar version temprano | ABORTAR si incompatible |
| Conflictos cherry-pick | MEDIA | MEDIO | Aplicacion manual con diff | Documentar resolucion |
| Tests fallan post-refactor | BAJA | ALTO | Rollback inmediato | Analizar causa y reintentar |
| Regresion no detectada | BAJA | ALTO | Suite completa + smoke tests | Code review adicional |
| Type checker falsos positivos | MEDIA | BAJO | Validacion manual | Actualizar configuracion |

## 10. Criterios de Exito

Una refactorizacion es exitosa cuando:

**Tecnicos:**
- [ ] Todas las refactorizaciones aplicadas sin conflictos
- [ ] 100% tests passing (mismo que baseline o mejor)
- [ ] 0 regresiones funcionales
- [ ] Type checking: 0 errores nuevos
- [ ] Sintaxis e imports: validados OK

**Proceso:**
- [ ] Metodologia TDD seguida estrictamente
- [ ] Evidencias completas en todas las tareas
- [ ] Rollback strategy ejecutable probada
- [ ] Cada fase cumple criterios de salida

**Persistencia:**
- [ ] Cambios commiteados con mensaje descriptivo
- [ ] Commit pusheado a rama remota
- [ ] Documentacion actualizada si necesario

## 11. Metricas y Reporting

### Metricas a Capturar:

**Codigo:**
- Archivos afectados
- Lineas modificadas
- Commits aplicados
- Tipo de cambios

**Tests:**
- Tests baseline
- Tests post-refactor
- Delta (mejora/regresion)
- Tiempo de ejecucion

**Tiempo:**
- Tiempo estimado vs real
- Tiempo por fase
- Tiempo total

**Calidad:**
- Riesgos identificados
- Riesgos materializados
- Rollbacks ejecutados

### Documento de Cierre:

Al finalizar, crear CONSOLIDADO-EVIDENCIAS.md con:
- Resumen ejecutivo
- Refactorizaciones aplicadas
- Estado final de tests
- Problemas encontrados y resoluciones
- Metricas completas
- Lecciones aprendidas

## 12. Frecuencia de Uso

**Ad-hoc:** Cuando se requiera refactorizar codigo

**Triggers comunes:**
- Actualizacion de version de runtime (Python 3.9 → 3.11)
- Adopcion de nuevos estandares (PEP 585, ES2022)
- Code review detecta magic numbers o code smells
- Consolidacion de trabajo de multiples ramas
- Mejora de mantenibilidad identificada

## 13. Herramientas Recomendadas

**Testing:**
- pytest (Python)
- jest/vitest (JavaScript)
- unittest (Python stdlib)

**Type Checking:**
- mypy (Python)
- pyright (Python)
- tsc (TypeScript)

**Validacion:**
- python -m py_compile (syntax)
- eslint (JavaScript)
- ruff/flake8 (Python linting)

**Git:**
- git cherry-pick (aplicar commits)
- git revert (rollback)
- git tag (backup)

## 14. Plantillas de Referencia

**Analisis:** docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/ANALISIS-REFACTORIZACIONES-2025-11-17.md

**Plan:** docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/PLAN-INTEGRACION-REFACTORIZACIONES-2025-11-17.md

**Tareas:** docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-NNN-*/

## 15. Historial de Cambios

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-11-17 | Creacion inicial basada en QA-REFACTOR-MCP-002 |

## 16. Referencias

- **Caso de estudio:** QA-REFACTOR-MCP-002 (2 refactorizaciones, 16 tareas, 100% exitoso)
- **PEP 585:** Type Hinting Generics In Standard Collections
- **TDD:** Test-Driven Development (Kent Beck)
- **Conventional Commits:** https://www.conventionalcommits.org/

---

**Procedimiento creado:** 2025-11-17
**Ultima revision:** 2025-11-17
**Próxima revisión:** 2026-11-17 (o después de 5 usos)
**Mantenedor:** Tech Lead Team
