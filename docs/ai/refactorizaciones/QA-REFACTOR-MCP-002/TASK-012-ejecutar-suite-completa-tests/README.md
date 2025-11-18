---
id: TASK-REFACTOR-MCP-012
tipo: tarea
categoria: validacion-final
titulo: Ejecutar Suite Completa de Tests
fase: FASE_4
prioridad: ALTA
duracion_estimada: 5min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-011]
---

# TASK-REFACTOR-MCP-012: Ejecutar Suite Completa de Tests

**Fase:** FASE 4 - Validacion Final
**Prioridad:** ALTA
**Duracion Estimada:** 5 minutos
**Tipo:** validacion-final
**Responsable:** Agente Claude
**Estado:** PENDIENTE
**Dependencias:** TASK-REFACTOR-MCP-011 (TDD-VALIDATE Type Checking)

---

## Objetivo

Ejecutar la suite completa de tests del proyecto (no solo tests MCP) para validar que las refactorizaciones aplicadas NO introducen regresiones en otros modulos o componentes del sistema.

---

## Prerequisitos

- [ ] TASK-REFACTOR-MCP-011 completada (type checking validado)
- [ ] Tests MCP pasando (validado en TASK-010)
- [ ] Refactorizaciones Playwright y PEP 585 aplicadas
- [ ] pytest disponible en entorno

---

## Pasos de Validacion

### Paso 1: Verificar Estado del Sistema

```bash
# Verificar commits aplicados
echo "=== Ultimos 3 commits ==="
git log --oneline -3

# Verificar que no hay cambios pendientes
echo ""
echo "=== Git status ==="
git status

# Verificar rama actual
echo ""
echo "=== Rama actual ==="
git branch --show-current
```

**Validaciones:**
- [ ] Commit PEP 585 (2ca3d25) aplicado
- [ ] Commit Playwright (0d1e1f2) aplicado (si ya se ejecuto FASE 2)
- [ ] Working directory limpio
- [ ] Rama: claude/fix-branch-issues-013FpGsYZUySbBL6bsMbhBf2

### Paso 2: Descubrir Suite de Tests Completa

```bash
# Descubrir todos los tests del proyecto
echo "=== Descubrir tests disponibles ==="
pytest --collect-only -q

# Contar total de tests
echo ""
echo "=== Total de tests en el proyecto ==="
pytest --collect-only -q | tail -1
```

**Documentar:**
- Total de tests encontrados: ________
- Distribución por directorio/modulo
- Tests de MCP incluidos en total

### Paso 3: Ejecutar Suite Completa de Tests

```bash
# Ejecutar TODOS los tests del proyecto
pytest -v --tb=short

# Capturar exit code
echo "Suite completa exit code: $?"
```

**Resultado Esperado:**
- Exit code: 0 (todos los tests pasan)
- 0 tests failed
- Tests passed: [documentar numero total]
- Tests skipped: [documentar si aplica]

**IMPORTANTE:**
- Esta es la validacion mas critica
- Cualquier fallo indica regresion potencial
- Comparar con estado pre-refactorizacion si posible

### Paso 4: Ejecutar Tests por Categoria (si suite muy grande)

```bash
# Tests de AI/MCP
echo "=== Tests AI/MCP ==="
pytest scripts/coding/tests/ai/mcp/ -v

# Tests de scripts/coding (si existen otros)
echo ""
echo "=== Tests de scripts/coding ==="
pytest scripts/coding/tests/ -v

# Tests del proyecto general (si existen)
echo ""
echo "=== Tests del proyecto ==="
pytest tests/ -v 2>&1 || echo "No hay directorio tests/ en raiz"
```

**Documentar Resultados por Categoria:**
- AI/MCP: __ passed, __ failed, __ skipped
- scripts/coding: __ passed, __ failed, __ skipped
- Proyecto general: __ passed, __ failed, __ skipped

### Paso 5: Validar Cobertura de Tests (si coverage disponible)

```bash
# Verificar si coverage esta instalado
which coverage && coverage --version || echo "coverage NO disponible"

# Ejecutar tests con cobertura (si disponible)
if which coverage > /dev/null 2>&1; then
  coverage run -m pytest -v
  coverage report -m scripts/coding/ai/mcp/registry.py
fi
```

**Documentar Cobertura (si disponible):**
- Cobertura de registry.py: ___%
- Lineas cubiertas: ___
- Lineas no cubiertas: ___

**NOTA:** Cobertura NO es bloqueante, es informativa

### Paso 6: Ejecutar Tests con Diferentes Niveles de Verbosidad

```bash
# Tests con output minimo (summary)
echo "=== Summary output ==="
pytest --tb=no -q

# Tests con output detallado (failures only)
echo ""
echo "=== Detailed failures (if any) ==="
pytest --tb=long -v --maxfail=1 || true
```

