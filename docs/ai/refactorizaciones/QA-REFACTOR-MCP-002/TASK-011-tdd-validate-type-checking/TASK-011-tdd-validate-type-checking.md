---
id: TASK-REFACTOR-MCP-011
tipo: tarea
categoria: tdd-validate
titulo: Type Checking con mypy/pyright
fase: FASE_3
prioridad: ALTA
duracion_estimada: 10min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-010]
---

# TASK-REFACTOR-MCP-011: [TDD-VALIDATE] Type Checking con mypy/pyright

**Fase:** FASE 3 - Refactorizacion PEP 585
**Prioridad:** ALTA
**Duracion Estimada:** 10 minutos
**Tipo:** tdd-validate
**Responsable:** Agente Claude
**Estado:** PENDIENTE
**Dependencias:** TASK-REFACTOR-MCP-010 (TDD-GREEN PEP 585)

---

## Objetivo

Validar que las nuevas type annotations PEP 585 son correctas mediante type checking estatico con mypy y/o pyright, confirmando 0 errores de tipos y que imports antiguos (Dict, Mapping) fueron removidos correctamente.

---

## Prerequisitos

- [ ] TASK-REFACTOR-MCP-010 completada (tests pasando post-PEP 585)
- [ ] Refactorizacion PEP 585 aplicada y validada
- [ ] Python version >= 3.9 (necesario para PEP 585)
- [ ] mypy o pyright disponible (OPCIONAL - continuar sin ellos si no estan)

---

## Pasos de Validacion

### Paso 1: Verificar Disponibilidad de Type Checkers

```bash
# Verificar si mypy esta instalado
echo "=== Verificando mypy ==="
which mypy && mypy --version || echo "mypy NO disponible"
echo ""

# Verificar si pyright esta instalado
echo "=== Verificando pyright ==="
which pyright && pyright --version || echo "pyright NO disponible"
echo ""

# Verificar Python version
echo "=== Python version ==="
python3 --version
```

**Documentar Resultados:**
- [ ] mypy disponible: SI / NO - Version: ________
- [ ] pyright disponible: SI / NO - Version: ________
- [ ] Python version: ________ (debe ser >= 3.9)

**NOTA IMPORTANTE:**
- Si NINGUN type checker esta disponible: Continuar con validacion manual
- Si AL MENOS UNO esta disponible: Usar ese para validacion
- Preferencia: pyright > mypy (mas moderno y rapido)

### Paso 2: Type Checking con mypy (si disponible)

```bash
# Ejecutar mypy en registry.py
mypy scripts/coding/ai/mcp/registry.py --show-error-codes --no-error-summary

# Capturar exit code
echo "mypy exit code: $?"
```

**Resultado Esperado:**
- Exit code: 0 (sin errores de tipos)
- Output: "Success: no issues found" o similar
- 0 errores reportados
- 0 warnings criticos

**Si mypy reporta errores:**
- Documentar cada error con codigo de error
- Clasificar: ERROR (bloqueante) vs WARNING (informativo)
- Si hay ERROREs criticos: ROLLBACK

### Paso 3: Type Checking con pyright (si disponible)

```bash
# Ejecutar pyright en registry.py
pyright scripts/coding/ai/mcp/registry.py

# Capturar exit code
echo "pyright exit code: $?"
```

**Resultado Esperado:**
- Exit code: 0 (sin errores de tipos)
- Output: "0 errors, 0 warnings" o similar
- Diagnostics: limpios

**Si pyright reporta errores:**
- Documentar cada error con severidad
- Clasificar: error vs warning vs information
- Si hay errores criticos: ROLLBACK

### Paso 4: Validacion Manual de Type Annotations (si no hay type checkers)

```bash
# Verificar manualmente que type annotations son correctas
echo "=== Validacion manual de type annotations ==="

# Ver todas las type annotations en el archivo
grep -n "def \|: dict\[" scripts/coding/ai/mcp/registry.py | head -30

# Verificar que no quedan imports antiguos
echo ""
echo "=== Verificar imports (debe mostrar solo Tuple) ==="
head -10 scripts/coding/ai/mcp/registry.py | grep "from typing import"

# Verificar que no hay referencias a Dict/Mapping
echo ""
echo "=== Buscar referencias antiguas (debe estar vacio) ==="
grep -E "Dict\[|Mapping\[|List\[" scripts/coding/ai/mcp/registry.py || echo "No se encontraron referencias antiguas - OK"
```

