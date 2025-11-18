#!/usr/bin/env bash
# ===================================================================
# scripts/ci-local.sh
# CI/CD Local Pipeline Orchestrator - IACT Project
# ===================================================================
# Uso:
#   ./ci-local.sh
#   ./ci-local.sh --verbose
#   ./ci-local.sh --stage=lint
#   ./ci-local.sh --skip-stage=build
#   ./ci-local.sh --dry-run
# ===================================================================

set -euo pipefail

# ===================================================================
# CONSTANTS
# ===================================================================
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly CONFIG_FILE="$PROJECT_ROOT/.ci-local.yaml"
readonly LOG_DIR="$PROJECT_ROOT/.automation-logs/ci-local"
readonly ARTIFACTS_DIR="$PROJECT_ROOT/.ci-artifacts"
readonly TIMESTAMP=$(date +%Y-%m-%d-%H-%M-%S)
readonly LOG_FILE="$LOG_DIR/$TIMESTAMP.log"
readonly REPORT_FILE="$ARTIFACTS_DIR/pipeline-report-$TIMESTAMP.json"

# Colors
if [ -t 1 ]; then
    readonly RED='\033[0;31m'
    readonly YELLOW='\033[1;33m'
    readonly GREEN='\033[0;32m'
    readonly BLUE='\033[0;34m'
    readonly CYAN='\033[0;36m'
    readonly BOLD='\033[1m'
    readonly NC='\033[0m'
else
    readonly RED=''
    readonly YELLOW=''
    readonly GREEN=''
    readonly BLUE=''
    readonly CYAN=''
    readonly BOLD=''
    readonly NC=''
fi

# ===================================================================
# GLOBAL VARIABLES
# ===================================================================
VERBOSE=false
DRY_RUN=false
SPECIFIC_STAGE=""
SPECIFIC_JOB=""
SKIP_STAGES=()

# Pipeline state
PIPELINE_START_TIME=$(date +%s)
PIPELINE_STATUS=0
STAGES_PASSED=0
STAGES_FAILED=0
STAGES_SKIPPED=0
JOBS_TOTAL=0
JOBS_PASSED=0
JOBS_FAILED=0
JOBS_SKIPPED=0

# Results tracking
declare -A STAGE_RESULTS
declare -A STAGE_DURATIONS
declare -A JOB_RESULTS
declare -A JOB_DURATIONS

# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

#####################################################################
# Print usage
#####################################################################
usage() {
    cat <<EOF
CI/CD LOCAL PIPELINE - IACT Project

Ejecuta pipeline CI/CD completo localmente (offline-capable)

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --verbose               Output detallado
    --dry-run               Simular sin ejecutar
    --stage=STAGE          Ejecutar solo este stage
    --job=JOB              Ejecutar solo este job (requiere --stage)
    --skip-stage=STAGE     Saltar este stage
    --help                  Mostrar esta ayuda

STAGES DISPONIBLES:
    lint      Linting UI + API + Markdown
    test      Tests UI (Jest) + API (Pytest)
    build     Build UI (Webpack) + API (collectstatic)
    validate  Validaciones IACT (security, DB, constitucion, docs)

EXAMPLES:
    $0                           # Ejecutar pipeline completo
    $0 --verbose                 # Con output detallado
    $0 --stage=lint              # Solo linting
    $0 --stage=test --job=test_ui  # Solo test UI
    $0 --skip-stage=build        # Saltar build
    $0 --dry-run                 # Simular ejecucion

EXIT CODES:
    0   Pipeline completo exitoso
    1   Al menos un stage fallo
    2   Error configuracion o ejecucion

DOCUMENTATION:
    docs/devops/automatizacion/planificacion/LLD_02_CI_LOCAL.md

EOF
    exit 0
}

