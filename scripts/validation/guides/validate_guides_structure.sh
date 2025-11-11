#!/bin/bash
# validate_guides_structure.sh
# Validator: Check guide section structure
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only validates guide sections
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - All guides have required sections
#   1 - Missing sections detected

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly GUIDES_PATH="${PROJECT_ROOT}/docs/guias"

# Required sections for guides
readonly REQUIRED_SECTIONS=(
    "## Proposito"
    "## Pre-requisitos"
    "## Pasos"
    "## Validacion"
    "## Troubleshooting"
    "## Referencias"
)

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
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

# Validate single guide file
validate_guide_sections() {
    local file="$1"
    local errors=0

    # Skip README and METRICS files
    if [[ "$(basename "$file")" == "README.md" || "$(basename "$file")" == "METRICS.md" ]]; then
        return 0
    fi

    # Read file content
    local content
    content=$(<"$file")

    # Check each required section
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! echo "$content" | grep -qF "$section"; then
            log_error "${file}: Missing section '${section}'"
            errors=$((errors + 1))
        fi
    done

    return "$errors"
}

# Main function
main() {
    log_info "Validating guide sections..."

    if [ ! -d "$GUIDES_PATH" ]; then
        log_error "Guides directory not found: ${GUIDES_PATH}"
        return 1
    fi

    local total_errors=0
    local total_guides=0

    # Find all markdown files in guides directory
    while IFS= read -r guide_file; do
        total_guides=$((total_guides + 1))
        validate_guide_sections "$guide_file" || total_errors=$((total_errors + $?))
    done < <(find "$GUIDES_PATH" -name "*.md" -type f)

    echo ""
    if [ "$total_errors" -gt 0 ]; then
        log_error "Found $total_errors missing section(s) in guides"
        echo ""
        echo "Required sections for guides:"
        for section in "${REQUIRED_SECTIONS[@]}"; do
            echo "  - $section"
        done
        return 1
    else
        log_success "All guides have required sections"
        return 0
    fi
}

main "$@"
