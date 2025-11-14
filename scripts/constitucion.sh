#!/usr/bin/env bash
# ===================================================================
# scripts/constitucion.sh
# Validador del Sistema de Constitucion IACT
# ===================================================================
# Uso:
#   ./constitucion.sh --mode=pre-commit
#   ./constitucion.sh --mode=pre-push
#   ./constitucion.sh --mode=devcontainer-init
#   ./constitucion.sh --mode=ci-local
#   ./constitucion.sh --mode=manual
#   ./constitucion.sh --validate-all
#   ./constitucion.sh --report
# ===================================================================

set -euo pipefail

# ===================================================================
# CONSTANTS
# ===================================================================
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly CONFIG_FILE="$PROJECT_ROOT/.constitucion.yaml"
readonly LOG_DIR="$PROJECT_ROOT/.automation-logs/constitucion"
readonly TIMESTAMP=$(date +%Y-%m-%d-%H-%M-%S)

# Source utilities (this also defines color variables)
if [ -f "$SCRIPT_DIR/utils/logging.sh" ]; then
    source "$SCRIPT_DIR/utils/logging.sh"
else
    # Fallback logging functions and colors if logging.sh not available
    log_info() { echo "[INFO] $*"; }
    log_success() { echo "[OK] $*"; }
    log_warn() { echo "[WARN] $*" >&2; }
    log_error() { echo "[ERROR] $*" >&2; }

    # Define colors only if not already defined
    if [ -z "${RED:-}" ]; then
        if [ -t 1 ]; then
            readonly RED='\033[0;31m'
            readonly YELLOW='\033[1;33m'
            readonly GREEN='\033[0;32m'
            readonly BLUE='\033[0;34m'
            readonly NC='\033[0m'  # No Color
        else
            readonly RED=''
            readonly YELLOW=''
            readonly GREEN=''
            readonly BLUE=''
            readonly NC=''
        fi
    fi
fi

# ===================================================================
# GLOBAL VARIABLES
# ===================================================================
MODE=""
VERBOSE=0
QUIET=0
VIOLATIONS_ERROR=()
VIOLATIONS_WARNING=()
EXIT_CODE=0
LOG_FILE=""

# ===================================================================
# FUNCTIONS
# ===================================================================

#####################################################################
# Print usage information
#####################################################################
usage() {
    cat <<EOF
CONSTITUCION VALIDATOR - IACT Project

Validar conformidad con principios y reglas codificadas en .constitucion.yaml

USAGE:
    $0 --mode=MODE [OPTIONS]

MODES:
    pre-commit          Valida reglas scope=pre-commit (R2: emojis)
    pre-push            Valida reglas scope=pre-push (R1, R3, R4, R5)
    devcontainer-init   Valida reglas scope=devcontainer-init (R6)
    ci-local            Valida reglas para CI local
    manual              Modo manual para testing
    validate-all        Valida TODAS las reglas (CI completo)
    report              Genera reporte conformidad (metricas)

OPTIONS:
    --verbose           Output detallado
    --quiet             Solo errores criticos
    --help              Muestra esta ayuda

EXAMPLES:
    $0 --mode=pre-commit
    $0 --mode=pre-push --verbose
    $0 --mode=validate-all
    $0 --mode=report

EXIT CODES:
    0   Todas las reglas pasaron (o solo warnings)
    1   Al menos una regla ERROR violada (bloqueante)
    2   Error en configuracion o ejecucion script (warnings no bloquean)

DOCUMENTATION:
    docs/devops/automatizacion/planificacion/LLD_01_CONSTITUCION.md
    docs/devops/automatizacion/CONSTITUCION_GUIDE.md

EOF
    exit 0
}

