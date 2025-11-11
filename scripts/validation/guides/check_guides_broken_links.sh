#!/bin/bash
# check_guides_broken_links.sh
# Validator: Check for broken internal links in guide documents
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks internal markdown links
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - No broken links found
#   2 - Broken links found (warning only, non-blocking)

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly GUIDES_PATH="${PROJECT_ROOT}/docs/guias"

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

# Extract markdown links from a file
# Returns: list of link paths (one per line)
extract_markdown_links() {
    local file="$1"

    # Match markdown links: [text](path)
    # This regex extracts the path from [anything](path) format
    grep -oE '\]\([^)]+\)' "$file" 2>/dev/null | sed 's/](\(.*\))/\1/' || true
}

# Check if a link should be validated
should_check_link() {
    local link="$1"

    # Skip external links (http://, https://)
    if [[ "$link" =~ ^https?:// ]]; then
        return 1
    fi

    # Skip anchor links (#section)
    if [[ "$link" =~ ^# ]]; then
        return 1
    fi

    # Skip links outside guides/ directory (../)
    if [[ "$link" =~ ^\.\.\/ ]]; then
        return 1
    fi

    return 0
}

# Check broken links in a single guide file
check_file_links() {
    local guide_file="$1"
    local errors=0

    # Extract all markdown links from the file
    local links
    if ! links=$(extract_markdown_links "$guide_file"); then
        # grep failed for real error (not just no matches)
        if [ $? -ne 1 ]; then
            log_warning "${guide_file}: Error extracting links"
            return 2
        fi
        # No links found - that's OK
        return 0
    fi

    # Check each link
    while IFS= read -r link_path; do
        # Skip if empty or should not be checked
        if [ -z "$link_path" ]; then
            continue
        fi

        if ! should_check_link "$link_path"; then
            continue
        fi

        # Resolve path relative to guide file's directory
        local guide_dir
        guide_dir=$(dirname "$guide_file")
        local target_path="${guide_dir}/${link_path}"

        # Check if target exists
        if [ ! -e "$target_path" ]; then
            log_warning "${guide_file}: Broken link to '${link_path}'"
            errors=$((errors + 1))
        fi
    done <<< "$links"

    return "$errors"
}

# Main function
main() {
    log_info "Checking for broken internal links..."

    if [ ! -d "$GUIDES_PATH" ]; then
        log_warning "Guides directory not found: ${GUIDES_PATH}"
        return 2
    fi

    local total_errors=0
    local total_guides=0

    # Find all markdown files and check their links
    while IFS= read -r guide_file; do
        total_guides=$((total_guides + 1))
        check_file_links "$guide_file" || total_errors=$((total_errors + $?))
    done < <(find "$GUIDES_PATH" -name "*.md" -type f)

    echo ""
    if [ "$total_errors" -gt 0 ]; then
        log_warning "BROKEN LINKS FOUND"
        log_warning "  - Total broken links: ${total_errors}"
        log_warning "  - Total guides checked: ${total_guides}"
        echo ""
        log_warning "Please fix broken links before merging"
        # Return 2 (warning) not 1 (failure) - don't block builds yet
        return 2
    else
        log_success "No broken internal links found"
        log_info "Checked ${total_guides} guide files"
        return 0
    fi
}

main "$@"
