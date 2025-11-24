---
id: TASK-REFACTOR-MCP-010
tipo: tarea
categoria: tdd-green
titulo: Validar Tests Post-PEP 585
fase: FASE_3
prioridad: ALTA
duracion_estimada: 5min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-009]
---

# TASK-REFACTOR-MCP-010: [TDD-GREEN] Validar Tests Post-PEP 585

**Fase:** FASE 3 - Refactorizacion PEP 585
**Prioridad:** ALTA
**Duracion Estimada:** 5 minutos
**Tipo:** tdd-green
**Responsable:** Agente Claude
**Estado:** PENDIENTE
**Dependencias:** TASK-REFACTOR-MCP-009 (TDD-REFACTOR PEP 585)

---

## Objetivo

Validar que los tests MCP siguen pasando despues de aplicar la refactorizacion PEP 585, confirmando que la modernizacion de type annotations NO introduce regresiones funcionales.

---

## Prerequisitos

- [ ] TASK-REFACTOR-MCP-009 completada (commit PEP 585 aplicado)
- [ ] Baseline de tests documentada en TASK-008
- [ ] Sintaxis Python validada en refactorizacion
- [ ] No hay cambios pendientes en working directory

---

## Pasos de Validacion

### Paso 1: Verificar Estado Post-Refactorizacion

```bash
# Verificar que commit PEP 585 esta aplicado
git log --oneline -1

# Verificar que no hay cambios pendientes
git status

# Verificar que archivo fue modificado
git diff HEAD~1 HEAD --name-only
```

**Validaciones:**
- [ ] Ultimo commit es refactorizacion PEP 585
- [ ] Working directory limpio
- [ ] scripts/coding/ai/mcp/registry.py fue modificado

### Paso 2: Ejecutar Suite de Tests MCP (misma que TASK-008)

```bash
# Ejecutar tests MCP con verbose output
pytest scripts/coding/tests/ai/mcp/ -v --tb=short

# Capturar exit code
echo "Tests exit code: $?"
```

**Resultado Esperado:**
- Exit code: 0 (todos los tests pasan)
- Tests passed: [mismo numero que TASK-008]
- Tests failed: 0
- Tests skipped: [mismo numero que TASK-008]

### Paso 3: Comparar con Baseline de TASK-008

```bash
# Leer baseline de TASK-008
echo "=== BASELINE (TASK-008) ==="
cat /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-008-tdd-red-pre-pep585/evidencias/01-baseline-tests-mcp.txt

echo ""
echo "=== ACTUAL (TASK-010) ==="
# Output actual ya capturado en paso anterior
```

**Analisis de Comparacion:**

| Metrica | TASK-008 (Baseline) | TASK-010 (Actual) | Status |
|---------|---------------------|-------------------|--------|
| Tests passed | __ | __ | [ ] OK / [ ] FAIL |
| Tests failed | __ | __ | [ ] OK / [ ] FAIL |
| Tests skipped | __ | __ | [ ] OK / [ ] FAIL |
| Total tests | __ | __ | [ ] OK / [ ] FAIL |
| Exit code | 0 | __ | [ ] OK / [ ] FAIL |

**Criterio de Exito:** TODAS las metricas deben ser IDENTICAS

### Paso 4: Validar Tests Individuales (si disponibles)

```bash
# Listar tests encontrados
pytest scripts/coding/tests/ai/mcp/ --collect-only

# Ejecutar tests individuales con maxima verbosidad
pytest scripts/coding/tests/ai/mcp/test_registry.py -vv
pytest scripts/coding/tests/ai/mcp/test_memory.py -vv
```

**Documentar Resultados:**
- test_registry.py: __ passed, __ failed, __ skipped
- test_memory.py: __ passed, __ failed, __ skipped

### Paso 5: Verificar Imports en Ejecucion

