---
id: TASK-REFACTOR-MCP-004
tipo: tdd-red
categoria: refactorizacion-mcp
titulo: TDD-RED Ejecutar Tests Pre-Refactorizacion Playwright
fase: FASE_2
prioridad: ALTA
duracion_estimada: 5min
estado: pendiente
dependencias: ["TASK-001", "TASK-002", "TASK-003"]
---

# TASK-REFACTOR-MCP-004: [TDD-RED] Ejecutar Tests Pre-Refactorizacion Playwright

**Fase:** FASE 2 - Refactorizacion Playwright
**Prioridad:** ALTA
**Duracion Estimada:** 5 minutos
**Tipo TDD:** RED
**Responsable:** Agente Claude
**Estado:** PENDIENTE

---

## Objetivo

Ejecutar la suite completa de tests relacionados con MCP registry ANTES de aplicar la refactorizacion de constante Playwright. Este paso establece el baseline especifico para la fase RED del ciclo TDD y permite detectar cualquier regresion introducida por la refactorizacion.

---

## Prerequisitos

- [ ] TASK-001 completada (backup creado)
- [ ] TASK-002 completada (tests identificados o smoke test creado)
- [ ] TASK-003 completada (Python 3.9+ validado)
- [ ] Working directory limpio (sin cambios sin commitear)
- [ ] Framework de tests funcional

---

## Pasos de Ejecucion

### Paso 1: Verificar estado limpio del repositorio
```bash
cd /home/user/IACT---project
git status > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/git-status-pre.log 2>&1
git diff >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/git-status-pre.log 2>&1
```

**Resultado Esperado:** Working directory limpio, sin cambios pendientes

### Paso 2: Verificar estado actual del archivo registry.py
```bash
# Capturar estado actual del archivo antes de refactorizacion
head -n 120 /home/user/IACT---project/scripts/coding/ai/mcp/registry.py > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/registry-pre-refactor.py

# Hash del archivo
md5sum /home/user/IACT---project/scripts/coding/ai/mcp/registry.py > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/registry-hash-pre.txt

# Verificar linea 106 actual (la que sera modificada)
sed -n '100,110p' /home/user/IACT---project/scripts/coding/ai/mcp/registry.py > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/linea-106-pre.txt
echo "Linea 106 ANTES de refactorizacion:" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/linea-106-pre.txt
grep -n "playwright" /home/user/IACT---project/scripts/coding/ai/mcp/registry.py | head -5 >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/linea-106-pre.txt
```

**Resultado Esperado:** Archivo registry.py capturado en estado pre-refactorizacion

### Paso 3: Ejecutar tests MCP (baseline RED)
```bash
# Ejecutar tests identificados en TASK-002
# Si existen tests especificos, ejecutarlos
if [ -f /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/tests-encontrados.log ]; then
    TEST_FILES=$(cat /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/tests-encontrados.log | grep -v "^Tests encontrados" | head -5)

    if [ -n "$TEST_FILES" ]; then
        echo "Ejecutando tests encontrados..." > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log
        pytest -v $TEST_FILES >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log 2>&1
        TEST_EXIT_CODE=$?
    else
        echo "No hay tests especificos, ejecutando smoke test..." > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log
        python -c "from scripts.coding.ai.mcp import registry; print('Import OK')" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log 2>&1
        TEST_EXIT_CODE=$?
    fi
else
    echo "Ejecutando smoke test de importacion..." > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log
    python -c "from scripts.coding.ai.mcp import registry; print('Registry import: OK')" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log 2>&1
    TEST_EXIT_CODE=$?
fi

echo "Exit code: $TEST_EXIT_CODE" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log
```

**Resultado Esperado:** Tests ejecutados, exit code documentado

