#!/bin/bash
#
# Feature: cpython-prebuilt
# Installs precompiled CPython with PGO+LTO optimizations
#
# References: SPEC-INFRA-001
#

set -e

# ==============================================================================
# Variables from devcontainer-feature.json
# ==============================================================================
VERSION="${VERSION:-3.12.6}"
ARTIFACT_URL="${ARTIFACTURL:-}"
CHECKSUM_URL="${CHECKSUMURL:-}"
INSTALL_PREFIX="${INSTALLPREFIX:-/opt/python}"
SKIP_VALIDATION="${SKIPVALIDATION:-false}"

# ==============================================================================
# Derived variables
# ==============================================================================
PYTHON_DIR="${INSTALL_PREFIX}-${VERSION}"
MARKER_FILE="${PYTHON_DIR}/.installed"
TEMP_DIR="/tmp/cpython-install-$$"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==============================================================================
# Logging functions
# ==============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_step() {
    local step="$1"
    local total="$2"
    local message="$3"
    echo ""
    echo -e "${BLUE}[STEP $step/$total]${NC} $message"
    echo "----------------------------------------"
}

# ==============================================================================
# Utility functions
# ==============================================================================

# Check if Python is already installed (idempotent detection)
check_if_installed() {
    log_step "1" "8" "Checking if Python ${VERSION} is already installed"

    if [ -f "${MARKER_FILE}" ]; then
        log_success "Python ${VERSION} already installed at ${PYTHON_DIR}"
        log_info "Skipping installation (idempotent)"
        exit 0
    fi

    if [ -d "${PYTHON_DIR}" ]; then
        log_warning "Directory ${PYTHON_DIR} exists but no marker file found"
        log_info "Will proceed with installation"
    fi
}

# Determine artifact URLs
determine_urls() {
    log_step "2" "8" "Determining artifact URLs"

    if [ -z "${ARTIFACT_URL}" ]; then
        # Use GitHub Releases (Fase 3+)
        ARTIFACT_URL="https://github.com/2-Coatl/IACT---project/releases/download/cpython-${VERSION}-build1/cpython-${VERSION}-ubuntu22.04-build1.tgz"
        log_info "Using GitHub Releases: ${ARTIFACT_URL}"
    else
        log_info "Using provided artifact URL: ${ARTIFACT_URL}"
    fi

    if [ -z "${CHECKSUM_URL}" ]; then
        # Derive checksum URL from artifact URL
        CHECKSUM_URL="${ARTIFACT_URL}.sha256"
        log_info "Derived checksum URL: ${CHECKSUM_URL}"
    else
        log_info "Using provided checksum URL: ${CHECKSUM_URL}"
    fi
}