```bash
# Validar que registry.py se puede importar sin errores
python3 -c "import sys; sys.path.insert(0, 'scripts/coding'); from ai.mcp import registry; print('Import SUCCESS')"

# Validar que clases/funciones son accesibles
python3 -c "import sys; sys.path.insert(0, 'scripts/coding'); from ai.mcp.registry import MCPRegistry; print('MCPRegistry import SUCCESS')" 2>&1 || echo "MCPRegistry no exportado directamente"
```

**Resultado Esperado:**
- [ ] Import de modulo: SUCCESS
- [ ] Sin errores de importacion
- [ ] Sin warnings de deprecation

### Paso 6: Smoke Test Funcional

```bash
# Crear smoke test basico para validar funcionalidad core
python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts/coding')

try:
    from ai.mcp import registry
    print("✓ Module imported")

    # Verificar que type annotations no afectan runtime
    # (PEP 585 es compatible en runtime con Python 3.9+)
    print("✓ Module loaded successfully")
    print("SMOKE TEST: PASS")
except Exception as e:
    print(f"✗ Error: {e}")
    print("SMOKE TEST: FAIL")
    sys.exit(1)
EOF
```

**Resultado Esperado:** SMOKE TEST: PASS

---

## Criterios de Exito

- [ ] Todos los tests MCP pasando (exit code 0)
- [ ] Resultados identicos a baseline TASK-008
- [ ] 0 tests fallando
- [ ] 0 regresiones detectadas
- [ ] Import del modulo exitoso
- [ ] Smoke test funcional: PASS
- [ ] No warnings criticos nuevos

---

## Checklist de Validacion

### Tests MCP
- [ ] pytest ejecutado sin errores
- [ ] Exit code: 0
- [ ] Tests passed: [mismo que baseline]
- [ ] Tests failed: 0
- [ ] Tests skipped: [mismo que baseline]

### Comparacion con Baseline
- [ ] Total tests identico
- [ ] Tests passed identico
- [ ] Tests failed identico (0)
- [ ] Tests skipped identico

### Validaciones Adicionales
- [ ] Import del modulo exitoso
- [ ] Sin errores de importacion
- [ ] Smoke test: PASS
- [ ] Sin warnings criticos

### Estado del Sistema
- [ ] No regresiones funcionales
- [ ] Comportamiento identico a pre-refactorizacion
- [ ] Type annotations funcionando correctamente

---

## Evidencias a Capturar

**Logs a Guardar en evidencias/:**

1. `01-post-refactor-git-status.txt`: Estado git post-refactorizacion
2. `02-tests-mcp-output.txt`: Output completo de pytest
3. `03-baseline-comparison.txt`: Comparacion con baseline TASK-008
4. `04-tests-individual-registry.txt`: Tests de test_registry.py
5. `05-tests-individual-memory.txt`: Tests de test_memory.py
6. `06-import-validation.txt`: Validacion de imports
7. `07-smoke-test.txt`: Output de smoke test funcional

**Comandos para Capturar Evidencias:**

```bash
cd /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-010-tdd-green-tests-post-pep585/evidencias/

# Git status
git log --oneline -1 > 01-post-refactor-git-status.txt 2>&1
git status >> 01-post-refactor-git-status.txt 2>&1
git diff HEAD~1 HEAD --name-only >> 01-post-refactor-git-status.txt 2>&1

# Tests MCP completos
pytest scripts/coding/tests/ai/mcp/ -v --tb=short > 02-tests-mcp-output.txt 2>&1

# Comparacion con baseline
{
  echo "=== BASELINE (TASK-008) ==="
  cat /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-008-tdd-red-pre-pep585/evidencias/01-baseline-tests-mcp.txt
  echo ""
  echo "=== ACTUAL (TASK-010) ==="
  cat 02-tests-mcp-output.txt
} > 03-baseline-comparison.txt 2>&1

# Tests individuales
pytest scripts/coding/tests/ai/mcp/test_registry.py -vv > 04-tests-individual-registry.txt 2>&1
pytest scripts/coding/tests/ai/mcp/test_memory.py -vv > 05-tests-individual-memory.txt 2>&1

# Validacion de imports
{
  echo "=== Import modulo ==="
  python3 -c "import sys; sys.path.insert(0, 'scripts/coding'); from ai.mcp import registry; print('Import SUCCESS')"
  echo ""
  echo "=== Import clases ==="
  python3 -c "import sys; sys.path.insert(0, 'scripts/coding'); from ai.mcp.registry import MCPRegistry; print('MCPRegistry import SUCCESS')" 2>&1 || echo "MCPRegistry no exportado directamente"
} > 06-import-validation.txt 2>&1

# Smoke test
python3 << 'EOF' > 07-smoke-test.txt 2>&1
import sys
sys.path.insert(0, 'scripts/coding')

try:
    from ai.mcp import registry
    print("✓ Module imported")
    print("✓ Module loaded successfully")
    print("SMOKE TEST: PASS")
except Exception as e:
    print(f"✗ Error: {e}")
    print("SMOKE TEST: FAIL")
    sys.exit(1)
EOF
```