### Paso 4: Capturar metricas de tests
```bash
# Extraer metricas de la ejecucion
cat > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/metricas-baseline.txt << EOF
=== METRICAS BASELINE RED ===
Fecha: $(date +"%Y-%m-%d %H:%M:%S")
Commit: $(git rev-parse --short HEAD)
Branch: $(git branch --show-current)

ESTADO TESTS PRE-REFACTORIZACION:
$(tail -20 /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log)

ARCHIVO REGISTRY.PY:
$(md5sum /home/user/IACT---project/scripts/coding/ai/mcp/registry.py)

LINEA A MODIFICAR (aprox 106):
$(grep -n "@playwright/mcp" /home/user/IACT---project/scripts/coding/ai/mcp/registry.py | head -1)

EOF
```

**Resultado Esperado:** Metricas baseline documentadas

### Paso 5: Validar que registry.py es sintacticamente correcto
```bash
# Verificar sintaxis Python
python -m py_compile /home/user/IACT---project/scripts/coding/ai/mcp/registry.py > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/syntax-check-pre.log 2>&1
SYNTAX_EXIT_CODE=$?

if [ $SYNTAX_EXIT_CODE -eq 0 ]; then
    echo "Syntax check: OK" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/syntax-check-pre.log
else
    echo "Syntax check: FAILED (exit code $SYNTAX_EXIT_CODE)" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/syntax-check-pre.log
fi
```

**Resultado Esperado:** Sintaxis correcta, exit code 0

### Paso 6: Verificar imports del modulo
```bash
# Verificar que el modulo se puede importar
python -c "
import sys
sys.path.insert(0, '/home/user/IACT---project')
from scripts.coding.ai.mcp import registry

# Verificar que contiene la string de Playwright
import inspect
source = inspect.getsource(registry)
if '@playwright/mcp' in source:
    print('OK: String @playwright/mcp encontrada en codigo fuente')
else:
    print('WARNING: String @playwright/mcp NO encontrada')

print(f'Modulo registry: {registry}')
print(f'Atributos: {dir(registry)[:10]}...')
" > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/import-check-pre.log 2>&1
```

**Resultado Esperado:** Modulo importable, string @playwright/mcp presente

### Paso 7: Crear snapshot del estado RED
```bash
cat > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/snapshot-red.txt << EOF
=== SNAPSHOT TDD-RED FASE 2 PLAYWRIGHT ===
Timestamp: $(date +"%Y-%m-%d %H:%M:%S")
Git commit: $(git rev-parse HEAD)
Git branch: $(git branch --show-current)

ESTADO:
- Working directory: LIMPIO
- Archivo registry.py: SIN MODIFICAR
- Tests ejecutados: SI
- Tests passing: $(grep -q "Exit code: 0" /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log && echo "YES" || echo "NO/UNKNOWN")

PROXIMO PASO:
TASK-005: Aplicar refactorizacion Playwright (cherry-pick commit 0d1e1f2)

EVIDENCIAS GENERADAS:
$(ls -1 /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/)

EOF
```

**Resultado Esperado:** Snapshot completo del estado RED

---

## Criterios de Exito

- [ ] Working directory limpio confirmado
- [ ] Archivo registry.py capturado en estado pre-refactorizacion
- [ ] Hash MD5 del archivo documentado
- [ ] Tests MCP ejecutados (o smoke test si no hay tests)
- [ ] Exit code de tests documentado
- [ ] Sintaxis Python validada (exit code 0)
- [ ] Modulo registry importable sin errores
- [ ] String @playwright/mcp presente en codigo fuente
- [ ] Snapshot del estado RED creado

---

## Validacion

```bash
# Validar que evidencias fueron creadas
EVIDENCIAS_OK=$(ls /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/ | wc -l)
echo "Evidencias creadas: $EVIDENCIAS_OK (esperado: >= 8)"

# Validar que tests se ejecutaron
test -f /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline-red.log && echo "VALIDACION OK: Tests ejecutados" || echo "ERROR: Tests no ejecutados"

# Validar sintaxis
SYNTAX_OK=$(grep -q "Syntax check: OK" /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/syntax-check-pre.log && echo "OK" || echo "FAIL")
echo "Validacion sintaxis: $SYNTAX_OK"

# Validar snapshot creado
test -f /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/snapshot-red.txt && echo "VALIDACION OK: Snapshot RED creado" || echo "ERROR: Snapshot no creado"

# Listar todas las evidencias
ls -lh /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/
```

