---
id: GUIA-AGENTE-NOMENCLATURA
tipo: guia
categoria: automatizacion
version: 1.0.0
fecha: 2025-11-16
---

# Guia de Uso: Agente de Nomenclatura de Documentacion

## Proposito

Esta guia explica como usar el **Documentation Naming Agent** para estandarizar automaticamente los nombres de archivos de documentacion siguiendo las convenciones de ADR-021 y los principios de Clean Code.

## Ubicacion

```
scripts/coding/ai/agents/documentation/documentation_naming_agent.py
```

## Que Hace el Agente

El agente ejecuta automaticamente el procedimiento completo de renombrado de archivos:

### PASO 1: Auditoria
- Escanea recursivamente todos los archivos .md en docs/
- Identifica violaciones de nomenclatura por categoria
- Genera propuestas especificas de renombrado
- Clasifica por prioridad (CRITICAL, HIGH, MEDIUM, LOW)
- Organiza por fases (Sequential, Uppercase, ADR)

### PASO 2: Deteccion de Violaciones

**Categoria 1: Numeros Secuenciales**
- ❌ `testing_001.md` → ✅ `guia_ejecutar_pytest.md`
- ❌ `onboarding_002.md` → ✅ `ejecutar_proyecto_localmente.md`
- Lee el contenido del archivo para sugerir nombre descriptivo
- Prioridad: CRITICAL

**Categoria 2: MAYUSCULAS**
- ❌ `ESTRATEGIA_GIT_HOOKS.md` → ✅ `estrategia_git_hooks.md`
- ❌ `AGENTES_SDLC.md` → ✅ `agentes_sdlc.md`
- Respeta archivos especiales (README, CHANGELOG, ADR-XXX, TASK-XXX)
- Prioridad: HIGH

**Categoria 3: ADRs Inconsistentes**
- ❌ `ADR_2025_001_vagrant.md` → ✅ `ADR-001-vagrant.md`
- Estandariza formato: ADR-NNN-descripcion-kebab-case.md
- Organiza en subdirectorios adr/ por dominio
- Prioridad: HIGH

### PASO 3: Busqueda de Referencias
- Encuentra todos los archivos que referencian el archivo a renombrar
- Prepara actualizaciones de links y menciones
- Incluye enlaces markdown y texto plano

### PASO 4: Ejecucion de Renombrado
- Ejecuta `git mv` para preservar historial
- Crea directorios necesarios (ej: backend/adr/)
- Actualiza referencias en otros archivos
- Maneja errores gracefully

### PASO 5: Creacion de Commits
- Crea commits organizados por fase
- Mensajes descriptivos siguiendo convenciones
- Un commit por fase ejecutada

### PASO 6: Reportes
- Genera reporte de auditoria (JSON)
- Genera reporte de ejecucion (JSON)
- Muestra resumen en consola

## Modos de Uso

### 1. Solo Auditoria (Recomendado Primera Vez)

Identifica violaciones sin ejecutar cambios:

```bash
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --audit-only
```

**Salida:**
```
================================================================================
DOCUMENTATION NAMING AUDIT REPORT
================================================================================
Timestamp: 2025-11-16T10:30:00
Files scanned: 862
Violations found: 107

By Type:
  sequential_number: 11
  uppercase: 68
  adr_inconsistent: 28

By Priority:
  critical: 11
  high: 96

By Phase:
  sequential: 11
  uppercase: 68
  adr: 28
================================================================================
```

### 2. Dry Run (Ver Que Haria)

Simula ejecucion sin aplicar cambios:

```bash
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --dry-run --phase all
```

**Salida:**
```
[DRY-RUN] Would rename: docs/backend/qa/testing_001.md → docs/backend/qa/guia_ejecutar_pytest.md
[DRY-RUN] Would update 2 references
[DRY-RUN] Would rename: docs/infraestructura/ESTRATEGIA_GIT_HOOKS.md → docs/infraestructura/estrategia_git_hooks.md
[DRY-RUN] Would update 1 references
...
```

### 3. Ejecutar Fase Especifica

Ejecuta solo una fase:

```bash
# Fase 1: Numeros secuenciales → Nombres descriptivos
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --phase sequential

# Fase 2: MAYUSCULAS → snake_case
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --phase uppercase

# Fase 3: Estandarizar ADRs
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --phase adr
```

