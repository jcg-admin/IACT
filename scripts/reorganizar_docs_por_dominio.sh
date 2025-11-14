#!/bin/bash
set -e

# Script de reorganización automática de docs/ - Todo por Dominio
# Elimina nivel docs/implementacion/ y mapea 1:1 con estructura del código
#
# Uso:
#   ./scripts/reorganizar_docs_por_dominio.sh [--dry-run]
#
# Opciones:
#   --dry-run    Muestra qué se haría sin ejecutar cambios

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"

DRY_RUN=false

# Procesar argumentos
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "MODO DRY-RUN: Mostrando cambios sin ejecutarlos"
    echo ""
fi

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

execute() {
    local cmd="$1"
    local description="$2"

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] $description"
        echo "  Comando: $cmd"
    else
        log_info "$description"
        eval "$cmd"
        if [ $? -eq 0 ]; then
            log_success "Completado"
        else
            log_error "Falló: $cmd"
            exit 1
        fi
    fi
}

# Banner
echo "=========================================="
echo "  Reorganización Docs - Todo por Dominio"
echo "=========================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -d "$DOCS_DIR/implementacion" ]; then
    log_error "No se encontró docs/implementacion/ - ¿Ya se ejecutó la reorganización?"
    exit 1
fi

cd "$PROJECT_ROOT"

# Fase 0: Preparación
echo ""
echo "=== FASE 0: Preparación ==="
echo ""

# Crear backup
BACKUP_NAME="docs_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
execute "tar -czf respaldo/$BACKUP_NAME docs/" "Crear backup de docs/ en respaldo/$BACKUP_NAME"

# Verificar que estamos en una rama git
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    log_error "No se detectó rama git activa"
    exit 1
fi
log_info "Rama actual: $CURRENT_BRANCH"

# Verificar estado git limpio
if [ "$DRY_RUN" = false ]; then
    if ! git diff-index --quiet HEAD --; then
        log_warning "Hay cambios sin commitear. Se continuará de todos modos..."
    fi
fi

# Fase 1: Reorganización Estructural
echo ""
echo "=== FASE 1: Reorganización Estructural ==="
echo ""

# 1.1 Mover backend
if [ -d "$DOCS_DIR/implementacion/backend" ]; then
    execute "mv $DOCS_DIR/implementacion/backend $DOCS_DIR/backend" "Mover implementacion/backend/ -> backend/"
else
    log_warning "implementacion/backend/ no existe, omitiendo"
fi

# 1.2 Mover frontend
if [ -d "$DOCS_DIR/implementacion/frontend" ]; then
    execute "mv $DOCS_DIR/implementacion/frontend $DOCS_DIR/frontend" "Mover implementacion/frontend/ -> frontend/"
else
    log_warning "implementacion/frontend/ no existe, omitiendo"
fi

# 1.3 Fusionar infrastructure
if [ -d "$DOCS_DIR/implementacion/infrastructure" ]; then
    execute "mkdir -p $DOCS_DIR/infrastructure_temp" "Crear directorio temporal para fusión"

    # Copiar contenido de implementacion/infrastructure/
    execute "cp -r $DOCS_DIR/implementacion/infrastructure/* $DOCS_DIR/infrastructure_temp/" "Copiar contenido de implementacion/infrastructure/"

    # Fusionar contenido de infraestructura/ si existe
    if [ -d "$DOCS_DIR/infraestructura" ]; then
        log_info "Fusionando contenido de infraestructura/"
        if [ -d "$DOCS_DIR/infraestructura/cpython_precompilado" ]; then
            execute "cp -r $DOCS_DIR/infraestructura/cpython_precompilado $DOCS_DIR/infrastructure_temp/" "Copiar cpython_precompilado/"
        fi
    fi

    # Renombrar a infrastructure/
    execute "mv $DOCS_DIR/infrastructure_temp $DOCS_DIR/infrastructure" "Renombrar a infrastructure/"

    # Eliminar directorios antiguos
    if [ "$DRY_RUN" = false ]; then
        log_info "Eliminando directorios antiguos"
        rm -rf "$DOCS_DIR/implementacion/infrastructure"
        rm -rf "$DOCS_DIR/infraestructura"
    else
        echo "[DRY-RUN] Eliminar $DOCS_DIR/implementacion/infrastructure"
        echo "[DRY-RUN] Eliminar $DOCS_DIR/infraestructura"
    fi
else
    log_warning "implementacion/infrastructure/ no existe, omitiendo"
fi

# 1.4 Eliminar directorio implementacion/ si está vacío
if [ -d "$DOCS_DIR/implementacion" ]; then
    if [ "$DRY_RUN" = false ]; then
        if [ -z "$(ls -A $DOCS_DIR/implementacion)" ]; then
            rmdir "$DOCS_DIR/implementacion"
            log_success "Eliminado directorio implementacion/ vacío"
        else
            log_warning "implementacion/ no está vacío, no se eliminó. Contenido:"
            ls -la "$DOCS_DIR/implementacion"
        fi
    else
        echo "[DRY-RUN] Verificar si implementacion/ está vacío y eliminarlo"
    fi
fi

# Fase 2: Actualizar Referencias
echo ""
echo "=== FASE 2: Actualizar Referencias ==="
echo ""

