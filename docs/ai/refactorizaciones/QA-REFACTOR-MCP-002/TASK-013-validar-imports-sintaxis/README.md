---
id: TASK-REFACTOR-MCP-013
tipo: tarea
categoria: validacion-final
titulo: Validar Imports y Sintaxis
fase: FASE_4
prioridad: MEDIA
duracion_estimada: 3min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-012]
---

# TASK-REFACTOR-MCP-013: Validar Imports y Sintaxis

**Fase:** FASE 4 - Validacion Final
**Prioridad:** MEDIA
**Duracion Estimada:** 3 minutos
**Responsable:** Agente Claude Code
**Estado:** PENDIENTE
**Dependencias:** TASK-REFACTOR-MCP-012 (Suite Completa de Tests)

---

## Objetivo

Validar que el archivo `scripts/coding/ai/mcp/registry.py` tiene imports correctos, sintaxis valida de Python y puede ser importado sin errores despues de aplicar ambas refactorizaciones (Playwright constant + PEP 585).

---

## Prerequisitos

- [ ] TASK-012 completada (suite completa de tests pasando)
- [ ] Python 3.9+ disponible en el entorno
- [ ] Archivo registry.py modificado con ambas refactorizaciones
- [ ] Working directory limpio

---

## Pasos de Ejecucion

### Paso 1: Validar Sintaxis con py_compile
```bash
# Compilar archivo para verificar sintaxis
python -m py_compile scripts/coding/ai/mcp/registry.py

# Verificar que no genero errores
echo "Exit code: $?"
```

**Resultado Esperado:** Exit code: 0 (sin errores de sintaxis)

**Evidencia:** Capturar salida completa
```bash
python -m py_compile scripts/coding/ai/mcp/registry.py 2>&1 | tee evidencias/py_compile-validation.log
```

### Paso 2: Verificar Imports del Archivo
```bash
# Ver imports en el archivo
grep "^from typing import" scripts/coding/ai/mcp/registry.py
grep "^import " scripts/coding/ai/mcp/registry.py
```

**Resultado Esperado:**
- `from typing import Tuple` (Dict y Mapping removidos por PEP 585)
- NO debe contener: `from typing import Dict, Mapping`

**Evidencia:** Guardar lista de imports
```bash
echo "=== IMPORTS ACTUALES ===" > evidencias/imports-verification.log
grep -E "^(from|import) " scripts/coding/ai/mcp/registry.py >> evidencias/imports-verification.log
```

### Paso 3: Validar Importabilidad del Modulo
```bash
# Intentar importar el modulo
python -c "import scripts.coding.ai.mcp.registry; print('Import successful')"
```

**Resultado Esperado:** "Import successful" sin errores

**Evidencia:** Capturar resultado
```bash
python -c "import scripts.coding.ai.mcp.registry; print('Import successful: OK')" 2>&1 | tee evidencias/import-test.log
```

### Paso 4: Verificar Constante Playwright
```bash
# Verificar que constante PLAYWRIGHT_MCP_VERSION existe
grep "PLAYWRIGHT_MCP_VERSION" scripts/coding/ai/mcp/registry.py
```

**Resultado Esperado:**
- Linea con definicion: `PLAYWRIGHT_MCP_VERSION = "0.0.40"`
- Linea con uso en f-string: `f"@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}"`

**Evidencia:** Guardar ocurrencias
```bash
echo "=== PLAYWRIGHT_MCP_VERSION OCCURRENCES ===" > evidencias/playwright-constant-check.log
grep -n "PLAYWRIGHT_MCP_VERSION" scripts/coding/ai/mcp/registry.py >> evidencias/playwright-constant-check.log
```

### Paso 5: Verificar Type Annotations Modernizadas
```bash
# Buscar uso de dict minuscula (PEP 585)
grep -E "dict\[" scripts/coding/ai/mcp/registry.py | head -5

# Verificar que NO hay Dict mayuscula (typing)
grep -E "Dict\[" scripts/coding/ai/mcp/registry.py || echo "OK: No Dict found"
```

**Resultado Esperado:**
- Encuentra: `dict[str, str]`, `dict[str, Any]`
- NO encuentra: `Dict[str, str]`

