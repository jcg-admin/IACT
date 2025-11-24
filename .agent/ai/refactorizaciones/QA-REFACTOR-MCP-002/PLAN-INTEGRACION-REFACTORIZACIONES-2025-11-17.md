---
id: PLAN-REFACTOR-MCP-002
tipo: plan
categoria: refactorizacion-codigo
titulo: Plan de Integracion de Refactorizaciones MCP Registry
fecha: 2025-11-17
autor: Claude Code Agent
rama: claude/fix-branch-issues-013FpGsYZUySbBL6bsMbhBf2
metodologia: TDD
---

# PLAN DE INTEGRACION DE REFACTORIZACIONES MCP REGISTRY

## 1. Resumen Ejecutivo

Este plan define la estrategia de integracion de dos refactorizaciones de calidad pendientes en el archivo `scripts/coding/ai/mcp/registry.py` del proyecto IACT, utilizando metodologia Test-Driven Development (TDD) para garantizar cero regresiones funcionales.

Las refactorizaciones a integrar son:
1. Extraccion de constante Playwright (commit 0d1e1f2)
2. Modernizacion de type annotations a PEP 585 (commit 2ca3d25)

Ambas refactorizaciones son mejoras de calidad de codigo sin impacto funcional, previamente validadas en ramas de trabajo paralelas. La aplicacion seguira el ciclo TDD riguroso: RED (tests existentes) → REFACTOR (cambios) → GREEN (validacion) → VALIDATE (verificaciones adicionales).

**Duracion estimada total:** 70 minutos (1h 10min)
**Criterio de exito:** 100% tests pasando + 0 regresiones + cambios persistidos en repositorio

## 2. Objetivos

- Integrar refactorizacion de constante Playwright (commit 0d1e1f2)
- Integrar refactorizacion PEP 585 type annotations (commit 2ca3d25)
- Mantener 100% de tests pasando
- Zero regresiones funcionales
- Documentar evidencias completas de cada fase
- Persistir cambios en repositorio remoto

## 3. Metodologia: Test-Driven Development (TDD)

### Ciclo TDD para cada refactorizacion:

1. **RED:** Verificar tests existentes (deben pasar con codigo actual)
   - Ejecutar suite de tests MCP
   - Documentar baseline de estado exitoso
   - Identificar coberturas existentes

2. **REFACTOR:** Aplicar cambios de refactorizacion
   - Cherry-pick commit especifico
   - Resolver conflictos si existen
   - Verificar sintaxis basica

3. **GREEN:** Validar que tests siguen pasando
   - Ejecutar misma suite de tests
   - Comparar resultados con baseline
   - Confirmar 100% passing

4. **VALIDATE:** Validaciones adicionales (type checking, smoke tests)
   - Type checking con mypy/pyright
   - Smoke tests de integracion
   - Validacion manual de cambios criticos

### Principios TDD aplicados:

- **Tests primero:** Nunca refactorizar sin verificar tests antes
- **Cambios incrementales:** Una refactorizacion a la vez
- **Validacion continua:** Tests despues de cada cambio
- **Rollback rapido:** Revertir inmediatamente si tests fallan
- **Evidencias obligatorias:** Documentar cada paso del ciclo

## 4. Fases del Plan

### FASE 1 - PREPARACION (15 min)

**Objetivo:** Crear backup y verificar estado inicial

**Tareas:**

- **TASK-001:** Crear backup de seguridad local
  - Crear tag git de respaldo
  - Verificar que tag se creo correctamente
  - Documentar hash del commit actual
  - **Estimacion:** 3 min

- **TASK-002:** Verificar tests existentes MCP
  - Buscar tests relacionados a MCP registry
  - Ejecutar tests encontrados
  - Documentar estado actual (passing/failing)
  - Si no hay tests, crear smoke test basico
  - **Estimacion:** 7 min

- **TASK-003:** Validar entorno Python (3.9+)
  - Verificar version de Python en entorno actual
  - Confirmar compatibilidad con PEP 585
  - Validar que type checker esta disponible
  - **Estimacion:** 5 min

