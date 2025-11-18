---
id: TASK-REFACTOR-MCP-002
tipo: tdd-baseline
categoria: refactorizacion-mcp
titulo: Verificar Tests Existentes MCP
fase: FASE_1
prioridad: CRITICA
duracion_estimada: 5min
estado: pendiente
dependencias: ["TASK-001"]
---

# TASK-REFACTOR-MCP-002: Verificar Tests Existentes MCP

**Fase:** FASE 1 - Preparacion
**Prioridad:** CRITICA
**Duracion Estimada:** 5 minutos
**Tipo TDD:** TDD Baseline
**Responsable:** Agente Claude
**Estado:** PENDIENTE

---

## Objetivo

Identificar y ejecutar tests existentes relacionados con el modulo MCP registry para establecer un baseline de validacion. Si no existen tests, crear un smoke test basico que permita validar el funcionamiento minimo del modulo durante las refactorizaciones.

---

## Prerequisitos

- [ ] TASK-001 completada exitosamente (backup creado)
- [ ] Python instalado y accesible
- [ ] Framework de tests disponible (pytest, unittest, etc.)
- [ ] Acceso al codigo fuente del modulo registry.py

---

## Pasos de Ejecucion

### Paso 1: Buscar tests relacionados a MCP registry
```bash
cd /home/user/IACT---project
find . -type f -name "*test*.py" -o -name "test_*.py" | grep -i mcp > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/busqueda-tests.log
find . -type f -name "*test*.py" -o -name "test_*.py" | xargs grep -l "registry" 2>/dev/null >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/busqueda-tests.log
```

**Resultado Esperado:** Lista de archivos de tests potencialmente relacionados con MCP registry

### Paso 2: Verificar existencia de tests especificos
```bash
# Buscar imports del modulo registry en tests
find . -path "*/test*" -name "*.py" -type f -exec grep -l "from.*mcp.*registry" {} \; 2>/dev/null > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/tests-encontrados.log
find . -path "*/test*" -name "*.py" -type f -exec grep -l "import.*mcp.*registry" {} \; 2>/dev/null >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/tests-encontrados.log

# Documentar resultado
TEST_COUNT=$(cat /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/tests-encontrados.log | wc -l)
echo "Tests encontrados: $TEST_COUNT" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/tests-encontrados.log
```

**Resultado Esperado:** Numero de tests que importan el modulo registry

### Paso 3: Ejecutar tests encontrados (si existen)
```bash
# Si existen tests, ejecutarlos
if [ -s /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/tests-encontrados.log ]; then
    echo "Ejecutando tests encontrados..." > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/ejecucion-tests.log
    pytest -v $(cat /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/tests-encontrados.log | head -1) >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/ejecucion-tests.log 2>&1
else
    echo "No se encontraron tests existentes para MCP registry" > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/ejecucion-tests.log
fi
```

**Resultado Esperado:** Output de ejecucion de tests o mensaje indicando ausencia

### Paso 4: Crear smoke test basico (si no hay tests)
```bash
# Verificar si necesitamos crear smoke test
TEST_COUNT=$(find . -path "*/test*" -name "*.py" -type f -exec grep -l "mcp.*registry" {} \; 2>/dev/null | wc -l)

if [ "$TEST_COUNT" -eq 0 ]; then
    echo "Creando smoke test basico para MCP registry..." > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/smoke-test-creado.log
    # El smoke test se creara en una ubicacion temporal para validacion
    mkdir -p /tmp/mcp_smoke_test
    cat > /tmp/mcp_smoke_test/test_registry_smoke.py << 'EOF'
"""Smoke test basico para MCP registry"""
import sys
sys.path.insert(0, '/home/user/IACT---project')

def test_import_registry():
    """Verificar que el modulo registry se puede importar"""
    try:
        from scripts.coding.ai.mcp import registry
        assert registry is not None
    except ImportError as e:
        assert False, f"No se pudo importar registry: {e}"

def test_registry_basic_structure():
    """Verificar estructura basica del modulo"""
    from scripts.coding.ai.mcp import registry

    # Verificar que existen las constantes/funciones esperadas
    assert hasattr(registry, 'MCP_REGISTRY') or hasattr(registry, 'get_registry'), \
        "Registry no tiene estructura esperada"

if __name__ == "__main__":
    test_import_registry()
    test_registry_basic_structure()
    print("Smoke test PASSED")
EOF

    # Ejecutar smoke test
    cd /tmp/mcp_smoke_test
    python test_registry_smoke.py >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/smoke-test-creado.log 2>&1
    cd /home/user/IACT---project
fi
```

