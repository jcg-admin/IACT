#!/bin/bash
#
# install_prebuilt_cpython.sh
# Installs precompiled CPython with PGO+LTO optimizations
#
# Purpose: Install CPython prebuilt artifacts in containers/VMs
# References: SPEC_INFRA_001
#
# Usage:
#   VERSION=3.12.6 ./install_prebuilt_cpython.sh
#   ARTIFACT_URL=https://... ./install_prebuilt_cpython.sh
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
# LOAD UTILITIES (with fallback for containers)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Try to load utilities if they exist
if [[ -f "$SCRIPT_DIR/../utils/logger.sh" ]]; then
    source "$SCRIPT_DIR/../utils/logger.sh"
    source "$SCRIPT_DIR/../utils/validator.sh" 2>/dev/null || true
    source "$SCRIPT_DIR/../utils/filesystem.sh" 2>/dev/null || true
    source "$SCRIPT_DIR/../utils/network.sh" 2>/dev/null || true
    LOGGING_LOADED=1
else
    # Fallback: define functions inline if utilities not found
    # This ensures the script works standalone in containers
    log_info() { echo "[INFO] $*"; }
    log_warning() { echo "[WARNING] $*"; }
    log_error() { echo "[ERROR] $*" >&2; }
    log_step() {
        local step="$1"
        local total="$2"
        local message="$3"
        echo ""
        echo "[STEP $step/$total] $message"
        echo "----------------------------------------"
    }
    log_separator() {
        local width="${1:-60}"
        printf '%*s\n' "$width" '' | tr ' ' '-'
    }

    # Filesystem fallbacks
    cleanup_temp_directory() {
        local temp_dir="$1"
        if [[ -n "$temp_dir" ]] && [[ -d "$temp_dir" ]]; then
            log_info "Cleaning temporary files: $temp_dir"
            rm -rf "$temp_dir"
        fi
    }

    create_temp_directory() {
        local prefix="${1:-temp_}"
        local temp_dir
        temp_dir=$(mktemp -d -t "${prefix}XXXXXX")
        echo "$temp_dir"
    }

    extract_tarball() {
        local tarball="$1"
        local dest_dir="$2"
        tar xzf "$tarball" -C "$dest_dir"
    }

    # Network fallbacks
    download_file() {
        local url="$1"
        local dest="$2"
        if command -v wget &> /dev/null; then
            wget -q --show-progress "$url" -O "$dest"
        elif command -v curl &> /dev/null; then
            curl -fsSL "$url" -o "$dest"
        else
            log_error "Neither wget nor curl found"
            return 1
        fi
    }

    # Validation fallbacks
    validate_file_exists() {
        local file="$1"
        local error_msg="${2:-File not found: $file}"
        if [[ ! -f "$file" ]]; then
            log_error "$error_msg"
            return 1
        fi
        return 0
    }

    validate_sha256_checksum() {
        local file="$1"
        local checksum_file="$2"

        cd "$(dirname "$file")"
        if ! sha256sum -c "$(basename "$checksum_file")" 2>&1 | grep -q "OK"; then
            log_error "SHA256 checksum validation failed"
            return 1
        fi
        return 0
    }
fi

# ==============================================================================
# FUNCTIONS
# ==============================================================================

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

    if [[ -z "${ARTIFACT_URL}" ]]; then
        # Use GitHub Releases (default)
        ARTIFACT_URL="https://github.com/2-Coatl/IACT---project/releases/download/cpython-${VERSION}-build1/cpython-${VERSION}-ubuntu20.04-build1.tgz"
        log_info "Using GitHub Releases: ${ARTIFACT_URL}"
    else
        log_info "Using provided artifact URL: ${ARTIFACT_URL}"
    fi

    if [[ -z "${CHECKSUM_URL}" ]]; then
        # Derive checksum URL from artifact URL
        CHECKSUM_URL="${ARTIFACT_URL}.sha256"
        log_info "Derived checksum URL: ${CHECKSUM_URL}"
    else
        log_info "Using provided checksum URL: ${CHECKSUM_URL}"
    fi
}

# Download CPython artifact and checksum
download_cpython_artifact() {
    log_step "3" "8" "Downloading artifact and checksum"

    mkdir -p "${TEMP_DIR}"

    local artifact_file="${TEMP_DIR}/cpython-${VERSION}.tgz"
    local checksum_file="${TEMP_DIR}/cpython-${VERSION}.tgz.sha256"

    log_info "Downloading artifact..."
    if ! download_file "${ARTIFACT_URL}" "${artifact_file}"; then
        log_error "Failed to download artifact"
        cleanup_temp_directory "${TEMP_DIR}"
        exit 1
    fi

    log_info "Downloading checksum..."
    if ! download_file "${CHECKSUM_URL}" "${checksum_file}"; then
        log_error "Failed to download checksum"
        cleanup_temp_directory "${TEMP_DIR}"
        exit 1
    fi

    log_info "Download completed"
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
        local modules=("ssl" "sqlite3" "uuid" "lzma" "bz2" "zlib")
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
    log_info "Python ${VERSION} installed successfully!"
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

main "$@"