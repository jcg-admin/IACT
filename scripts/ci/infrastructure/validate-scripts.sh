#!/bin/bash
# validate-scripts.sh
#
# Test Validation Scripts
# Replica: Infrastructure CI / Test Validation Scripts
#
# Exit codes:
#   0 - All scripts valid
#   1 - Some scripts invalid

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

log_info "Validating all shell scripts..."

SCRIPTS_VALID=0
SCRIPTS_INVALID=0

# Find all shell scripts
SHELL_SCRIPTS=$(find "$PROJECT_ROOT/scripts" -type f -name "*.sh")

for script in $SHELL_SCRIPTS; do
    log_info "Validating: $script"

    # Check 1: Shebang exists
    if ! head -n 1 "$script" | grep -q '^#!/'; then
        log_error "Missing shebang: $script"
        SCRIPTS_INVALID=$((SCRIPTS_INVALID + 1))
        continue
    fi

    # Check 2: Syntax check
    if bash -n "$script" &> /dev/null; then
        log_info "Syntax OK: $script"
        SCRIPTS_VALID=$((SCRIPTS_VALID + 1))
    else
        log_error "Syntax error: $script"
        bash -n "$script"
        SCRIPTS_INVALID=$((SCRIPTS_INVALID + 1))
    fi

    # Check 3: Executable permission
    if [ -x "$script" ]; then
        log_info "Executable: $script"
    else
        log_error "Not executable: $script"
        SCRIPTS_INVALID=$((SCRIPTS_INVALID + 1))
    fi
done

# Summary
echo ""
log_info "Script Validation Summary"
log_info "Valid: $SCRIPTS_VALID"
log_error "Invalid: $SCRIPTS_INVALID"

if [ $SCRIPTS_INVALID -eq 0 ]; then
    log_info "All scripts are valid"
    exit 0
else
    log_error "Some scripts are invalid"
    exit 1
fi