#####################################################################
# Initialize: create dirs, validate config
#####################################################################
initialize() {
    # Create log directory
    mkdir -p "$LOG_DIR"

    # Set log file
    LOG_FILE="$LOG_DIR/${MODE:-unknown}-$TIMESTAMP.log"

    # Validate config file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Constitucion config not found: $CONFIG_FILE"
        echo "Run: cp .constitucion.yaml.example .constitucion.yaml" >&2
        exit 2
    fi

    # Validate YAML syntax
    if command -v yq &> /dev/null; then
        if ! yq eval '.' "$CONFIG_FILE" &> /dev/null; then
            log_error "Invalid YAML in $CONFIG_FILE"
            exit 2
        fi
    else
        log_warn "yq not installed, skipping YAML validation"
    fi

    # Check dependencies
    if ! command -v jq &> /dev/null; then
        log_error "jq not installed. Run: apt-get install jq"
        exit 2
    fi

    # Log start
    if [ "$QUIET" -eq 0 ]; then
        {
            echo "===================================="
            echo "CONSTITUCION VALIDATION"
            echo "===================================="
            echo "Date: $(date)"
            echo "Mode: $MODE"
            echo "Config: $CONFIG_FILE"
            echo "===================================="
            echo ""
        } | tee -a "$LOG_FILE"
    fi
}

#####################################################################
# Load rules from .constitucion.yaml for given mode
#####################################################################
load_rules() {
    local mode="$1"
    local rules_json

    if [ "$mode" = "validate-all" ]; then
        # Load ALL enabled rules
        if command -v yq &> /dev/null; then
            rules_json=$(yq eval '.rules[] | select(.enabled == true)' "$CONFIG_FILE" -o=json)
        else
            log_error "yq required for loading rules"
            exit 2
        fi
    else
        # Load rules for specific scope
        if command -v yq &> /dev/null; then
            rules_json=$(yq eval ".rules[] | select(.enabled == true and .scope == \"$mode\")" "$CONFIG_FILE" -o=json)
        else
            log_error "yq required for loading rules"
            exit 2
        fi
    fi

    echo "$rules_json"
}

#####################################################################
# Evaluate single rule
# Args: rule_json
# Returns: 0 if passed, 1 if failed
#####################################################################
evaluate_rule() {
    local rule_json="$1"
    local rule_id severity title condition_type

    rule_id=$(echo "$rule_json" | jq -r '.id')
    severity=$(echo "$rule_json" | jq -r '.severity')
    title=$(echo "$rule_json" | jq -r '.title')
    condition_type=$(echo "$rule_json" | jq -r '.condition.type // "unknown"')

    if [ "$VERBOSE" -eq 1 ] || [ "$QUIET" -eq 0 ]; then
        echo -e "${BLUE}Evaluating: $rule_id - $title${NC}" | tee -a "$LOG_FILE"
    fi

    case "$condition_type" in
        branch_check)
            evaluate_rule_r1_branch_check "$rule_json"
            ;;
        file_content_check)
            evaluate_rule_r2_file_content_check "$rule_json"
            ;;
        files_analysis)
            evaluate_rule_r3_files_analysis "$rule_json"
            ;;
        files_trigger_validation)
            evaluate_rule_r4_files_trigger_validation "$rule_json"
            ;;
        command_execution)
            evaluate_rule_r5_command_execution "$rule_json"
            ;;
        environment_check)
            evaluate_rule_r6_environment_check "$rule_json"
            ;;
        *)
            log_warn "Unknown condition type: $condition_type for rule $rule_id"
            return 0  # Skip unknown types
            ;;
    esac
}

#####################################################################
# R1: Evaluate branch_check condition (No direct push to main)
#####################################################################
evaluate_rule_r1_branch_check() {
    local rule_json="$1"

    # For pre-push hook, Git provides remote branch via stdin
    # For manual testing, use env var REMOTE_BRANCH
    local remote_branch="${REMOTE_BRANCH:-}"

    # If called from pre-push hook, read from stdin
    if [ "$MODE" = "pre-push" ] && [ -z "$remote_branch" ]; then
        # pre-push hook receives: <local ref> <local sha1> <remote ref> <remote sha1>
        # We only care about remote ref
        while read -r local_ref local_sha remote_ref remote_sha; do
            if [ -n "$remote_ref" ]; then
                remote_branch="$remote_ref"
                break
            fi
        done
    fi

    # If still no branch, try to detect from git
    if [ -z "$remote_branch" ]; then
        local current_branch
        current_branch=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
        if [ -n "$current_branch" ]; then
            remote_branch="refs/heads/$current_branch"
        else
            # Can't detect branch, assume it's not main
            log_warn "Cannot detect remote branch, assuming not main"
            return 0
        fi
    fi

    # Check if pushing to main/master
    if [[ "$remote_branch" =~ refs/heads/(main|master) ]]; then
        log_error "Attempting to push directly to $remote_branch"
        return 1  # Violation
    fi

    return 0  # OK
}

