#!/usr/bin/env bash
# scripts/check_ui_api_coherence.sh
# Detecta cambios en API sin tests UI correspondientes
# Exit: 0=coherente, 1=incoherente (warning)

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source utilities
source "$SCRIPT_DIR/utils/logging.sh"
source "$SCRIPT_DIR/utils/colors.sh"

# Configuration
BASE_BRANCH="${1:-main}"
OUTPUT_JSON="${2:-/tmp/ui_api_coherence.json}"

main() {
    log_info "Verificando coherencia UI/API..."

    local api_changes
    local ui_changes
    local incoherent=0

    # Detect API changes
    api_changes=$(git diff --name-only "$BASE_BRANCH"...HEAD | grep -E '^api/callcentersite/(views|serializers|urls)\.py$' || true)

    if [ -z "$api_changes" ]; then
        log_success "No hay cambios en API"
        write_report "coherent" "No API changes detected"
        exit 0
    fi

    log_warn "Cambios detectados en API:"
    echo "$api_changes" | while read -r file; do
        echo "  - $file"
    done

    # Check UI tests
    ui_test_changes=$(git diff --name-only "$BASE_BRANCH"...HEAD | grep -E '^ui/src/__tests__/.*\.(test|spec)\.(js|jsx|ts|tsx)$' || true)

    # Check UI services (API integration)
    ui_service_changes=$(git diff --name-only "$BASE_BRANCH"...HEAD | grep -E '^ui/src/services/.*\.(js|jsx|ts|tsx)$' || true)

    if [ -z "$ui_test_changes" ] && [ -z "$ui_service_changes" ]; then
        log_warn "ADVERTENCIA: Cambios en API sin tests o servicios UI"
        write_report "incoherent" "API changes without UI tests or services"
        incoherent=1
    else
        log_success "Coherencia verificada: tests/servicios UI encontrados"
        write_report "coherent" "UI tests or services updated alongside API"
    fi

    exit $incoherent
}

write_report() {
    local status="$1"
    local message="$2"

    cat > "$OUTPUT_JSON" <<EOF
{
  "check": "ui_api_coherence",
  "status": "$status",
  "message": "$message",
  "timestamp": "$(date -Iseconds)",
  "api_changes": $(git diff --name-only "$BASE_BRANCH"...HEAD | grep -E '^api/' | jq -R . | jq -s . || echo "[]"),
  "ui_changes": $(git diff --name-only "$BASE_BRANCH"...HEAD | grep -E '^ui/' | jq -R . | jq -s . || echo "[]")
}
EOF
}

main "$@"
