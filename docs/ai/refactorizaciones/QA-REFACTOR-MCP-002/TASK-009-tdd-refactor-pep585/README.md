---
id: TASK-REFACTOR-MCP-009
tipo: tarea
categoria: tdd-refactor
titulo: Aplicar Commit PEP 585
fase: FASE_3
prioridad: ALTA
duracion_estimada: 5min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-008]
commit: 2ca3d25
---

# TASK-REFACTOR-MCP-009: [TDD-REFACTOR] Aplicar Commit PEP 585

**Fase:** FASE 3 - Refactorizacion PEP 585
**Prioridad:** ALTA
**Duracion Estimada:** 5 minutos
**Tipo:** tdd-refactor
**Responsable:** Agente Claude
**Estado:** PENDIENTE
**Dependencias:** TASK-REFACTOR-MCP-008 (TDD-RED PEP 585)
**Commit a Aplicar:** 2ca3d25

---

## Objetivo

Aplicar la refactorizacion de modernizacion de type annotations a PEP 585 mediante cherry-pick del commit 2ca3d25, que actualiza Dict/List/Mapping a dict/list y elimina imports innecesarios de typing.

---

## Prerequisitos

- [ ] TASK-REFACTOR-MCP-008 completada (baseline de tests documentada)
- [ ] Tests MCP pasando antes de refactorizacion
- [ ] Python version >= 3.9 validada
- [ ] Git working directory limpio

---

## Pasos de Ejecucion

### Paso 1: Verificar Estado Pre-Refactorizacion

```bash
# Verificar que estamos en rama correcta
git branch --show-current

# Verificar que working directory esta limpio
git status

# Verificar commit a aplicar
git log --oneline -1 2ca3d25
```

**Validaciones:**
- [ ] Rama: claude/fix-branch-issues-013FpGsYZUySbBL6bsMbhBf2
- [ ] Working directory: limpio (no cambios pendientes)
- [ ] Commit 2ca3d25 existe y es accesible

### Paso 2: Aplicar Cherry-Pick del Commit PEP 585

```bash
# Cherry-pick commit de refactorizacion PEP 585
git cherry-pick 2ca3d25

# Capturar resultado
echo "Cherry-pick exit code: $?"
```

**Resultados Esperados:**
- Exit code: 0 (exito)
- Mensaje: "refactor: modernize type annotations to PEP 585 style"
- Archivos modificados: 1 (scripts/coding/ai/mcp/registry.py)
- Cambios: 11 insertions(+), 11 deletions(-)

### Paso 3: Resolver Conflictos (si existen)

```bash
# Verificar si hay conflictos
git status | grep -E "(both modified|Unmerged)"

# Si hay conflictos, listarlos
if [ $? -eq 0 ]; then
  echo "CONFLICTOS DETECTADOS:"
  git diff --name-only --diff-filter=U
fi
```

**Plan de Resolucion de Conflictos:**

Si hay conflictos en registry.py:
1. Abrir archivo y localizar marcadores de conflicto
2. Aplicar cambios manualmente usando diff del commit original
3. Verificar que cambios son identicos a commit 2ca3d25
4. Ejecutar: `git add scripts/coding/ai/mcp/registry.py`
5. Ejecutar: `git cherry-pick --continue`

**IMPORTANTE:** Si conflictos son complejos, documentar y solicitar revision manual.

### Paso 4: Validar Cambios Aplicados

```bash
# Ver diff del commit aplicado
git show HEAD

# Contar cambios aplicados
echo "Cambios en registry.py:"
git diff HEAD~1 HEAD scripts/coding/ai/mcp/registry.py | grep -E "^[\+\-]" | wc -l
```

**Validaciones Esperadas:**
- [ ] Linea 6: `from typing import Dict, Mapping, Tuple` → `from typing import Tuple`
- [ ] Dict/Mapping removidos de imports
- [ ] 11 ocurrencias de Dict/Mapping reemplazadas por dict
- [ ] Total de lineas modificadas: ~22 (11 insertions + 11 deletions)

### Paso 5: Validar Sintaxis Basica

```bash
# Validar sintaxis Python del archivo modificado
python3 -m py_compile scripts/coding/ai/mcp/registry.py 2>&1

# Verificar exit code
if [ $? -eq 0 ]; then
  echo "SINTAXIS: OK"
else
  echo "SINTAXIS: ERROR - revisar archivo"
fi
```

**Resultado Esperado:** SINTAXIS: OK

### Paso 6: Verificar Cambios Especificos de PEP 585

