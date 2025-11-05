#!/bin/bash
# scripts/ai/examples/quickstart.sh
# Guía de inicio rápido para generación de tests con LLM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$AI_DIR/../.." && pwd)"

echo "=========================================="
echo "  GENERADOR DE TESTS - INICIO RAPIDO"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de ayuda
show_help() {
    echo "Uso: ./quickstart.sh [OPCION]"
    echo ""
    echo "Opciones:"
    echo "  check       - Validar entorno y dependencias"
    echo "  demo        - Ejecutar demo en modo dry-run"
    echo "  basic       - Ejecución básica (configuración por defecto)"
    echo "  aggressive  - Ejecución agresiva (90% cobertura, 10 tests)"
    echo "  conservative- Ejecución conservadora (80% cobertura, 3 tests)"
    echo "  help        - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./quickstart.sh check"
    echo "  ./quickstart.sh demo"
    echo "  ./quickstart.sh basic"
    exit 0
}

# Validar entorno
check_environment() {
    echo "Validando entorno..."
    echo ""

    ERRORS=0

    # Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}[OK]${NC} Python 3 encontrado: $PYTHON_VERSION"
    else
        echo -e "${RED}[FAIL]${NC} Python 3 no encontrado"
        ERRORS=$((ERRORS + 1))
    fi

    # pip
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} pip3 encontrado"
    else
        echo -e "${RED}[FAIL]${NC} pip3 no encontrado"
        ERRORS=$((ERRORS + 1))
    fi

    # pytest
    if python3 -c "import pytest" 2>/dev/null; then
        PYTEST_VERSION=$(python3 -c "import pytest; print(pytest.__version__)")
        echo -e "${GREEN}[OK]${NC} pytest encontrado: $PYTEST_VERSION"
    else
        echo -e "${YELLOW}[WARN]${NC} pytest no encontrado (instalar: pip install pytest)"
        ERRORS=$((ERRORS + 1))
    fi

    # pytest-cov
    if python3 -c "import pytest_cov" 2>/dev/null; then
        echo -e "${GREEN}[OK]${NC} pytest-cov encontrado"
    else
        echo -e "${YELLOW}[WARN]${NC} pytest-cov no encontrado (instalar: pip install pytest-cov)"
        ERRORS=$((ERRORS + 1))
    fi

    # anthropic
    if python3 -c "import anthropic" 2>/dev/null; then
        echo -e "${GREEN}[OK]${NC} anthropic SDK encontrado"
    else
        echo -e "${YELLOW}[WARN]${NC} anthropic SDK no encontrado (instalar: pip install anthropic)"
        ERRORS=$((ERRORS + 1))
    fi

    # API Key
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        echo -e "${GREEN}[OK]${NC} ANTHROPIC_API_KEY configurada"
    else
        echo -e "${YELLOW}[WARN]${NC} ANTHROPIC_API_KEY no configurada"
        echo "         export ANTHROPIC_API_KEY='tu-api-key'"
        ERRORS=$((ERRORS + 1))
    fi

    # gh CLI (opcional)
    if command -v gh &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} GitHub CLI encontrado"
    else
        echo -e "${YELLOW}[INFO]${NC} GitHub CLI no encontrado (PR creation deshabilitado)"
    fi

    echo ""

    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}Entorno OK - Listo para ejecutar${NC}"
        return 0
    else
        echo -e "${RED}Se encontraron $ERRORS problemas${NC}"
        echo ""
        echo "Instalar dependencias faltantes:"
        echo "  pip install pytest pytest-cov anthropic ruff black isort mypy"
        return 1
    fi
}

# Demo en dry-run
run_demo() {
    echo "Ejecutando DEMO (dry-run - sin modificar código)..."
    echo ""

    cd "$AI_DIR"

    python3 test_generation_orchestrator.py \
        --project-path "$PROJECT_ROOT/api/callcentersite" \
        --config config/test_generation_dry_run.json \
        --dry-run

    echo ""
    echo "Demo completado. Ver resultados en: output/test_generation_dryrun/"
}

# Ejecución básica
run_basic() {
    echo "Ejecutando configuración BÁSICA..."
    echo ""

    cd "$AI_DIR"

    python3 test_generation_orchestrator.py \
        --project-path "$PROJECT_ROOT/api/callcentersite" \
        --config config/test_generation.json

    echo ""
    echo "Ejecución completada. Ver resultados en: output/test_generation/"
}

# Ejecución agresiva
run_aggressive() {
    echo "Ejecutando configuración AGRESIVA (90% cobertura, 10 tests)..."
    echo ""
    echo -e "${YELLOW}ADVERTENCIA: Esta configuración es exigente${NC}"
    echo "  - Objetivo: 90% de cobertura"
    echo "  - Genera hasta 10 archivos de test"
    echo "  - Requiere +8% de incremento mínimo"
    echo ""
    read -p "Continuar? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelado"
        exit 0
    fi

    cd "$AI_DIR"

    python3 test_generation_orchestrator.py \
        --project-path "$PROJECT_ROOT/api/callcentersite" \
        --config config/test_generation_aggressive.json

    echo ""
    echo "Ejecución completada. Ver resultados en: output/test_generation/"
}

# Ejecución conservadora
run_conservative() {
    echo "Ejecutando configuración CONSERVADORA (80% cobertura, 3 tests)..."
    echo ""

    cd "$AI_DIR"

    python3 test_generation_orchestrator.py \
        --project-path "$PROJECT_ROOT/api/callcentersite" \
        --config config/test_generation_conservative.json

    echo ""
    echo "Ejecución completada. Ver resultados en: output/test_generation/"
}

# Main
main() {
    if [ $# -eq 0 ]; then
        show_help
    fi

    case "$1" in
        check)
            check_environment
            ;;
        demo)
            check_environment || exit 1
            run_demo
            ;;
        basic)
            check_environment || exit 1
            run_basic
            ;;
        aggressive)
            check_environment || exit 1
            run_aggressive
            ;;
        conservative)
            check_environment || exit 1
            run_conservative
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Error: Opción desconocida '$1'${NC}"
            echo ""
            show_help
            ;;
    esac
}

main "$@"
