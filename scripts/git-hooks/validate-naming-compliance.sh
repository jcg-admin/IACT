#!/bin/bash
# VALIDATE NAMING COMPLIANCE: Pre-commit Hook for Script Naming Standards

set -uo pipefail

# Dynamic paths setup (rutas dinámicas consistentes)
source "$(dirname "${BASH_SOURCE[0]}")/../utils/dynamic-paths-functions.sh" && setup_script_dynamic_paths


# Strategy registry
declare -A STRATEGIES
declare -A STRATEGY_CONFIG

# Register strategy
register_strategy() {
    local strategy_name="$1"
    local strategy_function="$2"
    local severity_level="$3"
    local enabled="${4:-true}"

    STRATEGIES["$strategy_name"]="$strategy_function|$severity_level"
    STRATEGY_CONFIG["$strategy_name"]="$enabled"
    log_debug "Strategy registered: $strategy_name [$severity_level]"
}

# Configure strategy
configure_strategy() {
    local strategy_name="$1"
    local enabled="$2"

    if [ -n "${STRATEGIES[$strategy_name]:-}" ]; then
        STRATEGY_CONFIG["$strategy_name"]="$enabled"
    fi
}

# Get enabled strategies by level
get_strategies_by_level() {
    local target_level="$1"
    local strategies=()

    for strategy_name in "${!STRATEGIES[@]}"; do
        local strategy_data="${STRATEGIES[$strategy_name]}"
        local enabled="${STRATEGY_CONFIG[$strategy_name]}"

        IFS='|' read -r strategy_function severity_level <<< "$strategy_data"

        if [ "$severity_level" = "$target_level" ] && [ "$enabled" = "true" ]; then
            strategies+=("$strategy_name:$strategy_function")
        fi
    done

    printf '%s\n' "${strategies[@]}"
}

# Execute strategy
execute_strategy() {
    local strategy_data="$1"
    local filename="$2"
    local context="$3"
    local filepath="${4:-$filename}"

    IFS=':' read -r strategy_name strategy_function <<< "$strategy_data"

    if [ "$(type -t "$strategy_function" 2>/dev/null)" = "function" ]; then
        $strategy_function "$filename" "$context" "$filepath"
    fi
}

# Initialize strategies
initialize_strategies() {
    log_info "Initializing validation strategies..."

    # IMMEDIATE level
    register_strategy "task_naming_check" "detect_task_naming_violations" "IMMEDIATE"
    register_strategy "framework_coupling_check" "detect_framework_coupling_violations" "IMMEDIATE"
    register_strategy "notation_coupling_check" "detect_hungarian_notation_violations" "IMMEDIATE"

    # CORRECTIVE level
    register_strategy "technology_coupling_check" "detect_technology_coupling_violations" "CORRECTIVE"
    register_strategy "naming_clarity_check" "detect_ambiguous_naming_violations" "CORRECTIVE"
    register_strategy "character_format_check" "detect_character_violations" "CORRECTIVE"
    register_strategy "component_structure_check" "detect_component_pattern_violations" "CORRECTIVE"
    register_strategy "location_check" "detect_location_violations" "CORRECTIVE"
    register_strategy "stability_check" "validate_stability" "CORRECTIVE"
    register_strategy "clean_code_check" "detect_clean_code_violations" "CORRECTIVE"

    # ADVISORY level
    register_strategy "length_check" "detect_length_violations" "ADVISORY"
    register_strategy "case_check" "detect_case_violations" "ADVISORY"

    log_info "Loaded ${#STRATEGIES[@]} validation strategies successfully"
}

# Load configuration
load_configuration() {
    log_info "Loading configuration from git config..."

    local immediate_config
    immediate_config=$(git config compliance.enforceImmediate 2>/dev/null)
    local immediate_enabled="${immediate_config:-true}"

    local corrective_config
    corrective_config=$(git config compliance.trackCorrective 2>/dev/null)
    local corrective_enabled="${corrective_config:-true}"

    local advisory_config
    advisory_config=$(git config compliance.showAdvisory 2>/dev/null)
    local advisory_enabled="${advisory_config:-true}"

    for strategy_name in "${!STRATEGIES[@]}"; do
        local strategy_config
        strategy_config=$(git config "compliance.strategy.${strategy_name}.enabled" 2>/dev/null)
        local strategy_enabled="${strategy_config:-true}"
        configure_strategy "$strategy_name" "$strategy_enabled"
    done

    log_info "Configuration loaded: immediate=$immediate_enabled, corrective=$corrective_enabled, advisory=$advisory_enabled"

    echo "$immediate_enabled:$corrective_enabled:$advisory_enabled"
}

