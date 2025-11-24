---
id: TASK-REFACTOR-MCP-005
tipo: tarea
categoria: tdd-refactor
titulo: Aplicar Commit Playwright Constant
fase: FASE_2
prioridad: ALTA
duracion_estimada: 5min
estado: pendiente
dependencias: [TASK-REFACTOR-MCP-004]
---

# TASK-005: [TDD-REFACTOR] Aplicar Commit Playwright Constant

**Fase:** FASE 2 - Refactorizacion Playwright
**Prioridad:** ALTA
**Duracion Estimada:** 5 minutos
**Responsable:** Desarrollador asignado
**Estado:** PENDIENTE
**Tipo TDD:** REFACTOR (aplicar cambios)
**Dependencias:** TASK-004 (baseline tests documentado)

---

## Objetivo

Aplicar la refactorizacion de extraccion de constante Playwright (commit 0d1e1f2) al archivo scripts/coding/ai/mcp/registry.py, siguiendo metodologia TDD para garantizar que los cambios de calidad no introducen regresiones funcionales.

---

## Justificacion

Esta refactorizacion mejora la mantenibilidad del codigo al:
- Extraer el magic string "@playwright/mcp@0.0.40" a una constante nombrada
- Facilitar actualizaciones futuras de version Playwright
- Documentar la version pinned con comentarios explicativos
- Usar string interpolation moderna (f-string) en lugar de concatenacion

**Impacto funcional:** CERO - Es una refactorizacion pura sin cambios de comportamiento.

---

## Prerequisitos

- [ ] TASK-004 completada con baseline de tests documentado
- [ ] Commit 0d1e1f2 existe y es accesible en el repositorio
- [ ] Archivo scripts/coding/ai/mcp/registry.py existe
- [ ] No hay cambios sin commit en el archivo registry.py

---

## Detalles del Commit 0d1e1f2

**Commit Hash:** 0d1e1f2bf6207fd45c0ea63c8aa434efaf914af9
**Autor:** copilot-swe-agent[bot]
**Fecha:** 2025-11-16 06:08:16
**Mensaje:** refactor: extract Playwright MCP version to constant

**Cambios aplicados:**
```diff
+# Playwright MCP version pinned to match Copilot CLI reference log (2025-01-16)
+# This version has been verified to work with the current integration
+PLAYWRIGHT_MCP_VERSION = "0.0.40"
+

-                "@playwright/mcp@0.0.40",
+                f"@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}",
```

**Lineas afectadas:**
- Lineas 16-18: Agregadas (constante + comentarios)
- Linea 106: Modificada (uso de constante con f-string)

**Total impacto:**
- +5 lineas agregadas
- -1 linea removida
- 1 archivo modificado

---

## Pasos de Ejecucion

### Paso 1: Verificar Estado Pre-Refactorizacion
```bash
# Ver estado del archivo antes de cambios
git status scripts/coding/ai/mcp/registry.py

# Ver contenido actual de linea 106 (debe contener string hardcodeado)
sed -n '106p' scripts/coding/ai/mcp/registry.py
```

**Evidencia Esperada:**
- Archivo sin cambios sin commit
- Linea 106 contiene: "@playwright/mcp@0.0.40"

### Paso 2: Cherry-Pick Commit de Refactorizacion
```bash
# Aplicar commit 0d1e1f2
git cherry-pick 0d1e1f2bf6207fd45c0ea63c8aa434efaf914af9

# Si hay conflictos, documentar en evidencias/
git status
```

**Evidencia Esperada:**
- Cherry-pick exitoso sin conflictos
- Mensaje: "1 file changed, 5 insertions(+), 1 deletion(-)"

**Si hay conflictos (escenario alternativo):**
```bash
# Documentar conflictos
git status > evidencias/cherry-pick-conflicts.txt

# Abortar y aplicar manualmente
git cherry-pick --abort

# Ver Paso 3-B (Aplicacion Manual)
```

### Paso 3-A: Verificar Cambios Aplicados (si cherry-pick exitoso)
```bash
# Ver diff del commit aplicado
git show --stat

# Verificar lineas especificas agregadas
sed -n '16,18p' scripts/coding/ai/mcp/registry.py

# Verificar linea modificada
sed -n '110p' scripts/coding/ai/mcp/registry.py  # Ajustar numero por offset
```

**Evidencia Esperada:**
- Lineas 16-18 contienen:
  ```python
  # Playwright MCP version pinned to match Copilot CLI reference log (2025-01-16)
  # This version has been verified to work with the current integration
  PLAYWRIGHT_MCP_VERSION = "0.0.40"
  ```
