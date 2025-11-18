#!/bin/bash
# Lista todos los requisitos con su información básica

echo "======================================"
echo "LISTA DE REQUISITOS"
echo "======================================"
echo ""

IMPL_PATH="docs/implementacion"

if [ ! -d "$IMPL_PATH" ]; then
    echo "ERROR: No existe la carpeta $IMPL_PATH"
    exit 1
fi

# Función para extraer el ID y título del frontmatter
extract_info() {
    local file=$1
    local id=$(grep "^id:" "$file" | head -1 | sed 's/id: *//' | tr -d ' ')
    local titulo=$(grep "^titulo:" "$file" | head -1 | sed 's/titulo: *//')
    local estado=$(grep "^estado:" "$file" | head -1 | sed 's/estado: *//' | tr -d ' ')

    if [ -n "$id" ]; then
        echo "  $id - $titulo [$estado]"
    else
        echo "  $(basename "$file") (sin ID)"
    fi
}

# Buscar y listar por tipo
echo "NECESIDADES DE NEGOCIO (N-XXX):"
necesidades=$(find "$IMPL_PATH" -path "*/necesidades/*.md" -type f ! -name "README.md" ! -name "_*.md" 2>/dev/null)
if [ -n "$necesidades" ]; then
    echo "$necesidades" | while read file; do
        extract_info "$file"
    done
else
    echo "  (ninguna)"
fi
echo ""

echo "REQUISITOS DE NEGOCIO (RN-XXX):"
negocio=$(find "$IMPL_PATH" -path "*/negocio/*.md" -type f ! -name "README.md" ! -name "_*.md" 2>/dev/null)
if [ -n "$negocio" ]; then
    echo "$negocio" | while read file; do
        extract_info "$file"
    done
else
    echo "  (ninguno)"
fi
echo ""

echo "REQUISITOS DE STAKEHOLDERS (RS-XXX):"
stakeholders=$(find "$IMPL_PATH" -path "*/stakeholders/*.md" -type f ! -name "README.md" ! -name "_*.md" 2>/dev/null)
if [ -n "$stakeholders" ]; then
    echo "$stakeholders" | while read file; do
        extract_info "$file"
    done
else
    echo "  (ninguno)"
fi
echo ""

echo "REQUISITOS FUNCIONALES (RF-XXX):"
funcionales=$(find "$IMPL_PATH" -path "*/funcionales/*.md" -type f ! -name "README.md" ! -name "_*.md" 2>/dev/null)
if [ -n "$funcionales" ]; then
    echo "$funcionales" | while read file; do
        extract_info "$file"
    done
else
    echo "  (ninguno)"
fi
echo ""

echo "REQUISITOS NO FUNCIONALES (RNF-XXX):"
no_funcionales=$(find "$IMPL_PATH" -path "*/no_funcionales/*.md" -type f ! -name "README.md" ! -name "_*.md" 2>/dev/null)
if [ -n "$no_funcionales" ]; then
    echo "$no_funcionales" | while read file; do
        extract_info "$file"
    done
else
    echo "  (ninguno)"
fi
echo ""