**Evidencia:** Documentar verificacion
```bash
echo "=== TYPE ANNOTATIONS CHECK ===" > evidencias/type-annotations-check.log
echo "--- dict[...] occurrences (should exist) ---" >> evidencias/type-annotations-check.log
grep -n "dict\[" scripts/coding/ai/mcp/registry.py >> evidencias/type-annotations-check.log || echo "NONE" >> evidencias/type-annotations-check.log
echo "" >> evidencias/type-annotations-check.log
echo "--- Dict[...] occurrences (should NOT exist) ---" >> evidencias/type-annotations-check.log
grep -n "Dict\[" scripts/coding/ai/mcp/registry.py >> evidencias/type-annotations-check.log || echo "OK: None found" >> evidencias/type-annotations-check.log
```

### Paso 6: Crear Resumen de Validacion
```bash
# Crear resumen consolidado
cat > evidencias/RESUMEN-VALIDACION.md << 'EOF'
# RESUMEN VALIDACION - TASK-013

## Estado: [PENDIENTE / EXITOSA / FALLIDA]

---

## Validaciones Ejecutadas

### 1. Sintaxis Python (py_compile)
- **Comando:** python -m py_compile registry.py
- **Resultado:** [OK / ERROR]
- **Exit Code:** [0 / otro]

### 2. Imports Verificados
- **Esperado:** from typing import Tuple (sin Dict, Mapping)
- **Real:** [copiar output]
- **Estado:** [OK / ERROR]

### 3. Importabilidad del Modulo
- **Resultado:** [Import successful / ERROR]
- **Estado:** [OK / ERROR]

### 4. Constante Playwright
- **Definicion encontrada:** [SI / NO]
- **Uso en f-string encontrado:** [SI / NO]
- **Estado:** [OK / ERROR]

### 5. Type Annotations PEP 585
- **dict[...] encontrado:** [SI / NO]
- **Dict[...] encontrado:** [SI (ERROR) / NO (OK)]
- **Estado:** [OK / ERROR]

---

## Criterios de Exito

- [ ] py_compile sin errores (exit code 0)
- [ ] Imports correctos (Tuple solo, sin Dict/Mapping)
- [ ] Modulo importable sin errores
- [ ] Constante PLAYWRIGHT_MCP_VERSION presente
- [ ] Type annotations modernizadas (dict vs Dict)

---

## Resultado Final

**Estado:** [EXITOSA / FALLIDA]
**Tiempo:** [X minutos]
**Problemas encontrados:** [NINGUNO / listar]

---

**Validacion ejecutada:** 2025-11-17
**Por:** Agente Claude Code
EOF
```

---

## Criterios de Exito

- [ ] `python -m py_compile` pasa sin errores (exit code 0)
- [ ] Imports verificados: `from typing import Tuple` (sin Dict, Mapping)
- [ ] Modulo importable: `import scripts.coding.ai.mcp.registry` exitoso
- [ ] Constante `PLAYWRIGHT_MCP_VERSION` presente y usada correctamente
- [ ] Type annotations modernizadas: `dict[...]` en lugar de `Dict[...]`
- [ ] NO hay ocurrencias de `Dict[` o `Mapping[` en el archivo
- [ ] Evidencias guardadas en carpeta `evidencias/`

---

## Validacion

```bash
# Script de validacion integral
#!/bin/bash

echo "=== VALIDACION INTEGRAL TASK-013 ==="
echo ""

# 1. Sintaxis
echo "1. Validando sintaxis..."
if python -m py_compile scripts/coding/ai/mcp/registry.py 2>&1; then
    echo "   OK: Sintaxis valida"
else
    echo "   ERROR: Sintaxis invalida"
    exit 1
fi

# 2. Imports
echo ""
echo "2. Verificando imports..."
if grep -q "^from typing import Tuple$" scripts/coding/ai/mcp/registry.py; then
    echo "   OK: Import Tuple encontrado"
else
    echo "   ERROR: Import Tuple no encontrado"
fi

if grep -q "from typing import Dict" scripts/coding/ai/mcp/registry.py; then
    echo "   ERROR: Import Dict aun presente (debe ser removido)"
else
    echo "   OK: Import Dict removido correctamente"
fi

# 3. Importabilidad
echo ""
echo "3. Verificando importabilidad..."
if python -c "import scripts.coding.ai.mcp.registry" 2>&1; then
    echo "   OK: Modulo importable"
else
    echo "   ERROR: Modulo no importable"
    exit 1
fi

# 4. Constante Playwright
echo ""
echo "4. Verificando constante Playwright..."
if grep -q "PLAYWRIGHT_MCP_VERSION = " scripts/coding/ai/mcp/registry.py; then
    echo "   OK: Constante PLAYWRIGHT_MCP_VERSION definida"
else
    echo "   ERROR: Constante no encontrada"
fi

# 5. Type annotations
echo ""
echo "5. Verificando type annotations PEP 585..."
if grep -q "dict\[" scripts/coding/ai/mcp/registry.py; then
    echo "   OK: Annotations PEP 585 (dict[...]) encontradas"
else
    echo "   ERROR: No se encontraron annotations PEP 585"
fi

if grep -q "Dict\[" scripts/coding/ai/mcp/registry.py; then
    echo "   ERROR: Annotations antiguas (Dict[...]) aun presentes"
else
    echo "   OK: Annotations antiguas (Dict[...]) removidas"
fi

echo ""
echo "=== VALIDACION COMPLETA ==="
```

