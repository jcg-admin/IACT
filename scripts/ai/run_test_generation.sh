#!/bin/bash
# Script rápido para ejecutar generación de tests

set -e

PROJECT_PATH="${1:-../../api/callcentersite}"
DRY_RUN="${2:-}"

echo "=========================================="
echo "Test Generation Pipeline"
echo "=========================================="
echo "Proyecto: $PROJECT_PATH"
echo ""

# Verificar API key
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: Configura ANTHROPIC_API_KEY o OPENAI_API_KEY"
    exit 1
fi

# Ejecutar orquestador
if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "Modo: DRY RUN (sin crear PR)"
    python test_generation_orchestrator.py --project-path "$PROJECT_PATH" --dry-run
else
    echo "Modo: PRODUCCIÓN (creará PR)"
    python test_generation_orchestrator.py --project-path "$PROJECT_PATH"
fi