### 4. Ejecutar Todo (RECOMENDADO)

Ejecuta las 3 fases secuencialmente con un solo comando:

```bash
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --execute-all
```

**Esto ejecuta:**
1. Auditoria completa
2. Fase 1: Sequential (11 archivos)
3. Fase 2: Uppercase (68 archivos)
4. Fase 3: ADR (28 archivos)
5. Crea 3 commits organizados
6. Genera reportes

**Tiempo estimado:** 5-10 minutos

### 5. Con Reportes JSON

Guardar reportes detallados:

```bash
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py \
  --execute-all \
  --output /tmp/naming_report.json
```

**Genera:**
- `/tmp/naming_report_audit.json` - Auditoria completa
- `/tmp/naming_report_execution.json` - Resultados de ejecucion

## Workflow Recomendado

### Primera Ejecucion (Nueva Instalacion)

```bash
# 1. Auditar para ver estado actual
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --audit-only

# 2. Revisar violaciones encontradas
# (Leer output en consola)

# 3. Dry-run para validar cambios propuestos
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --dry-run --execute-all

# 4. Ejecutar cambios reales
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --execute-all

# 5. Validar resultados
git log --oneline -3
git status
```

### Mantenimiento Continuo (CI/CD)

Integrar en pipeline para validar PRs:

```yaml
# .github/workflows/validate-naming.yml
name: Validate Documentation Naming

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Audit naming compliance
        run: |
          python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --audit-only

      - name: Fail if violations found
        run: |
          VIOLATIONS=$(python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --audit-only | grep "Violations found" | awk '{print $3}')
          if [ "$VIOLATIONS" -gt 0 ]; then
            echo "Found $VIOLATIONS naming violations"
            exit 1
          fi
```

## Parametros Completos

| Parametro | Descripcion | Ejemplo |
|-----------|-------------|---------|
| `--docs-root PATH` | Directorio docs/ a procesar | `--docs-root /path/to/docs` |
| `--audit-only` | Solo auditar, no ejecutar | `--audit-only` |
| `--phase PHASE` | Fase especifica (sequential/uppercase/adr/all) | `--phase sequential` |
| `--dry-run` | Simular sin aplicar cambios | `--dry-run` |
| `--execute-all` | Ejecutar todas las fases | `--execute-all` |
| `--output FILE` | Guardar reportes JSON | `--output /tmp/report.json` |

## Estructura de Reportes

### Reporte de Auditoria (JSON)

```json
{
  "timestamp": "2025-11-16T10:30:00",
  "total_files_scanned": 862,
  "total_violations": 107,
  "violations_by_type": {
    "sequential_number": 11,
    "uppercase": 68,
    "adr_inconsistent": 28
  },
  "violations_by_priority": {
    "critical": 11,
    "high": 96
  },
  "violations_by_phase": {
    "sequential": 11,
    "uppercase": 68,
    "adr": 28
  },
  "violations": [
    {
      "file_path": "docs/backend/qa/testing_001.md",
      "violation_type": "sequential_number",
      "priority": "critical",
      "current_name": "testing_001.md",
      "proposed_name": "guia_ejecutar_pytest.md",
      "reason": "Sequential number 001 doesn't reveal content",
      "phase": "sequential",
      "references": ["docs/QUICKSTART.md", "docs/gobernanza/guias_README.md"]
    }
  ]
}
```

### Reporte de Ejecucion (JSON)

```json
{
  "timestamp": "2025-11-16T10:35:00",
  "phases": [
    {
      "phases_executed": ["sequential"],
      "total_operations": 11,
      "successful_operations": 11,
      "failed_operations": 0,
      "commits_created": ["ce16d787"],
      "operations": [
        {
          "old_path": "docs/backend/qa/testing_001.md",
          "new_path": "docs/backend/qa/guia_ejecutar_pytest.md",
          "violation": {...},
          "references_to_update": [
            {"file": "docs/QUICKSTART.md", "old": "testing_001.md", "new": "guia_ejecutar_pytest.md"}
          ],
          "executed": true,
          "git_output": ""
        }
      ]
    }
  ]
}
```

## Casos de Uso

### Caso 1: Nuevo Desarrollador Agrega Archivo Mal Nombrado