**Criterios de salida:**
- Backup creado exitosamente con tag git
- Tests MCP ejecutados y estado documentado (o smoke test creado)
- Python version >= 3.9 confirmado
- Evidencias en carpeta TASK-001-preparacion/evidencias/

**Riesgos identificados:**
- Tests no existentes (MITIGACION: crear smoke test basico)
- Python < 3.9 (MITIGACION: validacion temprana, bloqueo de plan)

---

### FASE 2 - REFACTORIZACION PLAYWRIGHT CONSTANT (20 min)

**Objetivo:** Integrar extraccion de constante Playwright con TDD

**Tareas:**

- **TASK-004:** [TDD-RED] Ejecutar tests pre-refactorizacion
  - Ejecutar suite de tests MCP
  - Documentar resultados baseline
  - Capturar output completo
  - **Estimacion:** 4 min

- **TASK-005:** [TDD-REFACTOR] Aplicar commit 0d1e1f2 (Playwright constant)
  - Cherry-pick commit 0d1e1f2
  - Resolver conflictos si existen
  - Verificar que cambios aplican correctamente
  - Validar sintaxis basica (imports, indentacion)
  - **Estimacion:** 6 min

- **TASK-006:** [TDD-GREEN] Validar tests post-refactorizacion
  - Ejecutar misma suite de tests
  - Comparar con baseline de TASK-004
  - Confirmar 100% passing
  - **Estimacion:** 5 min

- **TASK-007:** [TDD-VALIDATE] Smoke test de integracion
  - Validar interpolacion de string manualmente
  - Verificar valor final de constante
  - Ejecutar smoke test de MCP registry
  - **Estimacion:** 5 min

**Criterios de salida:**
- Tests MCP: 100% passing (mismo estado que baseline)
- Constante PLAYWRIGHT_MCP_VERSION creada en linea 18
- String interpolation funcionando: f"@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}"
- Valor final identico: "@playwright/mcp@0.0.40"
- Evidencias en carpeta TASK-004-playwright/evidencias/

**Cambios esperados:**
- Lineas agregadas: 16-18 (constante + comentarios)
- Linea modificada: 106 (uso de constante con f-string)
- Total impacto: +4 lineas, 1 modificada

**Estrategia de rollback:**
```bash
git revert <commit-hash-playwright>  # < 1 min
```

---

### FASE 3 - REFACTORIZACION PEP 585 (20 min)

**Objetivo:** Integrar modernizacion type annotations con TDD

**Tareas:**

- **TASK-008:** [TDD-RED] Ejecutar tests pre-refactorizacion
  - Ejecutar suite de tests MCP
  - Documentar resultados baseline
  - Capturar output completo
  - **Estimacion:** 4 min

- **TASK-009:** [TDD-REFACTOR] Aplicar commit 2ca3d25 (PEP 585)
  - Cherry-pick commit 2ca3d25
  - Resolver conflictos si existen
  - Verificar que imports se actualizan correctamente
  - Validar sintaxis de nuevos tipos (dict, no Dict)
  - **Estimacion:** 6 min

- **TASK-010:** [TDD-GREEN] Validar tests post-refactorizacion
  - Ejecutar misma suite de tests
  - Comparar con baseline de TASK-008
  - Confirmar 100% passing
  - **Estimacion:** 5 min

- **TASK-011:** [TDD-VALIDATE] Type checking con mypy/pyright
  - Ejecutar mypy en registry.py
  - Ejecutar pyright si disponible
  - Verificar 0 errores de tipos
  - Validar que imports antiguos (Dict, Mapping) fueron removidos
  - **Estimacion:** 5 min

**Criterios de salida:**
- Tests MCP: 100% passing (mismo estado que baseline)
- Type annotations modernizadas: dict[str, str] en lugar de Dict[str, str]
- Imports removidos: Dict, Mapping de typing
- Type checker: 0 errores (mypy/pyright)
- Evidencias en carpeta TASK-008-pep585/evidencias/

**Cambios esperados:**
- Linea 6: from typing import Dict, Mapping, Tuple → from typing import Tuple
- 11 ocurrencias de Dict/Mapping reemplazadas por dict
- Lineas modificadas: 6, 24, 26, 27, 43, 45, 46, 66, 68, 73, 129

