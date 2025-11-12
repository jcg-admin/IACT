#!/bin/bash
# Cuenta requisitos por tipo en docs/implementacion/

echo "======================================"
echo "CONTADOR DE REQUISITOS"
echo "======================================"
echo ""

IMPL_PATH="docs/implementacion"

if [ ! -d "$IMPL_PATH" ]; then
    echo "ERROR: No existe la carpeta $IMPL_PATH"
    exit 1
fi

echo "INFO: Buscando en: $IMPL_PATH"
echo ""

# Contar por tipo
necesidades=$(find "$IMPL_PATH" -path "*/necesidades/*.md" -type f ! -name "README.md" ! -name "_*.md" | wc -l)
negocio=$(find "$IMPL_PATH" -path "*/negocio/*.md" -type f ! -name "README.md" ! -name "_*.md" | wc -l)
stakeholders=$(find "$IMPL_PATH" -path "*/stakeholders/*.md" -type f ! -name "README.md" ! -name "_*.md" | wc -l)
funcionales=$(find "$IMPL_PATH" -path "*/funcionales/*.md" -type f ! -name "README.md" ! -name "_*.md" | wc -l)
no_funcionales=$(find "$IMPL_PATH" -path "*/no_funcionales/*.md" -type f ! -name "README.md" ! -name "_*.md" | wc -l)

total=$((necesidades + negocio + stakeholders + funcionales + no_funcionales))

echo "Requisitos por tipo:"
echo "  Necesidades (N-XXX):        $necesidades"
echo "  Negocio (RN-XXX):           $negocio"
echo "  Stakeholders (RS-XXX):      $stakeholders"
echo "  Funcionales (RF-XXX):       $funcionales"
echo "  No Funcionales (RNF-XXX):   $no_funcionales"
echo ""
echo "======================================"
echo "  TOTAL:                      $total"
echo "======================================"
echo ""

# Contar por dominio
echo "Requisitos por dominio:"
backend=$(find "$IMPL_PATH/backend/requisitos" -name "*.md" -type f ! -name "README.md" ! -name "_*.md" 2>/dev/null | wc -l)
frontend=$(find "$IMPL_PATH/frontend/requisitos" -name "*.md" -type f ! -name "README.md" ! -name "_*.md" 2>/dev/null | wc -l)
infrastructure=$(find "$IMPL_PATH/infrastructure/requisitos" -name "*.md" -type f ! -name "README.md" ! -name "_*.md" 2>/dev/null | wc -l)

echo "  Backend:                    $backend"
echo "  Frontend:                   $frontend"
echo "  Infrastructure:             $infrastructure"
echo ""