# Apply enforcement
apply_enforcement() {
    local threat_level="$1"
    local enforcement_config="$2"

    IFS=':' read -r immediate_enabled corrective_enabled advisory_enabled <<< "$enforcement_config"

    case "$threat_level" in
        "IMMEDIATE")
            if [ "$immediate_enabled" = "true" ]; then
                log_error "ENFORCEMENT: Commit blocked due to IMMEDIATE violations"
                return 2
            else
                log_warning "ENFORCEMENT: IMMEDIATE disabled, degrading to CORRECTIVE"
                return 1
            fi
            ;;
        "CORRECTIVE")
            if [ "$corrective_enabled" = "true" ]; then
                log_warning "ENFORCEMENT: Commit allowed with CORRECTIVE tracking"
                return 1
            else
                log_info "ENFORCEMENT: CORRECTIVE disabled, proceeding as ADVISORY"
                return 0
            fi
            ;;
        "ADVISORY")
            log_success "ENFORCEMENT: Commit approved with optional suggestions"
            return 0
            ;;
        *)
            log_success "ENFORCEMENT: No violations detected, commit approved"
            return 0
            ;;
    esac
}

# Create result
create_result() {
    local level="$1"
    local violation_type="$2"
    local message="$3"
    local action="$4"

    echo "${level}|${violation_type}|${message}|${action}"
}

# Task-based naming violations
detect_task_naming_violations() {
    local filename="$1"
    local context="$2"

    case "$filename" in
        t[0-9]*|epic-[0-9]*|story-[0-9]*|sprint-[0-9]*)
            case "$context" in
                "ARCHIVES"|"EXAMPLE"|"TEMPLATE")
                    create_result "ADVISORY" "TASK_BASED_CONTEXT" \
                        "Task-based naming in $context context" \
                        "Consider component-based naming for consistency"
                    ;;
                *)
                    create_result "IMMEDIATE" "TASK_BASED_FORBIDDEN" \
                        "Task-based naming forbidden in production context" \
                        "Change to component-based naming immediately"
                    ;;
            esac
            ;;
    esac
}

# Framework coupling violations
detect_framework_coupling_violations() {
    local filename="$1"
    local context="$2"

    case "$filename" in
        *rails*|*django*|*spring*|*angular*|*react*|*vue*|*laravel*|*express*|*flask*|*fastapi*)
            create_result "IMMEDIATE" "FRAMEWORK_COUPLING" \
                "Framework coupling forbidden" \
                "Remove framework reference from component name"
            ;;
    esac
}

# Hungarian notation violations
detect_hungarian_notation_violations() {
    local filename="$1"
    local context="$2"

    case "$filename" in
        tst_*|val_*|str_*|int_*|chk_*|obj_*|arr_*|fn_*|bool_*|num_*)
            create_result "IMMEDIATE" "HUNGARIAN_NOTATION" \
                "Hungarian notation forbidden" \
                "Use intention-revealing names without type encoding"
            ;;
    esac
}

# Technology coupling violations
detect_technology_coupling_violations() {
    local filename="$1"
    local context="$2"

    case "$filename" in
        *mysql*|*postgresql*|*apache*|*nginx*|*redis*|*mongodb*|*elasticsearch*|*kafka*|*rabbitmq*)
            create_result "CORRECTIVE" "TECHNOLOGY_COUPLING" \
                "Technology coupling detected" \
                "Use abstract component names instead of technology names"
            ;;
    esac
}

