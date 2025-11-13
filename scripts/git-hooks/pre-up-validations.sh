#!/bin/bash

# ============================================================================
# Pre-Up Validations Hook - Master Runner
# Orchestrates all validation modules for deployment readiness
# Academic Reference: IEEE Software 1995 Kruchten 4+1 Model
# ============================================================================

set -euo pipefail

# Source centralized logging functions
if [ -f "infrastructure/utils/logging-functions.sh" ]; then
    source infrastructure/utils/logging-functions.sh
else
    echo "[ERROR] Missing infrastructure/utils/logging-functions.sh"
    echo "ACTION REQUIRED: Run T006-MINI logging setup first"
    exit 1
fi

log_section "PlantUML 4+1 Architecture Stack - Pre-Up Validations"
log_info "Academic Reference: IEEE Software 1995 Kruchten 4+1 Model"
log_info "Validating system requirements for dual-machine deployment"

# Validation modules to execute
VALIDATION_MODULES=(
    "infrastructure/hooks/validate-hardware-requirements.sh"
    "infrastructure/hooks/validate-software-dependencies.sh"
    "infrastructure/hooks/validate-network-configuration.sh"
    "infrastructure/hooks/validate-environment-files.sh"
)

# Results tracking
TOTAL_VALIDATIONS=0
PASSED_VALIDATIONS=0
FAILED_VALIDATIONS=0
VALIDATION_START_TIME=$(date +%s)

# Execute each validation module
for module in "${VALIDATION_MODULES[@]}"; do
    if [ -x "$module" ]; then
        log_info "Executing validation: $(basename "$module")"
        
        TOTAL_VALIDATIONS=$((TOTAL_VALIDATIONS + 1))
        MODULE_START=$(date +%s)
        
        if ./"$module"; then
            MODULE_END=$(date +%s)
            MODULE_DURATION=$((MODULE_END - MODULE_START))
            log_success "Validation PASSED: $(basename "$module") (${MODULE_DURATION}s)"
            PASSED_VALIDATIONS=$((PASSED_VALIDATIONS + 1))
        else
            MODULE_END=$(date +%s)
            MODULE_DURATION=$((MODULE_END - MODULE_START))
            log_error "Validation FAILED: $(basename "$module") (${MODULE_DURATION}s)"
            FAILED_VALIDATIONS=$((FAILED_VALIDATIONS + 1))
        fi
        echo
    else
        log_error "Validation module not executable: $module"
        TOTAL_VALIDATIONS=$((TOTAL_VALIDATIONS + 1))
        FAILED_VALIDATIONS=$((FAILED_VALIDATIONS + 1))
    fi
done

# Calculate total validation time
VALIDATION_END_TIME=$(date +%s)
TOTAL_DURATION=$((VALIDATION_END_TIME - VALIDATION_START_TIME))

# Final summary
log_section "VALIDATION SUMMARY"
log_info "Total validations: $TOTAL_VALIDATIONS"
log_info "Passed: $PASSED_VALIDATIONS"
log_info "Failed: $FAILED_VALIDATIONS"
log_info "Total validation time: ${TOTAL_DURATION} seconds"

# Performance assessment
if [ $TOTAL_DURATION -le 30 ]; then
    log_success "Validation performance: EXCELLENT (≤30s target met)"
elif [ $TOTAL_DURATION -le 45 ]; then
    log_success "Validation performance: GOOD (≤45s acceptable)"
else
    log_warning "Validation performance: SLOW (>45s - may indicate system issues)"
fi

# Final result
if [ $FAILED_VALIDATIONS -eq 0 ]; then
    log_success "OVERALL RESULT: PRE-UP VALIDATION PASSED"
    log_success "STATUS: System ready for 'vagrant up'"
    log_info ""
    log_info "DEPLOYMENT READINESS CONFIRMED:"
    log_info "  Hardware: Adequate resources for nginx01 + tomcat01"
    log_info "  Software: Required tools installed and compatible"
    log_info "  Network: Ports available and connectivity confirmed"
    log_info "  Environment: Project files and configuration ready"
    log_info ""
    log_info "NEXT STEP: Run 'vagrant up' to deploy PlantUML infrastructure"
    log_info "ESTIMATED DEPLOYMENT TIME: 5-10 minutes for complete setup"
    exit 0
else
    log_error "OVERALL RESULT: PRE-UP VALIDATION FAILED"
    log_error "VALIDATION FAILURES: $FAILED_VALIDATIONS out of $TOTAL_VALIDATIONS failed"
    log_info ""
    log_info "REMEDIATION REQUIRED:"
    echo "COMMON SOLUTIONS:"
    echo "* Install/update Vagrant: https://www.vagrantup.com/downloads"
    echo "* Install/update VirtualBox: https://www.virtualbox.org/wiki/Downloads"
    echo "* Enable VT-x/AMD-V in BIOS settings"
    echo "* Free up disk space (need 6GB+ available)"
    echo "* Close applications using ports 8080, 8081"
    echo "* Create .env file with required configuration"
    echo ""
    echo "ACTION: Fix failed validations and re-run this script"
    echo "COMMAND: ./infrastructure/hooks/pre-up-validations.sh"
    exit 1
fi