**Validaciones:**
- Summary: Todos pasan
- Si hay fallos: Documentar primer fallo detalladamente

### Paso 7: Validar Tests en Aislamiento (smoke test)

```bash
# Ejecutar solo tests de registry.py
echo "=== Tests de registry.py (aislados) ==="
pytest scripts/coding/tests/ai/mcp/test_registry.py -v

# Ejecutar solo tests de memory.py
echo ""
echo "=== Tests de memory.py (aislados) ==="
pytest scripts/coding/tests/ai/mcp/test_memory.py -v
```

**Resultado Esperado:**
- test_registry.py: PASS
- test_memory.py: PASS
- No hay dependencias rotas entre tests

---

## Criterios de Exito

- [ ] Suite completa de tests ejecutada exitosamente
- [ ] Exit code: 0 (todos los tests pasan)
- [ ] 0 tests failed
- [ ] 0 regresiones detectadas en otros modulos
- [ ] Tests de MCP incluidos y pasando
- [ ] Tests ejecutables en aislamiento
- [ ] Comportamiento identico a pre-refactorizacion (si baseline disponible)

---

## Checklist de Validacion

### Ejecucion de Tests
- [ ] Suite completa descubierta
- [ ] Total de tests documentado
- [ ] pytest ejecutado sin errores
- [ ] Exit code: 0

### Resultados
- [ ] Tests passed: __ (documentar numero)
- [ ] Tests failed: 0
- [ ] Tests skipped: __ (documentar si aplica)
- [ ] Tests errors: 0

### Validaciones por Categoria
- [ ] Tests AI/MCP: PASS
- [ ] Tests scripts/coding: PASS
- [ ] Tests proyecto general: PASS / N/A

### Regresiones
- [ ] 0 regresiones en modulos no modificados
- [ ] 0 tests que pasaban antes y fallan ahora
- [ ] Comportamiento funcional identico

### Aislamiento
- [ ] test_registry.py ejecutable aislado: PASS
- [ ] test_memory.py ejecutable aislado: PASS
- [ ] No hay dependencias rotas

---

## Evidencias a Capturar

**Logs a Guardar en evidencias/:**

1. `01-system-status.txt`: Estado del sistema pre-tests
2. `02-discover-tests.txt`: Descubrimiento de tests completos
3. `03-suite-completa-output.txt`: Output de suite completa
4. `04-tests-por-categoria.txt`: Tests por categoria/modulo
5. `05-coverage-report.txt`: Reporte de cobertura (si disponible)
6. `06-tests-verbosity-summary.txt`: Summary con diferentes verbosidades
7. `07-tests-aislados.txt`: Tests ejecutados en aislamiento

**Comandos para Capturar Evidencias:**

```bash
cd /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-012-ejecutar-suite-completa-tests/evidencias/

# Estado del sistema
{
  echo "=== Ultimos 3 commits ==="
  git log --oneline -3
  echo ""
  echo "=== Git status ==="
  git status
  echo ""
  echo "=== Rama actual ==="
  git branch --show-current
} > 01-system-status.txt 2>&1

# Descubrir tests
{
  echo "=== Descubrir tests ==="
  pytest --collect-only -q
  echo ""
  echo "=== Total ==="
  pytest --collect-only -q | tail -1
} > 02-discover-tests.txt 2>&1

# Suite completa
pytest -v --tb=short > 03-suite-completa-output.txt 2>&1
echo "Exit code: $?" >> 03-suite-completa-output.txt

# Tests por categoria
{
  echo "=== Tests AI/MCP ==="
  pytest scripts/coding/tests/ai/mcp/ -v
  echo ""
  echo "=== Tests scripts/coding ==="
  pytest scripts/coding/tests/ -v
  echo ""
  echo "=== Tests proyecto ==="
  pytest tests/ -v 2>&1 || echo "No hay directorio tests/ en raiz"
} > 04-tests-por-categoria.txt 2>&1

# Cobertura (si disponible)
{
  echo "=== Coverage disponibilidad ==="
  which coverage && coverage --version || echo "coverage NO disponible"
  echo ""
  if which coverage > /dev/null 2>&1; then
    echo "=== Ejecutar con cobertura ==="
    coverage run -m pytest -v
    echo ""
    echo "=== Reporte cobertura registry.py ==="
    coverage report -m scripts/coding/ai/mcp/registry.py
  fi
} > 05-coverage-report.txt 2>&1

# Verbosidad
{
  echo "=== Summary ==="
  pytest --tb=no -q
  echo ""
  echo "=== Failures detallados (if any) ==="
  pytest --tb=long -v --maxfail=1 || true
} > 06-tests-verbosity-summary.txt 2>&1

# Tests aislados
{
  echo "=== test_registry.py ==="
  pytest scripts/coding/tests/ai/mcp/test_registry.py -v
  echo ""
  echo "=== test_memory.py ==="
  pytest scripts/coding/tests/ai/mcp/test_memory.py -v
} > 07-tests-aislados.txt 2>&1
```

