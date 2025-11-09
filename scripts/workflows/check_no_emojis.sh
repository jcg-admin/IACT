#!/bin/bash
# check_no_emojis.sh
# Validator: NO Emojis policy enforcement
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only detects emojis in files
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - No emojis found
#   1 - Emojis detected (policy violation)
#
# USAGE:
#   bash scripts/workflows/check_no_emojis.sh [files...]
#   bash scripts/workflows/check_no_emojis.sh --all

set -euo pipefail

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# File extensions to check
readonly VALID_EXTENSIONS="md|txt|py|js|ts|jsx|tsx|yaml|yml|json|sh|bash"

# Directories to exclude
readonly EXCLUDE_DIRS=".git|.venv|venv|node_modules|__pycache__|.pytest_cache|htmlcov|.mypy_cache|dist|build"

# Unicode emoji ranges (PCRE patterns for grep -P)
# NOTE: Using literal emojis since PCRE Unicode ranges may not be available in all grep versions
readonly COMMON_EMOJIS=(
    "✅" "❌" "⚠️" "🚀" "🔧" "📝" "💡" "🚨" "🔒" "🔐"
    "👍" "👎" "✓" "✗" "♻️" "🎯" "🏆" "📊" "📈" "📉"
    "🔴" "🟢" "🟡" "🔵" "⚪" "⚫" "🟠" "🟣" "🟤"
    "💻" "🖥️" "📱" "⌚" "🔌" "💾" "💿" "📀" "🖱️" "⌨️"
    "🎉" "🎊" "🎈" "🎁" "🏅" "🥇" "🥈" "🥉" "🏃" "🚶"
)

# Box-drawing characters (PERMITTED for directory trees) - Unicode U+2500-U+257F
# These will be explicitly filtered out
readonly BOX_DRAWING_CHARS="─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"

# Counters
total_emojis=0
files_with_emojis=0
files_checked=0

# Logging functions
log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_info() {
    echo "$*"
}

# Check if file should be validated
should_check_file() {
    local file="$1"

    # Check if file exists
    if [ ! -f "$file" ]; then
        return 1
    fi

    # SPECIAL CASE: Exclude this script itself (contains emoji definitions for detection)
    if echo "$file" | grep -q "check_no_emojis.sh"; then
        return 1
    fi

    # Check extension
    if ! echo "$file" | grep -qE "\.($VALID_EXTENSIONS)$"; then
        return 1
    fi

    # Check excluded directories
    if echo "$file" | grep -qE "($EXCLUDE_DIRS)"; then
        return 1
    fi

    # Check if file is binary (skip binary files)
    if file "$file" | grep -q "binary"; then
        return 1
    fi

    return 0
}

# Check single file for emojis
check_file_for_emojis() {
    local file="$1"
    local found_in_file=0
    local line_num=0

    # Read file line by line
    while IFS= read -r line || [ -n "$line" ]; do
        line_num=$((line_num + 1))

        # Check each common emoji
        for emoji in "${COMMON_EMOJIS[@]}"; do
            if echo "$line" | grep -qF "$emoji"; then
                # Check if it's a box-drawing character (permitted)
                local is_box_drawing=false
                for box_char in $(echo "$BOX_DRAWING_CHARS" | fold -w1); do
                    if [ "$emoji" = "$box_char" ]; then
                        is_box_drawing=true
                        break
                    fi
                done

                if [ "$is_box_drawing" = false ]; then
                    if [ "$found_in_file" -eq 0 ]; then
                        echo ""
                        log_error "Emojis detectados en: $file"
                        echo "======================================================================"
                        found_in_file=1
                        files_with_emojis=$((files_with_emojis + 1))
                    fi

                    total_emojis=$((total_emojis + 1))
                    echo "  Línea $line_num: $emoji"
                    # Show context (first 60 chars)
                    local context="${line:0:60}"
                    echo "    Contexto: $context..."
                fi
            fi
        done

        # Additional check using grep with Unicode patterns (if available)
        # This catches emojis not in our common list
        # PCRE Unicode property classes: \p{Emoji}
        if command -v grep >/dev/null 2>&1; then
            # Try PCRE mode (-P) if available
            if echo "$line" | grep -qP '[\x{1F600}-\x{1F64F}\x{1F300}-\x{1F5FF}\x{1F680}-\x{1F6FF}\x{1F1E0}-\x{1F1FF}\x{2700}-\x{27BF}\x{1F900}-\x{1F9FF}\x{1FA00}-\x{1FA6F}\x{2600}-\x{26FF}]' 2>/dev/null; then
                # Found emoji via PCRE Unicode ranges
                if [ "$found_in_file" -eq 0 ]; then
                    echo ""
                    log_error "Emojis detectados en: $file"
                    echo "======================================================================"
                    found_in_file=1
                    files_with_emojis=$((files_with_emojis + 1))
                fi

                total_emojis=$((total_emojis + 1))
                echo "  Línea $line_num: (emoji Unicode detectado)"
                local context="${line:0:60}"
                echo "    Contexto: $context..."
            fi
        fi
    done < "$file"

    return 0
}

# Main function
main() {
    local files_to_check=()

    # Parse arguments
    if [ $# -eq 0 ]; then
        echo "Uso: bash scripts/workflows/check_no_emojis.sh <archivos...>"
        echo "     bash scripts/workflows/check_no_emojis.sh --all"
        exit 1
    fi

    if [ "$1" = "--all" ]; then
        # Check all files in project
        log_info "Escaneando todo el proyecto..."

        while IFS= read -r file; do
            if should_check_file "$file"; then
                files_to_check+=("$file")
            fi
        done < <(find "$PROJECT_ROOT" -type f \
            -name "*.md" -o \
            -name "*.txt" -o \
            -name "*.py" -o \
            -name "*.js" -o \
            -name "*.ts" -o \
            -name "*.jsx" -o \
            -name "*.tsx" -o \
            -name "*.yaml" -o \
            -name "*.yml" -o \
            -name "*.json" -o \
            -name "*.sh" -o \
            -name "*.bash" \
            2>/dev/null | grep -vE "($EXCLUDE_DIRS)" || true)
    else
        # Check specific files
        for arg in "$@"; do
            if should_check_file "$arg"; then
                files_to_check+=("$arg")
            fi
        done
    fi

    if [ ${#files_to_check[@]} -eq 0 ]; then
        log_info "No hay archivos para verificar."
        exit 0
    fi

    # Check all files
    for file in "${files_to_check[@]}"; do
        check_file_for_emojis "$file"
        files_checked=$((files_checked + 1))
    done

    # Print results
    if [ "$total_emojis" -gt 0 ]; then
        echo ""
        echo "======================================================================"
        echo "TOTAL: $total_emojis emojis encontrados en $files_with_emojis archivos"
        echo "======================================================================"
        echo ""
        log_error "El proyecto NO permite emojis en documentación o código"
        echo ""
        echo "Alternativas recomendadas:"
        echo "  - En lugar de ✅ usar: [x] o 'Completado'"
        echo "  - En lugar de ❌ usar: [ ] o 'Pendiente'"
        echo "  - En lugar de 🚀 usar: simplemente omitir"
        echo "  - En lugar de ⚠️  usar: 'ADVERTENCIA:' o 'Nota:'"
        echo ""
        echo "Ver: docs/gobernanza/GUIA_ESTILO.md para más información"
        exit 1
    else
        log_success "No se encontraron emojis en $files_checked archivos verificados."
        exit 0
    fi
}

main "$@"
