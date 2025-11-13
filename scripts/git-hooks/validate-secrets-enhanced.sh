#!/bin/bash

set -euo pipefail

# Source centralized logging functions
if [ -f "infrastructure/utils/logging-functions.sh" ]; then
    source infraestructura/utils/logging-functions.sh
else
    echo "[ERROR] Missing infrastructure/utils/logging-functions.sh"
    exit 1
fi

# Global state
script_start_time=""
operations_count=0
critical_threats_detected=false
suspicious_patterns_found=false
affected_files=()

# Business logic
threat_level_to_exit_code() {
    case "$1" in
        "IMMEDIATE") echo "2" ;;
        "CORRECTIVE") echo "1" ;;
        *) echo "0" ;;
    esac
}

threat_level_to_action() {
    case "$1" in
        "IMMEDIATE") echo "Remove secret from code immediately" ;;
        "CORRECTIVE") echo "Review and move to secure storage if needed" ;;
        *) echo "Follow security best practices" ;;
    esac
}

# Pattern detection strategies
detect_password_assignments() {
    local file="$1" findings="$2"
    scan_file_for_pattern "$file" "password[[:space:]]*=" "IMMEDIATE" "Password assignment" "$findings"
}

detect_secret_assignments() {
    local file="$1" findings="$2"
    scan_file_for_pattern "$file" "secret[[:space:]]*=" "IMMEDIATE" "Secret assignment" "$findings"
}

detect_api_key_assignments() {
    local file="$1" findings="$2"
    scan_file_for_pattern "$file" "api[_-]?key[[:space:]]*=" "IMMEDIATE" "API key assignment" "$findings"
}

detect_auth_token_assignments() {
    local file="$1" findings="$2"
    scan_file_for_pattern "$file" "(auth_token|access_token|bearer_token)[[:space:]]*=" "IMMEDIATE" "Auth token assignment" "$findings"
}

detect_private_key_material() {
    local file="$1" findings="$2"
    if grep -qiE "BEGIN[[:space:]]+(RSA[[:space:]]+)?PRIVATE[[:space:]]+KEY" "$file" 2>/dev/null; then
        if ! should_exclude_file "$file"; then
            record_finding "IMMEDIATE" "Private key material" "$file" "N/A" "-----BEGIN PRIVATE KEY-----" "$findings"
            return 0
        fi
    fi
    return 1
}

detect_database_credentials() {
    local file="$1" findings="$2"
    scan_file_for_pattern "$file" "DATABASE_URL.*://.*:.*@" "CORRECTIVE" "Database URL with credentials" "$findings"
}

detect_generic_tokens() {
    local file="$1" findings="$2"
    scan_file_for_pattern "$file" "token[[:space:]]*=[[:space:]]*[\"'][^\"']{16,}[\"']" "CORRECTIVE" "Generic token pattern" "$findings"
}

detect_config_credentials() {
    local file="$1" findings="$2"
    scan_file_for_pattern "$file" "(client_secret|private_key_id|service_account)[[:space:]]*=" "CORRECTIVE" "Config credential" "$findings"
}

# Orchestration
scan_for_immediate_threats() {
    local file="$1" findings="$2"
    local found=false

    detect_password_assignments "$file" "$findings" && found=true
    detect_secret_assignments "$file" "$findings" && found=true
    detect_api_key_assignments "$file" "$findings" && found=true
    detect_auth_token_assignments "$file" "$findings" && found=true
    detect_private_key_material "$file" "$findings" && found=true

    [ "$found" = true ]
}

scan_for_corrective_issues() {
    local file="$1" findings="$2"
    local found=false

    detect_database_credentials "$file" "$findings" && found=true
    if detect_generic_tokens "$file" "$findings"; then
        if ! grep -qiE "(auth_token|access_token|bearer_token|api.*key)" "$file" 2>/dev/null; then
            found=true
        fi
    fi
    detect_config_credentials "$file" "$findings" && found=true

    [ "$found" = true ]
}

# Support functions
load_configuration() {
    local immediate=$(git config --bool --default true secrets.enforceImmediate 2>/dev/null || echo "true")
    local corrective=$(git config --bool --default true secrets.trackCorrective 2>/dev/null || echo "true")

    [ "$immediate" = "false" ] && log_info "IMMEDIATE enforcement disabled"
    [ "$corrective" = "false" ] && log_info "CORRECTIVE tracking disabled"
}

update_state() {
    local level="$1" file="$2"
    case "$level" in
        "IMMEDIATE")
            critical_threats_detected=true
            affected_files+=("$file")
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
            ;;
        "CORRECTIVE")
            suspicious_patterns_found=true
            affected_files+=("$file")
            VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
            ;;
    esac
}

record_finding() {
    local level="$1" description="$2" file="$3" line="$4" content="$5" findings="$6"
    local clean_content=$(echo "$content" | sed 's/^[[:space:]]*//')
    local action=$(threat_level_to_action "$level")

    eval "$findings+=(\"$level: $description detected at line $line\")"
    eval "$findings+=(\"  Line: $clean_content\")"
    eval "$findings+=(\"ACTION REQUIRED: $action\")"

    update_state "$level" "$file"
    operations_count=$((operations_count + 1))
}