---

## Acciones Correctivas

**Si suite completa falla (exit code != 0):**
1. DETENER inmediatamente
2. Identificar cual test fallo
3. Determinar si test esta en modulo MCP o en otro modulo
4. Analizar si fallo es regresion o problema pre-existente
5. Si regresion: ROLLBACK ambas refactorizaciones
6. Si problema pre-existente: documentar y continuar

**Si solo tests de MCP fallan:**
1. Revisar TASK-010 para confirmar que pasaban antes
2. Analizar que cambio entre TASK-010 y TASK-012
3. Si es regresion nueva: ROLLBACK PEP 585
4. Documentar fallo detalladamente

**Si tests de otros modulos fallan:**
1. Verificar si tests fallaban antes de refactorizaciones
2. Determinar si refactorizaciones pueden haber causado fallo
3. Si NO hay relacion: documentar como problema pre-existente
4. Si HAY relacion: ROLLBACK ambas refactorizaciones

**Si hay fallos intermitentes (flaky tests):**
1. Ejecutar tests multiples veces (3-5 iteraciones)
2. Documentar patron de fallos
3. Si flaky era pre-existente: documentar y continuar
4. Si flaky es nuevo: ROLLBACK y analizar

**Si cobertura disminuye significativamente:**
1. Comparar con baseline (si disponible)
2. Analizar que lineas perdieron cobertura
3. Si perdida es menor (<5%): documentar, NO rollback
4. Si perdida es mayor (>=5%): investigar causa

---

## Estrategia de Rollback

**Rollback TOTAL (ambas refactorizaciones) si:**
- Tests de otros modulos fallan por regresion
- Tests de MCP fallan por regresion
- Errores criticos detectados
- Comportamiento funcional alterado

**Comando de Rollback TOTAL:**
```bash
# Opcion 1: Reset a backup tag
git reset --hard backup-refactor-mcp-2025-11-17

# Opcion 2: Revert commits individuales
git revert <commit-pep585>
git revert <commit-playwright>

# Validar que sistema vuelve a estado estable
pytest -v

# Tiempo estimado: < 2 minutos
```

**Rollback PARCIAL (solo PEP 585) si:**
- Solo tests relacionados a tipos fallan
- Playwright OK pero PEP 585 causa problemas

**Comando de Rollback PARCIAL:**
```bash
# Revertir solo PEP 585
git revert <commit-pep585>

# Validar tests
pytest -v

# Tiempo estimado: < 1 minuto
```

**Post-Rollback:**
1. Ejecutar suite completa nuevamente
2. Confirmar que todos los tests pasan
3. Documentar razon del rollback
4. Analizar causa raiz
5. Notificar al usuario

---

## Notas

- Esta es la validacion MAS CRITICA del plan
- Suite completa asegura 0 regresiones en todo el sistema
- No solo tests MCP, sino TODOS los tests del proyecto
- Cualquier fallo debe ser investigado exhaustivamente
- Fallos pre-existentes NO son bloqueantes (documentar)
- Fallos nuevos (regresiones) SON bloqueantes (ROLLBACK)
- Cobertura es informativa, NO bloqueante

**Diferencia con TASK-010:**
- TASK-010: Solo tests MCP
- TASK-012: TODOS los tests del proyecto
- TASK-012 es validacion integral del sistema

**Contexto:**
- Refactorizaciones aplicadas: Playwright + PEP 585
- Archivos modificados: scripts/coding/ai/mcp/registry.py
- Cambios totales: ~26 lineas (16 Playwright + 22 PEP 585)
- Expected: 0 impacto funcional

**Siguiente paso:**
- Si tests pasan: TASK-013 (Validar imports)
- Si tests fallan: ROLLBACK y analisis de causa raiz

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

**Tiempo de ejecucion de tests:** __ segundos

---

## Checklist de Finalizacion

- [ ] Estado del sistema verificado
- [ ] Suite completa descubierta
- [ ] Total de tests documentado: __
- [ ] Suite completa ejecutada: PASS
- [ ] Exit code: 0
- [ ] Tests passed: __ (total)
- [ ] Tests failed: 0
- [ ] Tests por categoria validados
- [ ] Cobertura verificada (si disponible)
- [ ] Tests aislados ejecutados: PASS
- [ ] 0 regresiones detectadas
- [ ] Evidencias capturadas en evidencias/
- [ ] Listo para TASK-013 (Validar imports)
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
