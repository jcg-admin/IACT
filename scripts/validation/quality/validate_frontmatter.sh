#!/bin/bash
# scripts/validation/quality/validate_frontmatter.sh
# Validates YAML frontmatter in Markdown requirement files
# Migrated from: .github/workflows/lint.yml (100% SHELL, NO Python)
# Reference: SHELL_SCRIPTS_CONSTITUTION.md

set -euo pipefail

readonly VERSION="1.0.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Exit codes
readonly EXIT_SUCCESS=0
readonly EXIT_FAIL=1
readonly EXIT_WARNING=2

# Required frontmatter fields
readonly REQUIRED_FIELDS="id tipo titulo dominio owner prioridad estado fecha_creacion"

# Valid ID pattern: (N|RN|RS|RF|RNF)-XXX
readonly ID_PATTERN='^(N|RN|RS|RF|RNF)-[0-9]{3}$'

# Global counters
VALID_COUNT=0
ERROR_COUNT=0
WARNING_COUNT=0

# Arrays for errors and warnings
declare -a ERRORS
declare -a WARNINGS

# Output format (text or json)
OUTPUT_FORMAT="text"

# =============================================================================
# FUNCTIONS
# =============================================================================

log_info() {
    echo "[INFO] $*"
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_warning() {
    echo "[WARNING] $*" >&2
}

# Extract frontmatter from markdown file
extract_frontmatter() {
    local file="$1"

    # Extract content between first --- and second ---
    awk '
        BEGIN { in_frontmatter=0; found_start=0 }
        /^---$/ {
            if (!found_start) {
                found_start=1
                in_frontmatter=1
                next
            } else if (in_frontmatter) {
                exit
            }
        }
        in_frontmatter { print }
    ' "$file"
}

# Parse simple YAML (key: value)
parse_yaml_field() {
    local yaml_content="$1"
    local field_name="$2"

    echo "$yaml_content" | grep "^${field_name}:" | sed "s/^${field_name}:[[:space:]]*//" | tr -d '\r'
}

# Check if frontmatter exists
has_frontmatter() {
    local file="$1"

    # Check if file starts with ---
    if ! head -1 "$file" | grep -q '^---$'; then
        return 1
    fi

    # Check if there's a closing ---
    if ! grep -q '^---$' <(tail -n +2 "$file"); then
        return 1
    fi

    return 0
}

# Validate single file
validate_file() {
    local file="$1"
    local filename=$(basename "$file")

    # Skip files starting with underscore
    if [[ "$filename" == _* ]]; then
        return 0
    fi

    # Check frontmatter exists
    if ! has_frontmatter "$file"; then
        ERRORS+=("ERROR: $file: No frontmatter found")
        ERROR_COUNT=$((ERROR_COUNT + 1))
        return 1
    fi

    # Extract frontmatter
    local frontmatter
    frontmatter=$(extract_frontmatter "$file")

    # Check required fields
    local missing_fields=""
    for field in $REQUIRED_FIELDS; do
        local value
        value=$(parse_yaml_field "$frontmatter" "$field")

        if [ -z "$value" ]; then
            if [ -z "$missing_fields" ]; then
                missing_fields="$field"
            else
                missing_fields="$missing_fields, $field"
            fi
        fi
    done

    if [ -n "$missing_fields" ]; then
        ERRORS+=("ERROR: $file: Missing required fields: $missing_fields")
        ERROR_COUNT=$((ERROR_COUNT + 1))
        return 1
    fi

    # File is valid
    VALID_COUNT=$((VALID_COUNT + 1))

    # Check ID format (warning only)
    local id_value
    id_value=$(parse_yaml_field "$frontmatter" "id")

    if [ -n "$id_value" ]; then
        if ! echo "$id_value" | grep -qE "$ID_PATTERN"; then
            WARNINGS+=("WARNING: $file: ID '$id_value' does not follow standard format (N|RN|RS|RF|RNF)-XXX")
            WARNING_COUNT=$((WARNING_COUNT + 1))
        fi
    fi

    return 0
}

# Find all markdown files in requisitos directories
find_requisitos_files() {
    local base_path="$1"

    # Find all .md files in directories containing "requisitos"
    find "$base_path" -type f -name "*.md" | while read -r file; do
        if echo "$file" | grep -q "requisitos"; then
            echo "$file"
        fi
    done
}

# Report results in text format
report_text() {
    echo "Validating requirements frontmatter..."
    echo "========================================"
    echo ""

    # Print errors
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "ERRORS:"
        for error in "${ERRORS[@]}"; do
            echo "  $error"
        done
        echo ""
    fi

    # Print warnings
    if [ $WARNING_COUNT -gt 0 ]; then
        echo "WARNINGS:"
        for warning in "${WARNINGS[@]}"; do
            echo "  $warning"
        done
        echo ""
    fi

    # Print summary
    echo "Validation Results:"
    echo "  Valid files: $VALID_COUNT"
    echo "  Errors: $ERROR_COUNT"
    echo "  Warnings: $WARNING_COUNT"
    echo ""

    if [ $ERROR_COUNT -gt 0 ]; then
        echo "VALIDATION FAILED"
        return $EXIT_FAIL
    else
        echo "VALIDATION PASSED"
        return $EXIT_SUCCESS
    fi
}

# Report results in JSON format
report_json() {
    local status
    local exit_code

    if [ $ERROR_COUNT -gt 0 ]; then
        status="FAIL"
        exit_code=$EXIT_FAIL
    elif [ $WARNING_COUNT -gt 0 ]; then
        status="WARNING"
        exit_code=$EXIT_WARNING
    else
        status="PASS"
        exit_code=$EXIT_SUCCESS
    fi

    # Build JSON manually (no Python, no jq dependency)
    echo "{"
    echo "  \"validator\": \"validate_frontmatter\","
    echo "  \"version\": \"$VERSION\","
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"status\": \"$status\","
    echo "  \"exit_code\": $exit_code,"
    echo "  \"summary\": {"
    echo "    \"valid_files\": $VALID_COUNT,"
    echo "    \"errors\": $ERROR_COUNT,"
    echo "    \"warnings\": $WARNING_COUNT"
    echo "  },"
    echo "  \"errors\": ["

    # Print errors
    local first=true
    for error in "${ERRORS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        # Escape quotes in error message
        local escaped_error="${error//\"/\\\"}"
        echo -n "    {\"message\": \"$escaped_error\"}"
    done
    echo ""
    echo "  ],"
    echo "  \"warnings\": ["

    # Print warnings
    first=true
    for warning in "${WARNINGS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        local escaped_warning="${warning//\"/\\\"}"
        echo -n "    {\"message\": \"$escaped_warning\"}"
    done
    echo ""
    echo "  ]"
    echo "}"

    return $exit_code
}

# Show help
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Validate YAML frontmatter in requirement Markdown files.

Options:
  --path PATH          Base path to search for requirement files (required)
  --output FORMAT      Output format: text or json (default: text)
  --version            Show version
  -h, --help           Show this help

Examples:
  # Validate requirements directory
  $(basename "$0") --path docs/requisitos/

  # Validate with JSON output
  $(basename "$0") --path docs/ --output json

Exit Codes:
  0    All files valid
  1    Errors found (missing required fields)
  2    Warnings found (ID format issues)

Required Frontmatter Fields:
  - id, tipo, titulo, dominio, owner, prioridad, estado, fecha_creacion

ID Format:
  - Pattern: (N|RN|RS|RF|RNF)-XXX
  - Examples: N-001, RN-042, RF-123

Version: $VERSION
EOF
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    local base_path=""

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --path)
                base_path="$2"
                shift 2
                ;;
            --output)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            --version)
                echo "validate_frontmatter.sh version $VERSION"
                exit 0
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Validate arguments
    if [ -z "$base_path" ]; then
        log_error "Missing required argument: --path"
        show_help
        exit 1
    fi

    if [ ! -d "$base_path" ]; then
        log_error "Path does not exist: $base_path"
        exit 1
    fi

    # Find and validate files
    while IFS= read -r file; do
        validate_file "$file"
    done < <(find_requisitos_files "$base_path")

    # Report results
    if [ "$OUTPUT_FORMAT" = "json" ]; then
        report_json
    else
        report_text
    fi

    return $?
}

main "$@"