**Estrategia de rollback:**
```bash
git revert <commit-hash-pep585>  # < 1 min
```

---

### FASE 4 - VALIDACION FINAL (10 min)

**Objetivo:** Validacion integral del sistema

**Tareas:**

- **TASK-012:** Ejecutar suite completa de tests
  - Ejecutar todos los tests del proyecto
  - Verificar que no hay regresiones en otros modulos
  - Documentar resultados completos
  - **Estimacion:** 5 min

- **TASK-013:** Validar imports y sintaxis
  - Verificar que no hay imports rotos
  - Validar sintaxis Python completa
  - Confirmar que archivo se puede importar
  - **Estimacion:** 2 min

- **TASK-014:** Documentar cambios en evidencias
  - Consolidar evidencias de todas las fases
  - Crear resumen de validaciones exitosas
  - Documentar metricas finales
  - **Estimacion:** 3 min

**Criterios de salida:**
- Todos los tests del proyecto pasando
- 0 errores de sintaxis o imports
- Archivo registry.py importable sin errores
- Evidencias completas generadas en TASK-012-validacion/evidencias/

**Validaciones finales:**
- Suite completa de tests: PASS
- Import check: SUCCESS
- Syntax validation: OK
- Smoke test integral: PASS

---

### FASE 5 - COMMIT Y PUSH (5 min)

**Objetivo:** Persistir cambios en repositorio

**Tareas:**

- **TASK-015:** Commit de refactorizaciones
  - Crear commit descriptivo con ambas refactorizaciones
  - Incluir referencia a commits originales
  - Documentar cambios en mensaje de commit
  - **Estimacion:** 2 min

- **TASK-016:** Push a rama remota
  - Push a rama claude/fix-branch-issues-013FpGsYZUySbBL6bsMbhBf2
  - Verificar que push fue exitoso
  - Confirmar que commit aparece en remoto
  - **Estimacion:** 3 min

**Criterios de salida:**
- Commit creado con mensaje descriptivo siguiendo formato:
  ```
  refactor(mcp): integrate Playwright constant and PEP 585 type annotations

  - Extract Playwright version to PLAYWRIGHT_MCP_VERSION constant
  - Modernize type annotations to PEP 585 style (dict vs Dict)

  Cherry-picked from:
  - 0d1e1f2: refactor: extract Playwright MCP version to constant
  - 2ca3d25: refactor: modernize type annotations to PEP 585 style

  Validated with TDD methodology:
  - All tests passing
  - Type checker clean
  - Zero functional regressions
  ```
- Push exitoso sin errores
- Commit visible en repositorio remoto

---

## 5. Matriz RACI

| Tarea | Responsable | Aprobador | Consultado | Informado |
|-------|-------------|-----------|------------|-----------|
| TASK-001: Crear backup | Agente Claude | Usuario | N/A | Usuario |
| TASK-002: Verificar tests MCP | Agente Claude | Usuario | N/A | Usuario |
| TASK-003: Validar Python | Agente Claude | Usuario | N/A | Usuario |
| TASK-004: TDD-RED Playwright | Agente Claude | Usuario | N/A | Usuario |
| TASK-005: TDD-REFACTOR Playwright | Agente Claude | Usuario | N/A | Usuario |
| TASK-006: TDD-GREEN Playwright | Agente Claude | Usuario | N/A | Usuario |
| TASK-007: TDD-VALIDATE Playwright | Agente Claude | Usuario | N/A | Usuario |
| TASK-008: TDD-RED PEP 585 | Agente Claude | Usuario | N/A | Usuario |
| TASK-009: TDD-REFACTOR PEP 585 | Agente Claude | Usuario | N/A | Usuario |
| TASK-010: TDD-GREEN PEP 585 | Agente Claude | Usuario | N/A | Usuario |
| TASK-011: TDD-VALIDATE PEP 585 | Agente Claude | Usuario | N/A | Usuario |
| TASK-012: Suite completa tests | Agente Claude | Usuario | N/A | Usuario |
| TASK-013: Validar imports | Agente Claude | Usuario | N/A | Usuario |
| TASK-014: Documentar evidencias | Agente Claude | Usuario | N/A | Usuario |
| TASK-015: Commit refactorizaciones | Agente Claude | Usuario | N/A | Usuario |
| TASK-016: Push remoto | Agente Claude | Usuario | N/A | Usuario |

