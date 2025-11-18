#!/usr/bin/env bash
# scripts/validate_devcontainer_env.sh
# Valida entorno DevContainer completo
# Exit: 0=valido, 1=invalido

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/utils/logging.sh"

OUTPUT_JSON="${1:-/tmp/devcontainer_validation.json}"

declare -a CHECKS_PASSED=()
declare -a CHECKS_FAILED=()

main() {
    log_info "Validando entorno DevContainer..."

    check_databases
    check_python_version
    check_node_version
    check_dependencies
    check_script_permissions

    # Generate report
    local total=$((${#CHECKS_PASSED[@]} + ${#CHECKS_FAILED[@]}))
    local passed=${#CHECKS_PASSED[@]}

    write_report

    if [ ${#CHECKS_FAILED[@]} -gt 0 ]; then
        log_error "Validacion fallida: $passed/$total checks pasaron"
        exit 1
    else
        log_success "Validacion completa: $passed/$total checks pasaron"
        exit 0
    fi
}

check_databases() {
    log_info "Verificando bases de datos..."

    # PostgreSQL
    if nc -z localhost 5432 2>/dev/null; then
        CHECKS_PASSED+=("postgresql:5432")
        log_success "  PostgreSQL (5432): OK"
    else
        CHECKS_FAILED+=("postgresql:5432")
        log_error "  PostgreSQL (5432): FAIL"
    fi

    # MariaDB
    if nc -z localhost 3306 2>/dev/null; then
        CHECKS_PASSED+=("mariadb:3306")
        log_success "  MariaDB (3306): OK"
    else
        CHECKS_FAILED+=("mariadb:3306")
        log_error "  MariaDB (3306): FAIL"
    fi
}

check_python_version() {
    log_info "Verificando Python..."

    if command -v python3 &>/dev/null; then
        local py_version=$(python3 --version | awk '{print $2}')
        if [[ "$py_version" =~ ^3\.12\. ]]; then
            CHECKS_PASSED+=("python:$py_version")
            log_success "  Python $py_version: OK"
        else
            CHECKS_FAILED+=("python:$py_version")
            log_warn "  Python $py_version: ADVERTENCIA (esperado 3.12.x)"
        fi
    else
        CHECKS_FAILED+=("python:missing")
        log_error "  Python: NO ENCONTRADO"
    fi
}

check_node_version() {
    log_info "Verificando Node.js..."

    if command -v node &>/dev/null; then
        local node_version=$(node --version | sed 's/v//')
        if [[ "$node_version" =~ ^18\. ]]; then
            CHECKS_PASSED+=("node:$node_version")
            log_success "  Node.js $node_version: OK"
        else
            CHECKS_FAILED+=("node:$node_version")
            log_warn "  Node.js $node_version: ADVERTENCIA (esperado 18.x)"
        fi
    else
        CHECKS_FAILED+=("node:missing")
        log_error "  Node.js: NO ENCONTRADO"
    fi
}

check_dependencies() {
    log_info "Verificando dependencias sistema..."

    local deps=("git" "jq" "yq" "nc")
    for dep in "${deps[@]}"; do
        if command -v "$dep" &>/dev/null; then
            CHECKS_PASSED+=("dep:$dep")
            log_success "  $dep: OK"
        else
            CHECKS_FAILED+=("dep:$dep")
            log_error "  $dep: NO ENCONTRADO"
        fi
    done
}

check_script_permissions() {
    log_info "Verificando permisos scripts..."

    local scripts=(
        "scripts/constitucion.sh"
        "scripts/ci-local.sh"
        "scripts/install_hooks.sh"
    )

    for script in "${scripts[@]}"; do
        local full_path="$PROJECT_ROOT/$script"
        if [ -f "$full_path" ]; then
            if [ -x "$full_path" ]; then
                CHECKS_PASSED+=("perm:$script")
                log_success "  $script: EJECUTABLE"
            else
                CHECKS_FAILED+=("perm:$script")
                log_error "  $script: NO EJECUTABLE"
            fi
        else
            CHECKS_FAILED+=("missing:$script")
            log_warn "  $script: NO EXISTE (pendiente instalacion)"
        fi
    done
}

write_report() {
    cat > "$OUTPUT_JSON" <<EOF
{
  "check": "devcontainer_environment",
  "timestamp": "$(date -Iseconds)",
  "summary": {
    "total": $((${#CHECKS_PASSED[@]} + ${#CHECKS_FAILED[@]})),
    "passed": ${#CHECKS_PASSED[@]},
    "failed": ${#CHECKS_FAILED[@]}
  },
  "checks_passed": $(printf '%s\n' "${CHECKS_PASSED[@]}" | jq -R . | jq -s . 2>/dev/null || echo "[]"),
  "checks_failed": $(printf '%s\n' "${CHECKS_FAILED[@]}" | jq -R . | jq -s . 2>/dev/null || echo "[]")
}
EOF
}

main "$@"