- Linea ~110 contiene: f"@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}",

### Paso 3-B: Aplicacion Manual (solo si cherry-pick fallo)
```bash
# Editar archivo manualmente
nano scripts/coding/ai/mcp/registry.py

# Agregar despues de imports (linea ~16):
# Playwright MCP version pinned to match Copilot CLI reference log (2025-01-16)
# This version has been verified to work with the current integration
PLAYWRIGHT_MCP_VERSION = "0.0.40"

# Modificar linea ~106 de:
#     "@playwright/mcp@0.0.40",
# A:
#     f"@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}",

# Guardar y salir

# Crear commit manual
git add scripts/coding/ai/mcp/registry.py
git commit -m "refactor: extract Playwright MCP version to constant

Cherry-picked manually from 0d1e1f2bf6207fd45c0ea63c8aa434efaf914af9

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>"
```

### Paso 4: Validar Sintaxis Basica
```bash
# Validar sintaxis Python
python3 -m py_compile scripts/coding/ai/mcp/registry.py

# Si disponible, validar con flake8/ruff
flake8 scripts/coding/ai/mcp/registry.py 2>&1 || echo "flake8 no disponible"
ruff check scripts/coding/ai/mcp/registry.py 2>&1 || echo "ruff no disponible"
```

**Evidencia Esperada:**
- py_compile: Sin errores
- flake8/ruff: Sin errores criticos (warnings aceptables)

### Paso 5: Verificar Interpolacion de String
```bash
# Crear script temporal para validar valor final
cat > /tmp/verify_playwright_version.py << 'EOF'
import sys
sys.path.insert(0, '/home/user/IACT---project')
from scripts.coding.ai.mcp.registry import PLAYWRIGHT_MCP_VERSION

# Verificar constante
print(f"PLAYWRIGHT_MCP_VERSION = {PLAYWRIGHT_MCP_VERSION}")

# Verificar interpolacion
resultado = f"@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}"
esperado = "@playwright/mcp@0.0.40"

assert resultado == esperado, f"FALLO: {resultado} != {esperado}"
print(f"EXITO: String interpolation correcta: {resultado}")
EOF

# Ejecutar validacion
python3 /tmp/verify_playwright_version.py

# Limpiar
rm /tmp/verify_playwright_version.py
```

**Evidencia Esperada:**
- PLAYWRIGHT_MCP_VERSION = 0.0.40
- EXITO: String interpolation correcta: @playwright/mcp@0.0.40

### Paso 6: Documentar Cambios en Evidencias
```bash
# Guardar diff completo
git show HEAD > evidencias/playwright-constant-commit.txt

# Guardar lineas especificas modificadas
echo "=== CONSTANTE AGREGADA ===" > evidencias/cambios-detallados.txt
sed -n '16,18p' scripts/coding/ai/mcp/registry.py >> evidencias/cambios-detallados.txt

echo -e "\n=== LINEA MODIFICADA ===" >> evidencias/cambios-detallados.txt
grep -n "PLAYWRIGHT_MCP_VERSION" scripts/coding/ai/mcp/registry.py >> evidencias/cambios-detallados.txt

# Ver evidencias
cat evidencias/cambios-detallados.txt
```

**Evidencia Esperada:**
- Archivo evidencias/playwright-constant-commit.txt con diff completo
- Archivo evidencias/cambios-detallados.txt con lineas especificas

---

## Criterios de Exito

- [ ] Commit 0d1e1f2 aplicado exitosamente (cherry-pick o manual)
- [ ] Constante PLAYWRIGHT_MCP_VERSION definida en lineas 16-18
- [ ] Comentarios explicativos agregados (2 lineas)
- [ ] Linea ~110 usa f-string con interpolacion de constante
- [ ] Sintaxis Python valida (py_compile pasa)
- [ ] String interpolation produce valor identico: "@playwright/mcp@0.0.40"
- [ ] Cambios commiteados en git
- [ ] Evidencias completas en evidencias/

---

## Validacion Post-Refactorizacion

### Validacion 1: Imports y Sintaxis
```bash
# Validar que modulo se puede importar
python3 -c "from scripts.coding.ai.mcp import registry; print('Import OK')"

# Validar que constante existe
python3 -c "from scripts.coding.ai.mcp.registry import PLAYWRIGHT_MCP_VERSION; print(f'Version: {PLAYWRIGHT_MCP_VERSION}')"
```

**Resultado Esperado:**
- Import OK
- Version: 0.0.40

