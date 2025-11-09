#!/bin/bash
#
# validate_build.sh - Validate compiled CPython artifact
#
# Reference: SPEC_INFRA_001
# Purpose: Verify integrity and functionality of artifact
#
# Usage:
#   ./validate_build.sh <artifact-name>
#
# Example:
#   ./validate_build.sh cpython-3.12.6-ubuntu20.04-build1.tgz
#

set -euo pipefail

# =============================================================================
# LOAD UTILITIES
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-/vagrant}"

# Load environment system
load_environment() {
    local env_path="$SCRIPT_DIR/../utils/environment.sh"

    if [[ ! -f "$env_path" ]]; then
        env_path="$PROJECT_ROOT/utils/environment.sh"
    fi

    if [[ ! -f "$env_path" ]]; then
        echo "ERROR: Environment system not found" >&2
        return 1
    fi

    source "$env_path"
    return 0
}

if ! load_environment; then
    echo "ERROR: Failed to load environment system" >&2
    exit 1
fi

# Load configuration
if [[ -f "$SCRIPT_DIR/../config/versions.conf" ]]; then
    source "$SCRIPT_DIR/../config/versions.conf"
elif [[ -f "$PROJECT_ROOT/config/versions.conf" ]]; then
    source "$PROJECT_ROOT/config/versions.conf"
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
ARTIFACT_DIR="/vagrant/artifacts/cpython"
ARTIFACT_PATH="$ARTIFACT_DIR/$ARTIFACT_NAME"
ARTIFACT_CHECKSUM="$ARTIFACT_PATH.sha256"

# =============================================================================
# DISPLAY VALIDATION INFO
# =============================================================================

log_header "CPython Artifact Validation" 73
log_info "Artifact: $ARTIFACT_NAME"
echo ""

# =============================================================================
# STEP 1: VERIFY ARTIFACT EXISTENCE
# =============================================================================

log_step 1 6 "Verifying artifact existence"

if ! validate_file_exists "$ARTIFACT_PATH" "Artifact not found: $ARTIFACT_PATH"; then
    exit 1
fi

log_info "Artifact exists: $ARTIFACT_PATH"

# =============================================================================
# STEP 2: VERIFY CHECKSUM EXISTENCE
# =============================================================================

log_step 2 6 "Verifying checksum existence"

if ! validate_file_exists "$ARTIFACT_CHECKSUM" "Checksum not found: $ARTIFACT_CHECKSUM"; then
    exit 1
fi

log_info "Checksum file exists: $ARTIFACT_CHECKSUM"

# =============================================================================
# STEP 3: VERIFY SHA256 INTEGRITY
# =============================================================================

log_step 3 6 "Verifying SHA256 integrity"

if ! validate_sha256_checksum "$ARTIFACT_PATH" "$ARTIFACT_CHECKSUM"; then
    log_error "SHA256 checksum validation failed"
    exit 1
fi

CHECKSUM=$(cut -d' ' -f1 "$ARTIFACT_CHECKSUM")
log_info "Checksum valid: $CHECKSUM"

# =============================================================================
# STEP 4: VERIFY ARTIFACT SIZE
# =============================================================================

log_step 4 6 "Verifying artifact size"

ARTIFACT_SIZE=$(stat -f%z "$ARTIFACT_PATH" 2>/dev/null || stat -c%s "$ARTIFACT_PATH")
ARTIFACT_SIZE_MB=$((ARTIFACT_SIZE / 1024 / 1024))

if (( ARTIFACT_SIZE_MB < 30 )); then
    log_error "Artifact too small ($ARTIFACT_SIZE_MB MB). Minimum expected: 30 MB"
    exit 1
fi

if (( ARTIFACT_SIZE_MB > 200 )); then
    log_warning "Artifact very large ($ARTIFACT_SIZE_MB MB). Maximum expected: 200 MB"
fi

log_info "Size acceptable: $ARTIFACT_SIZE_MB MB"

# =============================================================================
# STEP 5: TEST EXTRACTION
# =============================================================================

log_step 5 6 "Testing extraction"

# Create temporary test directory
TEST_DIR=$(create_temp_directory "validate_cpython_")
log_info "Test directory: $TEST_DIR"

# Extract artifact
if ! extract_tarball "$ARTIFACT_PATH" "$TEST_DIR"; then
    log_error "Failed to extract tarball"
    cleanup_temp_directory "$TEST_DIR"
    exit 1
fi

log_info "Extraction successful"

