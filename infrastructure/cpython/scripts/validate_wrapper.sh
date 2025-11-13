#!/bin/bash
#
# infraestructura/cpython/scripts/validate_wrapper.sh - Wrapper for validation in Vagrant
#
# Reference: SPEC_INFRA_001
# Purpose: Facilitate validation from outside Vagrant (host → VM)
#
# Usage:
#   ./infraestructura/cpython/scripts/validate_wrapper.sh <artifact-name>
#
# Example:
#   ./infraestructura/cpython/scripts/validate_wrapper.sh cpython-3.12.6-ubuntu20.04-build1.tgz
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
    log_error "Usage: $0 <artifact-name>"
    log_error "Example: $0 cpython-3.12.6-ubuntu20.04-build1.tgz"
    exit 1
fi

ARTIFACT_NAME="$1"

# Detect paths
VAGRANT_DIR="$PROJECT_ROOT/infrastructure/cpython"
ARTIFACT_PATH="$PROJECT_ROOT/infrastructure/cpython/artifacts/cpython/$ARTIFACT_NAME"

# =============================================================================
# VERIFY ARTIFACT
# =============================================================================

# Check artifact exists
if [[ ! -f "$ARTIFACT_PATH" ]]; then
    log_error "Artifact not found: $ARTIFACT_PATH"
    exit 1
fi

# Verify Vagrant directory exists
if [[ ! -d "$VAGRANT_DIR" ]]; then
    log_error "Vagrant directory not found: $VAGRANT_DIR"
    exit 1
fi

# =============================================================================
# DISPLAY VALIDATION INFO
# =============================================================================

log_header "CPython Artifact Validation Wrapper" 60
log_info "Artifact: $ARTIFACT_NAME"
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
# EXECUTE VALIDATION IN VM
# =============================================================================

log_info "Executing validation in VM..."
log_separator 60
echo ""

# Execute validation command in VM
vagrant ssh -c "cd /vagrant && ./scripts/validate_build.sh $ARTIFACT_NAME"

EXIT_CODE=$?

# =============================================================================
# DISPLAY RESULTS
# =============================================================================

echo ""
log_separator 60

if (( EXIT_CODE == 0 )); then
    log_header "Validation completed successfully" 60
    log_info "The artifact is valid and ready for distribution"
    log_separator 60
else
    log_error "Validation failed with exit code: $EXIT_CODE"
    echo ""
    log_info "For debugging, connect to VM:"
    log_info "  cd $VAGRANT_DIR"
    log_info "  vagrant ssh"
    exit $EXIT_CODE
fi