### Validacion 2: Diff vs Baseline
```bash
# Ver solo cambios en archivo registry.py
git diff HEAD~1 HEAD -- scripts/coding/ai/mcp/registry.py

# Contar lineas modificadas
git diff HEAD~1 HEAD --shortstat -- scripts/coding/ai/mcp/registry.py
```

**Resultado Esperado:**
- 1 file changed, 5 insertions(+), 1 deletion(-)

### Validacion 3: Grep de Constante
```bash
# Buscar todas las ocurrencias de la constante
grep -n "PLAYWRIGHT_MCP_VERSION" scripts/coding/ai/mcp/registry.py

# Verificar que NO queden strings hardcodeados
grep -n "@playwright/mcp@0.0.40" scripts/coding/ai/mcp/registry.py || echo "Sin strings hardcodeados - OK"
```

**Resultado Esperado:**
- 2 ocurrencias de PLAYWRIGHT_MCP_VERSION (definicion + uso)
- Sin strings hardcodeados @playwright/mcp@0.0.40

---

## Rollback

Si refactorizacion presenta problemas:

### Opcion A: Revertir Commit
```bash
# Revertir ultimo commit
git revert HEAD

# Ver estado
git log -2 --oneline
```

### Opcion B: Reset Hard al Baseline
```bash
# Volver al estado de TASK-004
git reset --hard HEAD~1

# Verificar estado
git status
```

### Opcion C: Restaurar desde Backup
```bash
# Volver al backup de seguridad
git reset --hard backup-refactor-mcp-2025-11-17

# Ver estado
git log -1 --oneline
```

**Criterio de Rollback INMEDIATO:**
- Si sintaxis Python invalida
- Si imports fallan
- Si string interpolation produce valor diferente
- Si TASK-006 (tests) falla

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| Conflictos en cherry-pick | BAJA | MEDIO | Aplicacion manual usando diff exacto del commit |
| Numero de linea diferente | MEDIA | BAJO | Buscar por contenido, no por numero de linea |
| Import falla | MUY BAJA | ALTO | Validar sintaxis con py_compile antes de continuar |
| String interpolation incorrecta | MUY BAJA | CRITICO | Validar valor final con script de verificacion |
| Tests fallan en TASK-006 | BAJA | ALTO | Rollback inmediato + analisis de causa raiz |

---

## Evidencias a Capturar

**Screenshots/Logs:**
1. Output de git cherry-pick (exitoso o conflictos)
2. Output de py_compile (sin errores)
3. Output de script de verificacion (string interpolation)
4. Output de git show HEAD (diff completo)
5. Output de grep (constante + ausencia de strings hardcodeados)

**Archivos Generados:**
- evidencias/cherry-pick-status.txt (o cherry-pick-conflicts.txt si aplica)
- evidencias/playwright-constant-commit.txt (diff completo)
- evidencias/cambios-detallados.txt (lineas especificas)
- evidencias/validacion-sintaxis.txt (py_compile + flake8/ruff)
- evidencias/validacion-interpolacion.txt (script de verificacion)

---

## Notas Importantes

- Esta es una refactorizacion PURA - cero cambios funcionales esperados
- La constante DEBE estar en scope global, no dentro de funciones
- Los comentarios explican PORQUE esta version (referencia a Copilot CLI log)
- El uso de f-string es mas moderno y pythonic que concatenacion
- NUNCA continuar si sintaxis Python invalida
- Siguiente paso obligatorio: TASK-006 (validar tests pasan)

**Relacion con TDD:**
- Esta es la fase REFACTOR del ciclo TDD
- Baseline documentado en TASK-004 (fase RED)
- Validacion en TASK-006 (fase GREEN)
- Smoke test en TASK-007 (fase VALIDATE)

**Valores esperados exactos:**
- Constante: PLAYWRIGHT_MCP_VERSION = "0.0.40"
- String final: "@playwright/mcp@0.0.40"
- Ambos DEBEN ser identicos al valor anterior

---

## Tiempo de Ejecucion

**Inicio:** __:__
**Fin:** __:__
**Duracion Real:** __ minutos

---

## Checklist de Finalizacion

- [ ] Cherry-pick exitoso o aplicacion manual completada
- [ ] Constante PLAYWRIGHT_MCP_VERSION definida correctamente
- [ ] Comentarios explicativos agregados
- [ ] F-string interpolation implementada
- [ ] Sintaxis Python validada (py_compile OK)
- [ ] String interpolation verificada (valor identico)
- [ ] Sin strings hardcodeados residuales
- [ ] Commit creado en git
- [ ] Evidencias capturadas (5 archivos minimo)
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
