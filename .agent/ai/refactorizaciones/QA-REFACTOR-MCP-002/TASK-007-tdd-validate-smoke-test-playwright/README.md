---
id: TASK-REFACTOR-MCP-007
tipo: tarea
categoria: tdd-validate
titulo: Smoke Test Playwright Integration
fase: FASE_2
prioridad: ALTA
duracion_estimada: 5min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-006]
---

# TASK-007: [TDD-VALIDATE] Smoke Test Playwright Integration

**Fase:** FASE 2 - Refactorizacion Playwright
**Prioridad:** ALTA
**Duracion Estimada:** 5 minutos
**Responsable:** Desarrollador asignado
**Estado:** PENDIENTE
**Tipo TDD:** VALIDATE (validaciones adicionales)
**Dependencias:** TASK-006 (tests GREEN confirmados)

---

## Objetivo

Ejecutar validaciones adicionales y smoke tests especificos para la integracion Playwright, enfocandose en string interpolation, valores finales de constante, y comportamiento de runtime del registry MCP. Esta es la fase VALIDATE del ciclo TDD extendido.

---

## Justificacion

Aunque TASK-006 confirmo que tests unitarios pasan (GREEN), esta tarea valida:
1. **String interpolation funciona correctamente** en runtime
2. **Valor final de constante es identico** al hardcoded anterior
3. **Registry MCP puede construirse** sin errores
4. **No hay side effects** de la refactorizacion en integracion

**Scope:** Validaciones de integracion y smoke tests, NO reemplaza tests unitarios.

---

## Prerequisitos

- [ ] TASK-006 completada con estado GREEN (tests passing)
- [ ] Refactorizacion Playwright aplicada y commiteada
- [ ] Python 3.x disponible en entorno
- [ ] Archivo scripts/coding/ai/mcp/registry.py accesible

---

## Pasos de Ejecucion

### Paso 1: Smoke Test - Importar Constante
```bash
# Test 1: Verificar que constante existe y es accesible
python3 -c "
from scripts.coding.ai.mcp.registry import PLAYWRIGHT_MCP_VERSION
print(f'PASS: Constante importada correctamente')
print(f'Valor: {PLAYWRIGHT_MCP_VERSION}')
assert PLAYWRIGHT_MCP_VERSION == '0.0.40', f'FAIL: Valor inesperado {PLAYWRIGHT_MCP_VERSION}'
print('PASS: Valor correcto (0.0.40)')
" 2>&1 | tee evidencias/smoke-test-1-constante.txt

# Verificar exit code
echo "Exit code: $?" >> evidencias/smoke-test-1-constante.txt
```

**Evidencia Esperada:**
- PASS: Constante importada correctamente
- Valor: 0.0.40
- PASS: Valor correcto (0.0.40)
- Exit code: 0

### Paso 2: Smoke Test - String Interpolation
```bash
# Test 2: Validar que interpolacion produce string identico al anterior
python3 -c "
from scripts.coding.ai.mcp.registry import PLAYWRIGHT_MCP_VERSION

# Construir string con interpolacion (nuevo metodo)
resultado_nuevo = f'@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}'

# String original hardcodeado (valor esperado)
esperado = '@playwright/mcp@0.0.40'

# Validar que son identicos
assert resultado_nuevo == esperado, f'FAIL: {resultado_nuevo} != {esperado}'
print(f'PASS: String interpolation correcta')
print(f'Resultado: {resultado_nuevo}')
print(f'Esperado:  {esperado}')
print(f'Match: {resultado_nuevo == esperado}')
" 2>&1 | tee evidencias/smoke-test-2-interpolation.txt

echo "Exit code: $?" >> evidencias/smoke-test-2-interpolation.txt
```

**Evidencia Esperada:**
- PASS: String interpolation correcta
- Resultado: @playwright/mcp@0.0.40
- Esperado:  @playwright/mcp@0.0.40
- Match: True
- Exit code: 0

