# Scripts de Reorganización de Documentación

Scripts automatizados para reorganizar la estructura de `docs/` siguiendo la estrategia "Todo por Dominio".

## Scripts Disponibles

### 1. `reorganizar_docs_por_dominio.sh`

Script principal que ejecuta la reorganización completa de forma automatizada.

#### Uso

```bash
# Probar en modo dry-run (sin ejecutar cambios)
./scripts/reorganizar_docs_por_dominio.sh --dry-run

# Ejecutar reorganización real
./scripts/reorganizar_docs_por_dominio.sh
```

#### Qué Hace

1. Crea backup automático en `respaldo/docs_backup_YYYYMMDD_HHMMSS.tar.gz`
2. Mueve `docs/implementacion/backend/` → `docs/backend/`
3. Mueve `docs/implementacion/frontend/` → `docs/frontend/`
4. Fusiona `docs/implementacion/infrastructure/` + `docs/infraestructura/` → `docs/infraestructura/`
5. Elimina directorio vacío `docs/implementacion/`
6. Actualiza TODAS las referencias en archivos `.md` automáticamente
7. Actualiza scripts Python de generación de índices
8. Valida estructura final
9. Agrega cambios a git staging

#### Opciones

- `--dry-run`: Simula la ejecución sin hacer cambios reales (RECOMENDADO probar primero)

#### Salida

- Output colorizado con estados: INFO (azul), OK (verde), WARNING (amarillo), ERROR (rojo)
- Resumen al final con estadísticas
- Exit code 0 si exitoso, 1 si hay errores

---

### 2. `validar_estructura_docs.sh`

Script de validación post-migración.

#### Uso

```bash
./scripts/validar_estructura_docs.sh
```

#### Qué Verifica

1. Directorio `implementacion/` eliminado o vacío
2. Directorios principales existen (backend/, frontend/, infrastructure/)
3. Subdirectorios de dominios tienen estructura correcta
4. No hay referencias huérfanas a "implementacion/" en archivos .md
5. No hay referencias huérfanas a "infraestructura/"
6. Conteo de archivos por dominio
7. Enlaces markdown en archivos principales no están rotos
8. Directorio `infraestructura/` antiguo eliminado
9. Estado de git

#### Salida

- Reporte detallado de validación
- Contadores de errores y warnings
- Exit code 0: Validación exitosa
- Exit code 1: Errores encontrados

---

## Flujo de Trabajo Recomendado

### Paso 1: Dry-Run

Ejecutar en modo simulación para ver qué cambios se harían:

```bash
./scripts/reorganizar_docs_por_dominio.sh --dry-run
```

Revisar el output y verificar que todo se ve correcto.

### Paso 2: Ejecutar Reorganización

Si el dry-run se ve bien, ejecutar la reorganización real:

```bash
./scripts/reorganizar_docs_por_dominio.sh
```

El script creará un backup automáticamente antes de hacer cambios.

### Paso 3: Validar

Verificar que la reorganización fue exitosa:

```bash
./scripts/validar_estructura_docs.sh
```

Si hay errores, revisar el output y corregir.

### Paso 4: Regenerar Índices ISO

Regenerar índices de requisitos conforme a ISO 29148:

```bash
python scripts/requisitos/generate_requirements_index.py
```

### Paso 5: Probar MkDocs

Verificar que la documentación se construye correctamente:

```bash
cd docs
mkdocs build --clean
mkdocs serve
```

Abrir http://127.0.0.1:8000 y verificar navegación.

### Paso 6: Commit y Push

Si todo está correcto, commitear y hacer push:

```bash
git status
git commit -m "refactor(docs): reorganizar estructura por dominio eliminando nivel implementacion/"
git push
```

---

## Rollback (Si algo sale mal)

Si la reorganización causa problemas, restaurar desde el backup:

```bash
# Identificar el backup más reciente
ls -lth respaldo/docs_backup_*.tar.gz | head -1

# Eliminar docs/ actual
rm -rf docs/

# Restaurar desde backup
tar -xzf respaldo/docs_backup_YYYYMMDD_HHMMSS.tar.gz

# Verificar
ls -la docs/

# Descartar cambios en git
git checkout -- docs/
```

---

## Métricas de Tiempo

| Método | Tiempo Estimado | Intervención Manual |
|--------|-----------------|---------------------|
| Automatizado | 5-10 minutos | Ninguna (solo ejecutar scripts) |
| Manual | 8-12 horas | Alta (múltiples pasos) |

---

## Requisitos

- Bash 4.0+
- Git
- Python 3.x (para regenerar índices)
- Permisos de escritura en `docs/` y `respaldo/`

---

## Troubleshooting

### Error: "No se encontró docs/implementacion/"

La reorganización ya fue ejecutada o la estructura es diferente. Verificar con:

```bash
ls -la docs/
```

### Error: Permisos denegados

Asegurarse de que los scripts son ejecutables:

```bash
chmod +x scripts/reorganizar_docs_por_dominio.sh
chmod +x scripts/validar_estructura_docs.sh
```

### Warning: "Hay cambios sin commitear"

El script continúa pero advierte que hay cambios sin commitear. Commitear antes si se prefiere:

```bash
git add .
git commit -m "cambios previos"
```

### Referencias rotas después de reorganización

Ejecutar el script de validación para identificarlas:

```bash
./scripts/validar_estructura_docs.sh
```

Corregir manualmente las referencias identificadas.

---

## Documentación Relacionada

- **Estrategia completa**: `docs/anexos/analisis_nov_2025/ESTRATEGIA_REORGANIZACION_TODO_POR_DOMINIO.md`
- **Análisis original**: `docs/anexos/analisis_nov_2025/PROPUESTA_FINAL_REESTRUCTURACION.md`
- **Reporte de duplicados**: `docs/anexos/analisis_nov_2025/REPORTE_DUPLICADOS.md`

---

## Contacto

Para preguntas o problemas, contactar al equipo de arquitectura.
