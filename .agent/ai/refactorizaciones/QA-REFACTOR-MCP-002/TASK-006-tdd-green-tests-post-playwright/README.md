---
id: TASK-REFACTOR-MCP-006
tipo: tarea
categoria: tdd-green
titulo: Validar Tests Post-Playwright
fase: FASE_2
prioridad: ALTA
duracion_estimada: 5min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-005]
---

# TASK-006: [TDD-GREEN] Validar Tests Post-Playwright

**Fase:** FASE 2 - Refactorizacion Playwright
**Prioridad:** ALTA
**Duracion Estimada:** 5 minutos
**Responsable:** Desarrollador asignado
**Estado:** PENDIENTE
**Tipo TDD:** GREEN (validar tests siguen pasando)
**Dependencias:** TASK-005 (refactorizacion aplicada)

---

## Objetivo

Ejecutar la misma suite de tests MCP que en TASK-004 y comparar resultados con baseline documentado, confirmando que la refactorizacion de constante Playwright NO introdujo regresiones funcionales. Esta es la fase GREEN del ciclo TDD.

---

## Justificacion

Segun metodologia TDD:
1. **RED:** Tests pasan con codigo original (TASK-004)
2. **REFACTOR:** Aplicar cambios de refactorizacion (TASK-005)
3. **GREEN:** Validar que tests SIGUEN pasando (ESTA TAREA)

**Criterio de exito:** 100% de tests en mismo estado que baseline de TASK-004.
**Criterio de fallo:** CUALQUIER test que pase a failing = ROLLBACK INMEDIATO.

---

## Prerequisitos

- [ ] TASK-005 completada (refactorizacion Playwright aplicada)
- [ ] TASK-004 evidencias disponibles (baseline de tests)
- [ ] Suite de tests MCP identificada y accesible
- [ ] Herramientas de testing disponibles (pytest o unittest)

---

## Pasos de Ejecucion

### Paso 1: Recuperar Baseline de TASK-004
```bash
# Leer resultados baseline de TASK-004
cat ../TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline.txt

# Extraer contadores clave
BASELINE_TESTS=$(grep -oP '\d+ passed' ../TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline.txt | grep -oP '^\d+' || echo "BASELINE_NO_ENCONTRADO")

echo "Baseline de TASK-004: $BASELINE_TESTS tests passing"
```

**Evidencia Esperada:**
- Archivo baseline existe y es legible
- Numero de tests passing documentado (ej: "5 passed" o "0 passed si no hay tests")

### Paso 2: Ejecutar Suite de Tests MCP (Post-Refactorizacion)
```bash
# Cambiar al directorio raiz del proyecto
cd /home/user/IACT---project

# Ejecutar tests MCP con pytest (opcion preferida)
pytest scripts/coding/tests/ai/mcp/ -v --tb=short > evidencias/tests-post-playwright.txt 2>&1
PYTEST_EXIT=$?

# Si pytest no disponible, intentar con unittest
if [ $PYTEST_EXIT -eq 127 ]; then
    python3 -m unittest discover -s scripts/coding/tests/ai/mcp/ -v > evidencias/tests-post-playwright.txt 2>&1
    UNITTEST_EXIT=$?
    echo "Framework usado: unittest (exit code: $UNITTEST_EXIT)" >> evidencias/tests-post-playwright.txt
else
    echo "Framework usado: pytest (exit code: $PYTEST_EXIT)" >> evidencias/tests-post-playwright.txt
fi

# Mostrar resultados
cat evidencias/tests-post-playwright.txt
```

**Evidencia Esperada:**
- Tests ejecutados exitosamente
- Exit code 0 (todos pasan) o mismo exit code que TASK-004
- Output completo guardado en evidencias/tests-post-playwright.txt

