#!/bin/bash
# install.sh - Dev Container Feature installer for CPython prebuilt artifacts
# Specification Reference: SPEC_INFRA_001 (CPython Precompiled Distribution)
# This script follows the Dev Container Features contract to install CPython with
# PGO+LTO optimizations and validates integrity, modules, and environment wiring.

set -euo pipefail

# ==============================================================================
# CONFIGURATION
# ==============================================================================
FEATURE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${FEATURE_DIR}/../../.." && pwd)"

VERSION="${VERSION:-${FEATURE_VERSION:-3.12.6}}"
ARTIFACT_URL="${ARTIFACTURL:-${artifactUrl:-}}"
CHECKSUM_URL="${CHECKSUMURL:-${checksumUrl:-}}"
INSTALL_PREFIX="${INSTALLPREFIX:-${installPrefix:-/opt/python}}"
SKIP_VALIDATION="${SKIPVALIDATION:-${skipValidation:-false}}"

DEFAULT_BUILD_NUMBER="1"
DEFAULT_DISTRO="ubuntu20.04"

CONFIG_FILE="${PROJECT_ROOT}/infrastructure/cpython/builder/config/versions.conf"
if [[ -f "${CONFIG_FILE}" ]]; then
    # shellcheck disable=SC1090
    source "${CONFIG_FILE}"
    DEFAULT_BUILD_NUMBER="${DEFAULT_BUILD_NUMBER:-1}"
    DEFAULT_DISTRO="${CPYTHON_DISTRO:-${DISTRO:-${DEFAULT_DISTRO}}}"
fi

RESOLVED_BUILD_NUMBER="${BUILDNUMBER:-${DEFAULT_BUILD_NUMBER}}"
RESOLVED_DISTRO="${CPYTHON_DISTRO:-${DEFAULT_DISTRO}}"
RELEASES_BASE="${GITHUB_RELEASES_BASE:-https://github.com/2-Coatl/IACT---project/releases}"
ARTIFACT_BASENAME="cpython-${VERSION}-${RESOLVED_DISTRO}-build${RESOLVED_BUILD_NUMBER}"
ARTIFACT_FILENAME="${ARTIFACT_BASENAME}.tgz"
RELEASE_TAG="cpython-${VERSION}-build${RESOLVED_BUILD_NUMBER}"
LOCAL_ARTIFACT_DIR="${PROJECT_ROOT}/infrastructure/cpython/artifacts"
PYTHON_DIR="${INSTALL_PREFIX}-${VERSION}"
MARKER_FILE="${PYTHON_DIR}/.installed"
TEMP_DIR="$(mktemp -d /tmp/cpython-feature.XXXXXX)"

trap 'cleanup_temp_directory "${TEMP_DIR}"' EXIT

# ==============================================================================
# LOGGING UTILITIES
# ==============================================================================
log_separator() {
    local width="${1:-60}"
    printf '%*s\n' "${width}" '' | tr ' ' '-'
}

log_info() {
    printf '[INFO] %s\n' "$1"
}

log_warning() {
    printf '[WARN] %s\n' "$1"
}

log_error() {
    printf '[ERROR] %s\n' "$1" >&2
}

log_success() {
    printf '[SUCCESS] %s\n' "$1"
}