#####################################################################
# R2: Evaluate file_content_check condition (No emojis)
#####################################################################
evaluate_rule_r2_file_content_check() {
    local rule_json="$1"
    local files_pattern script

    files_pattern=$(echo "$rule_json" | jq -r '.condition.files_pattern')
    script=$(echo "$rule_json" | jq -r '.condition.script')

    # Get staged files matching pattern
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep -E "$files_pattern" || true)

    if [ -z "$staged_files" ]; then
        [ "$VERBOSE" -eq 1 ] && echo "  No files to check" | tee -a "$LOG_FILE"
        return 0  # No files to check
    fi

    [ "$VERBOSE" -eq 1 ] && echo "  Checking files: $staged_files" | tee -a "$LOG_FILE"

    # Execute detection script
    local script_path=""
    if [ -f "$PROJECT_ROOT/$script" ]; then
        script_path="$PROJECT_ROOT/$script"
    elif [ -f "$PROJECT_ROOT/scripts/workflows/check_no_emojis.py" ]; then
        script_path="$PROJECT_ROOT/scripts/workflows/check_no_emojis.py"
    fi

    if [ -n "$script_path" ]; then
        if python3 "$script_path" $staged_files &>> "$LOG_FILE"; then
            return 0  # No emojis found
        else
            log_error "Emojis detected in staged files"
            return 1  # Emojis found
        fi
    else
        log_warn "Emoji detection script not found, skipping check"
        return 0  # Skip if script missing
    fi
}

#####################################################################
# R3: Evaluate files_analysis condition (UI/API coherence)
#####################################################################
evaluate_rule_r3_files_analysis() {
    local rule_json="$1"
    local script

    script=$(echo "$rule_json" | jq -r '.condition.script')

    if [ -f "$PROJECT_ROOT/$script" ]; then
        if bash "$PROJECT_ROOT/$script" &>> "$LOG_FILE"; then
            return 0  # Coherence OK
        else
            log_warn "UI/API coherence check detected potential issues"
            return 1  # Warning: incoherence detected
        fi
    else
        log_warn "Script not found: $script"
        return 0  # Skip if script missing
    fi
}

#####################################################################
# R4: Evaluate files_trigger_validation (Database router)
#####################################################################
evaluate_rule_r4_files_trigger_validation() {
    local rule_json="$1"
    local validation_script

    validation_script=$(echo "$rule_json" | jq -r '.condition.validation_script')

    # Get trigger file patterns
    local trigger_patterns
    trigger_patterns=$(echo "$rule_json" | jq -r '.condition.trigger_files[]' | tr '\n' '|' | sed 's/|$//')

    # Check if any trigger files changed (compare with main branch)
    local changed_trigger_files
    if git rev-parse --verify main &>/dev/null; then
        changed_trigger_files=$(git diff --name-only main...HEAD 2>/dev/null | grep -E "$trigger_patterns" || true)
    else
        # Fallback: check staged files
        changed_trigger_files=$(git diff --cached --name-only 2>/dev/null | grep -E "$trigger_patterns" || true)
    fi

    if [ -z "$changed_trigger_files" ]; then
        [ "$VERBOSE" -eq 1 ] && echo "  No trigger files changed, skip validation" | tee -a "$LOG_FILE"
        return 0  # Nothing to validate
    fi

    [ "$VERBOSE" -eq 1 ] && echo "  Trigger files changed: $changed_trigger_files" | tee -a "$LOG_FILE"
    echo "  Running validation: $validation_script" | tee -a "$LOG_FILE"

    # Run validation script
    if [ -f "$PROJECT_ROOT/$validation_script" ]; then
        if bash "$PROJECT_ROOT/$validation_script" &>> "$LOG_FILE"; then
            log_success "Database router validation passed"
            return 0  # Validation passed
        else
            log_error "Database router validation failed"
            return 1  # Validation failed
        fi
    else
        log_warn "Validation script not found: $validation_script"
        return 0  # Skip if script missing
    fi
}

