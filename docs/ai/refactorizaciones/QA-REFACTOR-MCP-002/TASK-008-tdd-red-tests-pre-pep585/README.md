---
id: TASK-REFACTOR-MCP-008
tipo: tarea
categoria: tdd-red
titulo: Ejecutar Tests Pre-Refactorizacion PEP 585
fase: FASE_3
prioridad: ALTA
duracion_estimada: 5min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-007]
---

# TASK-008: [TDD-RED] Ejecutar Tests Pre-Refactorizacion PEP 585

**Fase:** FASE 3 - Refactorizacion PEP 585
**Prioridad:** ALTA
**Duracion Estimada:** 5 minutos
**Responsable:** Desarrollador asignado
**Estado:** PENDIENTE
**Tipo TDD:** RED (establecer baseline antes de cambios)
**Dependencias:** TASK-007 (FASE 2 completada)

---

## Objetivo

Ejecutar suite de tests MCP ANTES de aplicar refactorizacion PEP 585 y documentar estado baseline completo, estableciendo la fase RED del ciclo TDD para la segunda refactorizacion. Este baseline servira como referencia para validar que cambios de type annotations no introducen regresiones.

---

## Justificacion

**Metodologia TDD para refactorizacion PEP 585:**
1. **RED:** Ejecutar tests pre-refactorizacion (ESTA TAREA)
2. **REFACTOR:** Aplicar commit 2ca3d25 (TASK-009)
3. **GREEN:** Validar tests siguen pasando (TASK-010)
4. **VALIDATE:** Type checking adicional (TASK-011)

**Diferencia con TASK-004:**
- TASK-004: Baseline PRE Playwright (estado original)
- **TASK-008: Baseline PRE PEP 585 (estado POST Playwright)**

El codigo actual ya incluye refactorizacion Playwright (FASE 2 completa), este baseline captura ese estado ANTES de aplicar PEP 585.

---

## Prerequisitos

- [ ] FASE 2 completada (TASK-004 a TASK-007)
- [ ] Refactorizacion Playwright aplicada y validada
- [ ] Suite de tests MCP identificada
- [ ] Python 3.9+ validado (requisito para PEP 585)
- [ ] Herramientas de testing disponibles (pytest o unittest)

---

## Pasos de Ejecucion

### Paso 1: Verificar Estado Pre-PEP585
```bash
# Confirmar que estamos POST Playwright, PRE PEP585
git log --oneline -5

# Verificar que refactorizacion Playwright esta aplicada
grep -n "PLAYWRIGHT_MCP_VERSION" scripts/coding/ai/mcp/registry.py || echo "WARNING: Constante Playwright no encontrada"

# Verificar que PEP 585 NO esta aplicada (debe tener Dict, Mapping de typing)
grep -n "from typing import.*Dict" scripts/coding/ai/mcp/registry.py

# Resultado esperado: Debe encontrar "from typing import Dict, Mapping, Tuple"
```

**Evidencia Esperada:**
- Commit de Playwright visible en git log
- PLAYWRIGHT_MCP_VERSION encontrado
- Import de Dict encontrado (linea ~6): "from typing import Dict, Mapping, Tuple"
- PEP 585 NO aplicado todavia