### Paso 3: Smoke Test - Registry Build
```bash
# Test 3: Validar que registry se puede construir sin errores
python3 << 'EOF' 2>&1 | tee evidencias/smoke-test-3-registry-build.txt
import sys
sys.path.insert(0, '/home/user/IACT---project')

try:
    from scripts.coding.ai.mcp.registry import build_default_registry, PLAYWRIGHT_MCP_VERSION

    print('PASS: Imports exitosos')

    # Construir registry
    registry = build_default_registry()
    print(f'PASS: Registry construido: {type(registry).__name__}')

    # Verificar que registry no es None
    assert registry is not None, 'FAIL: Registry es None'
    print('PASS: Registry no es None')

    # Verificar que tiene atributos esperados
    if hasattr(registry, 'servers'):
        print(f'PASS: Registry tiene atributo servers')
        print(f'Numero de servers: {len(registry.servers) if hasattr(registry.servers, "__len__") else "N/A"}')

    print(f'\nValor de constante Playwright: {PLAYWRIGHT_MCP_VERSION}')
    print('SMOKE TEST COMPLETO: PASS')

except ImportError as e:
    print(f'FAIL: Error de import: {e}')
    sys.exit(1)
except Exception as e:
    print(f'FAIL: Error al construir registry: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

echo "Exit code: $?" >> evidencias/smoke-test-3-registry-build.txt
```

**Evidencia Esperada:**
- PASS: Imports exitosos
- PASS: Registry construido: MCPRegistry (o tipo similar)
- PASS: Registry no es None
- PASS: Registry tiene atributo servers
- Numero de servers: X (cualquier numero >= 1)
- SMOKE TEST COMPLETO: PASS
- Exit code: 0

### Paso 4: Smoke Test - Grep de Uso de Constante
```bash
# Test 4: Verificar que constante se usa en el codigo (no quedo sin usar)
echo "=== BUSQUEDA DE USO DE CONSTANTE ===" > evidencias/smoke-test-4-grep-usage.txt

# Buscar definicion de constante
echo "1. Definicion de constante:" >> evidencias/smoke-test-4-grep-usage.txt
grep -n "^PLAYWRIGHT_MCP_VERSION" scripts/coding/ai/mcp/registry.py >> evidencias/smoke-test-4-grep-usage.txt

# Buscar usos de constante
echo -e "\n2. Usos de constante:" >> evidencias/smoke-test-4-grep-usage.txt
grep -n "PLAYWRIGHT_MCP_VERSION" scripts/coding/ai/mcp/registry.py >> evidencias/smoke-test-4-grep-usage.txt

# Contar ocurrencias
OCURRENCIAS=$(grep -c "PLAYWRIGHT_MCP_VERSION" scripts/coding/ai/mcp/registry.py)
echo -e "\n3. Total ocurrencias: $OCURRENCIAS" >> evidencias/smoke-test-4-grep-usage.txt

# Validar que hay al menos 2 ocurrencias (definicion + uso)
if [ "$OCURRENCIAS" -ge 2 ]; then
    echo "PASS: Constante definida y usada (${OCURRENCIAS} ocurrencias)" >> evidencias/smoke-test-4-grep-usage.txt
else
    echo "FAIL: Constante no usada suficiente (${OCURRENCIAS} ocurrencias, esperado >= 2)" >> evidencias/smoke-test-4-grep-usage.txt
fi

# Verificar que NO quedan strings hardcodeados
echo -e "\n4. Verificacion de strings hardcodeados:" >> evidencias/smoke-test-4-grep-usage.txt
if grep -q "@playwright/mcp@0.0.40" scripts/coding/ai/mcp/registry.py; then
    echo "FAIL: String hardcodeado encontrado" >> evidencias/smoke-test-4-grep-usage.txt
    grep -n "@playwright/mcp@0.0.40" scripts/coding/ai/mcp/registry.py >> evidencias/smoke-test-4-grep-usage.txt
else
    echo "PASS: Sin strings hardcodeados @playwright/mcp@0.0.40" >> evidencias/smoke-test-4-grep-usage.txt
fi

# Mostrar resultados
cat evidencias/smoke-test-4-grep-usage.txt
```

