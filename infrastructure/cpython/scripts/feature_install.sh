#!/bin/bash
#
# feature_install.sh
# Installs precompiled CPython with PGO+LTO optimizations for Dev Container features
#
# Purpose: Install CPython prebuilt artifacts in containers/VMs
# References: SPEC_INFRA_001
#
# Usage:
#   VERSION=3.12.6 ./feature_install.sh
#   ARTIFACT_URL=https://... ./feature_install.sh
#

set -e

# ==============================================================================
# CONFIGURATION FROM ENVIRONMENT
# ==============================================================================
VERSION="${VERSION:-3.12.6}"
ARTIFACT_URL="${ARTIFACTURL:-}"
CHECKSUM_URL="${CHECKSUMURL:-}"
INSTALL_PREFIX="${INSTALLPREFIX:-/opt/python}"
SKIP_VALIDATION="${SKIPVALIDATION:-false}"

# ==============================================================================
# DERIVED VARIABLES
# ==============================================================================
PYTHON_DIR="${INSTALL_PREFIX}-${VERSION}"
MARKER_FILE="${PYTHON_DIR}/.installed"
TEMP_DIR="/tmp/cpython-install-$$"

# ==============================================================================
# LOAD UTILITIES (Fail Fast - requires full project structure)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment system with strict validation
load_environment() {
    local env_path="$SCRIPT_DIR/../utils/environment.sh"

    if [[ ! -f "$env_path" ]]; then
        echo "ERROR: This script requires the full project structure" >&2
        echo "ERROR: environment.sh not found at: $env_path" >&2
        echo "" >&2
        echo "This script must be run from within the project directory:" >&2
        echo "  Expected location: infrastructure/cpython/builder/feature/install.sh" >&2
        echo "  Requires: infrastructure/cpython/utils/environment.sh" >&2
        echo "" >&2
        return 1
    fi

    source "$env_path"
    return 0
}

# Load environment with error handling
if ! load_environment; then
    echo "CRITICAL: Cannot run without environment system" >&2
    echo "Make sure you're running from the correct project directory" >&2
    exit 1
fi