### Paso 3: Comparar Resultados con Baseline
```bash
# Extraer contadores de tests actuales
POST_TESTS=$(grep -oP '\d+ passed' evidencias/tests-post-playwright.txt | grep -oP '^\d+' || echo "0")
POST_FAILED=$(grep -oP '\d+ failed' evidencias/tests-post-playwright.txt | grep -oP '^\d+' || echo "0")
POST_ERRORS=$(grep -oP '\d+ error' evidencias/tests-post-playwright.txt | grep -oP '^\d+' || echo "0")

# Comparar con baseline
echo "=== COMPARACION CON BASELINE ===" > evidencias/comparacion-tests.txt
echo "TASK-004 Baseline: $BASELINE_TESTS tests passing" >> evidencias/comparacion-tests.txt
echo "TASK-006 Post-Refactor: $POST_TESTS tests passing" >> evidencias/comparacion-tests.txt
echo "Diferencia: $((POST_TESTS - BASELINE_TESTS))" >> evidencias/comparacion-tests.txt
echo "" >> evidencias/comparacion-tests.txt
echo "Tests failed: $POST_FAILED" >> evidencias/comparacion-tests.txt
echo "Tests errors: $POST_ERRORS" >> evidencias/comparacion-tests.txt

# Mostrar comparacion
cat evidencias/comparacion-tests.txt

# Verificar que no hay regresiones
if [ "$POST_TESTS" -ne "$BASELINE_TESTS" ] || [ "$POST_FAILED" -ne "0" ] || [ "$POST_ERRORS" -ne "0" ]; then
    echo "ALERTA: REGRESION DETECTADA" >> evidencias/comparacion-tests.txt
    echo "Accion requerida: ROLLBACK INMEDIATO" >> evidencias/comparacion-tests.txt
    exit 1
else
    echo "EXITO: Tests en mismo estado que baseline" >> evidencias/comparacion-tests.txt
fi
```

**Evidencia Esperada:**
- POST_TESTS == BASELINE_TESTS (mismo numero de tests passing)
- POST_FAILED == 0 (ningun test nuevo fallando)
- POST_ERRORS == 0 (ningun error nuevo)
- Mensaje: "EXITO: Tests en mismo estado que baseline"

**Si hay regresion:**
- Mensaje: "ALERTA: REGRESION DETECTADA"
- Exit code 1
- Proceder a seccion Rollback

### Paso 4: Generar Diff de Outputs (Analisis Detallado)
```bash
# Crear diff lado a lado de outputs
diff -y --width=160 \
    ../TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline.txt \
    evidencias/tests-post-playwright.txt \
    > evidencias/diff-tests-outputs.txt || echo "Archivos difieren - revisar diff"

# Mostrar primeras 30 lineas del diff
head -30 evidencias/diff-tests-outputs.txt

# Contar lineas diferentes
DIFF_LINES=$(diff ../TASK-004-tdd-red-tests-pre-playwright/evidencias/tests-baseline.txt evidencias/tests-post-playwright.txt | wc -l)
echo "Lineas diferentes en outputs: $DIFF_LINES" >> evidencias/comparacion-tests.txt
```

**Evidencia Esperada:**
- Diff minimo o solo diferencias en timestamps/paths
- Sin diferencias en contadores de tests
- DIFF_LINES == 0 (ideal) o DIFF_LINES < 10 (aceptable si solo timestamps)

### Paso 5: Validar Tests Especificos de MCP Registry
```bash
# Si tests existen, ejecutar solo tests de registry
pytest scripts/coding/tests/ai/mcp/test_registry.py -v 2>&1 | tee evidencias/test-registry-detallado.txt

# Extraer informacion de test especifico que usa Playwright
grep -A5 -B5 "playwright" evidencias/test-registry-detallado.txt || echo "Sin tests especificos de playwright"

# Guardar resultado
echo "Tests de registry ejecutados: $(date)" >> evidencias/comparacion-tests.txt
```

**Evidencia Esperada:**
- test_registry.py ejecutado exitosamente
- Si existe test que usa "playwright", debe pasar