#####################################################################
# R5: Evaluate command_execution (Tests must pass)
#####################################################################
evaluate_rule_r5_command_execution() {
    local rule_json="$1"
    local command success_exit_code

    command=$(echo "$rule_json" | jq -r '.condition.command')
    success_exit_code=$(echo "$rule_json" | jq -r '.condition.success_exit_code')

    echo "  Executing: $command" | tee -a "$LOG_FILE"

    # Execute command
    set +e
    if [ "$VERBOSE" -eq 1 ]; then
        bash -c "cd $PROJECT_ROOT && $command" 2>&1 | tee -a "$LOG_FILE"
        local exit_code=${PIPESTATUS[0]}
    else
        bash -c "cd $PROJECT_ROOT && $command" &>> "$LOG_FILE"
        local exit_code=$?
    fi
    set -e

    echo "  Exit code: $exit_code (expected: $success_exit_code)" | tee -a "$LOG_FILE"

    if [ "$exit_code" -eq "$success_exit_code" ]; then
        log_success "Tests passed"
        return 0  # Command succeeded
    else
        log_error "Tests failed (exit code: $exit_code)"
        return 1  # Command failed
    fi
}

#####################################################################
# R6: Evaluate environment_check (DevContainer compatibility)
#####################################################################
evaluate_rule_r6_environment_check() {
    local rule_json="$1"
    local script

    script=$(echo "$rule_json" | jq -r '.condition.script')

    if [ -f "$PROJECT_ROOT/$script" ]; then
        if bash "$PROJECT_ROOT/$script" &>> "$LOG_FILE"; then
            log_success "DevContainer environment check passed"
            return 0  # Environment OK
        else
            log_warn "DevContainer environment has issues (non-blocking)"
            return 1  # Environment issues
        fi
    else
        log_warn "Environment check script not found: $script"
        return 0  # Skip if script missing
    fi
}

