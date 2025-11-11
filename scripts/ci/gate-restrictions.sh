#!/bin/bash
# gate-restrictions.sh
#
# Gate: Validates critical project restrictions
#
# Exit codes:
#   0 - All restrictions followed
#   1 - Restriction violations found

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log_info "Running Project Restrictions Gate"

# Activar entorno virtual si existe
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Ejecutar gate agent
cd "$PROJECT_ROOT"

python3 scripts/ai/agents/validation/restrictions_gate.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log_info "Project Restrictions Gate: PASS"
    exit 0
else
    log_error "Project Restrictions Gate: FAIL"
    exit 1
fi