#####################################################################
# Initialize: create dirs, validate config
#####################################################################
initialize() {
    # Create directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$ARTIFACTS_DIR"

    # Validate config exists
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}ERROR: Config not found: $CONFIG_FILE${NC}" >&2
        exit 2
    fi

    # Validate yq installed and correct version
    if ! command -v yq &> /dev/null; then
        echo -e "${RED}ERROR: yq not installed${NC}" >&2
        echo "This script requires mikefarah/yq (Go-based YAML processor)" >&2
        echo "" >&2
        echo "Install with:" >&2
        echo "  wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /tmp/yq" >&2
        echo "  sudo mv /tmp/yq /usr/local/bin/yq && sudo chmod +x /usr/local/bin/yq" >&2
        echo "" >&2
        echo "Or visit: https://github.com/mikefarah/yq" >&2
        exit 2
    fi

    # Check yq version (should be mikefarah/yq, not python-yq)
    local yq_version
    yq_version=$(yq --version 2>&1 || echo "unknown")
    if [[ "$yq_version" == *"jq"* ]] || [[ "$yq_version" == "yq 0.0.0" ]]; then
        echo -e "${YELLOW}WARNING: Incompatible yq version detected${NC}" >&2
        echo "Found: $yq_version" >&2
        echo "This appears to be python-yq (jq wrapper), not mikefarah/yq" >&2
        echo "" >&2
        echo "This script requires mikefarah/yq (Go-based YAML processor)" >&2
        echo "Install with:" >&2
        echo "  wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /tmp/yq" >&2
        echo "  sudo mv /tmp/yq /usr/local/bin/yq && sudo chmod +x /usr/local/bin/yq" >&2
        echo "" >&2
        echo "Or visit: https://github.com/mikefarah/yq" >&2
        echo "" >&2
        echo -e "${CYAN}Attempting to continue anyway...${NC}" >&2
        echo "" >&2
    fi

    # Log pipeline start
    {
        echo "========================================"
        echo "CI/CD LOCAL PIPELINE - IACT"
        echo "========================================"
        echo "Date: $(date)"
        echo "Config: $CONFIG_FILE"
        echo "Log: $LOG_FILE"
        echo "Report: $REPORT_FILE"
        if [ "$DRY_RUN" = "true" ]; then
            echo "Mode: DRY RUN (simulation)"
        fi
        echo "========================================"
        echo ""
    } | tee -a "$LOG_FILE"
}

#####################################################################
# Load config value
# Args: yq_query
# Returns: value
#####################################################################
get_config() {
    local query="$1"
    yq eval "$query" "$CONFIG_FILE" 2>/dev/null || echo ""
}

#####################################################################
# Check if files changed (smart detection)
# Args: pattern
# Returns: 0 if changed, 1 if not
#####################################################################
files_changed() {
    local pattern="$1"

    # If smart detection disabled, always return true
    local smart_enabled
    smart_enabled=$(get_config '.pipeline.smart_detection.enabled')
    if [ "$smart_enabled" != "true" ]; then
        return 0
    fi

    local base_branch
    base_branch=$(get_config '.pipeline.smart_detection.base_branch')

    if [ -z "$base_branch" ]; then
        base_branch="main"
    fi

    # Get changed files vs base branch
    local changed_files
    changed_files=$(git diff --name-only "$base_branch"...HEAD 2>/dev/null || \
                    git diff --name-only HEAD 2>/dev/null || \
                    git ls-files -m 2>/dev/null || \
                    echo "")

    # If no git or no changes, check working directory changes
    if [ -z "$changed_files" ]; then
        if $VERBOSE; then
            echo "  No git changes detected, assuming all files changed" >> "$LOG_FILE"
        fi
        return 0  # Assume files changed if can't detect
    fi

    # Check if any file matches pattern
    if echo "$changed_files" | grep -qE "$pattern"; then
        if $VERBOSE; then
            echo "  Files changed matching pattern: $pattern" >> "$LOG_FILE"
        fi
        return 0  # Files changed
    else
        if $VERBOSE; then
            echo "  No files changed matching pattern: $pattern" >> "$LOG_FILE"
        fi
        return 1  # No matching files
    fi
}

