#!/bin/bash
# gate-route-lint.sh
#
# Gate: Verifica que todos los ViewSets tengan permission_classes definidas
#
# Exit codes:
#   0 - No violations found
#   1 - Violations found
#   2 - Error de ejecución

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Encontrar raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log_info "Running Route Lint Gate"
log_info "Project root: $PROJECT_ROOT"

# Activar entorno virtual si existe
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    log_error "Python3 not found"
    exit 2
fi

# Ejecutar Route Lint Agent
cd "$PROJECT_ROOT"

python3 scripts/ai/agents/permissions/route_linter.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log_info "Route Lint Gate: PASS"
    exit 0
else
    log_error "Route Lint Gate: FAIL"
    exit 1
fi