```bash
# Verificar que Dict/Mapping fueron removidos de imports
echo "=== Verificar imports actualizados ==="
head -10 scripts/coding/ai/mcp/registry.py | grep "from typing import"

# Verificar que no quedan referencias a Dict/Mapping de typing
echo ""
echo "=== Buscar referencias antiguas (debe estar vacio) ==="
grep -n "Dict\[" scripts/coding/ai/mcp/registry.py || echo "No se encontraron referencias a Dict[] - OK"
grep -n "Mapping\[" scripts/coding/ai/mcp/registry.py || echo "No se encontraron referencias a Mapping[] - OK"

# Verificar nuevas referencias a dict (minuscula)
echo ""
echo "=== Verificar nuevas referencias a dict ==="
grep -n "dict\[" scripts/coding/ai/mcp/registry.py | wc -l
echo "Referencias a dict[] encontradas (esperado: 11)"
```

**Validaciones:**
- [ ] Import de typing NO contiene Dict ni Mapping
- [ ] Import de typing contiene solo: Tuple
- [ ] 0 referencias a Dict[] en el archivo
- [ ] 0 referencias a Mapping[] en el archivo
- [ ] 11 referencias a dict[] en el archivo

### Paso 7: Verificar Lineas Modificadas Detalladamente

```bash
# Ver lineas especificas modificadas segun plan
echo "=== Verificar cambios en lineas especificas ==="
sed -n '6p' scripts/coding/ai/mcp/registry.py  # Import line
echo ""
sed -n '24,27p' scripts/coding/ai/mcp/registry.py  # Type annotations
echo ""
sed -n '43,46p' scripts/coding/ai/mcp/registry.py  # Type annotations
echo ""
sed -n '66,68p' scripts/coding/ai/mcp/registry.py  # Type annotations
echo ""
sed -n '73p' scripts/coding/ai/mcp/registry.py     # Type annotation
echo ""
sed -n '129p' scripts/coding/ai/mcp/registry.py    # Type annotation
```

**Documentar Output:** (Se espera ver dict[str, ...] en lugar de Dict[str, ...])

---

## Criterios de Exito

- [ ] Cherry-pick ejecutado exitosamente (exit code 0)
- [ ] Conflictos resueltos (si existian)
- [ ] 1 archivo modificado: scripts/coding/ai/mcp/registry.py
- [ ] 22 cambios totales (11 insertions + 11 deletions)
- [ ] Sintaxis Python valida
- [ ] Import actualizado: `from typing import Tuple` (sin Dict/Mapping)
- [ ] 0 referencias a Dict[] o Mapping[] en registry.py
- [ ] 11 referencias a dict[] en registry.py
- [ ] Commit aplicado aparece en git log

---

## Checklist de Validacion

### Estado Git
- [ ] Working directory limpio antes de cherry-pick
- [ ] Cherry-pick exitoso
- [ ] Commit 2ca3d25 aplicado en HEAD
- [ ] Sin conflictos pendientes

### Cambios en Codigo
- [ ] Linea 6: Import actualizado (solo Tuple)
- [ ] Linea 24: dict[] en lugar de Dict[]
- [ ] Linea 26: dict[] en lugar de Dict[]
- [ ] Linea 27: dict[] en lugar de Dict[]
- [ ] Linea 43: dict[] en lugar de Dict[]
- [ ] Linea 45: dict[] en lugar de Dict[]
- [ ] Linea 46: dict[] en lugar de Dict[]
- [ ] Linea 66: dict[] en lugar de Mapping[]
- [ ] Linea 68: dict[] en lugar de Dict[]
- [ ] Linea 73: dict[] en lugar de Dict[]
- [ ] Linea 129: dict[] en lugar de Dict[]

### Sintaxis y Validaciones
- [ ] py_compile exitoso
- [ ] 0 referencias antiguas (Dict/Mapping)
- [ ] 11 referencias nuevas (dict)

---

## Evidencias a Capturar

**Logs a Guardar en evidencias/:**

1. `01-pre-cherry-pick-status.txt`: Output de git status pre-refactorizacion
2. `02-cherry-pick-output.txt`: Output completo del comando cherry-pick
3. `03-post-cherry-pick-show.txt`: Output de git show HEAD
4. `04-py-compile-validation.txt`: Output de validacion de sintaxis
5. `05-import-verification.txt`: Verificacion de imports actualizados
6. `06-dict-references.txt`: Conteo de referencias a dict[]
7. `07-lineas-modificadas.txt`: Output de lineas especificas modificadas

**Comandos para Capturar Evidencias:**