#####################################################################
# Get job configuration value
# Args: stage_name, job_name, config_key
# Returns: config value
#####################################################################
get_job_config() {
    local stage_name="$1"
    local job_name="$2"
    local config_key="$3"

    local value
    value=$(yq eval ".stages[] | select(.name == \"$stage_name\") | .jobs[] | select(.name == \"$job_name\") | .$config_key" "$CONFIG_FILE" 2>/dev/null || echo "")
    echo "$value"
}

#####################################################################
# Execute job
# Args: stage_name, job_name
# Returns: exit code of job
#####################################################################
execute_job() {
    local stage_name="$1"
    local job_name="$2"
    local job_start_time=$(date +%s)

    JOBS_TOTAL=$((JOBS_TOTAL + 1))

    # Load job config
    local working_dir
    working_dir=$(get_job_config "$stage_name" "$job_name" "working_dir")

    local command
    command=$(get_job_config "$stage_name" "$job_name" "command")

    local timeout
    timeout=$(get_job_config "$stage_name" "$job_name" "timeout")

    local continue_on_error
    continue_on_error=$(get_job_config "$stage_name" "$job_name" "continue_on_error")

    local description
    description=$(get_job_config "$stage_name" "$job_name" "description")

    # Check condition
    local condition_type
    condition_type=$(get_job_config "$stage_name" "$job_name" "condition.type")

    if [ "$condition_type" = "files_changed" ]; then
        local condition_pattern
        condition_pattern=$(get_job_config "$stage_name" "$job_name" "condition.pattern")

        if ! files_changed "$condition_pattern"; then
            echo -e "  ${CYAN}[$job_name]${NC} SKIP (no files changed matching: $condition_pattern)" | tee -a "$LOG_FILE"
            JOB_RESULTS["$stage_name:$job_name"]="SKIPPED"
            JOBS_SKIPPED=$((JOBS_SKIPPED + 1))
            return 0  # Skip job
        fi
    fi

    # Print job info
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}Executing job: $job_name${NC}" | tee -a "$LOG_FILE"
    if [ -n "$description" ] && [ "$description" != "null" ]; then
        echo "  Description: $description" | tee -a "$LOG_FILE"
    fi
    echo "  Working dir: $working_dir" | tee -a "$LOG_FILE"
    echo "  Command: $command" | tee -a "$LOG_FILE"
    echo "  Timeout: ${timeout}s" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    # Dry run mode
    if [ "$DRY_RUN" = "true" ]; then
        echo -e "  ${CYAN}DRY-RUN: Would execute job${NC}" | tee -a "$LOG_FILE"
        JOB_RESULTS["$stage_name:$job_name"]="DRY-RUN"
        return 0
    fi

    # Change to working directory
    local full_working_dir="$PROJECT_ROOT/$working_dir"
    if [ ! -d "$full_working_dir" ]; then
        echo -e "${YELLOW}WARNING: Working directory does not exist: $full_working_dir${NC}" | tee -a "$LOG_FILE"
        echo -e "  ${CYAN}SKIP${NC} (working directory missing)" | tee -a "$LOG_FILE"
        JOB_RESULTS["$stage_name:$job_name"]="SKIPPED"
        JOBS_SKIPPED=$((JOBS_SKIPPED + 1))
        return 0
    fi

    pushd "$full_working_dir" > /dev/null 2>&1 || {
        echo -e "${RED}ERROR: Cannot cd to $full_working_dir${NC}" | tee -a "$LOG_FILE"
        JOB_RESULTS["$stage_name:$job_name"]="ERROR"
        JOBS_FAILED=$((JOBS_FAILED + 1))
        return 1
    }

    # Execute with timeout
    set +e
    if [ -n "$timeout" ] && [ "$timeout" != "null" ]; then
        timeout "${timeout}s" bash -c "$command" &>> "$LOG_FILE"
        local exit_code=$?
    else
        bash -c "$command" &>> "$LOG_FILE"
        local exit_code=$?
    fi
    set -e

    # Return to project root
    popd > /dev/null 2>&1

    # Calculate duration
    local job_end_time=$(date +%s)
    local job_duration=$((job_end_time - job_start_time))
    JOB_DURATIONS["$stage_name:$job_name"]=$job_duration

    # Check result
    if [ $exit_code -eq 0 ]; then
        echo -e "  ${GREEN}PASS${NC} (${job_duration}s)" | tee -a "$LOG_FILE"
        JOB_RESULTS["$stage_name:$job_name"]="PASS"
        JOBS_PASSED=$((JOBS_PASSED + 1))
        return 0
    elif [ $exit_code -eq 124 ]; then
        echo -e "  ${RED}TIMEOUT${NC} (>${timeout}s)" | tee -a "$LOG_FILE"
        JOB_RESULTS["$stage_name:$job_name"]="TIMEOUT"
        JOBS_FAILED=$((JOBS_FAILED + 1))
        return 1
    else
        echo -e "  ${RED}FAIL${NC} (exit code: $exit_code, ${job_duration}s)" | tee -a "$LOG_FILE"
        JOB_RESULTS["$stage_name:$job_name"]="FAIL"
        JOBS_FAILED=$((JOBS_FAILED + 1))

        if [ "$continue_on_error" = "true" ]; then
            echo -e "  ${YELLOW}Continuing despite error (continue_on_error=true)${NC}" | tee -a "$LOG_FILE"
            return 0  # Treat as success
        else
            return $exit_code
        fi
    fi
}