### Paso 2: Documentar Type Annotations Actuales
```bash
# Capturar estado actual de type annotations
echo "=== TYPE ANNOTATIONS PRE-PEP585 ===" > evidencias/type-annotations-baseline.txt
echo "Fecha: $(date)" >> evidencias/type-annotations-baseline.txt
echo "" >> evidencias/type-annotations-baseline.txt

# Extraer linea de imports
echo "1. Import de typing:" >> evidencias/type-annotations-baseline.txt
grep "from typing import" scripts/coding/ai/mcp/registry.py >> evidencias/type-annotations-baseline.txt

# Encontrar todas las ocurrencias de Dict, Mapping (uppercase)
echo -e "\n2. Ocurrencias de Dict (uppercase):" >> evidencias/type-annotations-baseline.txt
grep -n "Dict\[" scripts/coding/ai/mcp/registry.py >> evidencias/type-annotations-baseline.txt

echo -e "\n3. Ocurrencias de Mapping (uppercase):" >> evidencias/type-annotations-baseline.txt
grep -n "Mapping\[" scripts/coding/ai/mcp/registry.py >> evidencias/type-annotations-baseline.txt

# Contar total de type annotations antiguas
DICT_COUNT=$(grep -c "Dict\[" scripts/coding/ai/mcp/registry.py || echo "0")
MAPPING_COUNT=$(grep -c "Mapping\[" scripts/coding/ai/mcp/registry.py || echo "0")
TOTAL_LEGACY=$(($DICT_COUNT + $MAPPING_COUNT))

echo -e "\n4. Contadores:" >> evidencias/type-annotations-baseline.txt
echo "   Dict[ ocurrencias: $DICT_COUNT" >> evidencias/type-annotations-baseline.txt
echo "   Mapping[ ocurrencias: $MAPPING_COUNT" >> evidencias/type-annotations-baseline.txt
echo "   Total legacy annotations: $TOTAL_LEGACY" >> evidencias/type-annotations-baseline.txt

# Mostrar resultado
cat evidencias/type-annotations-baseline.txt
```