should_exclude_file() {
    local file="$1"
    echo "$file" | grep -qiE "(example|placeholder|template|test|spec|mock)" && return 0
    echo "$file" | grep -qE "^(archives|\.git|node_modules|vendor|\.cache)/" && return 0
    echo "$file" | grep -qiE "\.(log|tmp|cache|lock|gz|zip|tar|pdf|jpg|png|gif)$" && return 0
    return 1
}

should_exclude_line() {
    local line="$1"
    echo "$line" | grep -qE "^[[:space:]]*#" && return 0
    echo "$line" | grep -qE "^[[:space:]]*(//|/\*|\*)" && return 0
    echo "$line" | grep -qE "^[[:space:]]*[\"\'].*[\"\'][[:space:]]*$" && \
        echo "$line" | grep -qiE "(example|placeholder|todo|fixme)" && return 0
    return 1
}

scan_file_for_pattern() {
    local file="$1" pattern="$2" level="$3" description="$4" findings="$5"
    local line_num=0 found=false

    [ ! -f "$file" ] || [ ! -r "$file" ] && return 1

    while IFS= read -r line; do
        line_num=$((line_num + 1))
        should_exclude_line "$line" && continue

        if echo "$line" | grep -qiE "$pattern" 2>/dev/null; then
            record_finding "$level" "$description" "$file" "$line_num" "$line" "$findings"
            found=true
        fi
    done < "$file"

    [ "$found" = true ]
}

# Main detection
analyze_file() {
    local file="$1"
    local findings=()
    local highest_level="ADVISORY"
    local threats_found=false

    [ ! -f "$file" ] || [ ! -r "$file" ] && return 0
    should_exclude_file "$file" && return 0

    if scan_for_immediate_threats "$file" "findings"; then
        highest_level="IMMEDIATE"
        threats_found=true
    elif scan_for_corrective_issues "$file" "findings"; then
        highest_level="CORRECTIVE"
        threats_found=true
    fi

    if [ "$threats_found" = true ]; then
        report_findings "$highest_level" "${findings[@]}"
        return $(threat_level_to_exit_code "$highest_level")
    fi

    return 0
}

report_findings() {
    local level="$1"
    shift
    local findings=("$@")

    case "$level" in
        "IMMEDIATE")
            log_error "[$level] SECURITY THREAT DETECTION:"
            for finding in "${findings[@]}"; do
                log_error "$finding"
            done
            ;;
        "CORRECTIVE")
            log_warning "[$level] SECURITY THREAT DETECTION:"
            for finding in "${findings[@]}"; do
                log_warning "$finding"
            done
            ;;
        *)
            log_info "[$level] SECURITY THREAT DETECTION:"
            for finding in "${findings[@]}"; do
                log_info "$finding"
            done
            ;;
    esac
    log_info ""
}

# Multi-file analysis
analyze_staged_files() {
    local staged_files overall_result=0 clean_count=0 total_count=0

    if ! staged_files=$(git diff --cached --name-only 2>/dev/null); then
        log_error "Failed to get staged files - ensure you're in a git repository"
        return 1
    fi

    log_section "SECURITY THREAT DETECTION"
    log_info "Analyzing staged files for security threats..."

    if [ -z "$staged_files" ]; then
        log_info "No staged files to analyze"
        log_success "Security detection completed - no files to scan"
        return 0
    fi

    # Count files safely without relying on wc behavior with empty input
    total_count=0
    for file in $staged_files; do
        total_count=$((total_count + 1))
    done

    log_info "Scanning $total_count staged file(s)"
    log_info ""

    local current=0
    for file in $staged_files; do
        current=$((current + 1))
        [ -f "$file" ] || continue

        log_info "[$current/$total_count] Scanning: $file"

        analyze_file "$file"
        local result=$?

        case $result in
            0) clean_count=$((clean_count + 1)) ;;
            *) ;;
        esac

        [ $result -gt $overall_result ] && overall_result=$result
    done

    log_info ""
    log_section "DETECTION SUMMARY"
    generate_summary "$overall_result" "$total_count" "$clean_count"

    return $overall_result
}

# Summary generation
generate_summary() {
    local result="$1" total="$2" clean="$3"

    case $result in
        2)
            log_error "CRITICAL SECURITY THREATS DETECTED"
            log_error "Files with violations:"
            for file in "${affected_files[@]}"; do
                log_error "  - $file"
            done
            log_error ""
            show_immediate_actions
            log_error "COMMIT BLOCKED"
            ;;
        1)
            log_warning "POTENTIAL SECURITY THREATS DETECTED"
            log_warning "Files requiring review:"
            for file in "${affected_files[@]}"; do
                log_warning "  - $file"
            done
            log_warning ""
            show_corrective_actions
            log_warning "COMMIT ALLOWED - Please review"
            ;;
        0)
            log_success "No security threats detected"
            log_info "Files analyzed: $total, Clean: $clean"
            log_success "Ready to commit"
            ;;
    esac
}

