---
id: TASK-REFACTOR-MCP-001
tipo: preparacion
categoria: refactorizacion-mcp
titulo: Crear Backup de Seguridad Local
fase: FASE_1
prioridad: CRITICA
duracion_estimada: 5min
estado: pendiente
dependencias: []
---

# TASK-REFACTOR-MCP-001: Crear Backup de Seguridad Local

**Fase:** FASE 1 - Preparacion
**Prioridad:** CRITICA
**Duracion Estimada:** 5 minutos
**Tipo TDD:** Preparacion
**Responsable:** Agente Claude
**Estado:** PENDIENTE

---

## Objetivo

Crear un punto de restauracion seguro mediante un tag de Git antes de iniciar cualquier refactorizacion. Este backup permitira revertir completamente todos los cambios en caso de fallos criticos durante la integracion de refactorizaciones MCP.

---

## Prerequisitos

- [ ] Estar en la rama `claude/fix-branch-issues-013FpGsYZUySbBL6bsMbhBf2`
- [ ] Tener permisos de escritura en el repositorio local
- [ ] Git instalado y configurado correctamente
- [ ] No tener cambios sin commitear (working directory limpio)

---

## Pasos de Ejecucion

### Paso 1: Verificar estado del repositorio
```bash
cd /home/user/IACT---project
git status
git branch --show-current
```

**Resultado Esperado:** Working directory limpio, branch correcto confirmado

### Paso 2: Obtener hash del commit actual
```bash
git log -1 --format="%H %s" > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-001-crear-backup-seguridad/evidencias/commit-actual.log
git log -1 --oneline
```

**Resultado Esperado:** Hash del commit actual guardado en evidencias

### Paso 3: Crear tag de backup
```bash
git tag -a backup-refactor-mcp-2025-11-17 -m "Backup antes de integrar refactorizaciones MCP (Playwright + PEP 585)"
```

**Resultado Esperado:** Tag creado exitosamente sin errores

### Paso 4: Verificar creacion del tag
```bash
git tag -l "backup-refactor-mcp-*"
git show backup-refactor-mcp-2025-11-17 --no-patch --format="%H %s %an %ad"
```

**Resultado Esperado:** Tag visible en la lista y muestra informacion correcta

### Paso 5: Guardar informacion completa del backup
```bash
git show backup-refactor-mcp-2025-11-17 --no-patch --format="%H%n%s%n%an%n%ae%n%ad" > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-001-crear-backup-seguridad/evidencias/backup-info.txt
```

**Resultado Esperado:** Archivo backup-info.txt creado con informacion completa del tag

### Paso 6: Documentar estado de archivos criticos
```bash
ls -lh /home/user/IACT---project/scripts/coding/ai/mcp/registry.py > /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-001-crear-backup-seguridad/evidencias/registry-estado-inicial.log
md5sum /home/user/IACT---project/scripts/coding/ai/mcp/registry.py >> /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-001-crear-backup-seguridad/evidencias/registry-estado-inicial.log
```

**Resultado Esperado:** Hash MD5 y metadatos del archivo registry.py guardados

---

## Criterios de Exito

- [ ] Tag `backup-refactor-mcp-2025-11-17` creado exitosamente
- [ ] Tag apunta al commit actual de la rama `claude/fix-branch-issues-013FpGsYZUySbBL6bsMbhBf2`
- [ ] Hash del commit actual documentado en evidencias
- [ ] Informacion completa del backup guardada en `backup-info.txt`
- [ ] Estado inicial del archivo `registry.py` documentado con hash MD5
- [ ] Tag verificable mediante `git tag -l`

---

## Validacion

```bash
# Verificar que el tag existe
git tag -l backup-refactor-mcp-2025-11-17

# Verificar que apunta al commit correcto
CURRENT_COMMIT=$(git rev-parse HEAD)
TAG_COMMIT=$(git rev-parse backup-refactor-mcp-2025-11-17)
[ "$CURRENT_COMMIT" = "$TAG_COMMIT" ] && echo "VALIDACION OK: Tag apunta al commit actual" || echo "ERROR: Tag no apunta al commit actual"

# Verificar archivos de evidencias
ls -1 /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-001-crear-backup-seguridad/evidencias/
```

**Salida Esperada:**
- Tag encontrado: `backup-refactor-mcp-2025-11-17`
- Mensaje: `VALIDACION OK: Tag apunta al commit actual`
- Archivos en evidencias:
  - `commit-actual.log`
  - `backup-info.txt`
  - `registry-estado-inicial.log`

---

## Rollback

Si falla esta tarea:
```bash
# Eliminar tag si fue creado incorrectamente
git tag -d backup-refactor-mcp-2025-11-17

# Limpiar evidencias
rm -rf /home/user/IACT---project/docs/ai/refactorizaciones/QA-REFACTOR-MCP-002/TASK-001-crear-backup-seguridad/evidencias/*

# Reintentar desde Paso 1
```

**Nota:** Esta tarea es de preparacion y no modifica codigo, por lo que el rollback es trivial.

---

## Evidencias Requeridas

Las siguientes evidencias deben guardarse en `evidencias/`:

1. **commit-actual.log** - Hash y mensaje del commit actual antes de iniciar refactorizaciones
2. **backup-info.txt** - Informacion completa del tag de backup (hash, autor, fecha, mensaje)
3. **registry-estado-inicial.log** - Hash MD5 y metadatos del archivo registry.py antes de modificaciones

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|-----------|
| Working directory no limpio | BAJA | MEDIO | Verificar con git status antes de crear tag |
| Permisos insuficientes para crear tag | MUY BAJA | BAJO | Tags son locales, no requieren permisos especiales |
| Tag ya existe con mismo nombre | BAJA | BAJO | Usar timestamp en nombre para unicidad |
| Fallo al guardar evidencias | MUY BAJA | MEDIO | Verificar permisos de escritura en directorio evidencias/ |

---

## Notas TDD

Esta tarea es el **punto de partida** del ciclo TDD para las refactorizaciones:

- **Backup primero:** Nunca refactorizar sin punto de restauracion
- **Evidencias obligatorias:** Documentar estado inicial para comparaciones futuras
- **Rollback rapido:** Tag permite revertir todo en < 1 minuto con `git reset --hard`
- **Sin impacto funcional:** Esta tarea solo crea referencia, no modifica codigo

El tag creado sera usado como punto de rollback total si ambas refactorizaciones fallan. Es el **ultimo recurso** de recuperacion.

---

## Checklist de Finalizacion

- [ ] Todos los pasos ejecutados exitosamente
- [ ] Criterios de exito cumplidos
- [ ] Validaciones pasadas
- [ ] Evidencias guardadas en evidencias/
- [ ] Tag verificable con `git tag -l`
- [ ] Hash MD5 de registry.py documentado
- [ ] Tarea marcada como COMPLETADA

---

**Tarea creada:** 2025-11-17
**Ultima actualizacion:** 2025-11-17
**Version:** 1.0.0
**Estado:** PENDIENTE