#####################################################################
# Get stage configuration value
# Args: stage_name, config_key
# Returns: config value
#####################################################################
get_stage_config() {
    local stage_name="$1"
    local config_key="$2"

    local value
    value=$(yq eval ".stages[] | select(.name == \"$stage_name\") | .$config_key" "$CONFIG_FILE" 2>/dev/null || echo "")
    echo "$value"
}

#####################################################################
# Check if stage dependencies are met
# Args: stage_name
# Returns: 0 if met, 1 if not
#####################################################################
check_dependencies() {
    local stage_name="$1"

    # Get dependencies
    local depends_on
    depends_on=$(get_stage_config "$stage_name" "depends_on[]")

    if [ -z "$depends_on" ] || [ "$depends_on" = "null" ]; then
        return 0  # No dependencies
    fi

    # Check each dependency
    while IFS= read -r dep_stage; do
        if [ -z "$dep_stage" ] || [ "$dep_stage" = "null" ]; then
            continue
        fi

        local dep_result="${STAGE_RESULTS[$dep_stage]:-}"
        if [ "$dep_result" != "PASSED" ]; then
            echo -e "${YELLOW}Dependency not met: $dep_stage (status: ${dep_result:-UNKNOWN})${NC}" | tee -a "$LOG_FILE"
            return 1
        fi
    done <<< "$depends_on"

    return 0
}