**Evidencia Esperada:**
- Definicion encontrada en linea ~18
- Uso encontrado en linea ~110
- Total ocurrencias: 2 (minimo)
- PASS: Constante definida y usada
- PASS: Sin strings hardcodeados

### Paso 5: Smoke Test - Validacion de Comentarios
```bash
# Test 5: Verificar que comentarios explicativos existen
echo "=== VALIDACION DE COMENTARIOS ===" > evidencias/smoke-test-5-comentarios.txt

# Extraer lineas con comentarios cerca de la constante
sed -n '16,19p' scripts/coding/ai/mcp/registry.py >> evidencias/smoke-test-5-comentarios.txt

# Verificar que comentarios explican razon de version pinned
if grep -q "Copilot CLI reference log" scripts/coding/ai/mcp/registry.py; then
    echo -e "\nPASS: Comentario con referencia a Copilot CLI encontrado" >> evidencias/smoke-test-5-comentarios.txt
else
    echo -e "\nWARNING: Comentario con referencia no encontrado" >> evidencias/smoke-test-5-comentarios.txt
fi

if grep -q "verified to work" scripts/coding/ai/mcp/registry.py; then
    echo "PASS: Comentario de verificacion encontrado" >> evidencias/smoke-test-5-comentarios.txt
else
    echo "WARNING: Comentario de verificacion no encontrado" >> evidencias/smoke-test-5-comentarios.txt
fi

cat evidencias/smoke-test-5-comentarios.txt
```

**Evidencia Esperada:**
- Comentarios extraidos (lineas 16-19)
- PASS: Comentario con referencia a Copilot CLI encontrado
- PASS: Comentario de verificacion encontrado

### Paso 6: Generar Resumen de Smoke Tests
```bash
# Consolidar resultados de todos los smoke tests
cat > evidencias/resumen-smoke-tests.txt << 'EOF'
=== TASK-007: SMOKE TESTS PLAYWRIGHT - Resumen ===
Fecha: $(date)
Fase: FASE 2 - Refactorizacion Playwright
Tipo: Validaciones adicionales (TDD VALIDATE)

SMOKE TEST 1: Importar Constante
$(grep "PASS\|FAIL" evidencias/smoke-test-1-constante.txt | head -3)

SMOKE TEST 2: String Interpolation
$(grep "PASS\|FAIL" evidencias/smoke-test-2-interpolation.txt | head -3)

SMOKE TEST 3: Registry Build
$(grep "PASS\|FAIL\|SMOKE TEST COMPLETO" evidencias/smoke-test-3-registry-build.txt)

SMOKE TEST 4: Uso de Constante
$(grep "PASS\|FAIL" evidencias/smoke-test-4-grep-usage.txt)

SMOKE TEST 5: Comentarios
$(grep "PASS\|WARNING" evidencias/smoke-test-5-comentarios.txt | tail -2)

RESULTADO GLOBAL:
$([ $(grep -c "^PASS" evidencias/smoke-test-*.txt) -ge 8 ] && echo "TODOS LOS SMOKE TESTS: PASS" || echo "ALGUNOS SMOKE TESTS FALLARON - REVISAR")

SIGUIENTE PASO:
$([ $(grep -c "^PASS" evidencias/smoke-test-*.txt) -ge 8 ] && echo "Continuar a FASE 3 - TASK-008 (PEP 585)" || echo "ANALIZAR FALLOS - NO CONTINUAR")
EOF

# Evaluar plantilla con bash
bash -c "cat > evidencias/resumen-smoke-tests.txt << 'EOFF'
=== TASK-007: SMOKE TESTS PLAYWRIGHT - Resumen ===
Fecha: $(date)
Fase: FASE 2 - Refactorizacion Playwright
Tipo: Validaciones adicionales (TDD VALIDATE)

SMOKE TEST 1: Importar Constante
$(grep "PASS\|FAIL" evidencias/smoke-test-1-constante.txt | head -3)

SMOKE TEST 2: String Interpolation
$(grep "PASS\|FAIL" evidencias/smoke-test-2-interpolation.txt | head -3)

SMOKE TEST 3: Registry Build
$(grep "PASS\|FAIL\|SMOKE TEST COMPLETO" evidencias/smoke-test-3-registry-build.txt)

SMOKE TEST 4: Uso de Constante
$(grep "PASS\|FAIL" evidencias/smoke-test-4-grep-usage.txt)

SMOKE TEST 5: Comentarios
$(grep "PASS\|WARNING" evidencias/smoke-test-5-comentarios.txt | tail -2)

RESULTADO GLOBAL:
$([ \$(grep -c \"^PASS\" evidencias/smoke-test-*.txt) -ge 8 ] && echo \"TODOS LOS SMOKE TESTS: PASS\" || echo \"ALGUNOS SMOKE TESTS FALLARON - REVISAR\")

SIGUIENTE PASO:
$([ \$(grep -c \"^PASS\" evidencias/smoke-test-*.txt) -ge 8 ] && echo \"Continuar a FASE 3 - TASK-008 (PEP 585)\" || echo \"ANALIZAR FALLOS - NO CONTINUAR\")
EOFF
"

cat evidencias/resumen-smoke-tests.txt
```