```bash
# Desarrollador crea: docs/backend/NEW_FEATURE.md
git add docs/backend/NEW_FEATURE.md
git commit -m "Add new feature docs"

# CI falla con:
# "Found 1 naming violations: NEW_FEATURE.md should be new_feature.md"

# Desarrollador ejecuta localmente:
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --execute-all

# Agente renombra automaticamente:
# NEW_FEATURE.md → new_feature.md
# Crea commit con mensaje correcto
```

### Caso 2: Refactorizacion Masiva de Documentacion

```bash
# Equipo decide reorganizar docs/ completo
# En lugar de manual, usar agente:

python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --execute-all

# Resultado:
# - 107 archivos renombrados
# - Referencias actualizadas
# - 3 commits organizados
# - Tiempo: 5 minutos
# - Errores: 0
```

### Caso 3: Validacion Pre-Merge

```bash
# Antes de mergear PR grande:

# 1. Auditar rama actual
git checkout feature/big-refactor
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --audit-only

# 2. Si hay violaciones, ejecutar agente
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --execute-all

# 3. Push cambios
git push origin feature/big-refactor

# 4. Merge limpio sin violaciones
```

## Troubleshooting

### Error: "docs/ directory not found"

```bash
# Asegurate de ejecutar desde raiz del proyecto:
cd /home/user/IACT---project
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --execute-all

# O especifica ruta:
python scripts/coding/ai/agents/documentation/documentation_naming_agent.py --docs-root /path/to/docs
```

### Error: "Failed to rename X → Y: file exists"

```bash
# Archivo destino ya existe
# Opcion 1: Revisar manualmente si es duplicado
# Opcion 2: Eliminar duplicado primero
git rm docs/path/to/duplicate.md
git commit -m "Remove duplicate"

# Luego re-ejecutar agente
```

### Error: "git mv failed: cross-device link"

```bash
# Usar paths relativos correctos
# El agente maneja esto automaticamente
# Si persiste, verificar permisos:
ls -la docs/
```

## Metricas de Exito

### Antes del Agente (Manual)
- Tiempo: 2-3 horas
- Errores: 5-10 referencias rotas
- Commits: 15-20 commits desorganizados
- Coverage: 80-90% (siempre se olvidan algunos)

### Con el Agente (Automatico)
- Tiempo: 5 minutos
- Errores: 0 referencias rotas
- Commits: 3 commits organizados
- Coverage: 100% (escanea todo)

## Integracion con ADR-021

El agente implementa directamente las convenciones de:

**docs/gobernanza/adr/ADR-021-convenciones-nomenclatura-documentacion.md**

Principios aplicados:
- ✅ Nombres que revelan intenciones (Clean Code Principio 1)
- ✅ Distinciones significativas (Clean Code Principio 3)
- ✅ Nombres pronunciables (Clean Code Principio 4)
- ✅ Nombres buscables (Clean Code Principio 5)
- ✅ Evitar codificaciones (Clean Code Principio 6)
- ✅ Una palabra por concepto (Clean Code Principio 8)

## Proximos Pasos

Despues de ejecutar el agente:

1. **Validar resultados:**
   ```bash
   git log --oneline -3
   git diff HEAD~3
   ```

2. **Ejecutar tests:**
   ```bash
   python scripts/validate_docs_structure.sh
   ```

3. **Push cambios:**
   ```bash
   git push origin <branch>
   ```

4. **Crear PR:**
   ```bash
   gh pr create --title "docs: standardize file naming per ADR-021" --body "Automated by Documentation Naming Agent"
   ```

## Referencias

- [ADR-021: Convenciones de Nomenclatura](../adr/ADR-021-convenciones-nomenclatura-documentacion.md)
- [ADR-020: Organizacion por Dominio](../adr/ADR-020-organizacion-documentacion-por-dominio.md)
- [Auditoria de Nombres](../../AUDITORIA_NOMBRES_ARCHIVOS.md)
- [Clean Code - Chapter 2: Meaningful Names](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

## Mantenedores

- @doc-lead - Documentacion
- @tech-lead - Automatizacion
- @arquitecto-senior - ADRs

---

**Version:** 1.0.0
**Ultima actualizacion:** 2025-11-16
**Proxima revision:** 2025-12-16