```bash
cd /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-009-tdd-refactor-pep585/evidencias/

# Pre-cherry-pick
git status > 01-pre-cherry-pick-status.txt 2>&1

# Cherry-pick (capturar durante ejecucion)
git cherry-pick 2ca3d25 > 02-cherry-pick-output.txt 2>&1

# Post-cherry-pick
git show HEAD > 03-post-cherry-pick-show.txt 2>&1

# Validaciones
python3 -m py_compile scripts/coding/ai/mcp/registry.py > 04-py-compile-validation.txt 2>&1

# Verificacion de imports
{
  echo "=== Imports actualizados ==="
  head -10 scripts/coding/ai/mcp/registry.py | grep "from typing import"
  echo ""
  echo "=== Referencias antiguas (debe estar vacio) ==="
  grep -n "Dict\[" scripts/coding/ai/mcp/registry.py || echo "No Dict[] - OK"
  grep -n "Mapping\[" scripts/coding/ai/mcp/registry.py || echo "No Mapping[] - OK"
} > 05-import-verification.txt 2>&1

# Conteo de referencias
grep -n "dict\[" scripts/coding/ai/mcp/registry.py > 06-dict-references.txt 2>&1

# Lineas modificadas
{
  echo "=== Linea 6 (Import) ==="
  sed -n '6p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "=== Lineas 24-27 ==="
  sed -n '24,27p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "=== Lineas 43-46 ==="
  sed -n '43,46p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "=== Lineas 66-68 ==="
  sed -n '66,68p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "=== Linea 73 ==="
  sed -n '73p' scripts/coding/ai/mcp/registry.py
  echo ""
  echo "=== Linea 129 ==="
  sed -n '129p' scripts/coding/ai/mcp/registry.py
} > 07-lineas-modificadas.txt 2>&1
```

---

## Acciones Correctivas

**Si cherry-pick falla con conflictos:**
1. Revisar archivos con conflictos: `git diff --name-only --diff-filter=U`
2. Abrir scripts/coding/ai/mcp/registry.py
3. Buscar marcadores: `<<<<<<<`, `=======`, `>>>>>>>`
4. Aplicar cambios manualmente usando diff de commit 2ca3d25
5. Ejecutar: `git add scripts/coding/ai/mcp/registry.py`
6. Continuar: `git cherry-pick --continue`
7. Validar que resultado final es identico a commit original

**Si sintaxis Python falla:**
1. Revisar output de py_compile
2. Verificar que indentacion no se corrompio
3. Verificar que brackets estan balanceados
4. Si error critico: `git cherry-pick --abort` y ROLLBACK

**Si validaciones de PEP 585 fallan:**
1. Verificar manualmente que imports fueron actualizados
2. Buscar manualmente referencias a Dict/Mapping
3. Si cambios incorrectos: `git cherry-pick --abort` y aplicar manualmente

**Si cambios no coinciden con commit original:**
1. Ejecutar: `git diff 2ca3d25 HEAD scripts/coding/ai/mcp/registry.py`
2. Si hay diferencias: documentar y analizar causa
3. Considerar abortar cherry-pick y aplicar manualmente

---

## Estrategia de Rollback

**Rollback Inmediato:**
```bash
# Si cherry-pick no completado
git cherry-pick --abort

# Si cherry-pick ya completado pero con errores
git reset --hard HEAD~1

# Tiempo estimado: < 30 segundos
```

**Validacion Post-Rollback:**
```bash
# Verificar que estamos en estado pre-refactorizacion
git log -1 --oneline
git status

# Ejecutar tests para confirmar estado estable
pytest scripts/coding/tests/ai/mcp/ -v
```

---

## Notas

- Esta es una refactorizacion de estilo, NO funcional
- Cambios son automaticos de commit 2ca3d25
- PEP 585 requiere Python >= 3.9 (ya validado en TASK-003)
- Cambios son superficiales: Dict → dict, List → list, Mapping → dict
- No hay cambios en logica de negocio
- Siguiente paso: Ejecutar tests (TASK-010)

**Contexto del Commit Original:**
- Commit: 2ca3d2568f10f4df2b9e82932fa3794faf49caee
- Autor: copilot-swe-agent[bot]
- Fecha: 2025-11-16
- Mensaje: "refactor: modernize type annotations to PEP 585 style"

**Cambios del Commit:**
- 1 archivo modificado (scripts/coding/ai/mcp/registry.py)
- 11 insertions(+), 11 deletions(-)
- Lineas afectadas: 6, 24, 26, 27, 43, 45, 46, 66, 68, 73, 129

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

---

## Checklist de Finalizacion

- [ ] Cherry-pick ejecutado
- [ ] Conflictos resueltos (si existian)
- [ ] Cambios validados contra commit original
- [ ] Sintaxis Python correcta
- [ ] Imports actualizados correctamente
- [ ] PEP 585 aplicado en todas las lineas necesarias
- [ ] Evidencias capturadas en evidencias/
- [ ] Listo para TASK-010 (TDD-GREEN)
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