**Evidencia Esperada:**
- Resumen completo con resultados de 5 smoke tests
- RESULTADO GLOBAL: TODOS LOS SMOKE TESTS: PASS
- SIGUIENTE PASO: Continuar a FASE 3 - TASK-008

---

## Criterios de Exito

- [ ] Smoke Test 1: Constante importa correctamente (PASS)
- [ ] Smoke Test 2: String interpolation produce valor identico (PASS)
- [ ] Smoke Test 3: Registry se construye sin errores (PASS)
- [ ] Smoke Test 4: Constante usada al menos 2 veces (PASS)
- [ ] Smoke Test 4: Sin strings hardcodeados residuales (PASS)
- [ ] Smoke Test 5: Comentarios explicativos presentes (PASS)
- [ ] Todos los smoke tests exit code 0
- [ ] Resumen generado con estado global PASS
- [ ] Evidencias completas (6 archivos)

**Criterio CRITICO:** Si CUALQUIER smoke test falla, analizar antes de continuar a FASE 3.

---

## Validacion Post-Ejecucion

### Validacion 1: Contar PASS vs FAIL
```bash
# Contar resultados exitosos
PASS_COUNT=$(grep -c "^PASS" evidencias/smoke-test-*.txt)
FAIL_COUNT=$(grep -c "^FAIL" evidencias/smoke-test-*.txt)

echo "Tests PASS: $PASS_COUNT"
echo "Tests FAIL: $FAIL_COUNT"

# Esperado: PASS_COUNT >= 8, FAIL_COUNT == 0
```

### Validacion 2: Exit Codes
```bash
# Verificar que todos los exit codes son 0
grep "Exit code:" evidencias/smoke-test-*.txt
# Esperado: Exit code: 0 en todos
```

### Validacion 3: String Interpolation Final
```bash
# Validacion final de string interpolation
python3 -c "from scripts.coding.ai.mcp.registry import PLAYWRIGHT_MCP_VERSION; print(f'@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}')"
# Esperado: @playwright/mcp@0.0.40
```

---

## Rollback

**Raramente necesario** en esta fase (solo validaciones), pero si smoke tests fallan consistentemente:

### Si Smoke Test Falla Criticamente:
```bash
# Analizar causa raiz primero
cat evidencias/smoke-test-*.txt | grep "FAIL\|Error"

# Si problema es en refactorizacion (no en entorno):
git revert HEAD~1  # Revertir TASK-005

# Re-ejecutar smoke tests para confirmar
python3 -c "from scripts.coding.ai.mcp.registry import build_default_registry; build_default_registry()"
```

### Criterios para Rollback:
- Constante no se puede importar (ImportError)
- String interpolation produce valor diferente
- Registry build falla con Exception
- Constante definida pero no usada (refactorizacion incompleta)