**Leyenda:**
- **R (Responsable):** Ejecuta la tarea
- **A (Aprobador):** Aprueba el resultado
- **C (Consultado):** Proporciona input
- **I (Informado):** Recibe actualizaciones

---

## 6. Dependencias entre Tareas

```
TASK-001 (Backup)
    ↓
TASK-002 (Tests existentes)
    ↓
TASK-003 (Validar Python)
    ↓
    ├─→ TASK-004 (TDD-RED Playwright)
    │       ↓
    │   TASK-005 (TDD-REFACTOR Playwright)
    │       ↓
    │   TASK-006 (TDD-GREEN Playwright)
    │       ↓
    │   TASK-007 (TDD-VALIDATE Playwright)
    │       ↓
    └─→ TASK-008 (TDD-RED PEP 585)
            ↓
        TASK-009 (TDD-REFACTOR PEP 585)
            ↓
        TASK-010 (TDD-GREEN PEP 585)
            ↓
        TASK-011 (TDD-VALIDATE PEP 585)
            ↓
        TASK-012 (Suite completa tests)
            ↓
        TASK-013 (Validar imports)
            ↓
        TASK-014 (Documentar evidencias)
            ↓
        TASK-015 (Commit)
            ↓
        TASK-016 (Push)
```

**Notas sobre dependencias:**
- TASK-001 a TASK-003 son prerequisitos obligatorios
- TASK-004 a TASK-007 (Playwright) deben completarse secuencialmente
- TASK-008 a TASK-011 (PEP 585) deben completarse secuencialmente
- TASK-008 depende de que TASK-007 este completa
- TASK-012 a TASK-016 deben ejecutarse en orden estricto

**Puntos de decision:**
- Despues de TASK-003: Si Python < 3.9, ABORTAR plan
- Despues de TASK-006: Si tests fallan, ROLLBACK Playwright
- Despues de TASK-010: Si tests fallan, ROLLBACK PEP 585
- Despues de TASK-012: Si suite completa falla, ROLLBACK ambas

---

## 7. Estrategia de Rollback

### Por Fase:

**FASE 2 - Rollback Playwright:**
```bash
git revert <commit-hash-playwright>
# Tiempo: < 2 min
# Impacto: Solo revierte constante Playwright
# Tests: Ejecutar suite MCP para confirmar
```

**FASE 3 - Rollback PEP 585:**
```bash
git revert <commit-hash-pep585>
# Tiempo: < 2 min
# Impacto: Solo revierte type annotations
# Tests: Ejecutar suite MCP para confirmar
```

**ROLLBACK TOTAL (ambas refactorizaciones):**
```bash
git reset --hard backup-refactor-mcp-2025-11-17
# Tiempo: < 1 min
# Impacto: Revierte todo a estado inicial
# Uso: Solo si ambas refactorizaciones fallan
```

### Criterios para Rollback:

**Rollback INMEDIATO si:**
- Tests fallan despues de refactorizacion
- Type checker reporta nuevos errores
- Imports rotos o errores de sintaxis
- Cualquier regresion funcional detectada
- Smoke tests fallan

**Rollback OPCIONAL si:**
- Performance degradada significativamente
- Warnings nuevos en CI/CD (evaluar impacto)

**NO hacer rollback si:**
- Solo warnings menores de linter
- Comentarios de estilo
- Documentacion faltante (se puede agregar despues)

### Procedimiento de Rollback:

1. Identificar fase con problema
2. Ejecutar comando de rollback apropiado
3. Verificar que tests pasan despues de rollback
4. Documentar razon del rollback en evidencias
5. Notificar al usuario
6. Analizar causa raiz antes de reintentar

---