# Download artifact and checksum
download_artifacts() {
    log_step "3" "8" "Downloading artifacts"

    mkdir -p "${TEMP_DIR}"

    # Download main artifact
    log_info "Downloading ${ARTIFACT_URL}"
    if [[ "${ARTIFACT_URL}" =~ ^https?:// ]]; then
        # Download from URL
        if command -v wget > /dev/null; then
            wget -q --show-progress -O "${TEMP_DIR}/cpython.tgz" "${ARTIFACT_URL}" || {
                log_error "Failed to download artifact"
                cleanup
                exit 1
            }
        elif command -v curl > /dev/null; then
            curl -fsSL -o "${TEMP_DIR}/cpython.tgz" "${ARTIFACT_URL}" || {
                log_error "Failed to download artifact"
                cleanup
                exit 1
            }
        else
            log_error "Neither wget nor curl found. Please install one."
            cleanup
            exit 1
        fi
    else
        # Copy from local path
        log_info "Copying from local path: ${ARTIFACT_URL}"
        cp "${ARTIFACT_URL}" "${TEMP_DIR}/cpython.tgz" || {
            log_error "Failed to copy artifact from ${ARTIFACT_URL}"
            cleanup
            exit 1
        }
    fi

    # Download checksum
    log_info "Downloading ${CHECKSUM_URL}"
    if [[ "${CHECKSUM_URL}" =~ ^https?:// ]]; then
        if command -v wget > /dev/null; then
            wget -q --show-progress -O "${TEMP_DIR}/cpython.tgz.sha256" "${CHECKSUM_URL}" || {
                log_error "Failed to download checksum"
                cleanup
                exit 1
            }
        elif command -v curl > /dev/null; then
            curl -fsSL -o "${TEMP_DIR}/cpython.tgz.sha256" "${CHECKSUM_URL}" || {
                log_error "Failed to download checksum"
                cleanup
                exit 1
            }
        fi
    else
        log_info "Copying checksum from local path: ${CHECKSUM_URL}"
        cp "${CHECKSUM_URL}" "${TEMP_DIR}/cpython.tgz.sha256" || {
            log_error "Failed to copy checksum from ${CHECKSUM_URL}"
            cleanup
            exit 1
        }
    fi

    log_success "Artifacts downloaded successfully"
}

# Validate checksum
validate_checksum() {
    log_step "4" "8" "Validating artifact integrity"

    if [ "${SKIP_VALIDATION}" = "true" ]; then
        log_warning "SKIPPING checksum validation (skipValidation=true)"
        log_warning "This is NOT RECOMMENDED for production use"
        return
    fi

    if [ ! -f "${TEMP_DIR}/cpython.tgz.sha256" ]; then
        log_error "Checksum file not found at ${TEMP_DIR}/cpython.tgz.sha256"
        cleanup
        exit 1
    fi

    log_info "Computing SHA256 checksum..."
    cd "${TEMP_DIR}"

    # Extract just the hash from the checksum file
    EXPECTED_HASH=$(awk '{print $1}' cpython.tgz.sha256)
    ACTUAL_HASH=$(sha256sum cpython.tgz | awk '{print $1}')

    log_info "Expected: ${EXPECTED_HASH}"
    log_info "Actual:   ${ACTUAL_HASH}"

    if [ "${EXPECTED_HASH}" != "${ACTUAL_HASH}" ]; then
        log_error "Checksum mismatch!"
        log_error "Artifact may be corrupted or tampered with"
        cleanup
        exit 1
    fi

    log_success "Checksum validation passed"
}

# Extract tarball
extract_tarball() {
    log_step "5" "8" "Extracting CPython tarball"

    log_info "Extracting to /"
    tar -xzf "${TEMP_DIR}/cpython.tgz" -C / || {
        log_error "Failed to extract tarball"
        cleanup
        exit 1
    }

    log_success "Tarball extracted successfully"
}

# Configure system
configure_system() {
    log_step "6" "8" "Configuring system"

    # Create symlinks
    log_info "Creating symlinks in /usr/local/bin"
    ln -sf "${PYTHON_DIR}/bin/python3" /usr/local/bin/python3 || true
    ln -sf "${PYTHON_DIR}/bin/python${VERSION%.*}" /usr/local/bin/python${VERSION%.*} || true
    ln -sf "${PYTHON_DIR}/bin/pip3" /usr/local/bin/pip3 || true
    ln -sf "${PYTHON_DIR}/bin/pip${VERSION%.*}" /usr/local/bin/pip${VERSION%.*} || true

    # Configure shared libraries
    log_info "Configuring shared libraries"
    echo "${PYTHON_DIR}/lib" > /etc/ld.so.conf.d/python${VERSION}.conf
    ldconfig || {
        log_warning "ldconfig failed, but continuing..."
    }

    # Update PATH for current session
    export PATH="${PYTHON_DIR}/bin:${PATH}"

    log_success "System configured successfully"
}

# Validate installation
validate_installation() {
    log_step "7" "8" "Validating installation"

    # Check python3 exists and reports correct version
    log_info "Checking Python version..."
    INSTALLED_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    log_info "Installed version: ${INSTALLED_VERSION}"

    if [[ ! "${INSTALLED_VERSION}" =~ ^${VERSION} ]]; then
        log_error "Version mismatch: expected ${VERSION}, got ${INSTALLED_VERSION}"
        exit 1
    fi

    # Validate critical native modules
    log_info "Validating native modules..."
    MODULES=("ssl" "sqlite3" "uuid" "lzma" "bz2" "zlib" "ctypes")

    for module in "${MODULES[@]}"; do
        if python3 -c "import ${module}" 2>/dev/null; then
            log_success "  - ${module}: OK"
        else
            log_error "  - ${module}: FAILED"
            log_error "Module ${module} not available"
            exit 1
        fi
    done

    # Check pip availability
    log_info "Checking pip availability..."
    if python3 -m pip --version > /dev/null 2>&1; then
        PIP_VERSION=$(python3 -m pip --version | awk '{print $2}')
        log_success "pip ${PIP_VERSION} available"
    else
        log_error "pip not available"
        exit 1
    fi

    log_success "All validations passed"
}

# Create marker file
create_marker() {
    log_step "8" "8" "Finalizing installation"

    log_info "Creating installation marker"
    cat > "${MARKER_FILE}" <<EOF
CPython ${VERSION}
Installed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Artifact URL: ${ARTIFACT_URL}
Install prefix: ${PYTHON_DIR}
Feature version: 1.0.0
Spec: SPEC-INFRA-001
EOF

    log_success "Marker file created at ${MARKER_FILE}"
}

# Cleanup temporary files
cleanup() {
    if [ -d "${TEMP_DIR}" ]; then
        log_info "Cleaning up temporary files"
        rm -rf "${TEMP_DIR}"
    fi
}

# ==============================================================================
# Main installation flow
# ==============================================================================
main() {
    echo "========================================"
    echo "  CPython Prebuilt Feature Installer"
    echo "========================================"
    echo "Version: ${VERSION}"
    echo "Install prefix: ${INSTALL_PREFIX}"
    echo "========================================"
    echo ""

    # Execute installation steps
    check_if_installed
    determine_urls
    download_artifacts
    validate_checksum
    extract_tarball
    configure_system
    validate_installation
    create_marker
    cleanup

    echo ""
    echo "========================================"
    log_success "CPython ${VERSION} installed successfully!"
    echo "========================================"
    echo ""
    echo "Python location: ${PYTHON_DIR}/bin/python3"
    echo "Pip location: ${PYTHON_DIR}/bin/pip3"
    echo ""
    echo "To use:"
    echo "  python3 --version"
    echo "  pip3 --version"
    echo ""
}

# Run main function
main "$@"