**Resultado Esperado:** Smoke test creado y ejecutado exitosamente (si no habia tests)

### Paso 5: Documentar baseline de tests
```bash
# Crear resumen del estado de tests
cat > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/baseline-tests.txt << EOF
=== BASELINE DE TESTS MCP REGISTRY ===
Fecha: $(date +"%Y-%m-%d %H:%M:%S")
Branch: $(git branch --show-current)
Commit: $(git rev-parse --short HEAD)

Tests encontrados: $(find . -path "*/test*" -name "*.py" -type f -exec grep -l "mcp.*registry" {} \; 2>/dev/null | wc -l)

Estado inicial: Ver archivos ejecucion-tests.log o smoke-test-creado.log

Archivos relacionados:
$(ls -1 /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/)

EOF
```

**Resultado Esperado:** Archivo baseline-tests.txt con resumen completo

---

## Criterios de Exito

- [ ] Busqueda de tests completada en todo el proyecto
- [ ] Numero de tests existentes documentado
- [ ] Tests encontrados ejecutados exitosamente (si existen)
- [ ] Smoke test creado y ejecutado si no habia tests previos
- [ ] Baseline de estado de tests documentado en evidencias
- [ ] Resultado de ejecucion (PASS/FAIL) capturado en logs

---

## Validacion

```bash
# Verificar que la busqueda se realizo
test -f /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/busqueda-tests.log && echo "VALIDACION OK: Busqueda realizada" || echo "ERROR: Busqueda no realizada"

# Verificar que hay evidencias de ejecucion
test -f /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/ejecucion-tests.log || test -f /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/smoke-test-creado.log && echo "VALIDACION OK: Tests ejecutados" || echo "ERROR: No hay evidencias de ejecucion"

# Verificar baseline creado
test -f /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/baseline-tests.txt && echo "VALIDACION OK: Baseline documentado" || echo "ERROR: Baseline no creado"

# Listar todas las evidencias
ls -lh /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/
```

**Salida Esperada:**
- `VALIDACION OK: Busqueda realizada`
- `VALIDACION OK: Tests ejecutados`
- `VALIDACION OK: Baseline documentado`
- Lista de archivos de evidencias

---

## Rollback

Si falla esta tarea:
```bash
# Limpiar smoke test temporal si fue creado
rm -rf /tmp/mcp_smoke_test

# Limpiar evidencias parciales
rm -rf /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-002-verificar-tests-mcp/evidencias/*

# Reintentar desde Paso 1
```

**Nota:** Esta tarea no modifica el repositorio, solo ejecuta tests y crea evidencias.

---

## Evidencias Requeridas

Las siguientes evidencias deben guardarse en `evidencias/`:

1. **busqueda-tests.log** - Lista de archivos encontrados en busqueda de tests MCP
2. **tests-encontrados.log** - Tests que importan el modulo registry
3. **ejecucion-tests.log** - Output de ejecucion de tests existentes
4. **smoke-test-creado.log** - Output del smoke test si fue necesario crearlo
5. **baseline-tests.txt** - Resumen del estado inicial de tests (baseline TDD)

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| No existen tests para MCP registry | MEDIA | MEDIO | Crear smoke test basico de importacion |
| Tests existentes fallan en baseline | BAJA | ALTO | Documentar estado, notificar antes de continuar |
| Framework de tests no instalado | BAJA | MEDIO | Usar smoke test con Python basico (sin pytest) |
| Modulo registry no importable | MUY BAJA | ALTO | Bloquear plan, resolver dependencias primero |

---

## Notas TDD

Esta tarea establece el **BASELINE** del ciclo TDD:

- **Tests primero:** Verificar que existen tests antes de refactorizar
- **Estado conocido:** Documentar si tests pasan o fallan ANTES de cambios
- **Smoke test fallback:** Si no hay tests, crear validacion minima de importacion
- **Baseline obligatorio:** Sin baseline, no hay forma de detectar regresiones

El baseline creado aqui sera comparado en:
- TASK-006 (despues de refactor Playwright)
- TASK-010 (despues de refactor PEP 585)
- TASK-012 (validacion final)

**IMPORTANTE:** Si tests fallan en baseline, documentar y analizar ANTES de continuar. Las refactorizaciones no deben introducir nuevos fallos, pero tampoco deben ocultar problemas preexistentes.

---

## Checklist de Finalizacion

- [ ] Todos los pasos ejecutados exitosamente
- [ ] Criterios de exito cumplidos
- [ ] Validaciones pasadas
- [ ] Evidencias guardadas en evidencias/
- [ ] Baseline de tests documentado
- [ ] Estado PASS/FAIL claramente identificado
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