**NO hacer rollback por:**
- Warnings menores en comentarios
- Numero de linea diferente al esperado (normal)
- Tests unitarios ya validados en TASK-006

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| Import falla por PYTHONPATH | BAJA | MEDIO | Agregar sys.path.insert en scripts de test |
| Registry build falla por dependencias | BAJA | MEDIO | Documentar dependencias faltantes, no es bloqueante |
| String interpolation incorrecta | MUY BAJA | CRITICO | Rollback inmediato si valor diferente |
| Constante no usada | MUY BAJA | ALTO | Validar con grep, revisar refactorizacion |
| Comentarios faltantes | BAJA | BAJO | Agregar manualmente si necesario |

---

## Evidencias a Capturar

**Screenshots/Logs:**
1. Smoke Test 1: Import constante (smoke-test-1-constante.txt)
2. Smoke Test 2: String interpolation (smoke-test-2-interpolation.txt)
3. Smoke Test 3: Registry build (smoke-test-3-registry-build.txt)
4. Smoke Test 4: Grep usage (smoke-test-4-grep-usage.txt)
5. Smoke Test 5: Comentarios (smoke-test-5-comentarios.txt)
6. Resumen consolidado (resumen-smoke-tests.txt)

**Archivos Generados:**
- evidencias/smoke-test-1-constante.txt
- evidencias/smoke-test-2-interpolation.txt
- evidencias/smoke-test-3-registry-build.txt
- evidencias/smoke-test-4-grep-usage.txt
- evidencias/smoke-test-5-comentarios.txt
- evidencias/resumen-smoke-tests.txt

**Metricas Clave:**
- Total smoke tests: 5
- Tests PASS: 8+ (varios checks por test)
- Tests FAIL: 0
- Exit codes: 0 (todos)
- String final: @playwright/mcp@0.0.40 (exacto)

---

## Notas Importantes

- Esta es la fase VALIDATE del ciclo TDD extendido
- Complementa TASK-006 (tests unitarios) con validaciones de integracion
- Focus especifico en string interpolation (critico para refactorizacion)
- Smoke tests NO reemplazan tests unitarios formales
- Si falla, analizar antes de rollback (puede ser problema de entorno)

**Relacion con TDD:**
- TASK-004: RED (baseline)
- TASK-005: REFACTOR (cambios)
- TASK-006: GREEN (tests unitarios)
- **TASK-007: VALIDATE (smoke tests) <- ESTAMOS AQUI**

**Smoke Tests vs Unit Tests:**
- Unit Tests (TASK-006): Formales, automatizados, coverage
- Smoke Tests (TASK-007): Manuales, integracion, casos criticos

**Decision Point:**
- Si todos PASS → Continuar a FASE 3 - TASK-008
- Si alguno FAIL → Analizar causa + decidir rollback o fix

**Completitud de FASE 2:**
Tras esta tarea, FASE 2 (Refactorizacion Playwright) esta COMPLETA:
- [x] TASK-004: Baseline documentado
- [x] TASK-005: Refactorizacion aplicada
- [x] TASK-006: Tests unitarios validados
- [x] TASK-007: Smoke tests ejecutados

Siguiente: FASE 3 - Refactorizacion PEP 585

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

---

## Checklist de Finalizacion

- [ ] Smoke Test 1 ejecutado (import constante)
- [ ] Smoke Test 2 ejecutado (string interpolation)
- [ ] Smoke Test 3 ejecutado (registry build)
- [ ] Smoke Test 4 ejecutado (grep usage)
- [ ] Smoke Test 5 ejecutado (comentarios)
- [ ] Todos los tests PASS (>=8 checks)
- [ ] Todos los exit codes 0
- [ ] String final validado: @playwright/mcp@0.0.40
- [ ] Sin strings hardcodeados residuales
- [ ] Resumen consolidado generado
- [ ] Evidencias completas (6 archivos)
- [ ] Decision: Continuar a FASE 3
- [ ] FASE 2 marcada como COMPLETADA
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
