#!/usr/bin/env bash
#
# check_no_emojis.sh - Valida que no haya emojis en scripts de producción
#
# Este script verifica que los archivos de código no contengan emojis
# ni caracteres Unicode decorativos en su output.
#
# Usage:
#   ./check_no_emojis.sh [files...]
#   git diff --name-only | xargs ./check_no_emojis.sh
#
# Exit codes:
#   0 - No se encontraron emojis
#   1 - Se encontraron emojis en scripts
#
# Relacionado:
#   docs/gobernanza/estandares_codigo.md - Regla Fundamental sobre Output Profesional
#

set -euo pipefail

# =============================================================================
# CONFIGURACION
# =============================================================================

# Directorios a excluir (permitimos emojis en docs)
readonly EXCLUDE_DIRS=(
    "docs/"
    "node_modules/"
    ".git/"
    ".venv/"
    "__pycache__/"
    "venv/"
    "env/"
)

# Archivos específicos a excluir
readonly EXCLUDE_FILES=(
    "README.md"
    "readme.md"
    "CHANGELOG.md"
    "changelog.md"
)

# Pattern de emojis y caracteres Unicode decorativos comunes
# Nota: Usamos grep con PCRE (-P) para Unicode
readonly EMOJI_PATTERN='[✅❌⚠️🚀📁💾🔍⏳✨🎉▶●→★♦■▸»╔═╗║╚╝┌─┐│└┘☑✓✔☒✗✘ℹ️💡📢🐛🔄⌛⏰⏱️🏁⏹️📄📂🗂️🌐📡👤👥📅🗓️⇒➜➔⚡⛔]'

# =============================================================================
# FUNCIONES
# =============================================================================

log_info() {
    echo "[INFO] $*"
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_success() {
    echo "[SUCCESS] $*"
}

should_exclude_file() {
    local file="$1"

    # Verificar si está en directorio excluido
    for exclude_dir in "${EXCLUDE_DIRS[@]}"; do
        if [[ "$file" == *"$exclude_dir"* ]]; then
            return 0  # true - excluir
        fi
    done

    # Verificar si es archivo específico excluido
    local basename
    basename=$(basename "$file")
    for exclude_file in "${EXCLUDE_FILES[@]}"; do
        if [[ "$basename" == "$exclude_file" ]]; then
            return 0  # true - excluir
        fi
    done

    return 1  # false - no excluir
}

check_file_for_emojis() {
    local file="$1"
    local found=0

    # Verificar que el archivo existe y es legible
    if [[ ! -f "$file" ]] || [[ ! -r "$file" ]]; then
        return 0
    fi

    # Verificar si debe excluirse
    if should_exclude_file "$file"; then
        return 0
    fi

    # Buscar emojis en el archivo
    # -P: Perl regex (para Unicode)
    # -n: Mostrar número de línea
    # -H: Mostrar nombre de archivo
    if grep -Pn "$EMOJI_PATTERN" "$file" > /dev/null 2>&1; then
        log_error "Emojis found in: $file"
        echo ""
        # Mostrar las líneas con emojis
        grep -Pn "$EMOJI_PATTERN" "$file" | while IFS=: read -r line_num line_content; do
            echo "  Line $line_num: $line_content"
        done
        echo ""
        found=1
    fi

    return $found
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    local files=("$@")
    local total_files=0
    local files_with_emojis=0
    local checked_files=0

    log_info "Starting emoji validation"
    echo ""

    # Si no se proporcionaron archivos, buscar todos los archivos de código
    if [[ ${#files[@]} -eq 0 ]]; then
        log_info "No files specified, checking all code files..."

        # Buscar archivos Python, Shell, PowerShell
        mapfile -t files < <(find . -type f \( \
            -name "*.py" -o \
            -name "*.sh" -o \
            -name "*.bash" -o \
            -name "*.ps1" -o \
            -name "*.psm1" \
        \) 2>/dev/null)

        total_files=${#files[@]}
        log_info "Found $total_files code files"
    else
        total_files=${#files[@]}
        log_info "Checking $total_files specified files"
    fi

    echo ""

    # Verificar cada archivo
    for file in "${files[@]}"; do
        if check_file_for_emojis "$file"; then
            continue  # No se encontraron emojis
        else
            ((files_with_emojis++))
        fi
        ((checked_files++))
    done

    # Resumen
    echo ""
    echo "------------------------------------------------------------"
    log_info "Validation Summary:"
    log_info "  Total files: $total_files"
    log_info "  Checked: $checked_files"
    log_info "  Files with emojis: $files_with_emojis"
    echo "------------------------------------------------------------"
    echo ""

    # Resultado final
    if [[ $files_with_emojis -gt 0 ]]; then
        log_error "Emoji validation FAILED"
        echo ""
        log_error "Found emojis in $files_with_emojis file(s)"
        log_error "Remove emojis from production scripts"
        log_error "See: docs/gobernanza/estandares_codigo.md"
        echo ""
        return 1
    fi

    log_success "Emoji validation PASSED"
    log_success "No emojis found in production scripts"
    echo ""
    return 0
}

# Ejecutar main con todos los argumentos
main "$@"
