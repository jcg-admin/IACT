#!/usr/bin/env bash
# scripts/validate_constitution_schema.sh
# Valida .constitucion.yaml contra schema
# Exit: 0=valido, 1=invalido

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/utils/logging.sh"

CONSTITUTION_FILE="${1:-$PROJECT_ROOT/.constitucion.yaml}"

declare -a ERRORS=()

main() {
    log_info "Validando schema .constitucion.yaml..."

    if [ ! -f "$CONSTITUTION_FILE" ]; then
        log_error "Archivo no encontrado: $CONSTITUTION_FILE"
        exit 1
    fi

    validate_yaml_syntax
    validate_required_fields
    validate_principles
    validate_rules
    validate_references

    if [ ${#ERRORS[@]} -gt 0 ]; then
        log_error "Validacion fallida con ${#ERRORS[@]} errores:"
        for error in "${ERRORS[@]}"; do
            echo "  - $error"
        done
        exit 1
    else
        log_success "Schema valido"
        exit 0
    fi
}

validate_yaml_syntax() {
    if ! yq eval '.' "$CONSTITUTION_FILE" &>/dev/null; then
        ERRORS+=("Sintaxis YAML invalida")
    fi
}

validate_required_fields() {
    local version=$(yq eval '.version' "$CONSTITUTION_FILE")
    if [ "$version" = "null" ]; then
        ERRORS+=("Campo 'version' faltante")
    fi

    local principles=$(yq eval '.principles' "$CONSTITUTION_FILE")
    if [ "$principles" = "null" ]; then
        ERRORS+=("Campo 'principles' faltante")
    fi

    local rules=$(yq eval '.rules' "$CONSTITUTION_FILE")
    if [ "$rules" = "null" ]; then
        ERRORS+=("Campo 'rules' faltante")
    fi
}

validate_principles() {
    local count=$(yq eval '.principles | length' "$CONSTITUTION_FILE")

    for ((i=0; i<count; i++)); do
        local id=$(yq eval ".principles[$i].id" "$CONSTITUTION_FILE")
        local name=$(yq eval ".principles[$i].name" "$CONSTITUTION_FILE")

        if [ "$id" = "null" ]; then
            ERRORS+=("Principle $i: campo 'id' faltante")
        fi

        if [ "$name" = "null" ]; then
            ERRORS+=("Principle $i ($id): campo 'name' faltante")
        fi
    done
}

validate_rules() {
    local count=$(yq eval '.rules | length' "$CONSTITUTION_FILE")

    for ((i=0; i<count; i++)); do
        local id=$(yq eval ".rules[$i].id" "$CONSTITUTION_FILE")
        local severity=$(yq eval ".rules[$i].severity" "$CONSTITUTION_FILE")

        if [ "$id" = "null" ]; then
            ERRORS+=("Rule $i: campo 'id' faltante")
        fi

        if [ "$severity" != "error" ] && [ "$severity" != "warning" ]; then
            ERRORS+=("Rule $i ($id): severity debe ser 'error' o 'warning', encontrado: '$severity'")
        fi
    done
}

validate_references() {
    # Extract all principle IDs
    local principle_ids=$(yq eval '.principles[].id' "$CONSTITUTION_FILE")

    # Check each rule references valid principle
    local rule_count=$(yq eval '.rules | length' "$CONSTITUTION_FILE")

    for ((i=0; i<rule_count; i++)); do
        local rule_id=$(yq eval ".rules[$i].id" "$CONSTITUTION_FILE")
        local principle_id=$(yq eval ".rules[$i].principle_id" "$CONSTITUTION_FILE")

        if [ "$principle_id" != "null" ]; then
            if ! echo "$principle_ids" | grep -qx "$principle_id"; then
                ERRORS+=("Rule $rule_id: referencia a principle_id '$principle_id' no existe")
            fi
        fi
    done
}

main "$@"