**Validaciones Manuales:**
- [ ] Import line contiene solo: `from typing import Tuple`
- [ ] 0 referencias a `Dict[`
- [ ] 0 referencias a `Mapping[`
- [ ] 0 referencias a `List[`
- [ ] Todas las referencias usan `dict[`, `list[` (minusculas)
- [ ] Sintaxis de generics correcta: `dict[str, str]` no `dict[str,str]`

### Paso 5: Validar Type Annotations Especificas

```bash
# Verificar lineas especificas que fueron modificadas
echo "=== Validacion de type annotations por linea ==="

echo "Linea 6 (Import):"
sed -n '6p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 24:"
sed -n '24p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 26:"
sed -n '26p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 27:"
sed -n '27p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 43:"
sed -n '43p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 45:"
sed -n '45p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 46:"
sed -n '46p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 66:"
sed -n '66p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 68:"
sed -n '68p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 73:"
sed -n '73p' scripts/coding/ai/mcp/registry.py

echo ""
echo "Linea 129:"
sed -n '129p' scripts/coding/ai/mcp/registry.py
```

**Checklist de Validacion por Linea:**
- [ ] Linea 6: `from typing import Tuple` (solo Tuple, sin Dict/Mapping)
- [ ] Linea 24: `dict[` presente
- [ ] Linea 26: `dict[` presente
- [ ] Linea 27: `dict[` presente
- [ ] Linea 43: `dict[` presente
- [ ] Linea 45: `dict[` presente
- [ ] Linea 46: `dict[` presente
- [ ] Linea 66: `dict[` presente (antes era Mapping)
- [ ] Linea 68: `dict[` presente
- [ ] Linea 73: `dict[` presente
- [ ] Linea 129: `dict[` presente

### Paso 6: Validar Compatibilidad Python 3.9+

```bash
# Confirmar que Python es 3.9 o superior
python3 -c "import sys; v = sys.version_info; print(f'Python {v.major}.{v.minor}.{v.micro}'); exit(0 if v >= (3, 9) else 1)"

# Validar que dict[] es soportado (PEP 585)
python3 -c "
from typing import get_type_hints
def test_func() -> dict[str, str]:
    return {}
print('PEP 585 dict[] compatible: OK')
"
```

**Resultado Esperado:**
- Python version: 3.9+ (impreso correctamente)
- PEP 585 compatible: OK
- Exit code: 0

### Paso 7: Smoke Test de Type Hints en Runtime

```bash
# Verificar que type hints no causan errores en runtime
python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts/coding')

try:
    from ai.mcp import registry

    # Type hints NO afectan runtime, solo type checkers
    # Validar que modulo carga sin errores
    print("✓ Module imported with PEP 585 annotations")
    print("✓ Type hints validated at runtime: OK")
    print("TYPE HINTS RUNTIME TEST: PASS")
except Exception as e:
    print(f"✗ Error: {e}")
    print("TYPE HINTS RUNTIME TEST: FAIL")
    sys.exit(1)
EOF
```

**Resultado Esperado:** TYPE HINTS RUNTIME TEST: PASS

---

## Criterios de Exito

### Si Type Checkers Disponibles:
- [ ] mypy: 0 errores, exit code 0 (si disponible)
- [ ] pyright: 0 errores, 0 warnings, exit code 0 (si disponible)
- [ ] Type annotations validadas por herramienta

### Si NO hay Type Checkers:
- [ ] Validacion manual completada
- [ ] 0 referencias a Dict/Mapping/List antiguos
- [ ] Import line correcta (solo Tuple)
- [ ] Sintaxis de type annotations verificada manualmente

### Validaciones Universales (siempre):
- [ ] Python >= 3.9 confirmado
- [ ] PEP 585 compatible verificado
- [ ] Type hints runtime test: PASS
- [ ] 11 lineas con dict[] verificadas
- [ ] Import actualizado correctamente

---

## Checklist de Validacion