### Paso 6: Documentar Estado Final
```bash
# Crear resumen ejecutivo
cat > evidencias/resumen-tdd-green.txt << EOF
=== TASK-006: TDD GREEN - Resumen Ejecutivo ===
Fecha: $(date)
Fase: FASE 2 - Refactorizacion Playwright
Tipo: Validacion post-refactorizacion

BASELINE (TASK-004):
  - Tests passing: $BASELINE_TESTS
  - Framework: pytest/unittest

POST-REFACTOR (TASK-006):
  - Tests passing: $POST_TESTS
  - Tests failed: $POST_FAILED
  - Tests errors: $POST_ERRORS
  - Framework: $(grep "Framework usado" evidencias/tests-post-playwright.txt || echo "pytest")

RESULTADO:
  - Regresiones detectadas: $([ "$POST_TESTS" -eq "$BASELINE_TESTS" ] && echo "NO" || echo "SI - CRITICO")
  - Estado TDD: $([ "$POST_TESTS" -eq "$BASELINE_TESTS" ] && echo "GREEN - PASS" || echo "RED - FAIL")
  - Accion: $([ "$POST_TESTS" -eq "$BASELINE_TESTS" ] && echo "Continuar a TASK-007" || echo "ROLLBACK INMEDIATO")

EVIDENCIAS GENERADAS:
  - evidencias/tests-post-playwright.txt
  - evidencias/comparacion-tests.txt
  - evidencias/diff-tests-outputs.txt
  - evidencias/test-registry-detallado.txt
  - evidencias/resumen-tdd-green.txt
EOF

cat evidencias/resumen-tdd-green.txt
```

**Evidencia Esperada:**
- Resumen completo con metricas
- Estado TDD: GREEN - PASS
- Accion: Continuar a TASK-007

---

## Criterios de Exito

- [ ] Suite de tests MCP ejecutada exitosamente
- [ ] Mismo numero de tests passing que baseline TASK-004
- [ ] Cero tests nuevos fallando (POST_FAILED == 0)
- [ ] Cero errores nuevos (POST_ERRORS == 0)
- [ ] Diff de outputs muestra solo cambios menores (timestamps)
- [ ] Tests de registry.py pasan (si existen)
- [ ] Estado TDD: GREEN
- [ ] Evidencias completas (5 archivos minimo)

**Criterio CRITICO:** Si CUALQUIER test pasa a failing, esta tarea FALLA y requiere ROLLBACK.

---

## Validacion Post-Ejecucion

### Validacion 1: Contadores Identicos
```bash
# Verificar contadores exactos
echo "Verificando contadores..."
[ "$POST_TESTS" -eq "$BASELINE_TESTS" ] && echo "PASS: Mismo numero de tests" || echo "FAIL: Numero diferente"
[ "$POST_FAILED" -eq "0" ] && echo "PASS: Cero failures" || echo "FAIL: Hay tests fallando"
[ "$POST_ERRORS" -eq "0" ] && echo "PASS: Cero errores" || echo "FAIL: Hay errores"
```

### Validacion 2: Exit Codes
```bash
# Verificar que exit code es exitoso
grep "exit code" evidencias/tests-post-playwright.txt
# Esperado: exit code 0
```

### Validacion 3: Grep de Regresiones
```bash
# Buscar palabras clave de problemas
grep -i "FAILED\|ERROR\|REGRES" evidencias/tests-post-playwright.txt || echo "Sin problemas detectados"
```

---

## Rollback

**IMPORTANTE:** Si esta tarea detecta regresiones, ejecutar rollback INMEDIATAMENTE.

### Criterios para Rollback INMEDIATO:
- POST_TESTS < BASELINE_TESTS (menos tests passing)
- POST_FAILED > 0 (tests nuevos fallando)
- POST_ERRORS > 0 (errores nuevos)
- Cualquier test critico de registry.py fallando

### Procedimiento de Rollback:

#### Opcion A: Revertir Commit TASK-005
```bash
# Revertir refactorizacion Playwright
git revert HEAD

# Re-ejecutar tests para confirmar
pytest scripts/coding/tests/ai/mcp/ -v

# Documentar rollback
echo "ROLLBACK ejecutado: $(date)" >> evidencias/rollback.txt
echo "Razon: Regresiones detectadas en TASK-006" >> evidencias/rollback.txt
```

