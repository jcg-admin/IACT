#!/bin/bash
# utils/name_parser.sh - Naming and parsing utilities for CPython Builder
# Reference: SPEC_INFRA_001
# Purpose: Standard naming conventions and version parsing utilities

set -euo pipefail

# =============================================================================
# DEPENDENCIES
# =============================================================================

# Use local module directory - prevents conflicts with calling script's SCRIPT_DIR
_MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Only source logger if not already loaded (environment.sh loads it first)
if [[ -z "${_LOGGER_SH_LOADED:-}" ]]; then
    source "$_MODULE_DIR/logger.sh"
fi

# =============================================================================
# CONSTANTS
# =============================================================================

readonly DEFAULT_ARTIFACT_PREFIX="cpython"
readonly DEFAULT_ARTIFACT_EXTENSION=".tgz"

# =============================================================================
# ARTIFACT NAMING
# =============================================================================

# Generate standard artifact name
# Args: $1 - version, $2 - distribution, $3 - build number
# Returns: Artifact name via stdout
# Example: name=$(parse_artifact_name "3.12.6" "ubuntu20.04" "1")
parse_artifact_name() {
    local version="$1"
    local distro="$2"
    local build_number="$3"

    echo "${DEFAULT_ARTIFACT_PREFIX}-${version}-${distro}-build${build_number}${DEFAULT_ARTIFACT_EXTENSION}"
}

# Parse artifact name into components
# Args: $1 - artifact name
# Returns: Components via stdout (one per line: version, distro, build_number)
# Example: parse_artifact_name_components "cpython-3.12.6-ubuntu20.04-build1.tgz"
parse_artifact_name_components() {
    local artifact_name="$1"

    # Remove prefix and extension
    local base_name="${artifact_name#${DEFAULT_ARTIFACT_PREFIX}-}"
    base_name="${base_name%${DEFAULT_ARTIFACT_EXTENSION}}"

    # Extract components
    # Format: VERSION-DISTRO-buildNUMBER
    if [[ "$base_name" =~ ^([0-9]+\.[0-9]+\.[0-9]+)-([a-z0-9.]+)-build([0-9]+)$ ]]; then
        echo "${BASH_REMATCH[1]}"  # version
        echo "${BASH_REMATCH[2]}"  # distro
        echo "${BASH_REMATCH[3]}"  # build_number
        return 0
    else
        log_error "Invalid artifact name format: $artifact_name"
        return 1
    fi
}

# Generate build directory name
# Args: $1 - version, $2 - optional suffix
# Returns: Build directory name via stdout
# Example: dir=$(generate_build_directory_name "3.12.6" "optimized")
generate_build_directory_name() {
    local version="$1"
    local suffix="${2:-}"

    if [[ -n "$suffix" ]]; then
        echo "Python-${version}-${suffix}"
    else
        echo "Python-${version}"
    fi
}

# =============================================================================
# VERSION PARSING
# =============================================================================

