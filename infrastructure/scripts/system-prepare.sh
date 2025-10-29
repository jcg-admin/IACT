#!/bin/bash

set -euo pipefail

# =================================================================
# SCRIPT CONFIGURATION
# =================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Detect Vagrant environment
if [ -d "/vagrant" ]; then
    PROJECT_ROOT="/vagrant"
fi

# =================================================================
# LOAD DEPENDENCIES
# =================================================================

# Source required libraries
if [ -f "$PROJECT_ROOT/utils/logging.sh" ]; then
    source "$PROJECT_ROOT/utils/logging.sh"
else
    echo "ERROR: Cannot find logging.sh at $PROJECT_ROOT/utils/logging.sh"
    exit 1
fi

if [ -f "$PROJECT_ROOT/utils/common.sh" ]; then
    source "$PROJECT_ROOT/utils/common.sh"
else
    log_error "Cannot find common.sh at $PROJECT_ROOT/utils/common.sh"
    exit 1
fi

# =================================================================
# SYSTEM PREPARATION FUNCTIONS
# =================================================================

prepare_essential_packages() {
    log_header "Essential Packages Installation"

    local packages=(
        "software-properties-common"
        "curl"
        "wget"
        "gnupg2"
        "ca-certificates"
        "lsb-release"
        "apt-transport-https"
    )

    # Use centralized function instead of manual installation
    if ! install_packages "${packages[@]}"; then
        log_error "Failed to install essential packages"
        return 1
    fi

    return 0
}

verify_system_requirements() {
    log_header "System Requirements Verification"

    # Use centralized function instead of manual checks
    if ! check_ubuntu_bionic; then
        return 1
    fi

    # Check essential commands are available
    local commands=("curl" "wget" "apt-get")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            log_error "Required command not found: $cmd"
            return 1
        fi
    done
    log_success "Essential commands available"

    # Use centralized function instead of manual ping
    if ! check_internet_connectivity; then
        return 1
    fi

    return 0
}

# =================================================================
# MAIN EXECUTION
# =================================================================

main() {
    log_header "System Preparation - Ubuntu 18.04"

    # Use centralized environment validation instead of manual checks
    if ! validate_environment; then
        log_error "Environment validation failed"
        exit 1
    fi

    # Update package cache using centralized function
    if ! update_package_cache; then
        log_error "Package cache update failed"
        exit 1
    fi

    # Install essential packages
    if ! prepare_essential_packages; then
        log_error "Essential packages installation failed"
        exit 1
    fi

    # Verify system requirements
    if ! verify_system_requirements; then
        log_error "System requirements verification failed"
        exit 1
    fi

    log_success "System preparation completed successfully"
    log_info "Next step: MariaDB installation"
    return 0
}

# Execute main function
main "$@"