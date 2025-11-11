#!/bin/bash
# check_guides_quality.sh
# Validator: Check guide quality (TODOs, length)
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks guide quality
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - All quality checks passed
#   2 - Warnings found (non-blocking)

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly GUIDES_PATH="${PROJECT_ROOT}/docs/guias"

# Quality thresholds
readonly MIN_LINES=50
readonly MAX_LINES=500

# Colors for output
readonly YELLOW='\033[1;33m'
readonly GREEN='\033[0;32m'
readonly NC='\033[0m' # No Color

# Logging functions
log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_info() {
    echo "[INFO] $*"
}

# Check for TODOs and placeholders
check_todos() {
    log_info "Checking for TODOs and placeholders..."

    local found_todos=false

    while IFS= read -r guide_file; do
        # Skip README and METRICS
        if [[ "$(basename "$guide_file")" == "README.md" || "$(basename "$guide_file")" == "METRICS.md" ]]; then
            continue
        fi

        if grep -qE "TBD|TODO|FIXME|XXX" "$guide_file"; then
            log_warning "${guide_file}: Contains TODOs or placeholders"
            found_todos=true
        fi
    done < <(find "$GUIDES_PATH" -name "*.md" -type f)

    if [ "$found_todos" = true ]; then
        log_warning "Found TODOs or placeholders in guides"
        log_warning "Please replace them with actual content before merging"
        return 2
    else
        log_success "No TODOs or placeholders found"
        return 0
    fi
}

# Check guide length
check_guide_length() {
    log_info "Checking guide lengths..."

    local warnings_found=false

    while IFS= read -r guide_file; do
        # Skip README and METRICS
        if [[ "$(basename "$guide_file")" == "README.md" || "$(basename "$guide_file")" == "METRICS.md" ]]; then
            continue
        fi

        local lines
        lines=$(wc -l < "$guide_file")

        # Guides should be comprehensive but not too long
        if [ "$lines" -lt "$MIN_LINES" ]; then
            log_warning "${guide_file}: Only $lines lines (might be too short)"
            warnings_found=true
        elif [ "$lines" -gt "$MAX_LINES" ]; then
            log_warning "${guide_file}: $lines lines (might be too long)"
            warnings_found=true
        fi
    done < <(find "$GUIDES_PATH" -name "*.md" -type f)

    if [ "$warnings_found" = true ]; then
        return 2
    else
        log_success "All guides have reasonable length"
        return 0
    fi
}

# Main function
main() {
    if [ ! -d "$GUIDES_PATH" ]; then
        log_warning "Guides directory not found: ${GUIDES_PATH}"
        return 2
    fi

    local exit_code=0

    # Run all quality checks
    check_todos || { local code=$?; [ "$code" -gt "$exit_code" ] && exit_code=$code; }
    echo ""
    check_guide_length || { local code=$?; [ "$code" -gt "$exit_code" ] && exit_code=$code; }

    return "$exit_code"
}

main "$@"