**Salida Esperada:**
- `Evidencias creadas: 8 (esperado: >= 8)`
- `VALIDACION OK: Tests ejecutados`
- `Validacion sintaxis: OK`
- `VALIDACION OK: Snapshot RED creado`
- Lista de archivos de evidencias

---

## Rollback

Si falla esta tarea:
```bash
# Esta tarea solo ejecuta tests, no modifica codigo
# No hay rollback necesario del codigo

# Limpiar evidencias si se desea reintentar
rm -rf /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-004-tdd-red-tests-pre-playwright/evidencias/*

# Reintentar desde Paso 1
```

**IMPORTANTE:** Si los tests fallan en este baseline (RED), NO continuar con TASK-005. Analizar por que fallan ANTES de refactorizar. La refactorizacion no debe introducir fallos, pero tampoco debe ejecutarse sobre codigo que ya tiene problemas.

---

## Evidencias Requeridas

Las siguientes evidencias deben guardarse en `evidencias/`:

1. **git-status-pre.log** - Estado del repositorio antes de refactorizacion
2. **registry-pre-refactor.py** - Contenido del archivo registry.py (primeras 120 lineas)
3. **registry-hash-pre.txt** - Hash MD5 del archivo pre-refactorizacion
4. **linea-106-pre.txt** - Contexto de la linea que sera modificada
5. **tests-baseline-red.log** - Output completo de ejecucion de tests baseline
6. **metricas-baseline.txt** - Metricas y estado de tests pre-refactorizacion
7. **syntax-check-pre.log** - Validacion de sintaxis Python
8. **import-check-pre.log** - Verificacion de importacion del modulo
9. **snapshot-red.txt** - Snapshot completo del estado RED

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| Tests fallan en baseline | BAJA | ALTO | DETENER plan, analizar causa, NO refactorizar sobre codigo con problemas |
| Modulo no importable | MUY BAJA | CRITICO | DETENER plan, resolver dependencias antes de continuar |
| Working directory sucio | BAJA | MEDIO | Commitear o stash cambios antes de continuar |
| Framework de tests no funcional | BAJA | MEDIO | Usar smoke test de importacion como fallback |

---

## Notas TDD

Esta tarea implementa la fase **RED** del ciclo TDD:

- **RED = Baseline:** Ejecutar tests ANTES de cambios
- **Documentar estado inicial:** Capturar metricas y outputs completos
- **Comparacion futura:** Estos resultados se comparan en TASK-006 (GREEN)
- **No modificar codigo:** Solo ejecutar, observar, documentar

**CICLO TDD FASE 2:**
```
TASK-004 (RED)   → Baseline: tests pasan/fallan
       ↓
TASK-005 (REFACTOR) → Aplicar cambio Playwright
       ↓
TASK-006 (GREEN)    → Validar: tests siguen pasando
       ↓
TASK-007 (VALIDATE) → Validaciones adicionales
```

**REGLA CRITICA:** Si tests fallan en RED (baseline), NO continuar. Refactorizar codigo roto perpetua problemas existentes. Resolver primero, refactorizar despues.

---

## Checklist de Finalizacion

- [ ] Todos los pasos ejecutados exitosamente
- [ ] Criterios de exito cumplidos
- [ ] Validaciones pasadas
- [ ] Todas las evidencias guardadas (minimo 9 archivos)
- [ ] Snapshot RED creado y completo
- [ ] Exit code de tests documentado
- [ ] Hash MD5 de registry.py capturado
- [ ] Modulo registry importable confirmado
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
