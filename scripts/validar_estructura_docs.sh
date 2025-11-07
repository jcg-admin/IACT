#!/bin/bash

# Script de validación de estructura docs/ después de reorganización
# Verifica que la reorganización fue exitosa

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ERRORS++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS++))
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo "=========================================="
echo "  Validación Estructura docs/"
echo "=========================================="
echo ""

# 1. Verificar que implementacion/ no existe o está vacío
echo "=== 1. Verificar eliminación de implementacion/ ==="
if [ -d "$DOCS_DIR/implementacion" ]; then
    if [ -z "$(ls -A $DOCS_DIR/implementacion)" ]; then
        log_warning "implementacion/ existe pero está vacío (debería eliminarse)"
    else
        log_error "implementacion/ todavía existe con contenido"
        ls -la "$DOCS_DIR/implementacion"
    fi
else
    log_success "implementacion/ eliminado correctamente"
fi
echo ""

# 2. Verificar que directorios principales existen
echo "=== 2. Verificar directorios principales ==="
EXPECTED_DIRS=("backend" "frontend" "infrastructure" "arquitectura" "gobernanza" "requisitos" "adr" "plantillas" "anexos")

for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$DOCS_DIR/$dir" ]; then
        log_success "$dir/ existe"
    else
        log_error "$dir/ no existe"
    fi
done
echo ""

# 3. Verificar subdirectorios por dominio
echo "=== 3. Verificar subdirectorios de dominios ==="

check_domain_structure() {
    local domain=$1
    local domain_dir="$DOCS_DIR/$domain"

    if [ ! -d "$domain_dir" ]; then
        log_error "$domain/ no existe"
        return
    fi

    log_info "Verificando $domain/"

    # Subdirectorios esperados
    local subdirs=("requisitos" "arquitectura")

    for subdir in "${subdirs[@]}"; do
        if [ -d "$domain_dir/$subdir" ]; then
            echo "  OK $domain/$subdir/"
        else
            echo "  WARNING Falta $domain/$subdir/"
        fi
    done
}

check_domain_structure "backend"
check_domain_structure "frontend"
check_domain_structure "infrastructure"
echo ""

# 4. Buscar referencias huérfanas a implementacion/
echo "=== 4. Buscar referencias a 'implementacion/' en archivos ==="
REFERENCES=$(grep -r "implementacion/" "$DOCS_DIR" --include="*.md" --exclude-dir=analisis_nov_2025 2>/dev/null || true)

if [ -z "$REFERENCES" ]; then
    log_success "No se encontraron referencias a 'implementacion/'"
else
    log_warning "Se encontraron referencias a 'implementacion/' en:"
    echo "$REFERENCES" | head -10
    if [ $(echo "$REFERENCES" | wc -l) -gt 10 ]; then
        echo "  ... y $(( $(echo "$REFERENCES" | wc -l) - 10 )) más"
    fi
fi
echo ""

# 5. Buscar referencias huérfanas a infraestructura/
echo "=== 5. Buscar referencias a 'infraestructura/' en archivos ==="
INFRA_REFS=$(grep -r "infraestructura/" "$DOCS_DIR" --include="*.md" --exclude-dir=analisis_nov_2025 2>/dev/null || true)

if [ -z "$INFRA_REFS" ]; then
    log_success "No se encontraron referencias a 'infraestructura/'"
else
    log_warning "Se encontraron referencias a 'infraestructura/' en:"
    echo "$INFRA_REFS" | head -10
fi
echo ""

# 6. Verificar conteo de archivos
echo "=== 6. Conteo de archivos por dominio ==="
BACKEND_COUNT=$(find "$DOCS_DIR/backend" -name "*.md" -type f 2>/dev/null | wc -l)
FRONTEND_COUNT=$(find "$DOCS_DIR/frontend" -name "*.md" -type f 2>/dev/null | wc -l)
INFRA_COUNT=$(find "$DOCS_DIR/infrastructure" -name "*.md" -type f 2>/dev/null | wc -l)
TOTAL_DOCS=$(find "$DOCS_DIR" -name "*.md" -type f 2>/dev/null | wc -l)

echo "Backend:        $BACKEND_COUNT archivos .md"
echo "Frontend:       $FRONTEND_COUNT archivos .md"
echo "Infrastructure: $INFRA_COUNT archivos .md"
echo "Total docs/:    $TOTAL_DOCS archivos .md"
echo ""

if [ $BACKEND_COUNT -eq 0 ]; then
    log_error "Backend no tiene archivos .md"
fi

if [ $FRONTEND_COUNT -eq 0 ]; then
    log_warning "Frontend no tiene archivos .md (puede ser normal)"
fi

if [ $INFRA_COUNT -eq 0 ]; then
    log_warning "Infrastructure no tiene archivos .md (puede ser normal)"
fi

# 7. Verificar enlaces markdown rotos (muestra de archivos principales)
echo "=== 7. Verificar enlaces en archivos principales ==="
MAIN_FILES=("$DOCS_DIR/README.md" "$DOCS_DIR/backend/README.md" "$DOCS_DIR/frontend/README.md" "$DOCS_DIR/infrastructure/README.md")

for file in "${MAIN_FILES[@]}"; do
    if [ -f "$file" ]; then
        BROKEN_LINKS=$(grep -oP '\[.*?\]\(\K[^)]+' "$file" 2>/dev/null | while read -r link; do
            # Solo verificar enlaces relativos (no URLs)
            if [[ ! "$link" =~ ^https?:// ]] && [[ ! "$link" =~ ^# ]]; then
                # Resolver ruta relativa
                LINK_DIR=$(dirname "$file")
                FULL_PATH="$LINK_DIR/$link"
                if [ ! -e "$FULL_PATH" ]; then
                    echo "$file -> $link (no existe)"
                fi
            fi
        done)

        if [ -z "$BROKEN_LINKS" ]; then
            log_success "$(basename $file) - enlaces OK"
        else
            log_warning "$(basename $file) tiene enlaces rotos:"
            echo "$BROKEN_LINKS"
        fi
    else
        log_warning "$(basename $file) no existe"
    fi
done
echo ""

# 8. Verificar que infraestructura/ antiguo no existe
echo "=== 8. Verificar fusión de infraestructura/ ==="
if [ -d "$DOCS_DIR/infraestructura" ]; then
    log_error "Directorio infraestructura/ (antiguo) todavía existe"
else
    log_success "Directorio infraestructura/ (antiguo) eliminado"
fi
echo ""

# 9. Verificar git status
echo "=== 9. Estado de git ==="
cd "$PROJECT_ROOT"

if git diff-index --quiet HEAD -- 2>/dev/null; then
    log_success "Working tree limpio (todos los cambios commiteados)"
else
    log_warning "Hay cambios sin commitear"
    git status --short | head -10
fi
echo ""

# Resumen final
echo "=========================================="
echo "  Resumen de Validación"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    log_success "Validación completada sin errores ni warnings"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    log_warning "Validación completada con $WARNINGS warnings"
    exit 0
else
    log_error "Validación completada con $ERRORS errores y $WARNINGS warnings"
    exit 1
fi