#####################################################################
# Execute stage
# Args: stage_name
# Returns: 0 if passed, 1 if failed
#####################################################################
execute_stage() {
    local stage_name="$1"
    local stage_start_time=$(date +%s)

    echo "" | tee -a "$LOG_FILE"
    echo -e "${BOLD}=======================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${BOLD}STAGE: $stage_name${NC}" | tee -a "$LOG_FILE"
    echo -e "${BOLD}=======================================${NC}" | tee -a "$LOG_FILE"

    local description
    description=$(get_stage_config "$stage_name" "description")
    if [ -n "$description" ] && [ "$description" != "null" ]; then
        echo "Description: $description" | tee -a "$LOG_FILE"
    fi
    echo "" | tee -a "$LOG_FILE"

    # Check if should skip
    for skip_stage in "${SKIP_STAGES[@]}"; do
        if [ "$skip_stage" = "$stage_name" ]; then
            echo -e "${CYAN}SKIPPED${NC} (--skip-stage specified)" | tee -a "$LOG_FILE"
            STAGE_RESULTS["$stage_name"]="SKIPPED"
            STAGES_SKIPPED=$((STAGES_SKIPPED + 1))
            return 0
        fi
    done

    # Check dependencies
    if ! check_dependencies "$stage_name"; then
        echo -e "${YELLOW}SKIPPED${NC} (dependencies not met)" | tee -a "$LOG_FILE"
        STAGE_RESULTS["$stage_name"]="SKIPPED"
        STAGES_SKIPPED=$((STAGES_SKIPPED + 1))
        return 0
    fi

    # Get jobs for stage
    local jobs
    jobs=$(yq eval ".stages[] | select(.name == \"$stage_name\") | .jobs[].name" "$CONFIG_FILE" 2>/dev/null || echo "")

    if [ -z "$jobs" ]; then
        echo -e "${YELLOW}WARNING: No jobs found for stage${NC}" | tee -a "$LOG_FILE"
        STAGE_RESULTS["$stage_name"]="SKIPPED"
        STAGES_SKIPPED=$((STAGES_SKIPPED + 1))
        return 0
    fi

    # Filter to specific job if requested
    if [ -n "$SPECIFIC_JOB" ]; then
        if echo "$jobs" | grep -q "^$SPECIFIC_JOB$"; then
            jobs="$SPECIFIC_JOB"
        else
            echo -e "${YELLOW}Job not found in stage: $SPECIFIC_JOB${NC}" | tee -a "$LOG_FILE"
            STAGE_RESULTS["$stage_name"]="SKIPPED"
            STAGES_SKIPPED=$((STAGES_SKIPPED + 1))
            return 0
        fi
    fi

    # Check if parallel
    local parallel
    parallel=$(get_stage_config "$stage_name" "parallel")

    local stage_failed=false

    # Execute jobs
    if [ "$parallel" = "true" ] && [ -z "$SPECIFIC_JOB" ]; then
        echo "Executing jobs in PARALLEL" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"

        # Execute jobs in parallel (background)
        local pids=()
        local job_list=()
        while IFS= read -r job_name; do
            if [ -n "$job_name" ] && [ "$job_name" != "null" ]; then
                execute_job "$stage_name" "$job_name" &
                pids+=($!)
                job_list+=("$job_name")
            fi
        done <<< "$jobs"

        # Wait for all jobs
        local any_failed=false
        for i in "${!pids[@]}"; do
            local pid="${pids[$i]}"
            if ! wait "$pid"; then
                any_failed=true
            fi
        done

        if $any_failed; then
            stage_failed=true
        fi
    else
        echo "Executing jobs SEQUENTIALLY" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"

        # Execute jobs sequentially
        while IFS= read -r job_name; do
            if [ -z "$job_name" ] || [ "$job_name" = "null" ]; then
                continue
            fi

            if ! execute_job "$stage_name" "$job_name"; then
                stage_failed=true

                # Check fail_fast
                local fail_fast
                fail_fast=$(get_config '.pipeline.fail_fast')

                if [ "$fail_fast" = "true" ]; then
                    echo -e "${RED}FAIL_FAST enabled, stopping stage${NC}" | tee -a "$LOG_FILE"
                    break
                fi
            fi
        done <<< "$jobs"
    fi

    # Calculate stage duration
    local stage_end_time=$(date +%s)
    local stage_duration=$((stage_end_time - stage_start_time))
    STAGE_DURATIONS["$stage_name"]=$stage_duration

    # Record result
    if $stage_failed; then
        echo "" | tee -a "$LOG_FILE"
        echo -e "${RED}Stage FAILED${NC} (${stage_duration}s)" | tee -a "$LOG_FILE"
        STAGE_RESULTS["$stage_name"]="FAILED"
        STAGES_FAILED=$((STAGES_FAILED + 1))
        return 1
    else
        echo "" | tee -a "$LOG_FILE"
        echo -e "${GREEN}Stage PASSED${NC} (${stage_duration}s)" | tee -a "$LOG_FILE"
        STAGE_RESULTS["$stage_name"]="PASSED"
        STAGES_PASSED=$((STAGES_PASSED + 1))
        return 0
    fi
}

