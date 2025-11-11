#!/bin/bash
# run-tdd-cycle.sh
#
# Ejecuta ciclo TDD completo usando TDD Agent v1.1
#
# Uso:
#   ./run-tdd-cycle.sh <component> <requirements_file> [agent_type] [--auto-fix]
#
# Argumentos:
#   component: Nombre del componente (ej: audit_validator)
#   requirements_file: Path a archivo JSON con requisitos
#   agent_type: Tipo de agente (gate|chain|template) [default: gate]
#   --auto-fix: Habilitar corrección automática de errores comunes (v1.1)
#
# Ejemplo:
#   ./run-tdd-cycle.sh audit_validator requirements/audit_validator.json gate
#   ./run-tdd-cycle.sh audit_validator requirements/audit_validator.json gate --auto-fix
#
# Exit codes:
#   0 - Todos los tests pasaron
#   1 - Tests fallaron (requiere intervención manual)
#   2 - Error de argumentos
#   3 - Error de ejecución

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones auxiliares
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validar argumentos
if [ $# -lt 2 ]; then
    log_error "Argumentos insuficientes"
    echo "Uso: $0 <component> <requirements_file> [agent_type]"
    exit 2
fi

COMPONENT=$1
REQUIREMENTS_FILE=$2
AGENT_TYPE=${3:-gate}
AUTO_FIX=""

# Detectar flag --auto-fix
for arg in "$@"; do
    if [ "$arg" == "--auto-fix" ]; then
        AUTO_FIX="--auto-fix"
        log_info "Auto-fix ENABLED (v1.1 feature)"
    fi
done

# Validar que existe el archivo de requisitos
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    log_error "Archivo de requisitos no encontrado: $REQUIREMENTS_FILE"
    exit 2
fi

# Validar tipo de agente
if [[ ! "$AGENT_TYPE" =~ ^(gate|chain|template)$ ]]; then
    log_error "Tipo de agente inválido: $AGENT_TYPE (debe ser: gate, chain, template)"
    exit 2
fi

# Encontrar raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log_info "Starting TDD cycle"
log_info "Component: $COMPONENT"
log_info "Requirements: $REQUIREMENTS_FILE"
log_info "Agent type: $AGENT_TYPE"
log_info "Project root: $PROJECT_ROOT"

# Activar entorno virtual si existe
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    log_info "Activating virtual environment"
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    log_info "Activating virtual environment"
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    log_error "Python3 not found"
    exit 3
fi

# Verificar que pytest está disponible
if ! command -v pytest &> /dev/null; then
    log_error "pytest not found. Install with: pip install pytest"
    exit 3
fi

# Ejecutar TDD Agent
log_info "Running TDD Agent..."
echo "========================================================================"

cd "$PROJECT_ROOT"

# Leer requirements del archivo JSON
if ! python3 -c "import json; json.load(open('$REQUIREMENTS_FILE'))" &> /dev/null; then
    log_error "Invalid JSON in requirements file: $REQUIREMENTS_FILE"
    exit 2
fi

# Extraer requirements text del JSON
REQUIREMENTS_TEXT=$(python3 -c "import json; print(json.load(open('$REQUIREMENTS_FILE')).get('requirements', ''))")

# Ejecutar TDD Agent v1.1
python3 "$PROJECT_ROOT/scripts/ai/agents/tdd/tdd_agent.py" \
    --component "$COMPONENT" \
    --requirements "$REQUIREMENTS_TEXT" \
    --type "$AGENT_TYPE" \
    $AUTO_FIX \
    --verbose

TDD_EXIT_CODE=$?

echo "========================================================================"

if [ $TDD_EXIT_CODE -eq 0 ]; then
    log_info "TDD Cycle completed successfully"
    log_info "All tests passing!"
    exit 0
else
    log_warn "TDD Cycle completed with failures"
    log_warn "Manual fixes required"

    # Encontrar el archivo de documentación generado
    DOC_FILE="$PROJECT_ROOT/docs/backend/permisos/promptops/TDD_${COMPONENT^^}_ERRORS.md"

    if [ -f "$DOC_FILE" ]; then
        log_info "Error documentation: $DOC_FILE"
        log_info "Review errors and fix code manually"

        # Encontrar el archivo de tests generado
        TEST_FILE="$PROJECT_ROOT/scripts/ai/agents/$COMPONENT/tests/test_${COMPONENT}.py"

        if [ -f "$TEST_FILE" ]; then
            log_info "Re-run tests with: pytest $TEST_FILE -v"
        fi
    fi

    exit 1
fi