**Salida Esperada:** Todos los checks marcan "OK", ninguno marca "ERROR"

---

## Rollback

Si alguna validacion falla:

**Paso 1: Identificar problema**
```bash
# Revisar logs de validacion
cat evidencias/py_compile-validation.log
cat evidencias/imports-verification.log
cat evidencias/import-test.log
```

**Paso 2: Revertir cambios si es necesario**
```bash
# Opcion A: Revertir ultimo commit (si ya commiteo)
git revert HEAD

# Opcion B: Revertir ambos commits de refactorizacion
git revert <commit-pep585>
git revert <commit-playwright>

# Opcion C: Restaurar desde backup
git reset --hard backup-refactor-mcp-2025-11-17
```

**Paso 3: Re-ejecutar validaciones**
```bash
# Verificar que archivo esta en estado funcional
python -m py_compile scripts/coding/ai/mcp/registry.py
python -c "import scripts.coding.ai.mcp.registry"
```

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| Error de sintaxis introducido | MUY BAJA | ALTO | py_compile detecta tempranamente |
| Import roto (Dict/Mapping removido mal) | BAJA | MEDIO | Verificacion manual de imports |
| Modulo no importable | MUY BAJA | ALTO | Test de import directo |
| Constante mal definida | MUY BAJA | BAJO | Grep verifica presencia |
| Type annotations inconsistentes | BAJA | BAJO | Grep verifica patron dict vs Dict |

---

## Notas

### Sobre py_compile
- `python -m py_compile` solo verifica sintaxis basica
- NO ejecuta el codigo, solo lo compila a bytecode
- Es validacion rapida y segura
- NO detecta errores de logica, solo sintaxis

### Sobre Imports
- PEP 585 (Python 3.9+) permite `dict[str, str]` en lugar de `Dict[str, str]`
- Imports antiguos (`Dict`, `Mapping`) deben ser removidos de `typing`
- `Tuple` aun se importa porque no tiene equivalente built-in para annotations

### Sobre Importabilidad
- `import scripts.coding.ai.mcp.registry` verifica que el modulo es valido
- NO ejecuta funciones, solo carga definiciones
- Detecta errores de imports, nombres indefinidos, etc.

### Sobre Validaciones
- Esta tarea es validacion FINAL antes de commit
- Si alguna validacion falla, NO continuar con TASK-014
- Todas las validaciones deben pasar para considerar tarea exitosa

### Archivos de Evidencia Generados
```
evidencias/
  py_compile-validation.log        # Salida de py_compile
  imports-verification.log         # Lista de imports del archivo
  import-test.log                  # Resultado de test de importacion
  playwright-constant-check.log    # Verificacion de constante
  type-annotations-check.log       # Verificacion de dict vs Dict
  RESUMEN-VALIDACION.md           # Resumen consolidado
```

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

---

## Checklist de Finalizacion

- [ ] py_compile ejecutado sin errores
- [ ] Imports verificados (Tuple solo, sin Dict/Mapping)
- [ ] Modulo importable exitosamente
- [ ] Constante PLAYWRIGHT_MCP_VERSION verificada
- [ ] Type annotations PEP 585 verificadas (dict vs Dict)
- [ ] Todas las evidencias guardadas en evidencias/
- [ ] RESUMEN-VALIDACION.md creado
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