#####################################################################
# Execute hooks
# Args: hook_type (pre_pipeline | post_pipeline)
#####################################################################
execute_hooks() {
    local hook_type="$1"

    local enabled
    enabled=$(get_config ".hooks.${hook_type}.enabled")

    if [ "$enabled" != "true" ]; then
        return 0
    fi

    echo "" | tee -a "$LOG_FILE"
    echo -e "${CYAN}Executing ${hook_type} hooks...${NC}" | tee -a "$LOG_FILE"

    # Get hook jobs
    local hook_jobs
    hook_jobs=$(yq eval ".hooks.${hook_type}.jobs[].name" "$CONFIG_FILE" 2>/dev/null || echo "")

    if [ -z "$hook_jobs" ]; then
        return 0
    fi

    # Execute each hook job
    while IFS= read -r job_name; do
        if [ -z "$job_name" ] || [ "$job_name" = "null" ]; then
            continue
        fi

        local command
        command=$(yq eval ".hooks.${hook_type}.jobs[] | select(.name == \"$job_name\") | .command" "$CONFIG_FILE")

        local timeout
        timeout=$(yq eval ".hooks.${hook_type}.jobs[] | select(.name == \"$job_name\") | .timeout" "$CONFIG_FILE")

        local continue_on_error
        continue_on_error=$(yq eval ".hooks.${hook_type}.jobs[] | select(.name == \"$job_name\") | .continue_on_error" "$CONFIG_FILE")

        echo "  Hook: $job_name" | tee -a "$LOG_FILE"
        echo "  Command: $command" | tee -a "$LOG_FILE"

        if [ "$DRY_RUN" = "true" ]; then
            echo -e "  ${CYAN}DRY-RUN: Would execute hook${NC}" | tee -a "$LOG_FILE"
            continue
        fi

        set +e
        if [ -n "$timeout" ] && [ "$timeout" != "null" ]; then
            timeout "${timeout}s" bash -c "$command" &>> "$LOG_FILE"
            local exit_code=$?
        else
            bash -c "$command" &>> "$LOG_FILE"
            local exit_code=$?
        fi
        set -e

        if [ $exit_code -eq 0 ]; then
            echo -e "  ${GREEN}Hook completed${NC}" | tee -a "$LOG_FILE"
        else
            if [ "$continue_on_error" = "true" ]; then
                echo -e "  ${YELLOW}Hook failed (continuing)${NC}" | tee -a "$LOG_FILE"
            else
                echo -e "  ${RED}Hook failed${NC}" | tee -a "$LOG_FILE"
                return 1
            fi
        fi
    done <<< "$hook_jobs"

    return 0
}

#####################################################################
# Generate JSON report
#####################################################################
generate_json_report() {
    local pipeline_end_time=$(date +%s)
    local pipeline_duration=$((pipeline_end_time - PIPELINE_START_TIME))

    # Build stages array
    local stages_json="["
    local first_stage=true
    for stage_name in "${!STAGE_RESULTS[@]}"; do
        if [ "$first_stage" = false ]; then
            stages_json+=","
        fi
        first_stage=false

        local result="${STAGE_RESULTS[$stage_name]}"
        local duration="${STAGE_DURATIONS[$stage_name]:-0}"

        stages_json+="{\"name\":\"$stage_name\",\"result\":\"$result\",\"duration\":$duration}"
    done
    stages_json+="]"

    # Build jobs array
    local jobs_json="["
    local first_job=true
    for job_key in "${!JOB_RESULTS[@]}"; do
        if [ "$first_job" = false ]; then
            jobs_json+=","
        fi
        first_job=false

        local result="${JOB_RESULTS[$job_key]}"
        local duration="${JOB_DURATIONS[$job_key]:-0}"

        # Split stage:job
        local stage_name="${job_key%%:*}"
        local job_name="${job_key#*:}"

        jobs_json+="{\"stage\":\"$stage_name\",\"job\":\"$job_name\",\"result\":\"$result\",\"duration\":$duration}"
    done
    jobs_json+="]"

    # Overall status
    local overall_status
    if [ $PIPELINE_STATUS -eq 0 ]; then
        overall_status="PASSED"
    else
        overall_status="FAILED"
    fi

    # Build complete report
    cat > "$REPORT_FILE" <<EOF
{
  "pipeline": {
    "name": "IACT Local CI",
    "timestamp": "$TIMESTAMP",
    "duration": $pipeline_duration,
    "status": "$overall_status"
  },
  "summary": {
    "stages": {
      "total": $((STAGES_PASSED + STAGES_FAILED + STAGES_SKIPPED)),
      "passed": $STAGES_PASSED,
      "failed": $STAGES_FAILED,
      "skipped": $STAGES_SKIPPED
    },
    "jobs": {
      "total": $JOBS_TOTAL,
      "passed": $JOBS_PASSED,
      "failed": $JOBS_FAILED,
      "skipped": $JOBS_SKIPPED
    }
  },
  "stages": $stages_json,
  "jobs": $jobs_json,
  "artifacts": {
    "log_file": "$LOG_FILE",
    "artifacts_dir": "$ARTIFACTS_DIR"
  }
}
EOF

    echo "" | tee -a "$LOG_FILE"
    echo "JSON report generated: $REPORT_FILE" | tee -a "$LOG_FILE"
}

