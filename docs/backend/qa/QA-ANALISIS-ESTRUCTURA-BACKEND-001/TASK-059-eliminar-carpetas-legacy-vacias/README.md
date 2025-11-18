# TASK-059: Eliminar Carpetas Legacy Vacías

## Metadatos
- **ID**: TASK-059
- **Fase**: FASE 4 - Validación y Limpieza
- **Prioridad**: MEDIA 🟢
- **Estimación**: 10 minutos
- **Estado**: PENDIENTE
- **Metodología**: Auto-CoT + Self-Consistency

## Descripción
Identificar y eliminar todas las carpetas vacías o legacy que ya no tienen propósito, limpiando la estructura y reduciendo el ruido en la navegación.

## Auto-CoT: Razonamiento Paso a Paso

### Paso 1: Definir Qué es una Carpeta Legacy Vacía
**Pensamiento**: ¿Qué carpetas debo eliminar?

**Criterios para Eliminación**:
1. **Completamente vacía**: Sin archivos ni subcarpetas
2. **Solo .gitkeep**: Carpeta con únicamente archivo .gitkeep sin propósito
3. **Legacy sin migrar**: Carpetas antiguas cuyo contenido ya se migró
4. **Duplicadas**: Carpetas con nombres similares a las nuevas
5. **Temporales**: Carpetas temp, old, backup sin uso

**Criterios para CONSERVAR**:
1. Carpeta tiene contenido válido
2. Carpeta es destino de migración planificada
3. Carpeta tiene .gitkeep intencionalmente (estructura planificada)
4. Carpeta referenciada en documentación activa

### Paso 2: Identificar Carpetas Candidatas
**Pensamiento**: ¿Cómo encuentro estas carpetas?
```bash
# Carpetas completamente vacías
find docs/backend -type d -empty

# Carpetas con solo .gitkeep
find docs/backend -type d -exec sh -c '
  [ $(ls -A "$1" | wc -l) -eq 1 ] && [ -f "$1/.gitkeep" ]
' sh {} \; -print

# Carpetas legacy conocidas
# Basado en análisis previo de estructura
```

### Paso 3: Verificar Seguridad de Eliminación
**Pensamiento**: ¿Es seguro eliminar cada carpeta?
1. ¿Está referenciada en algún enlace?
2. ¿Está en .gitignore?
3. ¿Tiene contenido oculto (.files)?
4. ¿Es parte de una estructura activa?
5. ¿Hay ramas que la modifican?

### Paso 4: Planificar Eliminación
**Pensamiento**: ¿En qué orden elimino?
1. Primero: Carpetas completamente vacías (bajo riesgo)
2. Segundo: Carpetas solo con .gitkeep innecesario
3. Tercero: Carpetas legacy confirmadas
4. Cuarto: Carpetas duplicadas tras validación

## Self-Consistency: Validación Múltiple

### Enfoque 1: Buscar Carpetas Vacías con find
```bash
# Carpetas sin contenido alguno
find docs/backend -type d -empty

# Listar con contexto
find docs/backend -type d -empty -exec ls -ld {} \;
```

### Enfoque 2: Script Python para Análisis Detallado
```python
import os

def analyze_directory(path):
    for root, dirs, files in os.walk(path):
        # Solo .gitkeep
        if len(files) == 1 and files[0] == '.gitkeep' and len(dirs) == 0:
            print(f"GITKEEP_ONLY: {root}")

        # Completamente vacía
        if len(files) == 0 and len(dirs) == 0:
            print(f"EMPTY: {root}")

        # Solo archivos ocultos
        if all(f.startswith('.') for f in files) and len(dirs) == 0:
            print(f"HIDDEN_ONLY: {root}")

analyze_directory('docs/backend')
```

### Enfoque 3: Revisión Manual del Árbol
```bash
# Generar árbol y revisar visualmente
tree docs/backend -a -L 4 > estructura-tree.txt

# Revisar manualmente carpetas sospechosas
# Validar contra estructura propuesta
```

### Convergencia de Resultados
- Carpetas identificadas por 2+ métodos: Candidatas fuertes
- Carpetas con contenido según un método: Revisar manualmente
- Decisión final: Consenso entre métodos