---

## Acciones Correctivas

**Si tests fallan (exit code != 0):**
1. DETENER inmediatamente
2. Capturar output completo de pytest
3. Analizar cual test fallo y por que
4. Verificar si es regresion real o problema de entorno
5. Si regresion real: ROLLBACK inmediato
6. Documentar causa raiz del fallo

**Si resultados difieren de baseline:**
1. Analizar diferencias especificas
2. Verificar si son aceptables (ej: warnings menores)
3. Si hay tests adicionales fallando: ROLLBACK
4. Si hay menos tests: investigar causa
5. Documentar cualquier diferencia

**Si import falla:**
1. Verificar que archivo no tiene errores de sintaxis
2. Revisar que PYTHONPATH esta configurado
3. Verificar que type annotations son validas
4. Si error critico: ROLLBACK

**Si smoke test falla:**
1. Revisar traceback completo
2. Verificar que modulo se cargo correctamente
3. Si error de runtime relacionado a tipos: ROLLBACK
4. Documentar error detalladamente

---

## Estrategia de Rollback

**Rollback Inmediato si:**
- Cualquier test falla (exit code != 0)
- Mas tests fallando que en baseline
- Import del modulo falla
- Smoke test falla
- Errores de runtime relacionados a tipos

**Comando de Rollback:**
```bash
# Revertir commit PEP 585
git revert HEAD

# O reset hard si preferible
git reset --hard HEAD~1

# Validar que tests pasan post-rollback
pytest scripts/coding/tests/ai/mcp/ -v

# Tiempo estimado: < 1 minuto
```

**Post-Rollback:**
1. Ejecutar tests para confirmar estado estable
2. Documentar razon del rollback
3. Analizar causa raiz antes de reintentar
4. Notificar al usuario

---

## Notas

- Este es el paso GREEN del ciclo TDD
- Los tests DEBEN pasar igual que en TASK-008 (baseline)
- Zero tolerancia a regresiones funcionales
- Cualquier diferencia debe ser justificada
- PEP 585 NO debe afectar comportamiento en runtime
- Type annotations son solo hints para type checker
- Siguiente paso: Type checking (TASK-011)

**Referencia Baseline:**
- Tarea baseline: TASK-008
- Ubicacion evidencias: TASK-008-tdd-red-pre-pep585/evidencias/
- Archivo clave: 01-baseline-tests-mcp.txt

**Contexto de Refactorizacion:**
- Commit aplicado: 2ca3d25
- Cambios: Dict → dict, Mapping → dict (11 ocurrencias)
- Impacto esperado: CERO en runtime
- Validacion: Tests identicos a baseline

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

---

## Checklist de Finalizacion

- [ ] Tests MCP ejecutados
- [ ] Exit code: 0 (todos pasan)
- [ ] Comparacion con baseline completada
- [ ] Resultados identicos a TASK-008
- [ ] Import validado exitosamente
- [ ] Smoke test: PASS
- [ ] 0 regresiones detectadas
- [ ] Evidencias capturadas en evidencias/
- [ ] Listo para TASK-011 (TDD-VALIDATE)
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
