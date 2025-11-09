#!/bin/bash
#
# infrastructure/cpython/scripts/build_wrapper.sh - Wrapper for building in Vagrant
#
# Reference: SPEC_INFRA_001
# Purpose: Facilitate building from outside Vagrant (host → VM)
#
# Usage:
#   ./infrastructure/cpython/scripts/build_wrapper.sh <version> [build-number]
#
# Examples:
#   ./infrastructure/cpython/scripts/build_wrapper.sh 3.12.6
#   ./infrastructure/cpython/scripts/build_wrapper.sh 3.12.6 2
#

set -euo pipefail

# =============================================================================
# LOAD UTILITIES (with fallback for host environment)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Try to load environment system (may not exist on host)
if [[ -f "$SCRIPT_DIR/../utils/environment.sh" ]]; then
    source "$SCRIPT_DIR/../utils/environment.sh"
elif [[ -f "$PROJECT_ROOT/infrastructure/cpython/utils/environment.sh" ]]; then
    source "$PROJECT_ROOT/infrastructure/cpython/utils/environment.sh"
else
    # Fallback: simple logging without colors (host environment)
    log_info() { echo "[INFO] $*"; }
    log_warning() { echo "[WARNING] $*"; }
    log_error() { echo "[ERROR] $*" >&2; }
    log_header() {
        local msg="$1"
        local width="${2:-60}"
        printf '%*s\n' "$width" '' | tr ' ' '='
        echo "  $msg"
        printf '%*s\n' "$width" '' | tr ' ' '='
    }
    log_separator() {
        local width="${1:-60}"
        printf '%*s\n' "$width" '' | tr ' ' '-'
    }
fi

# =============================================================================
# ARGUMENT PARSING
# =============================================================================

# Validate arguments
if (( $# < 1 )); then
    log_error "Usage: $0 <version> [build-number]"
    log_error "Example: $0 3.12.6 1"
    exit 1
fi

PYTHON_VERSION="$1"
BUILD_NUMBER="${2:-1}"

# Detect Vagrant directory
VAGRANT_DIR="$PROJECT_ROOT/infrastructure/cpython"

# Verify Vagrant directory exists
if [[ ! -d "$VAGRANT_DIR" ]]; then
    log_error "Vagrant directory not found: $VAGRANT_DIR"
    exit 1
fi

# =============================================================================
# DISPLAY BUILD INFO
# =============================================================================

log_header "CPython Build Wrapper" 60
log_info "Version: $PYTHON_VERSION"
log_info "Build number: $BUILD_NUMBER"
log_info "Vagrant dir: $VAGRANT_DIR"
echo ""

# =============================================================================
# VERIFY VAGRANT
# =============================================================================

# Check Vagrant is installed
if ! command -v vagrant &> /dev/null; then
    log_error "Vagrant is not installed"
    log_error "Install: https://www.vagrantup.com/downloads"
    exit 1
fi

# =============================================================================
# CHECK VM STATUS
# =============================================================================

log_info "Checking VM status..."
cd "$VAGRANT_DIR"

VM_STATUS=$(vagrant status --machine-readable 2>/dev/null | grep "state," | cut -d, -f4 || echo "unknown")

if [[ "$VM_STATUS" != "running" ]]; then
    log_info "VM is not running. Starting..."
    if ! vagrant up; then
        log_error "Failed to start VM"
        exit 1
    fi
fi

log_info "VM is running"
echo ""

# =============================================================================
# EXECUTE BUILD IN VM
# =============================================================================

log_info "Executing build in VM..."
log_separator 60
echo ""

# Execute build command in VM
vagrant ssh -c "cd /vagrant && ./scripts/build_cpython.sh $PYTHON_VERSION $BUILD_NUMBER"

EXIT_CODE=$?

# =============================================================================
# DISPLAY RESULTS
# =============================================================================

echo ""
log_separator 60

if (( EXIT_CODE == 0 )); then
    log_header "Build completed successfully" 60
    log_info "Artifact generated in: $PROJECT_ROOT/infrastructure/cpython/artifacts/"
    echo ""
    log_info "Next step:"
    log_info "  ./infrastructure/cpython/scripts/validate_wrapper.sh cpython-${PYTHON_VERSION}-ubuntu20.04-build${BUILD_NUMBER}.tgz"
    log_separator 60
else
    log_error "Build failed with exit code: $EXIT_CODE"
    echo ""
    log_info "For debugging, connect to VM:"
    log_info "  cd $VAGRANT_DIR"
    log_info "  vagrant ssh"
    exit $EXIT_CODE
fi