## Criterios de Aceptación
- [ ] Lista completa de carpetas vacías generada
- [ ] Lista de carpetas legacy identificada
- [ ] Verificación de referencias completada
- [ ] Carpetas eliminadas sin romper estructura
- [ ] Git commit con descripción clara
- [ ] Documentación actualizada si es necesario
- [ ] Validación post-eliminación (TASK-055 pasa)

## Entregables
1. **REPORTE-CARPETAS-ELIMINADAS.md**
   - Lista de carpetas eliminadas
   - Razón de eliminación
   - Ubicación original
   - Timestamp de eliminación

2. **script-encontrar-carpetas-vacias.sh/py**
   - Script reutilizable
   - Múltiples criterios de búsqueda
   - Modo dry-run para seguridad

3. **Commit de Git**
   - Mensaje descriptivo
   - Lista de carpetas en descripción
   - Tag opcional: cleanup-YYYY-MM-DD

## Proceso de Eliminación Segura

### Paso 1: Identificar (Dry Run)
```bash
# Listar sin eliminar
find docs/backend -type d -empty -print

# Guardar lista
find docs/backend -type d -empty > carpetas-a-eliminar.txt

# Revisar lista manualmente
cat carpetas-a-eliminar.txt
```

### Paso 2: Verificar Referencias
```bash
# Para cada carpeta en la lista
while read folder; do
  # Buscar referencias en documentación
  grep -r "$(basename $folder)" docs/backend --include="*.md"

  # Buscar en configuración
  grep -r "$(basename $folder)" . --include="*.json" --include="*.yml"
done < carpetas-a-eliminar.txt
```

### Paso 3: Backup
```bash
# Crear backup de carpetas a eliminar
mkdir -p .backup/carpetas-eliminadas-$(date +%Y%m%d)

while read folder; do
  cp -r "$folder" .backup/carpetas-eliminadas-$(date +%Y%m%d)/
done < carpetas-a-eliminar.txt
```

### Paso 4: Eliminar con Git
```bash
# Usar git rm para preservar historia
while read folder; do
  git rm -r "$folder"
  echo "Eliminado: $folder"
done < carpetas-a-eliminar.txt

# Commit
git commit -m "chore: eliminar carpetas legacy vacías

Carpetas eliminadas:
$(cat carpetas-a-eliminar.txt)

- Sin contenido útil
- Legacy o duplicadas
- Referencias validadas como inexistentes
"
```

### Paso 5: Validar
```bash
# Verificar que la estructura sigue funcional
tree docs/backend -L 2

# Ejecutar validación de enlaces
# (TASK-055)

# Verificar que nada se rompió
git status
git diff HEAD~1
```

## Carpetas Candidatas Comunes

### Alta Probabilidad de Eliminación
```
docs/backend/temp/
docs/backend/old/
docs/backend/backup/
docs/backend/archive/
docs/backend/legacy/
docs/backend/deprecated/
docs/backend/unused/
docs/backend/.old/
```

### Revisar Caso por Caso
```
docs/backend/*-old/
docs/backend/*-backup/
docs/backend/*-deprecated/
docs/backend/test/ (si no tiene tests reales)
docs/backend/examples/ (si está vacío)
```

### NO Eliminar (Generalmente)
```
docs/backend/core/
docs/backend/packages/
docs/backend/components/
docs/backend/.github/
docs/backend/config/
```

## Comandos Útiles

### Encontrar carpetas vacías
```bash
# Totalmente vacías
find docs/backend -type d -empty

# Con conteo de archivos
find docs/backend -type d -exec sh -c 'echo "$(ls -A "$1" | wc -l) $1"' sh {} \; | sort -n

# Solo .gitkeep
find docs/backend -type d -exec sh -c '
  files=$(ls -A "$1")
  if [ "$files" = ".gitkeep" ]; then echo "$1"; fi
' sh {} \;
```

### Estadísticas de carpetas
```bash
# Contar carpetas
find docs/backend -type d | wc -l

# Árbol de estructura con tamaños
du -h --max-depth=3 docs/backend | sort -hr
```