#####################################################################
# Print summary
#####################################################################
print_summary() {
    local pipeline_end_time=$(date +%s)
    local pipeline_duration=$((pipeline_end_time - PIPELINE_START_TIME))

    echo "" | tee -a "$LOG_FILE"
    echo -e "${BOLD}=======================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${BOLD}PIPELINE SUMMARY${NC}" | tee -a "$LOG_FILE"
    echo -e "${BOLD}=======================================${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    # Stage results
    echo "Stage Results:" | tee -a "$LOG_FILE"
    if [ ${#STAGE_RESULTS[@]} -eq 0 ]; then
        echo "  No stages executed" | tee -a "$LOG_FILE"
    else
        for stage_name in lint test build validate; do
            if [ -n "${STAGE_RESULTS[$stage_name]:-}" ]; then
                local result="${STAGE_RESULTS[$stage_name]}"
                local duration="${STAGE_DURATIONS[$stage_name]:-0}"

                case "$result" in
                    PASSED)
                        echo -e "  ${GREEN}[PASS]${NC} $stage_name (${duration}s)" | tee -a "$LOG_FILE"
                        ;;
                    FAILED)
                        echo -e "  ${RED}[FAIL]${NC} $stage_name (${duration}s)" | tee -a "$LOG_FILE"
                        ;;
                    SKIPPED)
                        echo -e "  ${CYAN}[SKIP]${NC} $stage_name" | tee -a "$LOG_FILE"
                        ;;
                    *)
                        echo -e "  ${YELLOW}[${result}]${NC} $stage_name" | tee -a "$LOG_FILE"
                        ;;
                esac
            fi
        done
    fi

    echo "" | tee -a "$LOG_FILE"

    # Job results (if verbose or failures)
    if $VERBOSE || [ $JOBS_FAILED -gt 0 ]; then
        echo "Job Results:" | tee -a "$LOG_FILE"
        if [ ${#JOB_RESULTS[@]} -eq 0 ]; then
            echo "  No jobs executed" | tee -a "$LOG_FILE"
        else
            for job_key in "${!JOB_RESULTS[@]}"; do
                local result="${JOB_RESULTS[$job_key]}"
                local duration="${JOB_DURATIONS[$job_key]:-0}"

                case "$result" in
                    PASS)
                        if $VERBOSE; then
                            echo -e "  ${GREEN}[PASS]${NC} $job_key (${duration}s)" | tee -a "$LOG_FILE"
                        fi
                        ;;
                    FAIL)
                        echo -e "  ${RED}[FAIL]${NC} $job_key (${duration}s)" | tee -a "$LOG_FILE"
                        ;;
                    TIMEOUT)
                        echo -e "  ${RED}[TIMEOUT]${NC} $job_key" | tee -a "$LOG_FILE"
                        ;;
                    SKIPPED)
                        if $VERBOSE; then
                            echo -e "  ${CYAN}[SKIP]${NC} $job_key" | tee -a "$LOG_FILE"
                        fi
                        ;;
                    *)
                        if $VERBOSE; then
                            echo -e "  ${YELLOW}[${result}]${NC} $job_key" | tee -a "$LOG_FILE"
                        fi
                        ;;
                esac
            done
        fi
        echo "" | tee -a "$LOG_FILE"
    fi

    # Overall stats
    echo "Overall Statistics:" | tee -a "$LOG_FILE"
    echo "  Stages Total:   $((STAGES_PASSED + STAGES_FAILED + STAGES_SKIPPED))" | tee -a "$LOG_FILE"
    echo "  Stages Passed:  $STAGES_PASSED" | tee -a "$LOG_FILE"
    echo "  Stages Failed:  $STAGES_FAILED" | tee -a "$LOG_FILE"
    echo "  Stages Skipped: $STAGES_SKIPPED" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "  Jobs Total:     $JOBS_TOTAL" | tee -a "$LOG_FILE"
    echo "  Jobs Passed:    $JOBS_PASSED" | tee -a "$LOG_FILE"
    echo "  Jobs Failed:    $JOBS_FAILED" | tee -a "$LOG_FILE"
    echo "  Jobs Skipped:   $JOBS_SKIPPED" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "  Total Duration: ${pipeline_duration}s ($(($pipeline_duration / 60))m $(($pipeline_duration % 60))s)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    # Final result
    if [ $PIPELINE_STATUS -eq 0 ]; then
        echo -e "${GREEN}${BOLD}PIPELINE: PASSED ✓${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}${BOLD}PIPELINE: FAILED ✗${NC}" | tee -a "$LOG_FILE"
    fi

    echo "" | tee -a "$LOG_FILE"
    echo "Artifacts:" | tee -a "$LOG_FILE"
    echo "  Log file:    $LOG_FILE" | tee -a "$LOG_FILE"
    echo "  Report:      $REPORT_FILE" | tee -a "$LOG_FILE"
    echo "  Artifacts:   $ARTIFACTS_DIR" | tee -a "$LOG_FILE"
    echo -e "${BOLD}=======================================${NC}" | tee -a "$LOG_FILE"
}