## 8. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Severidad | Mitigacion |
|--------|-------------|---------|-----------|-----------|
| Tests no existen | MEDIA | MEDIO | MEDIO | Crear smoke tests basicos en TASK-002 |
| Python < 3.9 | BAJA | ALTO | ALTO | Validar version en TASK-003, ABORTAR si incompatible |
| Type checker no disponible | MEDIA | BAJO | BAJO | Validacion manual de tipos, continuar sin type checker |
| Conflictos en cherry-pick | BAJA | MEDIO | MEDIO | Aplicacion manual de cambios usando diffs del ANALISIS |
| Tests fallan post-refactor | BAJA | ALTO | ALTO | Rollback inmediato + analisis de causa raiz |
| Regresion funcional | MUY BAJA | ALTO | CRITICO | Suite completa de tests + smoke tests + rollback |
| Imports rotos | MUY BAJA | MEDIO | MEDIO | Validacion de imports en TASK-013 + rollback si necesario |
| Performance degradada | MUY BAJA | BAJO | BAJO | Benchmarks basicos (si disponibles) |

### Riesgos detallados:

**RIESGO 1: Tests no existen**
- **Descripcion:** No hay tests unitarios para MCP registry
- **Probabilidad:** MEDIA (40%)
- **Impacto:** MEDIO (dificulta validacion TDD)
- **Mitigacion primaria:** Crear smoke test basico en TASK-002
- **Mitigacion secundaria:** Validacion manual exhaustiva
- **Accion si ocurre:** Crear test que valide:
  - Import exitoso del modulo
  - Creacion de instancia de registry
  - Acceso a atributos basicos

**RIESGO 2: Python < 3.9**
- **Descripcion:** Entorno usa Python version incompatible con PEP 585
- **Probabilidad:** BAJA (20%)
- **Impacto:** ALTO (bloquea FASE 3 completamente)
- **Mitigacion primaria:** Validacion temprana en TASK-003
- **Mitigacion secundaria:** ABORTAR plan, notificar usuario
- **Accion si ocurre:** DETENER plan, solicitar upgrade de Python

**RIESGO 3: Type checker no disponible**
- **Descripcion:** mypy/pyright no instalados en entorno
- **Probabilidad:** MEDIA (30%)
- **Impacto:** BAJO (validacion manual posible)
- **Mitigacion primaria:** Validacion manual de tipos
- **Mitigacion secundaria:** Continuar sin type checker
- **Accion si ocurre:** Documentar ausencia, validar manualmente

**RIESGO 4: Conflictos en cherry-pick**
- **Descripcion:** Cambios en lineas afectadas desde commits originales
- **Probabilidad:** BAJA (15%)
- **Impacto:** MEDIO (requiere resolucion manual)
- **Mitigacion primaria:** Aplicar cambios manualmente usando diffs del ANALISIS
- **Mitigacion secundaria:** Validacion exhaustiva post-resolucion
- **Accion si ocurre:** Resolver conflictos, validar contra diffs originales

---

## 9. Criterios de Exito Global

**El plan se considera exitoso cuando se cumplen TODOS los siguientes criterios:**

### Criterios Tecnicos:
- [ ] 2 refactorizaciones aplicadas exitosamente
- [ ] 100% tests passing (o estado documentado si no hay tests baseline)
- [ ] 0 regresiones funcionales detectadas
- [ ] Type annotations modernizadas a PEP 585 en 11 lineas
- [ ] Constante PLAYWRIGHT_MCP_VERSION extraida y documentada
- [ ] Imports actualizados (Dict, Mapping removidos)
- [ ] Type checker pasa sin errores (si disponible)

### Criterios de Proceso:
- [ ] Metodologia TDD seguida en ambas refactorizaciones
- [ ] Evidencias completas en cada carpeta TASK-NNN-*/evidencias/
- [ ] Backup creado antes de iniciar cambios
- [ ] Cada fase cumple sus criterios de salida

### Criterios de Persistencia:
- [ ] Cambios commiteados con mensaje descriptivo
- [ ] Commit pusheado a rama remota exitosamente
- [ ] Commit visible en repositorio remoto

### Criterios de Calidad:
- [ ] Codigo mas pythonic (PEP 585)
- [ ] Sin magic numbers (constante Playwright)
- [ ] Documentacion inline mejorada
- [ ] Mantenibilidad incrementada

