---
id: TASK-REFACTOR-MCP-003
tipo: validacion-prerequisitos
categoria: refactorizacion-mcp
titulo: Validar Entorno Python
fase: FASE_1
prioridad: CRITICA
duracion_estimada: 5min
estado: pendiente
dependencias: ["TASK-001", "TASK-002"]
---

# TASK-REFACTOR-MCP-003: Validar Entorno Python

**Fase:** FASE 1 - Preparacion
**Prioridad:** CRITICA
**Duracion Estimada:** 5 minutos
**Tipo TDD:** Validacion Prerequisitos
**Responsable:** Agente Claude
**Estado:** PENDIENTE

---

## Objetivo

Validar que el entorno Python cumple con los requisitos minimos para aplicar la refactorizacion PEP 585 (Python 3.9+) y verificar disponibilidad de herramientas de validacion de tipos (mypy, pyright). Esta validacion es BLOQUEANTE para la FASE 3 del plan.

---

## Prerequisitos

- [ ] TASK-001 completada (backup creado)
- [ ] TASK-002 completada (baseline de tests establecido)
- [ ] Python accesible desde linea de comandos
- [ ] pip instalado para verificar paquetes disponibles

---

## Pasos de Ejecucion

### Paso 1: Verificar version de Python
```bash
python --version > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/python-version.log 2>&1
python3 --version >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/python-version.log 2>&1

# Verificar version numerica
python -c "import sys; print(f'Version numerica: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/python-version.log
```

**Resultado Esperado:** Version Python 3.9 o superior documentada

### Paso 2: Validar compatibilidad con PEP 585
```bash
# PEP 585 requiere Python 3.9+
python -c "
import sys
major, minor = sys.version_info.major, sys.version_info.minor
pep585_compatible = (major == 3 and minor >= 9) or major > 3

print(f'Python version: {major}.{minor}')
print(f'PEP 585 compatible: {pep585_compatible}')

if not pep585_compatible:
    print('ERROR: Python < 3.9 no soporta PEP 585')
    print('ACCION REQUERIDA: Actualizar Python a version 3.9 o superior')
    sys.exit(1)
else:
    print('OK: Python version compatible con PEP 585')
" > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/pep585-compatibilidad.log 2>&1

# Guardar codigo de salida
echo "Exit code: $?" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/pep585-compatibilidad.log
```

**Resultado Esperado:** Mensaje "OK: Python version compatible con PEP 585" y exit code 0

### Paso 3: Probar sintaxis PEP 585
```bash
# Crear script de prueba con sintaxis PEP 585
cat > /tmp/test_pep585.py << 'EOF'
"""Test de sintaxis PEP 585"""

# Sintaxis PEP 585 (Python 3.9+)
def test_pep585_syntax() -> dict[str, str]:
    """Funcion que usa dict minuscula en lugar de Dict"""
    result: dict[str, str] = {"test": "ok"}
    return result

# Intentar ejecutar
if __name__ == "__main__":
    result = test_pep585_syntax()
    print(f"PEP 585 syntax test: {result}")
    print("OK: Sintaxis PEP 585 soportada")
EOF

# Ejecutar prueba
python /tmp/test_pep585.py > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/pep585-syntax-test.log 2>&1

# Guardar resultado
echo "Exit code: $?" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/pep585-syntax-test.log

# Limpiar
rm /tmp/test_pep585.py
```

**Resultado Esperado:** Script ejecutado sin errores, mensaje "OK: Sintaxis PEP 585 soportada"

### Paso 4: Verificar disponibilidad de type checkers
```bash
# Verificar mypy
which mypy > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log 2>&1
if [ $? -eq 0 ]; then
    mypy --version >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log 2>&1
    echo "mypy: DISPONIBLE" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log
else
    echo "mypy: NO DISPONIBLE" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log
fi

# Verificar pyright
which pyright >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log 2>&1
if [ $? -eq 0 ]; then
    pyright --version >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log 2>&1
    echo "pyright: DISPONIBLE" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log
else
    echo "pyright: NO DISPONIBLE" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log
fi

# Verificar pylint (opcional)
which pylint >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log 2>&1
if [ $? -eq 0 ]; then
    pylint --version >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log 2>&1
    echo "pylint: DISPONIBLE" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log
else
    echo "pylint: NO DISPONIBLE" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log
fi
```

**Resultado Esperado:** Lista de type checkers disponibles (al menos uno es deseable)

### Paso 5: Verificar modulo typing
```bash
# Verificar que el modulo typing esta disponible y funcional
python -c "
from typing import Tuple, Optional
import sys

print('Modulo typing: DISPONIBLE')
print(f'typing.__version__: {getattr(sys.modules[\"typing\"], \"__version__\", \"N/A\")}')

# Verificar que dict builtin tiene __getitem__ (requerido para PEP 585)
test_dict = dict[str, str]
print(f'dict[str, str]: {test_dict}')
print('OK: Type hints funcionando correctamente')
" > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/typing-module.log 2>&1

echo "Exit code: $?" >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/typing-module.log
```

**Resultado Esperado:** Modulo typing funcional, dict[str, str] soportado

