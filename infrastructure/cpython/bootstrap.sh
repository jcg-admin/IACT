#!/bin/bash
#
# bootstrap.sh - CPython Builder VM Provisioning
#
# Reference: SPEC_INFRA_001
# Purpose: Provision VM with CPython build dependencies
#
# Usage:
#   sudo ./bootstrap.sh
#

set -euo pipefail

# =============================================================================
# LOAD UTILITIES
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-/vagrant}"

# Source new modular utils
source "$SCRIPT_DIR/utils/logger.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/logger.sh"
source "$SCRIPT_DIR/utils/validator.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/validator.sh"
source "$SCRIPT_DIR/utils/filesystem.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/filesystem.sh"
source "$SCRIPT_DIR/utils/retry_handler.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/retry_handler.sh"
source "$SCRIPT_DIR/utils/state_manager.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/state_manager.sh"

# Initialize state management
export BUILD_STATE_DIR="$PROJECT_ROOT/.build_state"
initialize_state_directory

# =============================================================================
# FUNCTIONS
# =============================================================================

update_system() {
    log_step 1 6 "Updating system"

    # Skip if already completed
    if is_operation_complete "bootstrap_update_system"; then
        log_info "System update already completed, skipping"
        return 0
    fi

    log_info "Updating package lists..."
    if ! execute_with_retry 3 "apt-get update" apt-get update -qq; then
        log_error "Failed to update package lists"
        return 1
    fi

    log_info "Upgrading system packages..."
    if ! execute_with_retry 3 "apt-get upgrade" env DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq; then
        log_error "Failed to upgrade system packages"
        return 1
    fi

    mark_operation_complete "bootstrap_update_system"
    log_info "System updated successfully"
}

install_build_dependencies() {
    log_step 2 6 "Installing CPython build dependencies"

    # Skip if already completed
    if is_operation_complete "bootstrap_install_build_deps"; then
        log_info "Build dependencies already installed, skipping"
        return 0
    fi

    log_info "Installing build toolchain..."

    # Dependencies from: https://devguide.python.org/getting-started/setup-building/
    local packages=(
        build-essential
        gdb
        lcov
        pkg-config
        libbz2-dev
        libffi-dev
        libgdbm-dev
        libgdbm-compat-dev
        liblzma-dev
        libncurses5-dev
        libreadline6-dev
        libsqlite3-dev
        libssl-dev
        lzma
        lzma-dev
        tk-dev
        uuid-dev
        zlib1g-dev
        wget
        curl
        ca-certificates
    )

    # Install with retry logic
    if ! execute_with_retry 3 "Install build dependencies" \
        env DEBIAN_FRONTEND=noninteractive apt-get install -y -q "${packages[@]}"; then
        log_error "Failed to install build dependencies"
        log_error "Check network connectivity and APT repositories"
        return 1
    fi

    log_info "Build dependencies installed successfully"

    # Display critical library versions
    log_info "Critical library versions:"
    dpkg -l | grep -E "libssl-dev|libsqlite3-dev|liblzma-dev|libbz2-dev|libffi-dev" | \
        awk '{print "  " $2 ": " $3}' || log_warning "Could not list library versions"

    mark_operation_complete "bootstrap_install_build_deps"
}

install_additional_tools() {
    log_step 3 6 "Installing additional tools"

    # Skip if already completed
    if is_operation_complete "bootstrap_install_tools"; then
        log_info "Additional tools already installed, skipping"
        return 0
    fi

    log_info "Installing git, vim, htop..."
    if ! execute_with_retry 3 "Install additional tools" \
        env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git vim htop; then
        log_error "Failed to install additional tools"
        return 1
    fi

    mark_operation_complete "bootstrap_install_tools"
    log_info "Additional tools installed successfully"
}

verify_installation() {
    log_step 4 6 "Verifying installation"

    # Verify GCC
    if ! validate_command_exists "gcc"; then
        log_error "GCC not found"
        return 1
    fi
    local gcc_version
    gcc_version=$(gcc --version | head -1)
    log_info "GCC available: $gcc_version"

    # Verify make
    if ! validate_command_exists "make"; then
        log_error "Make not found"
        return 1
    fi
    local make_version
    make_version=$(make --version | head -1)
    log_info "Make available: $make_version"

    # Verify critical libraries
    local critical_libs=(
        "libssl-dev"
        "libsqlite3-dev"
        "liblzma-dev"
        "libbz2-dev"
        "libffi-dev"
    )

    log_info "Verifying critical libraries:"
    for lib in "${critical_libs[@]}"; do
        if dpkg -l "$lib" 2>/dev/null | grep -q "^ii"; then
            log_info "  $lib: installed"
        else
            log_error "  $lib: NOT installed"
            return 1
        fi
    done

    log_info "Installation verification completed"
}

setup_directories() {
    log_step 5 6 "Setting up directories"

    # Create logs directory
    if ! ensure_directory_exists "$PROJECT_ROOT/logs" "755"; then
        log_error "Failed to create logs directory"
        return 1
    fi

    # Create artifacts directory
    if ! ensure_directory_exists "$PROJECT_ROOT/artifacts/cpython" "755"; then
        log_error "Failed to create artifacts directory"
        return 1
    fi

    # Verify directories are writable
    if ! validate_directory_writable "$PROJECT_ROOT/logs"; then
        log_error "Logs directory is not writable"
        return 1
    fi

    if ! validate_directory_writable "$PROJECT_ROOT/artifacts/cpython"; then
        log_error "Artifacts directory is not writable"
        return 1
    fi

    log_info "Directories configured and verified"
}