### Metricas de Exito:
- **Tiempo total ejecutado:** <= 90 min (buffer 20 min sobre estimado)
- **Tests passing:** 100% (o baseline documentado)
- **Rollbacks ejecutados:** 0 (ideal)
- **Errores de sintaxis:** 0
- **Warnings criticos:** 0

---

## 10. Tiempo Estimado Total

### Desglose por Fase:

| Fase | Descripcion | Tiempo Estimado | Tareas |
|------|-------------|-----------------|--------|
| **FASE 1** | Preparacion | 15 min | TASK-001 (3min) + TASK-002 (7min) + TASK-003 (5min) |
| **FASE 2** | Playwright Constant | 20 min | TASK-004 (4min) + TASK-005 (6min) + TASK-006 (5min) + TASK-007 (5min) |
| **FASE 3** | PEP 585 Annotations | 20 min | TASK-008 (4min) + TASK-009 (6min) + TASK-010 (5min) + TASK-011 (5min) |
| **FASE 4** | Validacion Final | 10 min | TASK-012 (5min) + TASK-013 (2min) + TASK-014 (3min) |
| **FASE 5** | Commit y Push | 5 min | TASK-015 (2min) + TASK-016 (3min) |
| **TOTAL** | | **70 min** | **16 tareas** |

### Tiempo con Buffer:

- **Tiempo base estimado:** 70 minutos
- **Buffer para imprevistos (30%):** 21 minutos
- **Tiempo total con buffer:** 91 minutos (~1h 30min)

### Escenarios de Tiempo:

**Escenario Ideal (todo sale bien):**
- Tiempo: 60-70 min
- Condiciones: Tests existen, Python 3.9+, no hay conflictos

**Escenario Normal (problemas menores):**
- Tiempo: 70-90 min
- Condiciones: Crear smoke test, resolver conflictos menores

**Escenario Problematico (requiere rollback):**
- Tiempo: 90-120 min
- Condiciones: Rollback de una fase + diagnostico + reintento

---

## 11. Notas Importantes

### Sobre Metodologia TDD:

- Este plan sigue metodologia TDD estricta
- Cada refactorizacion se valida independientemente
- NUNCA refactorizar sin verificar tests primero
- SIEMPRE documentar baseline antes de cambios
- Rollback disponible en cada fase

### Sobre Evidencias:

- Cada TASK debe generar carpeta de evidencias
- Estructura: `TASK-NNN-descripcion/evidencias/`
- Contenido minimo:
  - Capturas de output de comandos ejecutados
  - Resultados de tests
  - Logs de errores (si aplica)
  - Validaciones manuales

### Sobre Regresiones:

- **Zero tolerancia a regresiones funcionales**
- Cualquier test que falle despues de refactorizacion = ROLLBACK
- Validar no solo tests MCP, sino suite completa
- Documentar CUALQUIER cambio de comportamiento

### Sobre Commits:

- Cherry-pick preserva autoria original
- Commit final debe referenciar commits originales
- Mensaje de commit debe ser descriptivo y completo
- Push solo despues de validaciones exitosas

### Sobre Type Checking:

- Type checker NO es bloqueante si no esta disponible
- Validacion manual es aceptable como fallback
- Documentar ausencia de type checker en evidencias

### Sobre Python Version:

- Python 3.9+ es REQUISITO OBLIGATORIO para PEP 585
- Si Python < 3.9: ABORTAR plan, notificar usuario
- NO intentar continuar con version incompatible

### Comandos de Referencia:

**Verificar estado:**
```bash
git status
python --version
pytest --version  # o framework de tests usado
```

**Aplicar refactorizaciones:**
```bash
git cherry-pick 0d1e1f2  # Playwright
git cherry-pick 2ca3d25  # PEP 585
```

**Validaciones:**
```bash
pytest tests/ -v
mypy scripts/coding/ai/mcp/registry.py
python -c "import scripts.coding.ai.mcp.registry"
```

**Rollback:**
```bash
git revert <commit-hash>
git reset --hard backup-refactor-mcp-2025-11-17
```

---

**Documento generado el:** 2025-11-17
**Autor:** Claude Code Agent
**Version:** 1.0
**Estado:** LISTO PARA EJECUCION
**Proximo paso:** Ejecutar FASE 1 - TASK-001