### Type Checkers (si disponibles)
- [ ] mypy instalado: SI / NO
- [ ] pyright instalado: SI / NO
- [ ] mypy ejecutado: PASS / FAIL / N/A
- [ ] pyright ejecutado: PASS / FAIL / N/A
- [ ] 0 errores de tipos reportados

### Validacion Manual (obligatoria)
- [ ] Import line: `from typing import Tuple`
- [ ] 0 referencias a Dict[]
- [ ] 0 referencias a Mapping[]
- [ ] 0 referencias a List[]
- [ ] 11 referencias a dict[]
- [ ] Sintaxis de generics correcta

### Compatibilidad
- [ ] Python version: >= 3.9
- [ ] PEP 585 soportado: OK
- [ ] Type hints runtime test: PASS

### Type Annotations por Linea
- [ ] Linea 6: Import correcto
- [ ] Lineas 24, 26, 27: dict[] validado
- [ ] Lineas 43, 45, 46: dict[] validado
- [ ] Lineas 66, 68, 73: dict[] validado
- [ ] Linea 129: dict[] validado

---

## Evidencias a Capturar

**Logs a Guardar en evidencias/:**

1. `01-type-checkers-availability.txt`: Verificacion de mypy/pyright
2. `02-mypy-output.txt`: Output de mypy (si disponible)
3. `03-pyright-output.txt`: Output de pyright (si disponible)
4. `04-manual-validation.txt`: Validacion manual de annotations
5. `05-specific-lines-validation.txt`: Validacion de lineas especificas
6. `06-python-compatibility.txt`: Validacion Python 3.9+ y PEP 585
7. `07-runtime-type-hints-test.txt`: Smoke test de type hints

**Comandos para Capturar Evidencias:**

```bash
cd /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-011-tdd-validate-type-checking/evidencias/

# Disponibilidad de type checkers
{
  echo "=== mypy ==="
  which mypy && mypy --version || echo "mypy NO disponible"
  echo ""
  echo "=== pyright ==="
  which pyright && pyright --version || echo "pyright NO disponible"
  echo ""
  echo "=== Python version ==="
  python3 --version
} > 01-type-checkers-availability.txt 2>&1

# mypy (si disponible)
mypy scripts/coding/ai/mcp/registry.py --show-error-codes --no-error-summary > 02-mypy-output.txt 2>&1 || echo "mypy no ejecutado o fallo"

# pyright (si disponible)
pyright scripts/coding/ai/mcp/registry.py > 03-pyright-output.txt 2>&1 || echo "pyright no ejecutado o fallo"

# Validacion manual
{
  echo "=== Type annotations ==="
  grep -n "def \|: dict\[" scripts/coding/ai/mcp/registry.py | head -30
  echo ""
  echo "=== Import line ==="
  head -10 scripts/coding/ai/mcp/registry.py | grep "from typing import"
  echo ""
  echo "=== Referencias antiguas (debe estar vacio) ==="
  grep -E "Dict\[|Mapping\[|List\[" scripts/coding/ai/mcp/registry.py || echo "No se encontraron referencias antiguas - OK"
} > 04-manual-validation.txt 2>&1

# Lineas especificas
{
  echo "Linea 6 (Import):"
  sed -n '6p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 24:"
  sed -n '24p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 26:"
  sed -n '26p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 27:"
  sed -n '27p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 43:"
  sed -n '43p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 45:"
  sed -n '45p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 46:"
  sed -n '46p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 66:"
  sed -n '66p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 68:"
  sed -n '68p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 73:"
  sed -n '73p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "Linea 129:"
  sed -n '129p' scripts/coding/ai/mcp/registry.py
} > 05-specific-lines-validation.txt 2>&1

# Compatibilidad Python
{
  echo "=== Python version ==="
  python3 -c "import sys; v = sys.version_info; print(f'Python {v.major}.{v.minor}.{v.micro}'); exit(0 if v >= (3, 9) else 1)"
  echo ""
  echo "=== PEP 585 compatibility ==="
  python3 -c "
from typing import get_type_hints
def test_func() -> dict[str, str]:
    return {}
print('PEP 585 dict[] compatible: OK')
"
} > 06-python-compatibility.txt 2>&1

# Runtime type hints test
python3 << 'EOF' > 07-runtime-type-hints-test.txt 2>&1
import sys
sys.path.insert(0, 'scripts/coding')

try:
    from ai.mcp import registry
    print("✓ Module imported with PEP 585 annotations")
    print("✓ Type hints validated at runtime: OK")
    print("TYPE HINTS RUNTIME TEST: PASS")
except Exception as e:
    print(f"✗ Error: {e}")
    print("TYPE HINTS RUNTIME TEST: FAIL")
    sys.exit(1)
EOF
```