show_immediate_actions() {
    log_fatal "IMMEDIATE ACTIONS REQUIRED:"
    log_fatal "1. Remove all secrets from source code"
    log_fatal "2. Use environment variables for sensitive data"
    log_fatal "3. Add secrets to .env files (ensure .env is in .gitignore)"
    log_fatal "4. Consider secret management tools"
    log_fatal "5. Rotate exposed credentials"
}

show_corrective_actions() {
    log_warning "RECOMMENDED ACTIONS:"
    log_warning "1. Review detected patterns for actual secrets"
    log_warning "2. Move real secrets to environment variables"
    log_warning "3. Update code to use secure credential management"
    log_warning "4. Consider team training on secure coding"
}

# Performance monitoring
setup_performance() {
    [ "${ENABLE_PERFORMANCE_TRACKING:-false}" = "true" ] && {
        script_start_time=$(date +%s)
        operations_count=0
    }
    VALIDATION_ERRORS=0
    VALIDATION_WARNINGS=0
}

show_performance() {
    if [ "${ENABLE_PERFORMANCE_TRACKING:-false}" = "true" ] && [ -n "$script_start_time" ]; then
        local end_time=$(date +%s)
        local duration=$((end_time - script_start_time))

        log_info "Performance: $operations_count operations in ${duration}s"

        # Simple average calculation without bc dependency
        if [ $operations_count -gt 0 ] && [ $duration -gt 0 ]; then
            local avg_seconds=$((duration / operations_count))
            if [ $avg_seconds -eq 0 ]; then
                log_info "  Average: <1s per operation"
            else
                log_info "  Average: ${avg_seconds}s per operation"
            fi
        fi
    fi
}

# Policy enforcement
apply_policy() {
    local level="$1"
    local base_code=$(threat_level_to_exit_code "$level")

    if [ "$level" = "IMMEDIATE" ]; then
        local immediate=$(git config --bool --default true secrets.enforceImmediate 2>/dev/null || echo "true")
        if [ "$immediate" = "false" ]; then
            log_warning "Enforcement disabled - commit allowed with warnings"
            echo "1"
            return
        fi
    fi

    echo "$base_code"
}

# CLI interface
show_help() {
    log_info "validate-secrets-enhanced.sh - Security Threat Detection"
    log_info ""
    log_info "USAGE:"
    log_info "  $0              # Analyze staged files"
    log_info "  $0 --config     # Show configuration"
    log_info "  $0 --help       # Show this help"
    log_info ""
    log_info "ENFORCEMENT LEVELS:"
    log_info "  IMMEDIATE:   Critical secrets - blocks commits"
    log_info "  CORRECTIVE:  Suspicious patterns - warns"
    log_info "  ADVISORY:    Documentation references"
    log_info ""
    log_info "CONFIGURATION:"
    log_info "  git config secrets.enforceImmediate true|false"
    log_info "  git config secrets.trackCorrective true|false"
}

show_config() {
    log_section "CONFIGURATION"

    local immediate=$(git config --bool --default true secrets.enforceImmediate 2>/dev/null || echo "true")
    local corrective=$(git config --bool --default true secrets.trackCorrective 2>/dev/null || echo "true")

    log_info "Current settings:"
    log_info "  IMMEDIATE enforcement: $immediate"
    log_info "  CORRECTIVE tracking: $corrective"
    log_info ""

    if [ -f "infrastructure/utils/logging-functions.sh" ]; then
        log_success "Logging integration: ACTIVE"
        log_info "  Environment: ${CURRENT_ENVIRONMENT:-DEVELOPMENT}"
        log_info "  Context: ${CURRENT_CONTEXT:-HOOK}"
    else
        log_error "Logging integration: MISSING"
    fi

    log_info ""
    log_info "Commands:"
    log_info "  git config secrets.enforceImmediate true|false"
    log_info "  git config secrets.trackCorrective true|false"
    log_info "  git config --unset secrets.enforceImmediate  # Reset"
}

# Main function
main() {
    setup_performance

    case "${1:-}" in
        "--help"|"-h") show_help; return 0 ;;
        "--config") show_config; return 0 ;;
        "--version"|"-v")
            log_info "validate-secrets-enhanced.sh v3.1"
            log_info "Enhanced security threat detection for git hooks"
            return 0
            ;;
        "--status")
            log_info "Status: Errors: ${VALIDATION_ERRORS:-0}, Warnings: ${VALIDATION_WARNINGS:-0}"
            return 0
            ;;
    esac

    # Validate git context
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_error "Not in a git repository"
        return 1
    fi

    # Load configuration and execute analysis
    load_configuration
    analyze_staged_files
    local result=$?

    # Show summary and apply policy
    log_info ""
    show_validation_summary
    show_performance

    local final_code
    case $result in
        2) final_code=$(apply_policy "IMMEDIATE") ;;
        1) final_code=$(apply_policy "CORRECTIVE") ;;
        *) final_code=0 ;;
    esac

    return "$final_code"
}

# Execute only if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi