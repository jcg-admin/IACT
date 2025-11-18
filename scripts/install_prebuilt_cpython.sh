#!/usr/bin/env bash

set -euo pipefail

# =============================================================================
# Configuration Defaults
# =============================================================================

PYTHON_VERSION_DEFAULT="3.12.6"
UBUNTU_RELEASE_DEFAULT="ubuntu20.04"
BUILD_ID_DEFAULT="build1"
ARTIFACT_BASE_URL_DEFAULT="https://github.com/2-Coatl/IACT---project/releases/download/cpython-3.12.6-build1"
ARTIFACT_NAME_DEFAULT="cpython-3.12.6-ubuntu20.04-build1.tgz"
TMP_ARTIFACT_DEFAULT="/tmp/cpython.tgz"
INSTALL_PREFIX_DEFAULT="/opt/python-3.12.6"

# Allow overrides through environment variables
PYTHON_VERSION="${PYTHON_VERSION:-$PYTHON_VERSION_DEFAULT}"
UBUNTU_RELEASE="${UBUNTU_RELEASE:-$UBUNTU_RELEASE_DEFAULT}"
BUILD_ID="${BUILD_ID:-$BUILD_ID_DEFAULT}"
ARTIFACT_BASE_URL="${ARTIFACT_BASE_URL:-$ARTIFACT_BASE_URL_DEFAULT}"
ARTIFACT_NAME="${ARTIFACT_NAME:-cpython-${PYTHON_VERSION}-${UBUNTU_RELEASE}-${BUILD_ID}.tgz}"
ARTIFACT_URL="${ARTIFACT_URL:-$ARTIFACT_BASE_URL/$ARTIFACT_NAME}"
TMP_ARTIFACT="${TMP_ARTIFACT:-$TMP_ARTIFACT_DEFAULT}"
INSTALL_PREFIX="${INSTALL_PREFIX:-/opt/python-${PYTHON_VERSION}}"

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/utils/logging.sh"

log_prefixed_info() {
    log_info "[install_prebuilt_cpython] $*"
}

log_prefixed_error() {
    log_error "[install_prebuilt_cpython] $*"
}

cleanup_tmp() {
    if [[ -f "$TMP_ARTIFACT" ]]; then
        rm -f "$TMP_ARTIFACT"
    fi
}

trap cleanup_tmp EXIT

require_command() {
    local cmd=$1
    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_prefixed_error "Required command not found: $cmd"
        exit 1
    fi
}

usage() {
    cat <<USAGE
Usage: ./install_prebuilt_cpython.sh

Downloads the prebuilt CPython artifact (cpython-3.12.6-ubuntu20.04-build1.tgz) and installs it under /opt/python-3.12.6.
Override defaults with environment variables:
  PYTHON_VERSION, UBUNTU_RELEASE, BUILD_ID, ARTIFACT_BASE_URL,
  ARTIFACT_NAME, ARTIFACT_URL, TMP_ARTIFACT, INSTALL_PREFIX.
USAGE
}

if [[ "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

log_prefixed_info "Preparing to install CPython ${PYTHON_VERSION} (${UBUNTU_RELEASE}, ${BUILD_ID})"
log_prefixed_info "Artifact URL: ${ARTIFACT_URL}"

require_command wget
require_command tar
require_command sudo

log_prefixed_info "Downloading artifact to ${TMP_ARTIFACT}"
wget --quiet "$ARTIFACT_URL" -O "$TMP_ARTIFACT"

log_prefixed_info "Creating installation directory ${INSTALL_PREFIX}"
sudo mkdir -p "$INSTALL_PREFIX"

log_prefixed_info "Extracting archive into ${INSTALL_PREFIX}"
sudo tar -xzf "$TMP_ARTIFACT" -C "$INSTALL_PREFIX" --strip-components=1

log_prefixed_info "Ensuring python binary is executable"
sudo chmod +x "$INSTALL_PREFIX/bin/python3"

installed_version=$("$INSTALL_PREFIX/bin/python3" --version)
log_prefixed_info "Installed Python version: ${installed_version}"

log_prefixed_info "Installation completed successfully"