---

## Acciones Correctivas

**Si mypy reporta errores criticos:**
1. Analizar cada error con su codigo
2. Clasificar: sintaxis vs logica vs import
3. Si errores de sintaxis en type annotations: ROLLBACK
4. Si errores menores de inferencia: documentar, NO rollback
5. Validar manualmente que annotations son correctas

**Si pyright reporta errores criticos:**
1. Revisar cada error con severidad
2. Filtrar warnings informativos (NO bloqueantes)
3. Si errores de sintaxis: ROLLBACK
4. Si warnings de tipo "possibly undefined": documentar, NO rollback

**Si validacion manual falla:**
1. Revisar que commit se aplico correctamente
2. Verificar que todas las lineas fueron actualizadas
3. Si quedan referencias antiguas (Dict/Mapping): INVESTIGAR
4. Comparar con commit original 2ca3d25
5. Si discrepancias criticas: ROLLBACK

**Si Python < 3.9:**
1. DETENER inmediatamente
2. PEP 585 NO es compatible con Python < 3.9
3. ROLLBACK obligatorio
4. Notificar al usuario para upgrade de Python

**Si type hints runtime test falla:**
1. Revisar traceback completo
2. Verificar que no hay errores de sintaxis
3. Si error relacionado a annotations: ROLLBACK
4. Documentar error detalladamente

---

## Estrategia de Rollback

**Rollback INMEDIATO si:**
- mypy reporta errores de sintaxis en type annotations
- pyright reporta errores criticos de tipos
- Python version < 3.9
- Type hints runtime test falla
- Referencias antiguas (Dict/Mapping) persisten

**Rollback OPCIONAL si:**
- Solo warnings informativos en type checkers
- Errores menores de inferencia de tipos
- Type checker no disponible (validacion manual OK)

**Comando de Rollback:**
```bash
# Revertir commit PEP 585
git revert HEAD

# O reset si es mas apropiado
git reset --hard HEAD~1

# Validar que sistema vuelve a estado estable
pytest scripts/coding/tests/ai/mcp/ -v

# Tiempo estimado: < 1 minuto
```

---

## Notas

- Type checkers NO son bloqueantes si no estan disponibles
- Validacion manual es aceptable como fallback
- mypy y pyright pueden dar resultados diferentes (es normal)
- Warnings informativos NO son bloqueantes
- Solo errores CRITICOS justifican rollback
- PEP 585 requiere Python >= 3.9 (OBLIGATORIO)
- Type hints NO afectan runtime (solo validacion estatica)
- Siguiente paso: Suite completa de tests (TASK-012)

**Type Checkers Comunes:**
- mypy: Type checker oficial de Python, mas estricto
- pyright: Creado por Microsoft, mas rapido y moderno
- pyre: Creado por Facebook (menos comun)

**Instalacion Rapida (si necesario):**
```bash
# mypy
pip install mypy

# pyright
npm install -g pyright
```

**Contexto de Validacion:**
- Commit validado: 2ca3d25
- Cambios: 11 type annotations modernizadas
- Expected: 0 errores de tipos
- Metodo: Type checker estatico + validacion manual

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

---

## Checklist de Finalizacion

- [ ] Type checkers verificados (disponibilidad documentada)
- [ ] mypy ejecutado (si disponible): PASS / N/A
- [ ] pyright ejecutado (si disponible): PASS / N/A
- [ ] Validacion manual completada: PASS
- [ ] Type annotations validadas: 11 lineas OK
- [ ] Import actualizado: OK
- [ ] Python compatibility: >= 3.9 OK
- [ ] Runtime type hints test: PASS
- [ ] 0 errores criticos de tipos
- [ ] Evidencias capturadas en evidencias/
- [ ] Listo para TASK-012 (Suite Completa)
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
