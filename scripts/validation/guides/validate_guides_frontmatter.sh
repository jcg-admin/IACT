#!/bin/bash
# validate_guides_frontmatter.sh
# Validator: Check frontmatter in guide documents
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only validates guide frontmatter
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - All guides have valid frontmatter
#   1 - Missing or invalid frontmatter detected

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly GUIDES_PATH="${PROJECT_ROOT}/docs/guias"

# Required frontmatter fields for guides
readonly REQUIRED_FIELDS=("id" "tipo" "categoria" "audiencia" "prioridad" "version")

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

# Extract frontmatter from guide file
extract_frontmatter() {
    local file="$1"

    # Extract content between first two "---" markers
    awk '
        BEGIN { in_frontmatter=0; found_start=0; count=0 }
        /^---$/ {
            count++
            if (count == 1) {
                found_start=1
                in_frontmatter=1
                next
            } else if (count == 2 && in_frontmatter) {
                exit
            }
        }
        in_frontmatter { print }
    ' "$file"
}

# Validate single guide file
validate_guide() {
    local file="$1"
    local errors=0

    # Skip README and METRICS files
    if [[ "$(basename "$file")" == "README.md" || "$(basename "$file")" == "METRICS.md" ]]; then
        return 0
    fi

    # Check if file starts with frontmatter marker
    if ! head -1 "$file" | grep -q "^---$"; then
        log_error "${file}: Missing frontmatter"
        return 1
    fi

    # Extract frontmatter
    local frontmatter
    frontmatter=$(extract_frontmatter "$file")

    if [ -z "$frontmatter" ]; then
        log_error "${file}: Invalid frontmatter format"
        return 1
    fi

    # Check each required field
    for field in "${REQUIRED_FIELDS[@]}"; do
        if ! echo "$frontmatter" | grep -q "^${field}:"; then
            log_error "${file}: Missing required field '${field}'"
            errors=$((errors + 1))
        fi
    done

    return "$errors"
}

# Main function
main() {
    log_info "Validating frontmatter in all guides..."

    if [ ! -d "$GUIDES_PATH" ]; then
        log_error "Guides directory not found: ${GUIDES_PATH}"
        return 1
    fi

    local total_errors=0
    local total_guides=0

    # Find all markdown files in guides directory
    while IFS= read -r guide_file; do
        total_guides=$((total_guides + 1))
        validate_guide "$guide_file" || total_errors=$((total_errors + $?))
    done < <(find "$GUIDES_PATH" -name "*.md" -type f)

    echo ""
    if [ "$total_errors" -gt 0 ]; then
        log_error "Found $total_errors error(s) in guides frontmatter"
        echo ""
        echo "Required fields for guides:"
        for field in "${REQUIRED_FIELDS[@]}"; do
            echo "  - $field"
        done
        return 1
    else
        log_success "All $total_guides guides have valid frontmatter"
        return 0
    fi
}

main "$@"