**Evidencia Esperada:**
- Import: "from typing import Dict, Mapping, Tuple"
- Dict[ ocurrencias: ~9-11
- Mapping[ ocurrencias: ~2
- Total legacy annotations: ~11 (segun plan)

### Paso 3: Ejecutar Suite de Tests MCP (Baseline)
```bash
# Cambiar al directorio raiz
cd /home/user/IACT---project

# Ejecutar tests MCP con pytest
pytest scripts/coding/tests/ai/mcp/ -v --tb=short > evidencias/tests-baseline-pre-pep585.txt 2>&1
PYTEST_EXIT=$?

# Si pytest no disponible, usar unittest
if [ $PYTEST_EXIT -eq 127 ]; then
    python3 -m unittest discover -s scripts/coding/tests/ai/mcp/ -v > evidencias/tests-baseline-pre-pep585.txt 2>&1
    UNITTEST_EXIT=$?
    echo "Framework usado: unittest (exit code: $UNITTEST_EXIT)" >> evidencias/tests-baseline-pre-pep585.txt
else
    echo "Framework usado: pytest (exit code: $PYTEST_EXIT)" >> evidencias/tests-baseline-pre-pep585.txt
fi

# Mostrar resultados
cat evidencias/tests-baseline-pre-pep585.txt
```

**Evidencia Esperada:**
- Tests ejecutados exitosamente
- Exit code 0 (todos pasan)
- Output completo con contadores: "X passed"
- Mismo estado que TASK-006 (tests deben seguir pasando)

### Paso 4: Extraer Metricas de Tests
```bash
# Extraer contadores clave del baseline
echo "=== METRICAS TESTS BASELINE PRE-PEP585 ===" > evidencias/metricas-baseline.txt
echo "Fecha: $(date)" >> evidencias/metricas-baseline.txt
echo "" >> evidencias/metricas-baseline.txt

# Extraer contadores
TESTS_PASSED=$(grep -oP '\d+ passed' evidencias/tests-baseline-pre-pep585.txt | grep -oP '^\d+' || echo "0")
TESTS_FAILED=$(grep -oP '\d+ failed' evidencias/tests-baseline-pre-pep585.txt | grep -oP '^\d+' || echo "0")
TESTS_ERROR=$(grep -oP '\d+ error' evidencias/tests-baseline-pre-pep585.txt | grep -oP '^\d+' || echo "0")
TESTS_SKIPPED=$(grep -oP '\d+ skipped' evidencias/tests-baseline-pre-pep585.txt | grep -oP '^\d+' || echo "0")

# Documentar
echo "Tests passed:  $TESTS_PASSED" >> evidencias/metricas-baseline.txt
echo "Tests failed:  $TESTS_FAILED" >> evidencias/metricas-baseline.txt
echo "Tests error:   $TESTS_ERROR" >> evidencias/metricas-baseline.txt
echo "Tests skipped: $TESTS_SKIPPED" >> evidencias/metricas-baseline.txt

# Calcular total
TESTS_TOTAL=$(($TESTS_PASSED + $TESTS_FAILED + $TESTS_ERROR))
echo "Tests total:   $TESTS_TOTAL" >> evidencias/metricas-baseline.txt

# Estado esperado
echo "" >> evidencias/metricas-baseline.txt
echo "Estado esperado para TASK-010:" >> evidencias/metricas-baseline.txt
echo "  - Tests passed: $TESTS_PASSED (debe mantenerse)" >> evidencias/metricas-baseline.txt
echo "  - Tests failed: 0 (debe mantenerse)" >> evidencias/metricas-baseline.txt
echo "  - Tests error:  0 (debe mantenerse)" >> evidencias/metricas-baseline.txt

# Mostrar
cat evidencias/metricas-baseline.txt
```

**Evidencia Esperada:**
- Tests passed: X (numero positivo)
- Tests failed: 0
- Tests error: 0
- Tests skipped: Y (cualquier numero)
- Estado esperado documentado para TASK-010

### Paso 5: Validar Python Version (Requisito PEP 585)
```bash
# Validar que Python es 3.9+ (requisito obligatorio para PEP 585)
python3 --version > evidencias/python-version-check.txt

PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Python version detectada: $PYTHON_VERSION" >> evidencias/python-version-check.txt
echo "Major: $PYTHON_MAJOR, Minor: $PYTHON_MINOR" >> evidencias/python-version-check.txt

# Validar requisito minimo (3.9+)
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
    echo "PASS: Python 3.9+ detectado - Compatible con PEP 585" >> evidencias/python-version-check.txt
    echo "OK para continuar a TASK-009" >> evidencias/python-version-check.txt
elif [ "$PYTHON_MAJOR" -gt 3 ]; then
    echo "PASS: Python 4+ detectado - Compatible con PEP 585" >> evidencias/python-version-check.txt
    echo "OK para continuar a TASK-009" >> evidencias/python-version-check.txt
else
    echo "FAIL: Python $PYTHON_VERSION NO compatible con PEP 585" >> evidencias/python-version-check.txt
    echo "REQUISITO: Python 3.9 o superior" >> evidencias/python-version-check.txt
    echo "ACCION: ABORTAR plan - Actualizar Python" >> evidencias/python-version-check.txt
    cat evidencias/python-version-check.txt
    exit 1
fi

cat evidencias/python-version-check.txt
```

**Evidencia Esperada:**
- Python version: 3.9.x o superior
- PASS: Python 3.9+ detectado
- OK para continuar a TASK-009

**Si Python < 3.9:**
- FAIL: Python X.Y NO compatible
- ACCION: ABORTAR plan
- Exit code 1

### Paso 6: Crear Snapshot del Archivo Pre-PEP585
```bash
# Crear copia de seguridad del archivo ANTES de PEP 585
cp scripts/coding/ai/mcp/registry.py evidencias/registry-snapshot-pre-pep585.py

# Generar hash del archivo para validacion
sha256sum scripts/coding/ai/mcp/registry.py > evidencias/registry-sha256-pre-pep585.txt

# Contar lineas del archivo
wc -l scripts/coding/ai/mcp/registry.py >> evidencias/registry-sha256-pre-pep585.txt

# Documentar
echo "Snapshot creado: evidencias/registry-snapshot-pre-pep585.py"
cat evidencias/registry-sha256-pre-pep585.txt
```

**Evidencia Esperada:**
- Archivo copiado: evidencias/registry-snapshot-pre-pep585.py
- SHA256 hash documentado
- Lineas: ~145-150 (incluyendo refactorizacion Playwright)

### Paso 7: Generar Resumen Baseline
```bash
# Crear resumen ejecutivo del baseline
cat > evidencias/resumen-baseline-pre-pep585.txt << EOF
=== TASK-008: TDD RED - Baseline Pre-PEP585 ===
Fecha: $(date)
Fase: FASE 3 - Refactorizacion PEP 585
Tipo: Establecer baseline antes de cambios

ESTADO DEL CODIGO:
  - Refactorizacion Playwright: APLICADA (FASE 2 completa)
  - Refactorizacion PEP 585: NO APLICADA (pendiente TASK-009)
  - Constante PLAYWRIGHT_MCP_VERSION: Presente
  - Type annotations legacy: Dict, Mapping (uppercase)

METRICAS DE TESTS:
  - Tests passing: $TESTS_PASSED
  - Tests failing: $TESTS_FAILED
  - Tests error: $TESTS_ERROR
  - Framework: $(grep "Framework usado" evidencias/tests-baseline-pre-pep585.txt | cut -d: -f2 || echo "pytest")

TYPE ANNOTATIONS ACTUALES:
  - Import: from typing import Dict, Mapping, Tuple
  - Dict[ ocurrencias: $DICT_COUNT
  - Mapping[ ocurrencias: $MAPPING_COUNT
  - Total legacy: $TOTAL_LEGACY

PYTHON VERSION:
  - Version: $PYTHON_VERSION
  - Compatible PEP 585: $([ "$PYTHON_MINOR" -ge 9 ] && echo "SI" || echo "NO")

EVIDENCIAS GENERADAS:
  - evidencias/type-annotations-baseline.txt
  - evidencias/tests-baseline-pre-pep585.txt
  - evidencias/metricas-baseline.txt
  - evidencias/python-version-check.txt
  - evidencias/registry-snapshot-pre-pep585.py
  - evidencias/registry-sha256-pre-pep585.txt
  - evidencias/resumen-baseline-pre-pep585.txt

SIGUIENTE PASO:
  - TASK-009: Aplicar refactorizacion PEP 585 (commit 2ca3d25)
  - Cambios esperados: 11 type annotations (Dict/Mapping → dict)
  - Validacion: Tests deben seguir pasando (TASK-010)

BASELINE ESTABLECIDO: SI
LISTO PARA REFACTORIZACION: SI
EOF

cat evidencias/resumen-baseline-pre-pep585.txt
```

**Evidencia Esperada:**
- Resumen completo con todas las metricas
- BASELINE ESTABLECIDO: SI
- LISTO PARA REFACTORIZACION: SI

---

## Criterios de Exito

- [ ] Estado PRE-PEP585 verificado (Dict, Mapping presentes)
- [ ] Type annotations legacy documentadas (11 ocurrencias)
- [ ] Suite de tests ejecutada exitosamente
- [ ] Metricas baseline extraidas (passed, failed, error)
- [ ] Python 3.9+ validado (requisito PEP 585)
- [ ] Snapshot del archivo creado
- [ ] SHA256 hash documentado
- [ ] Resumen baseline generado
- [ ] Evidencias completas (7 archivos)

**Criterio BLOQUEANTE:** Si Python < 3.9, ABORTAR plan completo.

---

## Validacion Post-Ejecucion

### Validacion 1: Type Annotations Legacy Presentes
```bash
# Debe encontrar imports legacy
grep "from typing import.*Dict" scripts/coding/ai/mcp/registry.py
# Esperado: Linea encontrada con "Dict, Mapping, Tuple"
```

### Validacion 2: Contadores de Tests
```bash
# Verificar que contadores fueron capturados
cat evidencias/metricas-baseline.txt | grep "Tests passed:"
# Esperado: Numero >= 0
```

### Validacion 3: Python Version Compatible
```bash
# Verificar PASS de Python version
grep "PASS: Python" evidencias/python-version-check.txt
# Esperado: PASS encontrado
```

### Validacion 4: Snapshot Existe
```bash
# Verificar que snapshot fue creado
ls -lh evidencias/registry-snapshot-pre-pep585.py
# Esperado: Archivo existe, ~145-150 lineas
```

---

## Rollback

**No aplica en esta tarea** - Es solo documentacion de baseline, sin cambios al codigo.

Sin embargo, si se detectan problemas:

### Si Tests Fallan Inesperadamente:
```bash
# Comparar con baseline TASK-006 (deberian ser identicos)
diff ../TASK-006-tdd-green-tests-post-playwright/evidencias/tests-post-playwright.txt \
     evidencias/tests-baseline-pre-pep585.txt

# Si hay diferencias significativas, investigar
```

### Si Python < 3.9:
```bash
# ABORTAR plan
echo "Plan ABORTADO: Python incompatible con PEP 585" > evidencias/plan-abortado.txt
echo "Requisito: Python 3.9+" >> evidencias/plan-abortado.txt
echo "Actual: $PYTHON_VERSION" >> evidencias/plan-abortado.txt

# Notificar al usuario
cat evidencias/plan-abortado.txt

# NO continuar a TASK-009
exit 1
```

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| Python < 3.9 | BAJA | CRITICO | Validacion temprana, ABORTAR plan si incompatible |
| Tests fallan inesperadamente | BAJA | ALTO | Comparar con TASK-006, investigar regresion |
| Type annotations ya aplicadas | MUY BAJA | MEDIO | Verificar git log, revisar commits recientes |
| Framework de tests no disponible | BAJA | MEDIO | Usar unittest como fallback |
| Snapshot no se crea | MUY BAJA | BAJO | Crear manualmente con cp |

---

## Evidencias a Capturar

**Screenshots/Logs:**
1. Estado pre-PEP585 con grep de Dict/Mapping
2. Type annotations baseline completo
3. Output de tests baseline
4. Metricas extraidas de tests
5. Validacion Python version
6. SHA256 del archivo
7. Resumen ejecutivo baseline

**Archivos Generados:**
- evidencias/type-annotations-baseline.txt (annotations actuales)
- evidencias/tests-baseline-pre-pep585.txt (output tests completo)
- evidencias/metricas-baseline.txt (contadores tests)
- evidencias/python-version-check.txt (validacion Python 3.9+)
- evidencias/registry-snapshot-pre-pep585.py (copia del archivo)
- evidencias/registry-sha256-pre-pep585.txt (hash + lineas)
- evidencias/resumen-baseline-pre-pep585.txt (resumen ejecutivo)

**Metricas Clave:**
- Dict[ ocurrencias: ~9-11
- Mapping[ ocurrencias: ~2
- Total legacy: ~11
- Tests passed: X
- Tests failed: 0
- Python version: 3.9+

---

## Notas Importantes

- Esta es la fase RED del ciclo TDD para PEP 585
- Baseline diferente de TASK-004 (incluye Playwright)
- Python 3.9+ es REQUISITO ABSOLUTO para PEP 585
- NO continuar si Python < 3.9
- Tests deben estar en mismo estado que TASK-006

**Relacion con Fases:**
- FASE 2 (Playwright): COMPLETADA antes de esta tarea
- **FASE 3 (PEP 585): INICIANDO con esta tarea**

**Relacion con TDD:**
- **TASK-008: RED (baseline) <- ESTAMOS AQUI**
- TASK-009: REFACTOR (aplicar PEP 585)
- TASK-010: GREEN (validar tests)
- TASK-011: VALIDATE (type checking)

**Diferencias con TASK-004:**
| Aspecto | TASK-004 | TASK-008 |
|---------|----------|----------|
| Fase | FASE 2 | FASE 3 |
| Baseline para | Playwright | PEP 585 |
| Estado codigo | Original | Post-Playwright |
| PLAYWRIGHT_MCP_VERSION | NO | SI |
| Dict/Mapping | SI | SI |

**Decision Point:**
- Si Python >= 3.9 && Tests PASS → Continuar a TASK-009
- Si Python < 3.9 → ABORTAR plan, notificar usuario
- Si Tests FAIL → Investigar regresion antes de continuar

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

---

## Checklist de Finalizacion

- [ ] Estado PRE-PEP585 confirmado (Dict/Mapping presentes)
- [ ] Type annotations legacy documentadas (11 total)
- [ ] Suite de tests ejecutada
- [ ] Metricas baseline capturadas
- [ ] Python version validada (3.9+)
- [ ] Snapshot del archivo creado
- [ ] SHA256 hash generado
- [ ] Resumen baseline completo
- [ ] Evidencias completas (7 archivos)
- [ ] Tests passing: X (mismo que TASK-006)
- [ ] Tests failing: 0
- [ ] Decision: Continuar a TASK-009
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