if [ "$DRY_RUN" = false ]; then
    log_info "Actualizando referencias en archivos .md"

    # Buscar y reemplazar referencias a implementacion/backend
    find "$DOCS_DIR" -name "*.md" -type f -exec sed -i \
        -e 's|docs/implementacion/backend/|docs/backend/|g' \
        -e 's|implementacion/backend/|backend/|g' \
        -e 's|\.\./\.\./\.\./implementacion/backend/|../../backend/|g' \
        -e 's|\.\./implementacion/backend/|../backend/|g' \
        {} +

    # Buscar y reemplazar referencias a implementacion/frontend
    find "$DOCS_DIR" -name "*.md" -type f -exec sed -i \
        -e 's|docs/implementacion/frontend/|docs/frontend/|g' \
        -e 's|implementacion/frontend/|frontend/|g' \
        -e 's|\.\./\.\./\.\./implementacion/frontend/|../../frontend/|g' \
        -e 's|\.\./implementacion/frontend/|../frontend/|g' \
        {} +

    # Buscar y reemplazar referencias a implementacion/infrastructure e infraestructura
    find "$DOCS_DIR" -name "*.md" -type f -exec sed -i \
        -e 's|docs/implementacion/infrastructure/|docs/infrastructure/|g' \
        -e 's|implementacion/infrastructure/|infrastructure/|g' \
        -e 's|\.\./\.\./\.\./implementacion/infrastructure/|../../infrastructure/|g' \
        -e 's|\.\./implementacion/infrastructure/|../infrastructure/|g' \
        -e 's|docs/infraestructura/|docs/infrastructure/|g' \
        -e 's|infraestructura/cpython|infrastructure/cpython|g' \
        {} +

    log_success "Referencias actualizadas en archivos .md"

    # Actualizar scripts si existen
    if [ -f "$PROJECT_ROOT/scripts/requisitos/generate_requirements_index.py" ]; then
        log_info "Actualizando script generate_requirements_index.py"
        sed -i 's|docs/implementacion|docs|g' "$PROJECT_ROOT/scripts/requisitos/generate_requirements_index.py"
    fi

    if [ -f "$PROJECT_ROOT/.github/workflows/scripts/generate_requirements_index.py" ]; then
        log_info "Actualizando script en .github/workflows/"
        sed -i 's|docs/implementacion|docs|g' "$PROJECT_ROOT/.github/workflows/scripts/generate_requirements_index.py"
    fi
else
    echo "[DRY-RUN] Actualizar referencias en todos los archivos .md"
    echo "[DRY-RUN] Patrones a reemplazar:"
    echo "  - docs/implementacion/backend/ -> docs/backend/"
    echo "  - docs/implementacion/frontend/ -> docs/frontend/"
    echo "  - docs/implementacion/infrastructure/ -> docs/infrastructure/"
    echo "  - docs/infraestructura/ -> docs/infrastructure/"
fi

# Fase 3: Validación
echo ""
echo "=== FASE 3: Validación ==="
echo ""

# Contar archivos
log_info "Contando archivos por dominio"
BACKEND_COUNT=$(find "$DOCS_DIR/backend" -name "*.md" -type f 2>/dev/null | wc -l || echo "0")
FRONTEND_COUNT=$(find "$DOCS_DIR/frontend" -name "*.md" -type f 2>/dev/null | wc -l || echo "0")
INFRA_COUNT=$(find "$DOCS_DIR/infrastructure" -name "*.md" -type f 2>/dev/null | wc -l || echo "0")

echo ""
echo "Archivos por dominio:"
echo "  Backend:        $BACKEND_COUNT archivos .md"
echo "  Frontend:       $FRONTEND_COUNT archivos .md"
echo "  Infrastructure: $INFRA_COUNT archivos .md"
echo ""

# Verificar que directorios principales existen
log_info "Verificando estructura final"
EXPECTED_DIRS=("backend" "frontend" "infrastructure" "arquitectura" "gobernanza" "requisitos" "adr" "plantillas" "anexos")
ALL_OK=true

for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$DOCS_DIR/$dir" ]; then
        echo "  OK $dir/"
    else
        echo "  WARNING Falta $dir/"
        ALL_OK=false
    fi
done

echo ""

if [ "$ALL_OK" = true ]; then
    log_success "Estructura validada correctamente"
else
    log_warning "Algunos directorios esperados no existen"
fi

# Fase 4: Git
echo ""
echo "=== FASE 4: Git Operations ==="
echo ""

if [ "$DRY_RUN" = false ]; then
    log_info "Agregando cambios a git"
    git add "$DOCS_DIR/"

    log_info "Estado de git:"
    git status --short | head -20

    echo ""
    log_info "Los cambios han sido agregados a staging"
    log_info "Para commitear, ejecutar:"
    echo ""
    echo "  git commit -m \"refactor(docs): reorganizar estructura por dominio eliminando nivel implementacion/\""
    echo ""
else
    echo "[DRY-RUN] git add docs/"
    echo "[DRY-RUN] git commit con mensaje apropiado"
fi

# Resumen final
echo ""
echo "=========================================="
echo "  Resumen de Reorganización"
echo "=========================================="
echo ""
echo "Backup creado:      respaldo/$BACKUP_NAME"
echo "Archivos backend:   $BACKEND_COUNT"
echo "Archivos frontend:  $FRONTEND_COUNT"
echo "Archivos infra:     $INFRA_COUNT"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "MODO DRY-RUN: Ningún cambio fue aplicado"
    echo "Para ejecutar la reorganización real, ejecutar:"
    echo "  $0"
else
    log_success "Reorganización completada exitosamente"
    echo ""
    echo "Próximos pasos:"
    echo "1. Revisar cambios: git status"
    echo "2. Verificar estructura: tree -L 2 docs/"
    echo "3. Regenerar índices ISO: python scripts/requisitos/generate_requirements_index.py"
    echo "4. Probar MkDocs: cd docs && mkdocs serve"
    echo "5. Commitear: git commit -m \"refactor(docs): reorganizar por dominio\""
    echo "6. Push: git push"
fi

echo ""