# Ambiguous naming violations
detect_ambiguous_naming_violations() {
    local filename="$1"
    local context="$2"
    local filepath="${3:-$filename}"

    # Skip validation in certain contexts
    case "$context" in
        "ARCHIVES"|"EXAMPLE"|"TEMPLATE"|"TEST_DATA"|"TEMPORARY")
            return 1
            ;;
    esac

    # Skip validation in certain locations
    case "$filepath" in
        examples/*|templates/*|docs/examples/*|prototype/*|skeleton/*|tutorial/*)
            return 1
            ;;
        script/setup|script/bootstrap|script/test|script/console|script/update|script/cibuild)
            return 1
            ;;
    esac

    # Skip valid generic patterns in specific contexts
    case "$filename" in
        "setup.sh"|"bootstrap.sh"|"test.sh"|"console.sh"|"update.sh"|"cibuild.sh")
            if echo "$filepath" | grep '^script/' >/dev/null 2>&1; then
                return 1
            fi
            ;;
    esac

    # Check for ambiguity in production contexts
    case "$filename" in
        "test-files.sh")
            create_result "CORRECTIVE" "AMBIGUOUS_NAMING" \
                "Ambiguous: which files? what type of test?" \
                "Be specific: test-git-ignore-files.sh, test-project-essential-files.sh"
            ;;
        "validate-config.sh")
            create_result "CORRECTIVE" "AMBIGUOUS_NAMING" \
                "Ambiguous: which config? what component?" \
                "Be specific: validate-database-config.sh, validate-nginx-config.sh"
            ;;
        "setup-environment.sh")
            create_result "CORRECTIVE" "AMBIGUOUS_NAMING" \
                "Ambiguous: which environment? what aspect?" \
                "Be specific: setup-vagrant-environment.sh, setup-docker-environment.sh"
            ;;
        "process-data.sh")
            create_result "CORRECTIVE" "AMBIGUOUS_NAMING" \
                "Ambiguous: what data? what processing?" \
                "Be specific: process-log-data.sh, process-user-data.sh"
            ;;
        "handle-request.sh")
            create_result "CORRECTIVE" "AMBIGUOUS_NAMING" \
                "Ambiguous: what type of request? what handling?" \
                "Be specific: handle-api-request.sh, handle-webhook-request.sh"
            ;;
    esac
}

# Character violations
detect_character_violations() {
    local filename="$1"
    local context="$2"

    if echo "$filename" | grep -v '^[a-z0-9.-]*$' >/dev/null 2>&1; then
        create_result "CORRECTIVE" "INVALID_CHARACTERS" \
            "Contains non-standard characters" \
            "Use only lowercase letters, hyphens, and dots"
    fi
}

# Component pattern violations
detect_component_pattern_violations() {
    local filename="$1"
    local context="$2"

    case "$filename" in
        test-*-*.sh|validate-*-*.sh|setup-*-*.sh|bootstrap-*-*.sh|maintenance-*-*.sh|load-*-*.sh|console-*-*.sh)
            return 1
            ;;
        bootstrap.sh|setup.sh|test.sh|console.sh|update.sh|cibuild.sh)
            return 1
            ;;
        *)
            create_result "CORRECTIVE" "COMPONENT_PATTERN" \
                "Does not follow component-based pattern" \
                "Expected [action]-[component]-[aspect].sh format"
            ;;
    esac
}

# Location violations
detect_location_violations() {
    local filename="$1"
    local context="$2"
    local filepath="$3"

    if [ "$context" = "TEST_DATA" ] || [ "$context" = "TEMPORARY" ] || [ "$context" = "TEMPLATE" ]; then
        return 1
    fi

    case "$filename" in
        test-*)
            case "$filepath" in
                test/unit/*|test/integration/*|test/system/*)
                    return 1
                    ;;
                *)
                    create_result "CORRECTIVE" "WRONG_LOCATION_TEST" \
                        "Test script in wrong location" \
                        "Move to test/unit/, test/integration/, or test/system/"
                    ;;
            esac
            ;;
        validate-*)
            case "$filepath" in
                infraestructura/hooks/*)
                    return 1
                    ;;
                *)
                    create_result "CORRECTIVE" "WRONG_LOCATION_VALIDATE" \
                        "Validation script in wrong location" \
                        "Move to infrastructure/hooks/"
                    ;;
            esac
            ;;
        setup-*|bootstrap-*)
            case "$filepath" in
                bin/setup/*)
                    return 1
                    ;;
                *)
                    create_result "CORRECTIVE" "WRONG_LOCATION_SETUP" \
                        "Setup script in wrong location" \
                        "Move to bin/setup/"
                    ;;
            esac
            ;;
        maintenance-*)
            case "$filepath" in
                bin/maintenance/*)
                    return 1
                    ;;
                *)
                    create_result "CORRECTIVE" "WRONG_LOCATION_MAINTENANCE" \
                        "Maintenance script in wrong location" \
                        "Move to bin/maintenance/"
                    ;;
            esac
            ;;
        load-*-env.sh)
            case "$filepath" in
                infraestructura/configs/*)
                    return 1
                    ;;
                *)
                    create_result "CORRECTIVE" "WRONG_LOCATION_CONFIG" \
                        "Configuration loader in wrong location" \
                        "Move to infrastructure/configs/"
                    ;;
            esac
            ;;
        bootstrap|setup|test|console|update|cibuild)
            case "$filepath" in
                script/*)
                    return 1
                    ;;
                *)
                    create_result "CORRECTIVE" "WRONG_LOCATION_STANDARD" \
                        "GitHub standard script in wrong location" \
                        "Move to script/ directory"
                    ;;
            esac
            ;;
        *)
            case "$filepath" in
                infraestructura/utils/*)
                    validate_utils_criteria "$filename"
                    ;;
            esac
            ;;
    esac
}

# Validate utils criteria
validate_utils_criteria() {
    local filename="$1"

    local violations=()

    if echo "$filename" | grep -E '^(t[0-9]+|epic-|story-|sprint-|project-specific)' >/dev/null 2>&1; then
        violations+=("NOT_REUSABLE: Task-specific or project-specific, should be in bin/")
    fi

    if echo "$filename" | grep -E '^(setup-|bootstrap-|install-)' >/dev/null 2>&1; then
        violations+=("ONE_TIME_SETUP: Should be in bin/setup/, not utils/")
    fi

    if echo "$filename" | grep -E '^(maintenance-|cleanup-|backup-|repair-)' >/dev/null 2>&1; then
        violations+=("MAINTENANCE_SCRIPT: Should be in bin/maintenance/, not utils/")
    fi

    if echo "$filename" | grep -E '^(load-.*-env\.sh|config-loader)' >/dev/null 2>&1; then
        violations+=("CONFIG_LOADER: Should be in infrastructure/configs/, not utils/")
    fi

    case "$filename" in
        *-functions.sh|*-helpers.sh|*-utilities.sh|*-common.sh|*-shared.sh)
            ;;
        *)
            violations+=("NOT_LIBRARY_LIKE: Should be library-like functions, consider bin/ instead")
            ;;
    esac

    if [ ${#violations[@]} -gt 0 ]; then
        for violation in "${violations[@]}"; do
            IFS=':' read -r violation_type violation_message <<< "$violation"
            create_result "CORRECTIVE" "$violation_type" \
                "infrastructure/utils/ violation: $violation_message" \
                "Move to appropriate directory"
        done
    fi
}

# Validate stability
validate_stability() {
    local filename="$1"
    local context="$2"
    local filepath="${3:-$filename}"

    case "$context" in
        "ARCHIVES"|"EXAMPLE"|"TEMPLATE"|"TEST_DATA"|"TEMPORARY")
            return 1
            ;;
    esac

    local predicted_ca=0
    local predicted_ce=0

    if echo "$filename" | grep -E '^(test|validate|setup|bootstrap|maintenance|load|console)-[a-z]+-[a-z-]+\.sh$' >/dev/null 2>&1; then
        predicted_ca=5
        predicted_ce=2
    fi

    if echo "$filename" | grep -E '^(t[0-9]+|epic-|story-|sprint-)' >/dev/null 2>&1; then
        predicted_ca=1
        predicted_ce=7
    fi

    case "$filename" in
        bootstrap|setup|test|console|update|cibuild)
            predicted_ca=8
            predicted_ce=3
            ;;
    esac

    case "$filepath" in
        infraestructura/utils/*)
            predicted_ca=10
            predicted_ce=1
            ;;
    esac

    if [ $((predicted_ca + predicted_ce)) -gt 0 ]; then
        local instability=$((predicted_ce * 100 / (predicted_ca + predicted_ce)))

        if [ $instability -gt 70 ]; then
            create_result "CORRECTIVE" "HIGH_INSTABILITY" \
                "Predicted instability: ${instability}%" \
                "Refactor to component-based naming for better stability"
        fi

        case "$filepath" in
            infraestructura/utils/*)
                if [ $instability -gt 20 ]; then
                    create_result "CORRECTIVE" "UTILS_INSTABILITY" \
                        "Utils instability: ${instability}%" \
                        "Utils must be highly stable - reconsider if this belongs in utils/"
                fi
                ;;
        esac
    fi
}

# Clean code violations
detect_clean_code_violations() {
    local filename="$1"
    local context="$2"

    case "$context" in
        "ARCHIVES"|"EXAMPLE"|"TEMPLATE"|"TEST_DATA"|"TEMPORARY")
            return 1
            ;;
    esac

    if echo "$filename" | grep -E '[bcdfghjklmnpqrstvwxyz]{4,}' >/dev/null 2>&1; then
        create_result "CORRECTIVE" "UNPRONOUNCEABLE" \
            "Contains unpronounceable consonant clusters" \
            "Use vowels to make names pronounceable"
    fi

    if [ ${#filename} -lt 10 ] && [ "$context" = "PRODUCTION" ]; then
        create_result "ADVISORY" "NOT_SEARCHABLE" \
            "Name too short to be easily searchable in large projects" \
            "Add descriptive elements for better searchability"
    fi

    case "$filename" in
        *list*.sh)
            if ! echo "$filename" | grep -E '(test-.*-list|validate-.*-list)' >/dev/null 2>&1; then
                create_result "CORRECTIVE" "MISLEADING_NAME" \
                    "Contains 'list' but may not actually list items" \
                    "Use 'list' only when script actually lists/enumerates items"
            fi
            ;;
        *data*.sh)
            create_result "ADVISORY" "GENERIC_WORD" \
                "Contains generic word 'data' - be more specific" \
                "Replace 'data' with specific data type: logs, users, configs, etc."
            ;;
        *info*.sh)
            create_result "ADVISORY" "GENERIC_WORD" \
                "Contains generic word 'info' - be more specific" \
                "Replace 'info' with specific information type"
            ;;
    esac
}

# Length violations
detect_length_violations() {
    local filename="$1"
    local context="$2"

    local filename_length=${#filename}

    if [ "$filename_length" -gt 50 ]; then
        create_result "ADVISORY" "NAME_TOO_LONG" \
            "Very long name may impact usability" \
            "Consider shortening while maintaining clarity"
    fi

    if [ "$filename_length" -lt 15 ] && [ "$context" = "PRODUCTION" ]; then
        create_result "ADVISORY" "NAME_TOO_SHORT" \
            "Name length less than 15 chars may impact searchability" \
            "Consider more descriptive naming"
    fi
}

# Case violations
detect_case_violations() {
    local filename="$1"
    local context="$2"

    if echo "$filename" | grep '^[A-Z]' >/dev/null 2>&1; then
        create_result "ADVISORY" "CAPITAL_LETTERS" \
            "Capital letters not following naming conventions" \
            "Use lowercase naming convention"
    fi
}

# Detect context
detect_context() {
    local filepath="$1"

    if echo "$filepath" | grep '^archives/' >/dev/null 2>&1; then
        echo "ARCHIVES"
    elif echo "$filepath" | grep -E '(template|example|prototype|skeleton|tutorial)' >/dev/null 2>&1; then
        echo "TEMPLATE"
    elif echo "$filepath" | grep -E '(^test-data/|/test-data/)' >/dev/null 2>&1; then
        echo "TEST_DATA"
    elif echo "$filepath" | grep '/tmp/' >/dev/null 2>&1 || echo "$PWD" | grep '/tmp/' >/dev/null 2>&1; then
        echo "TEMPORARY"
    elif echo "$filepath" | grep -i -E '(example|placeholder|demo)' >/dev/null 2>&1; then
        echo "EXAMPLE"
    else
        echo "PRODUCTION"
    fi
}

# Execute strategies by level
execute_strategies_by_level() {
    local level="$1"
    local filename="$2"
    local filepath="$3"
    local context="$4"
    local findings_array_name="$5"

    local strategies
    strategies=$(get_strategies_by_level "$level")
    local violations_found=false

    local active_count=0
    while IFS= read -r strategy_data; do
        if [ -n "$strategy_data" ]; then
            active_count=$((active_count + 1))
        fi
    done <<< "$strategies"

    log_info "Executing $active_count $level level strategies..."

    while IFS= read -r strategy_data; do
        if [ -n "$strategy_data" ]; then
            local result
            result=$(execute_strategy "$strategy_data" "$filename" "$context" "$filepath")

            if [ -n "$result" ]; then
                eval "${findings_array_name}+=(\"\$result\")"
                violations_found=true
            fi
        fi
    done <<< "$strategies"

    if [ "$violations_found" = true ]; then
        log_info "$level analysis completed - violations found"
        return 0
    else
        log_info "$level analysis completed - no violations"
        return 1
    fi
}

# Display findings
display_findings() {
    local findings_array_name="$1"
    local findings_ref="${findings_array_name}[@]"
    local findings=("${!findings_ref}")

    local has_immediate=false
    local has_corrective=false
    local has_advisory=false

    for finding in "${findings[@]}"; do
        if [ -n "$finding" ]; then
            IFS='|' read -r level violation_type message action <<< "$finding"

            case "$level" in
                "IMMEDIATE")
                    has_immediate=true
                    log_error "IMMEDIATE [$violation_type]: $message"
                    log_error "ACTION REQUIRED: $action"
                    ;;
                "CORRECTIVE")
                    has_corrective=true
                    log_warning "CORRECTIVE [$violation_type]: $message"
                    log_warning "ACTION REQUIRED: $action"
                    ;;
                "ADVISORY")
                    has_advisory=true
                    log_info "ADVISORY [$violation_type]: $message"
                    log_info "ACTION REQUIRED: $action"
                    ;;
            esac
        fi
    done

    if [ "$has_immediate" = true ]; then
        return 2
    elif [ "$has_corrective" = true ]; then
        return 1
    else
        return 0
    fi
}

# Validación del entorno de ejecución
validate_execution_environment() {
    local script_file="$1"

    if [[ ! -f "$script_file" ]]; then
        log_error "Script file not found: $script_file"
        log_info "Usage: $0 <script-file-path>"
        return 1
    fi

    log_debug "Execution environment validated for: $script_file"
    return 0
}

# Sistema de logging especializado
setup_naming_compliance_logging() {
    local validation_type="${1:-validation}"

    setup_infrastructure_logging "$validation_type"
    export ENABLE_PERFORMANCE_TRACKING=true
    log_info "Naming compliance validation started"
}

teardown_naming_compliance_logging() {
    log_info "Naming compliance validation completed"

    # Clean up temporary environment variables
    unset ENABLE_PERFORMANCE_TRACKING

    # Reset any global counters to prevent interference with other scripts
    # (Add other cleanup as needed based on your infraestructura)
}

get_naming_compliance_errors() {
    get_validation_errors
}

get_naming_compliance_warnings() {
    get_validation_warnings
}

# Función de análisis específica
analyze_script_for_naming_violations() {
    local script_file="$1"

    log_section "NAMING VIOLATIONS ANALYSIS"
    log_info "Analyzing: $script_file"
    log_debug "Starting analysis of $script_file for naming violations"

    execute_validation "$script_file"
    local validation_result=$?

    log_debug "Analysis completed with result: $validation_result"

    # Conversión limpia de exit codes a threat levels
    case $validation_result in
        2) echo "IMMEDIATE" ;;
        1) echo "CORRECTIVE" ;;
        0) echo "ADVISORY" ;;
        *) echo "CLEAN" ;;
    esac
}

# CLI functions
display_help() {
    log_section "NAMING COMPLIANCE VALIDATION SYSTEM"
    log_info ""
    log_info "Usage: $0 <script-file-path>"
    log_info "       $0 --config      # Show configuration"
    log_info "       $0 --status      # Show status"
    log_info "       $0 --strategies  # List strategies"
    log_info "       $0 --version     # Show version"
    log_info "       $0 --help        # Show help"
    log_info ""
    log_info "VALIDATION LEVELS:"
    log_info "  IMMEDIATE: Blocks commits"
    log_info "  CORRECTIVE: Warns and tracks"
    log_info "  ADVISORY: Suggests improvements"
    log_info ""
    log_info "Example: $0 my-script.sh"
    log_info "         $0 --config"
    log_info ""
    log_info "CONFIGURATION:"
    log_info "  git config compliance.enforceImmediate true|false"
    log_info "  git config compliance.trackCorrective true|false"
    log_info "  git config compliance.showAdvisory true|false"
    log_info "  git config compliance.strategy.<strategy_name>.enabled true|false"
}

display_config() {
    log_section "CONFIGURATION"
    local enforcement_config=$(load_configuration)
    IFS=':' read -r immediate corrective advisory <<< "$enforcement_config"

    log_info "Enforcement Levels:"
    log_info "  IMMEDIATE: $immediate"
    log_info "  CORRECTIVE: $corrective"
    log_info "  ADVISORY: $advisory"
    log_info ""
    log_info "Strategies:"
    for strategy_name in "${!STRATEGIES[@]}"; do
        local strategy_data="${STRATEGIES[$strategy_name]}"
        local enabled="${STRATEGY_CONFIG[$strategy_name]}"
        IFS='|' read -r strategy_function severity_level <<< "$strategy_data"
        log_info "  $strategy_name [$severity_level]: $enabled"
    done
    log_info ""
    log_info "Configuration commands:"
    log_info "  git config compliance.enforceImmediate true|false"
    log_info "  git config compliance.trackCorrective true|false"
    log_info "  git config compliance.showAdvisory true|false"
    log_info "  git config compliance.strategy.<strategy_name>.enabled true|false"
}

display_status() {
    log_section "SYSTEM STATUS"
    log_info "Validation Errors: $(get_naming_compliance_errors)"
    log_info "Validation Warnings: $(get_naming_compliance_warnings)"
    log_info "Strategy Registry: ${#STRATEGIES[@]} strategies"
    log_info "Configuration Entries: ${#STRATEGY_CONFIG[@]} settings"
    log_info "Performance Tracking: ${ENABLE_PERFORMANCE_TRACKING:-false}"
}

display_version() {
    log_info "validate-naming-compliance.sh v3.3"
    log_info "Strategy-based validation with context-aware rules"
    log_info "Enhanced with specialized logging and environment validation"
}

execute_validation() {
    local file="$1"

    local filename=$(basename "$file")
    local filepath="$file"
    local context=$(detect_context "$filepath")

    log_section "NAMING COMPLIANCE VALIDATION"
    log_info "File: $file"
    log_info "Context: $context"
    log_info "Starting validation process..."

    local enforcement_config=$(load_configuration)

    local findings=()

    log_info "Immediate Threat Detection:"
    execute_strategies_by_level "IMMEDIATE" "$filename" "$filepath" "$context" "findings"

    log_info "Corrective Analysis:"
    execute_strategies_by_level "CORRECTIVE" "$filename" "$filepath" "$context" "findings"

    log_info "Advisory Suggestions:"
    execute_strategies_by_level "ADVISORY" "$filename" "$filepath" "$context" "findings"

    log_section "VALIDATION RESULTS"
    log_info "Analysis completed - found ${#findings[@]} total findings"

    if [ ${#findings[@]} -eq 0 ]; then
        log_success "SUCCESS: $filename passes all naming compliance checks"
        return 0
    fi

    display_findings "findings"
    local severity_level=$?

    log_section "ENFORCEMENT DECISION"

    case $severity_level in
        2) echo "IMMEDIATE" ;;
        1) echo "CORRECTIVE" ;;
        *) echo "ADVISORY" ;;
    esac
}

# Main function
main() {
    setup_naming_compliance_logging "naming-validation"

    log_info "Starting naming compliance validation system..."
    initialize_strategies

    case "${1:-}" in
        "--help"|"-h"|"")
            display_help
            teardown_naming_compliance_logging
            return 0
            ;;
        "--config")
            display_config
            teardown_naming_compliance_logging
            return 0
            ;;
        "--strategies")
            display_strategies
            teardown_naming_compliance_logging
            return 0
            ;;
        "--version"|"-v")
            display_version
            teardown_naming_compliance_logging
            return 0
            ;;
        "--status")
            display_status
            teardown_naming_compliance_logging
            return 0
            ;;
    esac

    local script_file="$1"

    # Validación del entorno
    if ! validate_execution_environment "$script_file"; then
        teardown_naming_compliance_logging
        return 1
    fi

    log_info "Validating script: $script_file"

    local enforcement_config=$(load_configuration)

    # Análisis específico
    local threat_level
    threat_level=$(analyze_script_for_naming_violations "$script_file")

    log_info "Validation process completed"

    # Mostrar resumen con métricas reales
    show_validation_summary

    apply_enforcement "$threat_level" "$enforcement_config"
    local exit_code=$?

    log_info "Enforcement decision applied with exit code: $exit_code"

    # Teardown con logging especializado
    teardown_naming_compliance_logging
    return $exit_code
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi