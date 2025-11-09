#!/bin/bash
# check_docs_old_references.sh
# Validator: Check for old documentation structure references
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks for old docs references
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - No old references found
#   1 - Old structure references detected

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly DOCS_PATH="${PROJECT_ROOT}/docs"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Logging functions
log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_info() {
    echo "[INFO] $*"
}

# Check for old "implementacion/" references
check_implementacion_references() {
    log_info "Checking for old 'implementacion/' references..."

    if [ ! -d "$DOCS_PATH" ]; then
        log_error "docs/ directory not found: ${DOCS_PATH}"
        return 1
    fi

    local broken_refs
    broken_refs=$(grep -r "docs/implementacion/" "$DOCS_PATH" --include="*.md" 2>/dev/null || true)

    if [ -n "$broken_refs" ]; then
        log_error "Found references to old structure 'docs/implementacion/'"
        echo "The following files contain references to the old structure:"
        echo "$broken_refs"
        echo ""
        echo "Please update these references to use the new structure:"
        echo "  - docs/implementacion/backend/  -> docs/backend/"
        echo "  - docs/implementacion/frontend/ -> docs/frontend/"
        echo "  - docs/implementacion/infrastructure/ -> docs/infrastructure/"
        return 1
    else
        log_success "No references to old structure found"
        return 0
    fi
}

# Check for old "infraestructura/" references (Spanish)
check_infraestructura_references() {
    log_info "Checking for old 'infraestructura/' references..."

    local broken_refs
    broken_refs=$(grep -r "docs/infraestructura/" "$DOCS_PATH" --include="*.md" 2>/dev/null || true)

    if [ -n "$broken_refs" ]; then
        log_error "Found references to old structure 'docs/infraestructura/'"
        echo "The following files contain references to the old structure:"
        echo "$broken_refs"
        echo ""
        echo "Please update these references to use: docs/infrastructure/"
        return 1
    else
        log_success "No references to old 'infraestructura/' found"
        return 0
    fi
}

# Main function
main() {
    local exit_code=0

    log_info "Starting documentation old references check..."

    # Check for both types of old references
    check_implementacion_references || exit_code=1
    echo ""
    check_infraestructura_references || exit_code=1

    if [ "$exit_code" -eq 0 ]; then
        echo ""
        log_success "All documentation references are up to date"
    else
        echo ""
        log_error "Documentation structure validation failed"
        log_error "Please update old references before proceeding"
    fi

    return "$exit_code"
}

main "$@"