setup_convenience_symlinks() {
    log_step 6 6 "Setting up convenience symlinks"

    # Symlink: install.sh → scripts/install_prebuilt_cpython.sh
    if [[ -f "$PROJECT_ROOT/scripts/install_prebuilt_cpython.sh" ]]; then
        ln -sf scripts/install_prebuilt_cpython.sh "$PROJECT_ROOT/install.sh"
        log_info "Created symlink: install.sh → scripts/install_prebuilt_cpython.sh"
    else
        log_warning "install_prebuilt_cpython.sh not found, skipping symlink creation"
    fi

    # Future symlinks can be added here
    # Example: ln -sf scripts/build_cpython.sh "$PROJECT_ROOT/build.sh"

    log_info "Convenience symlinks configured"
}

auto_build_python() {
    local auto_build="${AUTO_BUILD:-false}"
    local python_version="${PYTHON_VERSION:-}"
    local build_number="${BUILD_NUMBER:-1}"

    if [[ "$auto_build" != "true" ]]; then
        log_info "Auto-build disabled"
        return 0
    fi

    if [[ -z "$python_version" ]]; then
        log_warning "AUTO_BUILD enabled but PYTHON_VERSION not set"
        return 0
    fi

    log_separator 73
    log_info "Auto-build enabled: Python $python_version"
    log_separator 73
    echo ""

    local artifact_name="cpython-${python_version}-ubuntu20.04-build${build_number}.tgz"

    # Check if already built
    if [[ -f "$PROJECT_ROOT/artifacts/cpython/$artifact_name" ]]; then
        log_info "Artifact already exists: $artifact_name"
        log_info "To rebuild, delete the artifact or use a different build number"
        return 0
    fi

    log_info "Building Python $python_version (this will take 10-15 minutes)..."
    echo ""

    if bash "$PROJECT_ROOT/scripts/build_cpython.sh" "$python_version" "$build_number"; then
        echo ""
        log_separator 73
        log_info "Python $python_version built successfully"
        log_separator 73
        echo ""

        if [[ -f "$PROJECT_ROOT/artifacts/cpython/$artifact_name" ]]; then
            log_info "Artifact: $artifact_name"

            # Auto-validate
            log_info "Validating artifact..."
            if bash "$PROJECT_ROOT/scripts/validate_build.sh" "$artifact_name" >/dev/null 2>&1; then
                log_info "Artifact validated successfully"
            else
                log_warning "Artifact validation failed"
            fi
        fi
    else
        echo ""
        log_error "Auto-build failed"
        log_info "You can build manually: ./scripts/build_cpython.sh $python_version"
        # Don't exit - VM is still usable
    fi

    echo ""
}

display_summary() {
    echo ""
    log_separator 73
    echo "  CPython Builder - Bootstrap Completed"
    log_separator 73
    echo ""
    echo "Build environment ready:"
    echo ""
    echo "  Toolchain:"
    gcc --version | head -1 | sed 's/^/    /'
    make --version | head -1 | sed 's/^/    /'
    echo ""
    echo "  Available scripts:"
    echo "    ./scripts/build_cpython.sh <version> [build-number]"
    echo "    ./scripts/validate_build.sh <artifact-name>"
    echo "    ./scripts/cleanup.sh [--all] [--state]"
    echo ""
    if [[ -L "$PROJECT_ROOT/install.sh" ]]; then
        echo "  Convenience symlinks:"
        echo "    ./install.sh → $(readlink "$PROJECT_ROOT/install.sh")"
        echo ""
    fi
    echo "  Usage example:"
    echo "    ./scripts/build_cpython.sh 3.12.6"
    echo ""
    echo "  Artifacts will be generated in:"
    echo "    $PROJECT_ROOT/artifacts/cpython/"
    echo ""
    log_separator 73
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    log_header "CPython Builder - Starting Bootstrap" 73

    # Check if bootstrap is already complete
    if is_operation_complete "bootstrap_complete"; then
        log_info "Bootstrap already completed"
        log_info "To force re-bootstrap, run:"
        log_info "  source utils/state_manager.sh"
        log_info "  reset_operation_state bootstrap_complete"
        log_info "  sudo ./bootstrap.sh"
        echo ""
        display_summary

        # Check if should auto-build even if bootstrap already done
        auto_build_python
        return 0
    fi

    echo ""

    # Execute bootstrap steps
    update_system || return 1
    install_build_dependencies || return 1
    install_additional_tools || return 1
    verify_installation || return 1
    setup_directories || return 1
    setup_convenience_symlinks || return 1

    # Mark bootstrap as complete
    mark_operation_complete "bootstrap_complete" "timestamp=$(date +%s)"

    # Display summary
    display_summary

    log_info "Bootstrap completed successfully"
    log_separator 73

    # Auto-build if enabled
    auto_build_python
}

# Execute main
main "$@"