### Paso 6: Crear resumen de validacion
```bash
cat > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/resumen-validacion.txt << EOF
=== VALIDACION ENTORNO PYTHON ===
Fecha: $(date +"%Y-%m-%d %H:%M:%S")

PYTHON VERSION:
$(cat /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/python-version.log)

PEP 585 COMPATIBILIDAD:
$(cat /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/pep585-compatibilidad.log)

TYPE CHECKERS DISPONIBLES:
$(cat /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log)

DECISION:
$(python -c "import sys; major, minor = sys.version_info.major, sys.version_info.minor; print('CONTINUAR CON PLAN' if (major == 3 and minor >= 9) or major > 3 else 'ABORTAR PLAN - Python < 3.9')")

EOF
```

**Resultado Esperado:** Resumen completo con decision de continuar o abortar

---

## Criterios de Exito

- [ ] Python version >= 3.9 confirmado
- [ ] Compatibilidad PEP 585 verificada (exit code 0)
- [ ] Sintaxis PEP 585 ejecutada sin errores
- [ ] Al menos un type checker disponible (mypy o pyright) - DESEABLE pero no bloqueante
- [ ] Modulo typing funcional y dict[str, str] soportado
- [ ] Resumen de validacion creado con decision clara (CONTINUAR/ABORTAR)

---

## Validacion

```bash
# Validacion critica: Python >= 3.9
PYTHON_OK=$(python -c "import sys; print('OK' if (sys.version_info.major == 3 and sys.version_info.minor >= 9) or sys.version_info.major > 3 else 'FAIL')")
echo "Python version check: $PYTHON_OK"

# Validacion: PEP 585 syntax
PEP585_OK=$(grep -q "OK: Sintaxis PEP 585 soportada" /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/pep585-syntax-test.log && echo "OK" || echo "FAIL")
echo "PEP 585 syntax check: $PEP585_OK"

# Validacion: Type checkers (no bloqueante)
TYPE_CHECKER_AVAILABLE=$(grep -q "DISPONIBLE" /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/type-checkers.log && echo "YES" || echo "NO")
echo "Type checker available: $TYPE_CHECKER_AVAILABLE (not blocking)"

# Decision final
if [ "$PYTHON_OK" = "OK" ] && [ "$PEP585_OK" = "OK" ]; then
    echo "DECISION: CONTINUAR CON PLAN DE REFACTORIZACIONES"
    exit 0
else
    echo "DECISION: ABORTAR PLAN - Requisitos no cumplidos"
    exit 1
fi
```

**Salida Esperada:**
- `Python version check: OK`
- `PEP 585 syntax check: OK`
- `Type checker available: YES` (o NO, pero no bloqueante)
- `DECISION: CONTINUAR CON PLAN DE REFACTORIZACIONES`
- Exit code: 0

---

## Rollback

Si falla esta tarea:
```bash
# No hay rollback necesario, esta tarea solo valida

# Si Python < 3.9: ABORTAR PLAN COMPLETO
# Notificar al usuario que necesita Python 3.9+

# Limpiar evidencias si se desea reintentar
rm -rf /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-003-validar-entorno-python/evidencias/*
```

**IMPORTANTE:** Si Python < 3.9, NO continuar con el plan. La refactorizacion PEP 585 es incompatible con versiones anteriores.

---

## Evidencias Requeridas

Las siguientes evidencias deben guardarse en `evidencias/`:

1. **python-version.log** - Version de Python instalada
2. **pep585-compatibilidad.log** - Verificacion de compatibilidad con PEP 585
3. **pep585-syntax-test.log** - Prueba de sintaxis PEP 585 ejecutada
4. **type-checkers.log** - Disponibilidad de mypy, pyright, pylint
5. **typing-module.log** - Verificacion del modulo typing
6. **resumen-validacion.txt** - Resumen completo con decision CONTINUAR/ABORTAR

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| Python < 3.9 | BAJA | CRITICO | ABORTAR plan, notificar usuario para upgrade |
| Type checkers no disponibles | MEDIA | BAJO | Validacion manual en TASK-011, documentar ausencia |
| Sintaxis PEP 585 no soportada | MUY BAJA | CRITICO | Indicaria inconsistencia en version Python |
| Modulo typing corrupto | MUY BAJA | ALTO | Reinstalar Python o usar entorno virtual limpio |

---

## Notas TDD

Esta tarea es un **GATE CRITICO** del plan:

- **Prerequisito obligatorio:** Sin Python 3.9+, FASE 3 (PEP 585) es imposible
- **Decision temprana:** Validar antes de invertir tiempo en refactorizaciones
- **Abortar rapido:** Si falla, detener plan inmediatamente
- **Documentar estado:** Evidencias necesarias para troubleshooting

**DECISION LOGIC:**
- Python >= 3.9 + PEP 585 OK → CONTINUAR
- Python < 3.9 → ABORTAR PLAN COMPLETO
- Type checkers ausentes → CONTINUAR (validacion manual en TASK-011)

Esta tarea NO es opcional. Es un checkpoint bloqueante para las fases de refactorizacion.

---

## Checklist de Finalizacion

- [ ] Todos los pasos ejecutados exitosamente
- [ ] Criterios de exito cumplidos
- [ ] Python >= 3.9 confirmado (BLOQUEANTE)
- [ ] PEP 585 syntax test pasado (BLOQUEANTE)
- [ ] Validaciones pasadas
- [ ] Evidencias guardadas en evidencias/
- [ ] Resumen de validacion creado
- [ ] Decision documentada: CONTINUAR o ABORTAR
- [ ] Tarea marcada como COMPLETADA (solo si CONTINUAR)

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
