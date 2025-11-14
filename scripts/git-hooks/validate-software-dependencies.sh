#!/bin/bash

# ============================================================================
# Software Dependencies Validation Hook
# Validates required software for VM deployment
# Single responsibility: Software installation and version validation only
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

log_section "REQUIRED SOFTWARE VALIDATION"

# Minimum software versions
MIN_VAGRANT_VERSION="2.2.19"
MIN_VBOX_VERSION="6.1.0"

# Version comparison function
version_compare() {
    local version1=$1
    local version2=$2
    local op=$3
    
    # Convert versions to comparable format
    local ver1=$(echo "$version1" | sed 's/[^0-9.]//g')
    local ver2=$(echo "$version2" | sed 's/[^0-9.]//g')
    
    case $op in
        ">=")
            [ "$(printf '%s\n' "$ver2" "$ver1" | sort -V | head -n1)" = "$ver2" ]
            ;;
    esac
}

# Vagrant validation
log_info "Checking Vagrant installation..."
if command -v vagrant >/dev/null 2>&1; then
    VAGRANT_VERSION=$(vagrant --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if version_compare "$VAGRANT_VERSION" "$MIN_VAGRANT_VERSION" ">="; then
        log_success "Vagrant: $VAGRANT_VERSION (minimum $MIN_VAGRANT_VERSION required)"
    else
        log_error "Vagrant: $VAGRANT_VERSION (minimum $MIN_VAGRANT_VERSION required)"
        log_error "Please update Vagrant: https://www.vagrantup.com/downloads"
    fi
else
    log_error "Vagrant: Not installed"
    log_error "Please install Vagrant: https://www.vagrantup.com/downloads"
fi

# VirtualBox validation with enhanced Windows detection
log_info "Checking VirtualBox installation..."
VBOX_CMD=""
VBOX_VERSION=""

# Try different VirtualBox command variations (cross-platform)
if command -v vboxmanage >/dev/null 2>&1; then
    VBOX_CMD="vboxmanage"
elif command -v VBoxManage >/dev/null 2>&1; then
    VBOX_CMD="VBoxManage"
elif command -v VBoxManage.exe >/dev/null 2>&1; then
    VBOX_CMD="VBoxManage.exe"
elif [ -f "/c/Program Files/Oracle/VirtualBox/VBoxManage.exe" ]; then
    VBOX_CMD="/c/Program Files/Oracle/VirtualBox/VBoxManage.exe"
elif [ -f "/mnt/c/Program Files/Oracle/VirtualBox/VBoxManage.exe" ]; then
    VBOX_CMD="/mnt/c/Program Files/Oracle/VirtualBox/VBoxManage.exe"
fi

if [ -n "$VBOX_CMD" ]; then
    VBOX_VERSION=$("$VBOX_CMD" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [ -n "$VBOX_VERSION" ] && version_compare "$VBOX_VERSION" "$MIN_VBOX_VERSION" ">="; then
        log_success "VirtualBox: $VBOX_VERSION (minimum $MIN_VBOX_VERSION required)"
    elif [ -n "$VBOX_VERSION" ]; then
        log_error "VirtualBox: $VBOX_VERSION (minimum $MIN_VBOX_VERSION required)"
        log_error "Please update VirtualBox: https://www.virtualbox.org/wiki/Downloads"
    else
        log_warning "VirtualBox: Found but version detection failed"
        log_warning "Command: $VBOX_CMD"
    fi
    
    # Check VirtualBox functionality
    log_info "Testing VirtualBox functionality..."
    if "$VBOX_CMD" list hostinfo >/dev/null 2>&1; then
        log_success "VirtualBox service is functional"
    else
        log_warning "VirtualBox service may not be responding properly"
    fi
    
    # Check VirtualBox kernel modules (Linux only)
    if [ "$(uname)" = "Linux" ]; then
        if lsmod | grep -q vboxdrv; then
            log_success "VirtualBox kernel modules: Loaded"
        else
            log_warning "VirtualBox kernel modules: Not loaded"
            log_warning "Run: sudo /sbin/vboxconfig"
        fi
    fi
else
    log_error "VirtualBox: Not found in PATH or standard locations"
    log_error "Please install VirtualBox: https://www.virtualbox.org/wiki/Downloads"
    log_error "Or add VirtualBox to your PATH environment variable"
fi

# Git validation
log_info "Checking Git installation..."
if command -v git >/dev/null 2>&1; then
    GIT_VERSION=$(git --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    log_success "Git: $GIT_VERSION"
    
    # Test Git functionality in repository context
    if git rev-parse --git-dir >/dev/null 2>&1; then
        log_success "Git repository functionality confirmed"
    else
        log_info "Git functional but not in repository context"
    fi
else
    log_warning "Git: Not installed (recommended for development)"
fi

# Check for recommended Vagrant plugins
log_info "Checking recommended Vagrant plugins..."
if command -v vagrant >/dev/null 2>&1 && vagrant plugin list >/dev/null 2>&1; then
    VAGRANT_PLUGINS=$(vagrant plugin list)
    
    if echo "$VAGRANT_PLUGINS" | grep -q "vagrant-vbguest"; then
        log_success "vagrant-vbguest plugin detected (recommended)"
    else
        log_info "vagrant-vbguest plugin not found (recommended: vagrant plugin install vagrant-vbguest)"
    fi
    
    if echo "$VAGRANT_PLUGINS" | grep -q "vagrant-hostmanager"; then
        log_success "vagrant-hostmanager plugin detected (useful)"
    else
        log_info "vagrant-hostmanager plugin not found (optional: vagrant plugin install vagrant-hostmanager)"
    fi
else
    log_info "Cannot check Vagrant plugins"
fi

# Summary
show_validation_summary

if [ $VALIDATION_ERRORS -eq 0 ]; then
    log_success "Required software validation completed successfully"
    exit 0
else
    log_error "Required software validation failed"
    log_error "Please install or update required software"
    exit 1
fi