log_step() {
    local current="$1"
    local total="$2"
    local message="$3"
    log_info "[${current}/${total}] ${message}"
}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
is_remote_resource() {
    local candidate="$1"
    [[ "$candidate" =~ ^https?:// ]]
}

_strip_file_scheme() {
    local candidate="$1"
    if [[ "$candidate" == file://* ]]; then
        printf '%s' "${candidate#file://}"
    else
        printf '%s' "$candidate"
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
    elif [[ -f "${PROJECT_ROOT}/${candidate}" ]]; then
        echo "${PROJECT_ROOT}/${candidate}"
    else
        echo "${FEATURE_DIR}/${candidate}"
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
    if [[ -n "$artifact_path" && -f "${artifact_path}.sha256" ]]; then
        echo "${artifact_path}.sha256"
    fi
}

cleanup_temp_directory() {
    local dir="$1"
    if [[ -n "$dir" && -d "$dir" ]]; then
        rm -rf "$dir"
    fi
}

validate_file_exists() {
    local file_path="$1"
    local error_msg="$2"
    if [[ ! -f "$file_path" ]]; then
        log_error "$error_msg"
        exit 1
    fi
}

validate_sha256_checksum() {
    local artifact="$1"
    local checksum_file="$2"

    if ! command -v sha256sum >/dev/null 2>&1; then
        log_error "sha256sum command not available"
        exit 1
    fi

    (cd "$(dirname "$artifact")" && sha256sum -c "${checksum_file}")
}

extract_tarball() {
    local artifact="$1"
    local destination="$2"

    mkdir -p "$destination"
    tar -xzf "$artifact" -C "$destination"
}

download_file() {
    local url="$1"
    local destination="$2"

    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$url" -o "$destination"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$url" -O "$destination"
    else
        log_error "Neither curl nor wget is installed"
        return 1
    fi
}

# ==============================================================================
# INSTALLATION STEPS
# ==============================================================================
check_cpython_already_installed() {
    log_step "1" "8" "Checking idempotency markers"
    if [[ -f "${MARKER_FILE}" ]]; then
        log_info "Installation marker found at ${MARKER_FILE}"
        log_info "CPython ${VERSION} already installed. Exiting idempotently."
        exit 0
    fi
}

determine_cpython_artifact_urls() {
    log_step "2" "8" "Resolving artifact and checksum locations"
    local resolved_artifact=""
    local resolved_checksum=""

    if [[ -n "${ARTIFACT_URL}" ]]; then
        if is_remote_resource "${ARTIFACT_URL}"; then
            resolved_artifact="${ARTIFACT_URL}"
            log_info "Using provided remote artifact URL: ${resolved_artifact}"
        else
            resolved_artifact="$(resolve_local_path "${ARTIFACT_URL}")"
            if [[ -z "$resolved_artifact" || ! -f "$resolved_artifact" ]]; then
                log_error "Local artifact not found: ${ARTIFACT_URL}"
                exit 1
            fi
            log_info "Using provided local artifact path: ${resolved_artifact}"
        fi
    else
        resolved_artifact="$(default_local_artifact_path)"
        if [[ -n "$resolved_artifact" ]]; then
            log_info "Using artifact built locally: ${resolved_artifact}"
        else
            resolved_artifact="${RELEASES_BASE%/}/download/${RELEASE_TAG}/${ARTIFACT_FILENAME}"
            log_info "Defaulting to GitHub Releases artifact: ${resolved_artifact}"
        fi
    fi

    if [[ -n "${CHECKSUM_URL}" ]]; then
        if is_remote_resource "${CHECKSUM_URL}"; then
            resolved_checksum="${CHECKSUM_URL}"
            log_info "Using provided remote checksum URL: ${resolved_checksum}"
        else
            resolved_checksum="$(resolve_local_path "${CHECKSUM_URL}")"
            if [[ -z "$resolved_checksum" || ! -f "$resolved_checksum" ]]; then
                log_error "Local checksum not found: ${CHECKSUM_URL}"
                exit 1
            fi
            log_info "Using provided local checksum path: ${resolved_checksum}"
        fi
    else
        if is_remote_resource "$resolved_artifact"; then
            resolved_checksum="${resolved_artifact}.sha256"
            log_info "Derived checksum URL: ${resolved_checksum}"
        else
            resolved_checksum="$(default_local_checksum_path "$resolved_artifact")"
            if [[ -z "$resolved_checksum" ]]; then
                log_error "Checksum file missing next to artifact"
                exit 1
            fi
            log_info "Using checksum generated with artifact: ${resolved_checksum}"
        fi
    fi

    ARTIFACT_URL="$resolved_artifact"
    CHECKSUM_URL="$resolved_checksum"
}

download_cpython_artifact() {
    log_step "3" "8" "Downloading artifact and checksum"
    mkdir -p "${TEMP_DIR}"

    local artifact_file="${TEMP_DIR}/cpython-${VERSION}.tgz"
    local checksum_file="${TEMP_DIR}/cpython-${VERSION}.tgz.sha256"

    if is_remote_resource "${ARTIFACT_URL}"; then
        log_info "Downloading artifact..."
        if ! download_file "${ARTIFACT_URL}" "${artifact_file}"; then
            log_error "Failed to download artifact"
            exit 1
        fi
    else
        log_info "Copying artifact from local filesystem"
        cp "${ARTIFACT_URL}" "${artifact_file}"
    fi

    if is_remote_resource "${CHECKSUM_URL}"; then
        log_info "Downloading checksum..."
        if ! download_file "${CHECKSUM_URL}" "${checksum_file}"; then
            log_error "Failed to download checksum"
            exit 1
        fi
    else
        log_info "Copying checksum from local filesystem"
        cp "${CHECKSUM_URL}" "${checksum_file}"
    fi

    DOWNLOADED_ARTIFACT="${artifact_file}"
    DOWNLOADED_CHECKSUM="${checksum_file}"
}

verify_cpython_checksum() {
    log_step "4" "8" "Validating SHA256 checksum"
    if [[ "${SKIP_VALIDATION}" == "true" ]]; then
        log_warning "Checksum validation skipped by configuration"
        return 0
    fi

    if ! validate_sha256_checksum "${DOWNLOADED_ARTIFACT}" "${DOWNLOADED_CHECKSUM}"; then
        log_error "Checksum verification failed"
        exit 1
    fi
    log_info "Checksum validated successfully"
}

extract_cpython_artifact() {
    log_step "5" "8" "Extracting artifact into ${INSTALL_PREFIX}"
    extract_tarball "${DOWNLOADED_ARTIFACT}" "/opt"
}

verify_cpython_installation() {
    log_step "6" "8" "Verifying Python binary and modules"
    local major_minor
    major_minor=$(echo "${VERSION}" | cut -d. -f1,2)
    local python_bin="${PYTHON_DIR}/bin/python${major_minor}"

    validate_file_exists "${python_bin}" "Python binary not found at ${python_bin}"

    chmod +x "${python_bin}"
    export LD_LIBRARY_PATH="${PYTHON_DIR}/lib:${LD_LIBRARY_PATH:-}"

    local reported_version
    reported_version=$("${python_bin}" --version 2>&1 | awk '{print $2}')
    if [[ "${reported_version}" != "${VERSION}" ]]; then
        log_error "Version mismatch: expected ${VERSION}, got ${reported_version}"
        exit 1
    fi

    if [[ "${SKIP_VALIDATION}" != "true" ]]; then
        local modules=(ssl sqlite3 uuid lzma bz2 zlib ctypes)
        for module in "${modules[@]}"; do
            if "${python_bin}" -c "import ${module}" >/dev/null 2>&1; then
                log_info "Module ${module} OK"
            else
                log_error "Module ${module} missing"
                exit 1
            fi
        done
    fi
}

setup_cpython_environment() {
    log_step "7" "8" "Configuring environment, symlinks, and ld.so"
    local major_minor
    major_minor=$(echo "${VERSION}" | cut -d. -f1,2)

    mkdir -p "${PYTHON_DIR}"
    touch "${MARKER_FILE}"

    mkdir -p /usr/local/bin
    ln -sf "${PYTHON_DIR}/bin/python${major_minor}" /usr/local/bin/python3
    ln -sf "${PYTHON_DIR}/bin/pip${major_minor}" /usr/local/bin/pip3
    ln -sf "${PYTHON_DIR}/bin/python${major_minor}" /usr/local/bin/python${major_minor}
    ln -sf "${PYTHON_DIR}/bin/pip${major_minor}" /usr/local/bin/pip${major_minor}

    local ld_conf="/etc/ld.so.conf.d/python${major_minor}.conf"
    echo "${PYTHON_DIR}/lib" > "${ld_conf}"
    ldconfig

    local profile_d="/etc/profile.d/cpython-${VERSION}.sh"
    cat > "${profile_d}" <<EOF_PROFILE
# CPython ${VERSION} installed via Dev Container Feature
export PATH="${PYTHON_DIR}/bin:\$PATH"
export LD_LIBRARY_PATH="${PYTHON_DIR}/lib:\${LD_LIBRARY_PATH:-}"
EOF_PROFILE
}

cleanup_installation_temp_files() {
    log_step "8" "8" "Cleaning up temporary files"
    if [[ -d "${TEMP_DIR}" ]]; then
        rm -rf "${TEMP_DIR}" || true
    fi
}

print_summary() {
    log_separator 70
    log_success "CPython ${VERSION} installed successfully"
    log_info "Binary: ${PYTHON_DIR}/bin/python${VERSION%.*}"
    log_info "pip:    ${PYTHON_DIR}/bin/pip${VERSION%.*}"
    log_info "Symlinks created under /usr/local/bin"
    log_info "ld.so configured via /etc/ld.so.conf.d"
    log_separator 70
}

main() {
    log_info "=== CPython Prebuilt Feature Installer ==="
    log_info "Specification: SPEC_INFRA_001"
    check_cpython_already_installed
    determine_cpython_artifact_urls
    download_cpython_artifact
    verify_cpython_checksum
    extract_cpython_artifact
    verify_cpython_installation
    setup_cpython_environment
    cleanup_installation_temp_files
    print_summary
    exit 0
}

main "$@"