# Parse version components (major.minor.patch)
# Args: $1 - version string
# Returns: Components via stdout (one per line: major, minor, patch)
# Example: parse_version_components "3.12.6"
parse_version_components() {
    local version="$1"

    if [[ ! "$version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        log_error "Invalid version format: $version"
        return 1
    fi

    echo "${BASH_REMATCH[1]}"  # major
    echo "${BASH_REMATCH[2]}"  # minor
    echo "${BASH_REMATCH[3]}"  # patch
    return 0
}

# Get major.minor from version (3.12.6 -> 3.12)
# Args: $1 - version string
# Returns: Major.minor via stdout
# Example: major_minor=$(get_version_major_minor "3.12.6")
get_version_major_minor() {
    local version="$1"

    echo "$version" | cut -d. -f1,2
}

# Get major version only
# Args: $1 - version string
# Returns: Major version via stdout
# Example: major=$(get_version_major "3.12.6")
get_version_major() {
    local version="$1"

    echo "$version" | cut -d. -f1
}

# Get minor version only
# Args: $1 - version string
# Returns: Minor version via stdout
# Example: minor=$(get_version_minor "3.12.6")
get_version_minor() {
    local version="$1"

    echo "$version" | cut -d. -f2
}

# Get patch version only
# Args: $1 - version string
# Returns: Patch version via stdout
# Example: patch=$(get_version_patch "3.12.6")
get_version_patch() {
    local version="$1"

    echo "$version" | cut -d. -f3
}

# Compare two versions
# Args: $1 - version1, $2 - version2
# Returns: 0 if equal, 1 if version1 < version2, 2 if version1 > version2
# Example: compare_versions "3.12.6" "3.12.5"
compare_versions() {
    local version1="$1"
    local version2="$2"

    if [[ "$version1" == "$version2" ]]; then
        return 0
    fi

    # Parse components
    local v1_major v1_minor v1_patch
    local v2_major v2_minor v2_patch

    v1_major=$(get_version_major "$version1")
    v1_minor=$(get_version_minor "$version1")
    v1_patch=$(get_version_patch "$version1")

    v2_major=$(get_version_major "$version2")
    v2_minor=$(get_version_minor "$version2")
    v2_patch=$(get_version_patch "$version2")

    # Compare major
    if (( v1_major < v2_major )); then
        return 1
    elif (( v1_major > v2_major )); then
        return 2
    fi

    # Compare minor
    if (( v1_minor < v2_minor )); then
        return 1
    elif (( v1_minor > v2_minor )); then
        return 2
    fi

    # Compare patch
    if (( v1_patch < v2_patch )); then
        return 1
    elif (( v1_patch > v2_patch )); then
        return 2
    fi

    return 0
}

# =============================================================================
# OS VERSION DETECTION
# =============================================================================

# Detect OS version
# Returns: OS version string via stdout (e.g., "20.04")
# Example: os_version=$(detect_os_version)
detect_os_version() {
    if [[ -f /etc/os-release ]]; then
        # Source the os-release file
        . /etc/os-release
        echo "${VERSION_ID:-unknown}"
        return 0
    else
        log_warning "Cannot detect OS version (/etc/os-release not found)"
        echo "unknown"
        return 1
    fi
}

# Get OS name
# Returns: OS name via stdout (e.g., "Ubuntu")
# Example: os_name=$(get_os_name)
get_os_name() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "${NAME:-unknown}"
        return 0
    else
        echo "unknown"
        return 1
    fi
}

# Get OS ID
# Returns: OS ID via stdout (e.g., "ubuntu")
# Example: os_id=$(get_os_id)
get_os_id() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "${ID:-unknown}"
        return 0
    else
        echo "unknown"
        return 1
    fi
}

# Generate distro identifier for artifacts
# Returns: Distro identifier via stdout (e.g., "ubuntu20.04")
# Example: distro=$(generate_distro_identifier)
generate_distro_identifier() {
    local os_id
    os_id=$(get_os_id)

    local os_version
    os_version=$(detect_os_version)

    echo "${os_id}${os_version}"
}

# =============================================================================
# PATH UTILITIES
# =============================================================================

# Generate standard installation path
# Args: $1 - version
# Returns: Installation path via stdout
# Example: install_path=$(generate_installation_path "3.12.6")
generate_installation_path() {
    local version="$1"
    local major_minor
    major_minor=$(get_version_major_minor "$version")

    echo "/opt/python${major_minor}"
}

# Generate source directory name
# Args: $1 - version
# Returns: Source directory name via stdout
# Example: source_dir=$(generate_source_directory_name "3.12.6")
generate_source_directory_name() {
    local version="$1"
    echo "Python-${version}"
}

# Generate download filename
# Args: $1 - version
# Returns: Download filename via stdout
# Example: filename=$(generate_download_filename "3.12.6")
generate_download_filename() {
    local version="$1"
    echo "Python-${version}.tgz"
}

# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

# Validate artifact name format
# Args: $1 - artifact name
# Returns: 0 if valid, 1 if invalid
# Example: validate_artifact_name_format "cpython-3.12.6-ubuntu20.04-build1.tgz"
validate_artifact_name_format() {
    local artifact_name="$1"

    if [[ "$artifact_name" =~ ^${DEFAULT_ARTIFACT_PREFIX}-[0-9]+\.[0-9]+\.[0-9]+-[a-z0-9.]+-build[0-9]+${DEFAULT_ARTIFACT_EXTENSION}$ ]]; then
        return 0
    else
        log_error "Invalid artifact name format: $artifact_name"
        return 1
    fi
}

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

# Alias for backward compatibility
get_artifact_name() {
    parse_artifact_name "$@"
}

# Alias for backward compatibility
get_python_major_minor() {
    get_version_major_minor "$@"
}