CONFIG_FILE="$SCRIPT_DIR/../config/versions.conf"
if [[ -f "$CONFIG_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
fi

DEFAULT_BUILD_NUMBER="${DEFAULT_BUILD_NUMBER:-1}"
DEFAULT_DISTRO="${DISTRO:-ubuntu20.04}"
RELEASES_BASE="${GITHUB_RELEASES_BASE:-https://github.com/2-Coatl/IACT---project/releases}"

RESOLVED_BUILD_NUMBER="${BUILDNUMBER:-$DEFAULT_BUILD_NUMBER}"
RESOLVED_DISTRO="${CPYTHON_DISTRO:-$DEFAULT_DISTRO}"

ARTIFACT_BASENAME="cpython-${VERSION}-${RESOLVED_DISTRO}-build${RESOLVED_BUILD_NUMBER}"
ARTIFACT_FILENAME="${ARTIFACT_BASENAME}.tgz"
LOCAL_ARTIFACT_DIR="${PROJECT_ROOT}/infrastructure/cpython/artifacts"
RELEASE_TAG="cpython-${VERSION}-build${RESOLVED_BUILD_NUMBER}"

# ==============================================================================
# FUNCTIONS
# ==============================================================================

is_remote_resource() {
    local candidate="$1"
    [[ "$candidate" =~ ^https?:// ]]
}

_strip_file_scheme() {
    local candidate="$1"
    if [[ "$candidate" == file://* ]]; then
        echo "${candidate#file://}"
    else
        echo "$candidate"
    fi
}

resolve_local_path() {
    local candidate
    candidate=$(_strip_file_scheme "$1")

    if [[ -z "$candidate" ]]; then
        echo ""
        return 0
    fi

    if [[ "$candidate" == /* ]]; then
        echo "$candidate"
    else
        echo "${PROJECT_ROOT}/${candidate#./}"
    fi
}

default_local_artifact_path() {
    local candidate="${LOCAL_ARTIFACT_DIR}/${ARTIFACT_FILENAME}"
    if [[ -f "$candidate" ]]; then
        echo "$candidate"
    fi
}

default_local_checksum_path() {
    local artifact_path="$1"
    if [[ -z "$artifact_path" ]]; then
        echo ""
        return 0
    fi

    local checksum_candidate="${artifact_path}.sha256"
    if [[ -f "$checksum_candidate" ]]; then
        echo "$checksum_candidate"
    fi
}

# Check if CPython is already installed (idempotent detection)
check_cpython_already_installed() {
    log_step "1" "8" "Checking if Python ${VERSION} is already installed"

    if [[ -f "${MARKER_FILE}" ]]; then
        log_info "Python ${VERSION} already installed at ${PYTHON_DIR}"
        log_info "Skipping installation (idempotent)"
        exit 0
    fi

    if [[ -d "${PYTHON_DIR}" ]]; then
        log_warning "Directory ${PYTHON_DIR} exists but no marker file found"
        log_info "Will proceed with installation"
    fi
}

# Determine CPython artifact URLs
determine_cpython_artifact_urls() {
    log_step "2" "8" "Determining artifact URLs"

    local resolved_artifact=""
    local resolved_checksum=""

    if [[ -n "${ARTIFACT_URL}" ]]; then
        if is_remote_resource "${ARTIFACT_URL}"; then
            resolved_artifact="${ARTIFACT_URL}"
            log_info "Using provided remote artifact URL: ${resolved_artifact}"
        else
            resolved_artifact="$(resolve_local_path "${ARTIFACT_URL}")"
            if [[ -z "$resolved_artifact" ]] || [[ ! -f "$resolved_artifact" ]]; then
                log_error "Local artifact not found: ${ARTIFACT_URL}"
                exit 1
            fi
            log_info "Using provided local artifact: ${resolved_artifact}"
        fi
    else
        resolved_artifact="$(default_local_artifact_path)"
        if [[ -n "$resolved_artifact" ]]; then
            log_info "Using local artifact from builder pipeline: ${resolved_artifact}"
        else
            resolved_artifact="${RELEASES_BASE%/}/download/${RELEASE_TAG}/${ARTIFACT_FILENAME}"
            log_info "Local artifact not found; falling back to GitHub Releases: ${resolved_artifact}"
        fi
    fi

    if [[ -n "${CHECKSUM_URL}" ]]; then
        if is_remote_resource "${CHECKSUM_URL}"; then
            resolved_checksum="${CHECKSUM_URL}"
            log_info "Using provided remote checksum URL: ${resolved_checksum}"
        else
            resolved_checksum="$(resolve_local_path "${CHECKSUM_URL}")"
            if [[ -z "$resolved_checksum" ]] || [[ ! -f "$resolved_checksum" ]]; then
                log_error "Local checksum not found: ${CHECKSUM_URL}"
                exit 1
            fi
            log_info "Using provided local checksum: ${resolved_checksum}"
        fi
    else
        if is_remote_resource "$resolved_artifact"; then
            resolved_checksum="${resolved_artifact}.sha256"
            log_info "Derived remote checksum URL: ${resolved_checksum}"
        else
            resolved_checksum="$(default_local_checksum_path "$resolved_artifact")"
            if [[ -z "$resolved_checksum" ]]; then
                log_error "Checksum file not found next to artifact: ${resolved_artifact}.sha256"
                exit 1
            fi
            log_info "Using checksum generated by builder: ${resolved_checksum}"
        fi
    fi

    ARTIFACT_URL="$resolved_artifact"
    CHECKSUM_URL="$resolved_checksum"
}

# Download CPython artifact and checksum
# download_file helper internally prefers curl and falls back to wget per SPEC_INFRA_001
download_cpython_artifact() {
    log_step "3" "8" "Downloading artifact and checksum"

    mkdir -p "${TEMP_DIR}"

    local artifact_file="${TEMP_DIR}/cpython-${VERSION}.tgz"
    local checksum_file="${TEMP_DIR}/cpython-${VERSION}.tgz.sha256"

    if is_remote_resource "${ARTIFACT_URL}"; then
        log_info "Downloading artifact..."
        if ! download_file "${ARTIFACT_URL}" "${artifact_file}"; then
            log_error "Failed to download artifact"
            cleanup_temp_directory "${TEMP_DIR}"
            exit 1
        fi
    else
        log_info "Copying local artifact..."
        if ! cp "${ARTIFACT_URL}" "${artifact_file}"; then
            log_error "Failed to copy local artifact from ${ARTIFACT_URL}"
            cleanup_temp_directory "${TEMP_DIR}"
            exit 1
        fi
    fi

    if is_remote_resource "${CHECKSUM_URL}"; then
        log_info "Downloading checksum..."
        if ! download_file "${CHECKSUM_URL}" "${checksum_file}"; then
            log_error "Failed to download checksum"
            cleanup_temp_directory "${TEMP_DIR}"
            exit 1
        fi
    else
        log_info "Copying local checksum..."
        if ! cp "${CHECKSUM_URL}" "${checksum_file}"; then
            log_error "Failed to copy local checksum from ${CHECKSUM_URL}"
            cleanup_temp_directory "${TEMP_DIR}"
            exit 1
        fi
    fi

    log_info "Artifact and checksum ready"
}

# Verify CPython artifact checksum
verify_cpython_checksum() {
    log_step "4" "8" "Verifying SHA256 checksum"

    local artifact_file="${TEMP_DIR}/cpython-${VERSION}.tgz"
    local checksum_file="${TEMP_DIR}/cpython-${VERSION}.tgz.sha256"

    if [[ "${SKIP_VALIDATION}" == "true" ]]; then
        log_warning "Skipping checksum verification (SKIP_VALIDATION=true)"
        return 0
    fi

    if ! validate_sha256_checksum "${artifact_file}" "${checksum_file}"; then
        log_error "Checksum verification failed"
        cleanup_temp_directory "${TEMP_DIR}"
        exit 1
    fi

    log_info "Checksum verified successfully"
}

# Extract CPython artifact
extract_cpython_artifact() {
    log_step "5" "8" "Extracting artifact"

    local artifact_file="${TEMP_DIR}/cpython-${VERSION}.tgz"

    log_info "Extracting to /opt..."

    if ! extract_tarball "${artifact_file}" /opt; then
        log_error "Failed to extract artifact"
        cleanup_temp_directory "${TEMP_DIR}"
        exit 1
    fi

    log_info "Extraction completed"
}

# Verify CPython installation
verify_cpython_installation() {
    log_step "6" "8" "Verifying installation"

    # Get major.minor version
    local major_minor
    major_minor=$(echo "${VERSION}" | cut -d. -f1,2)

    local python_bin="${PYTHON_DIR}/bin/python${major_minor}"

    if ! validate_file_exists "${python_bin}" "Python binary not found: ${python_bin}"; then
        cleanup_temp_directory "${TEMP_DIR}"
        exit 1
    fi

    # Make executable
    chmod +x "${python_bin}"

    # Verify version
    export LD_LIBRARY_PATH="${PYTHON_DIR}/lib:${LD_LIBRARY_PATH:-}"
    local installed_version
    installed_version=$("${python_bin}" --version 2>&1 | awk '{print $2}')

    if [[ "${installed_version}" != "${VERSION}" ]]; then
        log_error "Version mismatch: expected ${VERSION}, got ${installed_version}"
        cleanup_temp_directory "${TEMP_DIR}"
        exit 1
    fi

    log_info "Python ${installed_version} verified successfully"

    # Test critical modules
    if [[ "${SKIP_VALIDATION}" != "true" ]]; then
        log_info "Testing critical modules..."
        local modules=("ssl" "sqlite3" "uuid" "lzma" "bz2" "zlib" "ctypes")
        for module in "${modules[@]}"; do
            if "${python_bin}" -c "import $module" 2>/dev/null; then
                log_info "  Module $module: OK"
            else
                log_error "  Module $module: FAILED"
                cleanup_temp_directory "${TEMP_DIR}"
                exit 1
            fi
        done
    fi
}

# Setup CPython environment
setup_cpython_environment() {
    log_step "7" "8" "Setting up environment"

    local major_minor
    major_minor=$(echo "${VERSION}" | cut -d. -f1,2)

    # Create marker file
    touch "${MARKER_FILE}"

    # Update alternatives (if update-alternatives exists)
    if command -v update-alternatives &> /dev/null; then
        log_info "Configuring alternatives..."
        update-alternatives --install /usr/local/bin/python python \
            "${PYTHON_DIR}/bin/python${major_minor}" 100
        update-alternatives --install /usr/local/bin/python${major_minor} python${major_minor} \
            "${PYTHON_DIR}/bin/python${major_minor}" 100
        update-alternatives --install /usr/local/bin/pip pip \
            "${PYTHON_DIR}/bin/pip${major_minor}" 100
        update-alternatives --install /usr/local/bin/pip${major_minor} pip${major_minor} \
            "${PYTHON_DIR}/bin/pip${major_minor}" 100
    fi

    # Create convenience symlinks for python and pip binaries
    mkdir -p /usr/local/bin
    ln -sf "${PYTHON_DIR}/bin/python${major_minor}" /usr/local/bin/python3
    ln -sf "${PYTHON_DIR}/bin/pip${major_minor}" /usr/local/bin/pip3
    ln -sf "${PYTHON_DIR}/bin/python${major_minor}" /usr/local/bin/python${major_minor}
    ln -sf "${PYTHON_DIR}/bin/pip${major_minor}" /usr/local/bin/pip${major_minor}

    # Configure dynamic linker so shared libraries are picked up correctly
    local ld_conf="/etc/ld.so.conf.d/python${major_minor}.conf"
    echo "${PYTHON_DIR}/lib" > "${ld_conf}"
    ldconfig

    # Add to PATH in profile
    local profile_d="/etc/profile.d/cpython-${VERSION}.sh"
    cat > "${profile_d}" <<EOF
# CPython ${VERSION} environment
export PATH="${PYTHON_DIR}/bin:\$PATH"
export LD_LIBRARY_PATH="${PYTHON_DIR}/lib:\${LD_LIBRARY_PATH:-}"
EOF

    log_info "Environment configured"
}

# Cleanup temporary files
cleanup_installation_temp_files() {
    log_step "8" "8" "Cleaning up"

    cleanup_temp_directory "${TEMP_DIR}"

    log_info "Cleanup completed"
}

# Display installation summary
display_installation_summary() {
    echo ""
    log_separator 60
    log_success "Python ${VERSION} installed successfully!"
    log_separator 60
    echo ""
    log_info "Installation directory: ${PYTHON_DIR}"
    log_info "Python binary: ${PYTHON_DIR}/bin/python${VERSION%.*}"
    log_info "pip binary: ${PYTHON_DIR}/bin/pip${VERSION%.*}"
    echo ""
    log_info "Usage:"
    log_info "  python${VERSION%.*} --version"
    log_info "  pip${VERSION%.*} --version"
    echo ""
    log_separator 60
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

main() {
    log_info "=== CPython Prebuilt Installation ==="
    log_info "Version: ${VERSION}"
    echo ""

    check_cpython_already_installed
    determine_cpython_artifact_urls
    download_cpython_artifact
    verify_cpython_checksum
    extract_cpython_artifact
    verify_cpython_installation
    setup_cpython_environment
    cleanup_installation_temp_files
    display_installation_summary
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