### Eliminar de forma segura
```bash
# Dry run - mostrar qué se eliminaría
find docs/backend -type d -empty -print

# Eliminar (sin git)
find docs/backend -type d -empty -delete

# Eliminar con git (preferido)
find docs/backend -type d -empty -exec git rm -r {} \; 2>/dev/null
```

## Checklist de Verificación

Antes de eliminar cada carpeta, verificar:

- [ ] ¿Está completamente vacía o solo tiene .gitkeep?
- [ ] ¿No está referenciada en ningún documento?
- [ ] ¿No está en uso por alguna herramienta o script?
- [ ] ¿No es destino de migración planificada?
- [ ] ¿Backup creado (si contiene algo)?
- [ ] ¿Se usará git rm en lugar de rm?

## Categorización de Carpetas

### Tipo A: Eliminar Inmediatamente
- Completamente vacías
- Sin referencias
- Sin propósito documentado
- **Acción**: git rm -r

### Tipo B: Eliminar Tras Validación
- Solo .gitkeep innecesario
- Legacy confirmado
- Duplicadas de nueva estructura
- **Acción**: Validar referencias → git rm -r

### Tipo C: Conservar
- Carpetas de nueva estructura (aunque vacías)
- Destino de migraciones futuras
- Con .gitkeep intencional
- **Acción**: Ninguna (mantener)

### Tipo D: Investigar
- Nombre ambiguo
- Posiblemente en uso
- Referencias no claras
- **Acción**: Investigar → Reclasificar

## Prioridades

### P1 - Eliminar Ahora
- Carpetas temp/old/backup vacías
- Carpetas completamente vacías sin propósito
- Duplicados obvios

### P2 - Eliminar en Esta Fase
- Carpetas solo con .gitkeep innecesario
- Legacy cuyo contenido ya migró
- Carpetas deprecated documentadas

### P3 - Evaluar Posteriormente
- Carpetas con nombres ambiguos
- Posible contenido histórico
- Casos límite

## Dependencias
- TASK-053/054: Migraciones de contenido completadas
- TASK-002: Estructura de carpetas nuevas creada
- Antes de TASK-060: Actualizar README principal

## Notas
- **IMPORTANTE**: Siempre usar `git rm` en lugar de `rm` para preservar historia
- Crear backup antes de eliminaciones masivas
- Documentar razón de eliminación en commit message
- Validar que enlaces no se rompan (TASK-055) después de eliminar
- Considerar que otras ramas pueden estar usando carpetas

## Script de Ejemplo Completo

```bash
#!/bin/bash
# script-limpiar-carpetas-vacias.sh

BACKEND_DIR="docs/backend"
REPORT_FILE="REPORTE-CARPETAS-ELIMINADAS-$(date +%Y%m%d-%H%M%S).md"
DRY_RUN=true  # Cambiar a false para eliminar realmente

echo "# Reporte de Limpieza de Carpetas" > $REPORT_FILE
echo "Fecha: $(date)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "## Carpetas Vacías Encontradas" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Encontrar y procesar carpetas vacías
find $BACKEND_DIR -type d -empty | while read folder; do
  echo "- $folder" >> $REPORT_FILE

  if [ "$DRY_RUN" = false ]; then
    git rm -r "$folder" 2>/dev/null && echo "  ✅ Eliminada" >> $REPORT_FILE || echo "  ❌ Error" >> $REPORT_FILE
  else
    echo "  🔍 Modo dry-run (no eliminada)" >> $REPORT_FILE
  fi
done

echo "" >> $REPORT_FILE
echo "## Resumen" >> $REPORT_FILE
echo "- Total carpetas vacías: $(find $BACKEND_DIR -type d -empty | wc -l)" >> $REPORT_FILE

cat $REPORT_FILE
```

## Referencias
- [Git Remove Directory](https://git-scm.com/docs/git-rm)
- [Linux find Command Examples](https://www.tecmint.com/35-practical-examples-of-linux-find-command/)
- Auto-CoT: Wei et al. (2022)
- Self-Consistency: Wang et al. (2022)