# =============================================================================
# STEP 6: VALIDATE ARTIFACT CONTENT
# =============================================================================

log_step 6 6 "Validating artifact content"

# Detect Python directory
PYTHON_DIR=$(find "$TEST_DIR/opt" -maxdepth 1 -name "python-*" -type d 2>/dev/null | head -1)

if [[ -z "$PYTHON_DIR" ]]; then
    log_error "Python directory not found in artifact"
    cleanup_temp_directory "$TEST_DIR"
    exit 1
fi

PYTHON_VERSION=$(basename "$PYTHON_DIR" | sed 's/python-//')
PYTHON_MAJOR_MINOR=$(get_version_major_minor "$PYTHON_VERSION")

log_info "Detected version: $PYTHON_VERSION"

# Verify main binary
PYTHON_BIN="$PYTHON_DIR/bin/python${PYTHON_MAJOR_MINOR}"

if ! validate_file_exists "$PYTHON_BIN" "Python binary not found: $PYTHON_BIN"; then
    cleanup_temp_directory "$TEST_DIR"
    exit 1
fi

chmod +x "$PYTHON_BIN"
log_info "Binary exists and is executable"

# Verify binary version
export LD_LIBRARY_PATH="$PYTHON_DIR/lib:${LD_LIBRARY_PATH:-}"
BINARY_VERSION=$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')

if [[ "$BINARY_VERSION" != "$PYTHON_VERSION" ]]; then
    log_error "Binary version ($BINARY_VERSION) does not match expected ($PYTHON_VERSION)"
    cleanup_temp_directory "$TEST_DIR"
    exit 1
fi

log_info "Binary version correct: $BINARY_VERSION"

# Verify critical native modules
log_info "Verifying critical native modules..."

# Usar REQUIRED_MODULES del config si existe, sino usar default
MODULES_TO_CHECK=("${REQUIRED_MODULES[@]:-ssl sqlite3 uuid lzma bz2 zlib _ctypes}")
FAILED_MODULES=()

for module in "${MODULES_TO_CHECK[@]}"; do
    if "$PYTHON_BIN" -c "import $module" 2>/dev/null; then
        log_info "  Module $module: OK"
    else
        log_error "  Module $module: FAILED"
        FAILED_MODULES+=("$module")
    fi
done

if (( ${#FAILED_MODULES[@]} > 0 )); then
    log_error "Failed modules: ${FAILED_MODULES[*]}"
    cleanup_temp_directory "$TEST_DIR"
    exit 1
fi

# Verify pip
PIP_BIN="$PYTHON_DIR/bin/pip${PYTHON_MAJOR_MINOR}"

if ! validate_file_exists "$PIP_BIN" "pip not found"; then
    cleanup_temp_directory "$TEST_DIR"
    exit 1
fi

chmod +x "$PIP_BIN"
PIP_VERSION=$("$PIP_BIN" --version 2>&1 | head -1)
log_info "pip available: $PIP_VERSION"

# Check build info (optional)
BUILD_INFO="$PYTHON_DIR/.build-info"
if [[ -f "$BUILD_INFO" ]]; then
    log_info "Build info present"
else
    log_warning "Build info not found (optional)"
fi

# Check LICENSE (optional)
LICENSE_FILE="$PYTHON_DIR/LICENSE"
if [[ -f "$LICENSE_FILE" ]]; then
    log_info "LICENSE present"
else
    log_warning "LICENSE not found (recommended)"
fi

# =============================================================================
# CLEANUP
# =============================================================================

log_info "Cleaning up temporary files..."
cleanup_temp_directory "$TEST_DIR"

# =============================================================================
# FINAL SUMMARY
# =============================================================================

echo ""
log_header "Validation Completed Successfully" 73
log_info "Artifact:  $ARTIFACT_NAME"
log_info "Version:   Python $PYTHON_VERSION"
log_info "Size:      $ARTIFACT_SIZE_MB MB"
log_info "Checksum:  $CHECKSUM"
echo ""
log_info "The artifact is valid and ready for distribution"
echo ""
log_info "Next step:"
log_info "  gh release create cpython-${PYTHON_VERSION}-build<N> \\"
log_info "    $ARTIFACT_PATH \\"
log_info "    $ARTIFACT_CHECKSUM \\"
log_info "    --title 'CPython $PYTHON_VERSION Build <N>' \\"
log_info "    --notes 'Precompiled CPython for Ubuntu 20.04'"
log_separator 73