#####################################################################
# Main pipeline execution
#####################################################################
run_pipeline() {
    # Execute pre-pipeline hooks
    execute_hooks "pre_pipeline"

    # Get stages
    local stages
    if [ -n "$SPECIFIC_STAGE" ]; then
        stages="$SPECIFIC_STAGE"
    else
        stages=$(get_config '.stages[].name')
    fi

    # Execute stages
    local fail_fast
    fail_fast=$(get_config '.pipeline.fail_fast')

    while IFS= read -r stage_name; do
        if [ -z "$stage_name" ] || [ "$stage_name" = "null" ]; then
            continue
        fi

        if ! execute_stage "$stage_name"; then
            PIPELINE_STATUS=1

            if [ "$fail_fast" = "true" ]; then
                echo -e "${RED}FAIL_FAST enabled, stopping pipeline${NC}" | tee -a "$LOG_FILE"
                break
            fi
        fi
    done <<< "$stages"

    # Execute post-pipeline hooks
    execute_hooks "post_pipeline"
}

#####################################################################
# MAIN
#####################################################################
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose)
                VERBOSE=true
                set -x
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --stage=*)
                SPECIFIC_STAGE="${1#*=}"
                shift
                ;;
            --job=*)
                SPECIFIC_JOB="${1#*=}"
                shift
                ;;
            --skip-stage=*)
                SKIP_STAGES+=("${1#*=}")
                shift
                ;;
            --help)
                usage
                ;;
            *)
                echo "Unknown option: $1"
                usage
                ;;
        esac
    done

    # Validate job requires stage
    if [ -n "$SPECIFIC_JOB" ] && [ -z "$SPECIFIC_STAGE" ]; then
        echo -e "${RED}ERROR: --job requires --stage to be specified${NC}" >&2
        exit 2
    fi

    # Initialize
    initialize

    # Run pipeline
    run_pipeline

    # Generate JSON report
    generate_json_report

    # Print summary
    print_summary

    # Exit
    exit $PIPELINE_STATUS
}

# Entry point
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