#####################################################################
# Print violation message
#####################################################################
print_violation() {
    local rule_json="$1"
    local rule_id severity title message

    rule_id=$(echo "$rule_json" | jq -r '.id')
    severity=$(echo "$rule_json" | jq -r '.severity')
    title=$(echo "$rule_json" | jq -r '.title')
    message=$(echo "$rule_json" | jq -r '.message')

    echo "" | tee -a "$LOG_FILE"

    if [ "$severity" = "error" ]; then
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
        echo -e "${RED}CONSTITUCION VIOLADA (ERROR - Bloqueante)${NC}" | tee -a "$LOG_FILE"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
        echo -e "${YELLOW}CONSTITUCION ADVERTENCIA (WARNING - No bloqueante)${NC}" | tee -a "$LOG_FILE"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
    fi

    echo "" | tee -a "$LOG_FILE"
    echo "Rule: $rule_id" | tee -a "$LOG_FILE"
    echo "Title: $title" | tee -a "$LOG_FILE"
    echo "Severity: $severity" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "$message" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

#####################################################################
# Main validation logic
#####################################################################
validate() {
    local rules_json

    # Load rules for mode
    rules_json=$(load_rules "$MODE")

    if [ -z "$rules_json" ]; then
        log_info "No rules to validate for mode: $MODE"
        return 0
    fi

    # Count rules
    local rule_count
    rule_count=$(echo "$rules_json" | jq -s 'length')
    log_info "Loaded $rule_count rule(s) for mode: $MODE"
    echo "" | tee -a "$LOG_FILE"

    # Evaluate each rule
    local rules_array
    rules_array=$(echo "$rules_json" | jq -s '.')
    local array_length
    array_length=$(echo "$rules_array" | jq 'length')

    for ((i=0; i<array_length; i++)); do
        local rule_json
        rule_json=$(echo "$rules_array" | jq -c ".[$i]")

        local rule_id severity
        rule_id=$(echo "$rule_json" | jq -r '.id')
        severity=$(echo "$rule_json" | jq -r '.severity')

        if evaluate_rule "$rule_json"; then
            echo -e "${GREEN}  PASS${NC}" | tee -a "$LOG_FILE"
        else
            echo -e "${RED}  FAIL${NC}" | tee -a "$LOG_FILE"
            print_violation "$rule_json"

            # Record violation
            if [ "$severity" = "error" ]; then
                VIOLATIONS_ERROR+=("$rule_id")
            else
                VIOLATIONS_WARNING+=("$rule_id")
            fi
        fi

        echo "" | tee -a "$LOG_FILE"
    done
}

#####################################################################
# Print final summary
#####################################################################
print_summary() {
    echo "====================================" | tee -a "$LOG_FILE"
    echo "VALIDATION SUMMARY" | tee -a "$LOG_FILE"
    echo "====================================" | tee -a "$LOG_FILE"
    echo "Mode: $MODE" | tee -a "$LOG_FILE"
    echo "Violations (ERROR): ${#VIOLATIONS_ERROR[@]}" | tee -a "$LOG_FILE"
    echo "Violations (WARNING): ${#VIOLATIONS_WARNING[@]}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    if [ ${#VIOLATIONS_ERROR[@]} -gt 0 ]; then
        echo -e "${RED}RESULT: FAILED (blocking)${NC}" | tee -a "$LOG_FILE"
        echo "Rules violated (ERROR): ${VIOLATIONS_ERROR[*]}" | tee -a "$LOG_FILE"
        EXIT_CODE=1
    elif [ ${#VIOLATIONS_WARNING[@]} -gt 0 ]; then
        echo -e "${YELLOW}RESULT: PASSED with warnings${NC}" | tee -a "$LOG_FILE"
        echo "Rules violated (WARNING): ${VIOLATIONS_WARNING[*]}" | tee -a "$LOG_FILE"
        EXIT_CODE=0  # Warnings don't block
    else
        echo -e "${GREEN}RESULT: PASSED (all rules)${NC}" | tee -a "$LOG_FILE"
        EXIT_CODE=0
    fi

    echo "" | tee -a "$LOG_FILE"
    echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "====================================" | tee -a "$LOG_FILE"
}

#####################################################################
# Generate compliance report
#####################################################################
generate_report() {
    log_info "Generating constitucion compliance report..."

    local report_file="$LOG_DIR/constitucion_report_$TIMESTAMP.json"

    # Collect metrics (placeholder - implement full metrics later)
    cat > "$report_file" <<EOF
{
  "generated_at": "$(date -Iseconds)",
  "config_file": "$CONFIG_FILE",
  "total_rules": $(yq eval '.rules | length' "$CONFIG_FILE"),
  "enabled_rules": $(yq eval '.rules[] | select(.enabled == true) | .id' "$CONFIG_FILE" | wc -l),
  "violations_error": ${#VIOLATIONS_ERROR[@]},
  "violations_warning": ${#VIOLATIONS_WARNING[@]},
  "compliance_rate": "N/A",
  "note": "Full metrics collection not yet implemented"
}
EOF

    log_success "Report generated: $report_file"
    cat "$report_file"

    exit 0
}

#####################################################################
# MAIN
#####################################################################
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mode=*)
                MODE="${1#*=}"
                shift
                ;;
            --help|-h)
                usage
                ;;
            --verbose|-v)
                VERBOSE=1
                shift
                ;;
            --quiet|-q)
                QUIET=1
                shift
                ;;
            --validate-all)
                MODE="validate-all"
                shift
                ;;
            --report)
                MODE="report"
                shift
                ;;
            *)
                echo "Unknown option: $1"
                usage
                ;;
        esac
    done

    # Validate mode
    if [ -z "$MODE" ]; then
        echo "ERROR: --mode required"
        usage
    fi

    case "$MODE" in
        pre-commit|pre-push|devcontainer-init|ci-local|manual|validate-all|report)
            ;;
        *)
            echo "ERROR: Invalid mode: $MODE"
            usage
            ;;
    esac

    # Initialize
    initialize

    # Run validation or report
    if [ "$MODE" = "report" ]; then
        generate_report
    else
        validate
        print_summary
        exit $EXIT_CODE
    fi
}

# Entry point
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