#### Opcion B: Reset Hard al Estado Pre-TASK-005
```bash
# Volver al commit antes de TASK-005
git reset --hard HEAD~1

# Verificar estado
git status
git log -1 --oneline

# Documentar
echo "ROLLBACK con reset hard ejecutado: $(date)" >> evidencias/rollback.txt
```

#### Opcion C: Restaurar Backup Completo
```bash
# Volver al backup de seguridad TASK-001
git reset --hard backup-refactor-mcp-2025-11-17

# Verificar
git log -1 --oneline
```

### Post-Rollback:
1. Re-ejecutar tests para confirmar que vuelven a baseline
2. Analizar causa raiz de regresion
3. Documentar hallazgos en evidencias/analisis-regresion.txt
4. Notificar al responsable
5. NO continuar a TASK-007 hasta resolver regresion

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| Tests fallan post-refactor | BAJA | CRITICO | Rollback inmediato + analisis de causa raiz |
| Framework de tests no disponible | BAJA | MEDIO | Usar unittest como fallback |
| Baseline TASK-004 corrupto | MUY BAJA | ALTO | Re-ejecutar TASK-004 para regenerar baseline |
| Diff muestra falsos positivos | BAJA | BAJO | Analisis manual de diferencias |
| Tests pasan pero con warnings | MEDIA | BAJO | Documentar warnings, continuar si no son criticos |

---

## Evidencias a Capturar

**Screenshots/Logs:**
1. Output completo de pytest/unittest (tests-post-playwright.txt)
2. Comparacion de contadores (comparacion-tests.txt)
3. Diff de outputs baseline vs post-refactor (diff-tests-outputs.txt)
4. Tests detallados de registry (test-registry-detallado.txt)
5. Resumen ejecutivo TDD GREEN (resumen-tdd-green.txt)

**Archivos Generados:**
- evidencias/tests-post-playwright.txt (output completo)
- evidencias/comparacion-tests.txt (comparacion con baseline)
- evidencias/diff-tests-outputs.txt (diff detallado)
- evidencias/test-registry-detallado.txt (tests especificos)
- evidencias/resumen-tdd-green.txt (resumen ejecutivo)
- evidencias/rollback.txt (solo si rollback ejecutado)

**Metricas Clave:**
- BASELINE_TESTS: X tests
- POST_TESTS: X tests (debe ser igual)
- POST_FAILED: 0 (obligatorio)
- POST_ERRORS: 0 (obligatorio)
- DIFF_LINES: 0-10 (aceptable)

---

## Notas Importantes

- Esta es la fase GREEN del ciclo TDD - CRITICA para validacion
- NO continuar a TASK-007 si esta tarea falla
- Rollback debe ser INMEDIATO ante cualquier regresion
- Diferencias en timestamps/paths son aceptables
- Diferencias en contadores de tests NO son aceptables
- Si no hay tests baseline, ambos deben mostrar "0 tests"

**Relacion con TDD:**
- TASK-004: RED (baseline)
- TASK-005: REFACTOR (cambios)
- **TASK-006: GREEN (validacion) <- ESTAMOS AQUI**
- TASK-007: VALIDATE (smoke tests adicionales)

**Decision Point:**
- Si GREEN PASS → Continuar a TASK-007
- Si GREEN FAIL → ROLLBACK + analisis + NO continuar

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

---

## Checklist de Finalizacion

- [ ] Baseline TASK-004 recuperado correctamente
- [ ] Suite de tests MCP ejecutada post-refactorizacion
- [ ] Contadores comparados: POST_TESTS == BASELINE_TESTS
- [ ] Cero tests fallando (POST_FAILED == 0)
- [ ] Cero errores (POST_ERRORS == 0)
- [ ] Diff de outputs analizado (solo cambios menores)
- [ ] Tests de registry.py validados
- [ ] Resumen ejecutivo generado
- [ ] Estado TDD: GREEN - PASS
- [ ] Evidencias completas (5 archivos)
- [ ] Decision: Continuar a TASK-007 (si PASS) o ROLLBACK (si FAIL)
- [ ] Tarea marcada como COMPLETADA (solo si PASS)

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
