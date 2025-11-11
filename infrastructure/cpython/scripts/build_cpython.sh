#!/bin/bash
#
# build_cpython.sh - Build CPython from source
#
# Reference: SPEC_INFRA_001
# Purpose: Generate reproducible precompiled CPython artifact
#
# Usage:
#   ./build_cpython.sh <version> [build-number] [--force]
#
# Examples:
#   ./build_cpython.sh 3.12.6
#   ./build_cpython.sh 3.12.6 2
#   ./build_cpython.sh 3.12.6 1 --force
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
    log_error "Usage: $0 <version> [build-number] [--force]"
    log_error "Example: $0 3.12.6 1"
    log_error "  --force: Overwrite existing artifact without prompting"
    exit 1
fi

PYTHON_VERSION="$1"
BUILD_NUMBER="${2:-${DEFAULT_BUILD_NUMBER:-1}}"
DISTRO="${DISTRO:-ubuntu20.04}"
FORCE_BUILD=0

# Parse optional arguments
for arg in "$@"; do
    if [[ "$arg" == "--force" ]]; then
        FORCE_BUILD=1
    fi
done

# =============================================================================
# VALIDATION AND CONFIGURATION
# =============================================================================

# Validate version format
if ! validate_version_format "$PYTHON_VERSION"; then
    exit 1
fi

# Extract major.minor for directories
PYTHON_MAJOR_MINOR=$(get_version_major_minor "$PYTHON_VERSION")

# Configuration
BUILD_DIR="/tmp/cpython-build"
SOURCE_DIR="$BUILD_DIR/Python-$PYTHON_VERSION"
INSTALL_PREFIX="/opt/python-$PYTHON_VERSION"
ARTIFACT_DIR="/vagrant/artifacts/cpython"
ARTIFACT_NAME=$(parse_artifact_name "$PYTHON_VERSION" "$DISTRO" "$BUILD_NUMBER")
ARTIFACT_PATH="$ARTIFACT_DIR/$ARTIFACT_NAME"

# =============================================================================
# DISPLAY BUILD INFO
# =============================================================================

log_header "Building CPython $PYTHON_VERSION" 73
log_info "Build number: $BUILD_NUMBER"
log_info "Distribution: $DISTRO"
log_info "Artifact: $ARTIFACT_NAME"
echo ""

# =============================================================================
# CHECK BUILD STATE
# =============================================================================

# Check if build is already complete
if is_operation_complete "build_cpython_${PYTHON_VERSION}_${BUILD_NUMBER}"; then
    log_info "Build already completed for this version and build number"
    if [[ $FORCE_BUILD -eq 0 ]]; then
        log_info "Use --force to rebuild or increment build number"
        exit 0
    else
        log_warning "Rebuilding with --force"
        reset_operation_state "build_cpython_${PYTHON_VERSION}_${BUILD_NUMBER}"
    fi
fi

# =============================================================================
# CHECK EXISTING ARTIFACT
# =============================================================================

# Verify artifact does not exist (idempotency)
if [[ -f "$ARTIFACT_PATH" ]]; then
    if [[ $FORCE_BUILD -eq 1 ]]; then
        log_warning "Artifact already exists: $ARTIFACT_PATH (overwriting with --force)"
        remove_path_safely "$ARTIFACT_PATH"
        remove_path_safely "$ARTIFACT_PATH.sha256"
    else
        log_error "Artifact already exists: $ARTIFACT_PATH"
        log_error "Use --force to overwrite or delete manually"
        log_error "Or increment build number: $0 $PYTHON_VERSION $((BUILD_NUMBER + 1))"
        exit 1
    fi
fi

# =============================================================================
# SETUP BUILD ENVIRONMENT
# =============================================================================

# Create directories
log_info "Creating working directories..."
ensure_directory_exists "$BUILD_DIR" || exit 1
ensure_directory_exists "$ARTIFACT_DIR" || exit 1

# Verify critical dependencies
log_info "Verifying system dependencies..."
CRITICAL_COMMANDS=("gcc" "make" "tar" "wget")
if ! validate_commands_exist "${CRITICAL_COMMANDS[@]}"; then
    log_error "Missing critical build tools"
    exit 1
fi

# Display critical library versions
log_info "Critical library versions:"
dpkg -l | grep -E "libssl-dev|libsqlite3-dev|liblzma-dev|libbz2-dev|libffi-dev" | \
    awk '{print "  " $2 ": " $3}' || log_warning "Could not list library versions"

# =============================================================================
# STEP 1: DOWNLOAD SOURCE CODE
# =============================================================================

log_step 1 5 "Downloading Python source code"

cd "$BUILD_DIR" || exit 1

PYTHON_URL="${PYTHON_DOWNLOAD_BASE:-https://www.python.org/ftp/python}/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
TARBALL="Python-$PYTHON_VERSION.tgz"

if [[ -d "$SOURCE_DIR" ]]; then
    log_warning "Source directory already exists"
    if [[ $FORCE_BUILD -eq 1 ]]; then
        log_warning "Removing existing directory with --force"
        remove_path_safely "$SOURCE_DIR"
        remove_path_safely "$TARBALL"
    else
        log_info "Using existing source code (use --force to re-download)"
    fi
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
    log_info "Downloading from: $PYTHON_URL"

    # Download with retry
    if ! download_file_with_retry "$PYTHON_URL" "$TARBALL" 5; then
        log_error "Failed to download source code"
        log_error "Verify that version $PYTHON_VERSION exists on python.org"
        exit 1
    fi

    # Verify tarball downloaded correctly
    if ! validate_file_exists "$TARBALL" || [[ ! -s "$TARBALL" ]]; then
        log_error "Downloaded tarball is empty or does not exist"
        exit 1
    fi

    log_info "Extracting source code..."
    if ! extract_tarball "$TARBALL" "$BUILD_DIR"; then
        log_error "Failed to extract tarball (possibly corrupted)"
        remove_path_safely "$TARBALL"
        exit 1
    fi

    if ! validate_directory_exists "$SOURCE_DIR" "Source directory not found after extraction"; then
        log_error "Unexpected structure in tarball"
        exit 1
    fi

    log_info "Source code extracted successfully"
fi

cd "$SOURCE_DIR" || exit 1

# =============================================================================
# STEP 2: CONFIGURE BUILD
# =============================================================================

log_step 2 5 "Configuring build with optimizations"

log_info "Configuration flags:"
log_info "  --prefix=$INSTALL_PREFIX"
log_info "  --enable-optimizations (PGO)"
log_info "  --with-lto (Link-Time Optimization)"
log_info "  --enable-shared"
log_info "  --with-system-ffi"
echo ""

# Clean previous build if exists
if [[ -f "Makefile" ]]; then
    log_info "Cleaning previous build..."
    make distclean || true
fi

# Execute configure
if ! ./configure \
    --prefix="$INSTALL_PREFIX" \
    --enable-optimizations \
    --with-lto \
    --enable-shared \
    --with-system-ffi \
    --enable-loadable-sqlite-extensions \
    2>&1 | tee configure.log; then
    log_error "Configuration failed. See configure.log for details"
    exit 1
fi

# =============================================================================
# STEP 3: COMPILE
# =============================================================================

log_step 3 5 "Compiling Python (may take 10-15 minutes with PGO)"

NPROC=$(nproc)
log_info "Using $NPROC cores in parallel..."
echo ""

if ! make -j"$NPROC" 2>&1 | tee make.log; then
    log_error "Compilation failed. See make.log for details"
    exit 1
fi

log_info "Compilation completed"

# =============================================================================
# STEP 4: INSTALL
# =============================================================================

log_step 4 5 "Installing to $INSTALL_PREFIX"

# Clean previous installation if exists (idempotency)
if [[ -d "$INSTALL_PREFIX" ]]; then
    log_warning "Previous installation found at $INSTALL_PREFIX, removing..."
    if ! sudo rm -rf "$INSTALL_PREFIX"; then
        log_error "Failed to remove previous installation (sudo required)"
        exit 1
    fi
    log_info "Previous installation removed"
fi

# Install
if ! sudo make install 2>&1 | tee make-install.log; then
    log_error "Installation failed. See make-install.log for details"
    exit 1
fi

log_info "Installation completed"

# =============================================================================
# VALIDATE INSTALLATION
# =============================================================================

log_info "Validating installation..."

PYTHON_BIN="$INSTALL_PREFIX/bin/python${PYTHON_MAJOR_MINOR}"
if ! validate_file_exists "$PYTHON_BIN" "Python binary not found"; then
    exit 1
fi

# Verify version
INSTALLED_VERSION=$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')
if [[ "$INSTALLED_VERSION" != "$PYTHON_VERSION" ]]; then
    log_error "Installed version ($INSTALLED_VERSION) does not match expected ($PYTHON_VERSION)"
    exit 1
fi

log_info "Correct version: $INSTALLED_VERSION"

# =============================================================================
# VALIDATE MODULES (Critical vs Optional)
# =============================================================================

log_info "Validating Python modules..."

# Critical modules - build fails if these are missing
# SSL is absolutely required for secure connections (pip, https, etc)
CRITICAL_MODULES=("ssl" "_ssl")
log_info "Checking critical modules: ${CRITICAL_MODULES[*]}"

if ! validate_python_modules "$PYTHON_BIN" "${CRITICAL_MODULES[@]}"; then
    log_error "Critical module validation failed"
    log_error "SSL support is required for secure connections (pip, https, etc)"
    log_error "Ensure libssl-dev was installed before building"
    exit 1
fi

log_info "✓ Critical modules validated successfully"

# Optional modules - warn if missing but don't fail build
# These enhance functionality but Python is still usable without them
OPTIONAL_MODULES=("sqlite3" "uuid" "lzma" "bz2" "zlib" "_ctypes")
log_info "Checking optional modules: ${OPTIONAL_MODULES[*]}"

missing_optional=()
for module in "${OPTIONAL_MODULES[@]}"; do
    # Set LD_LIBRARY_PATH temporarily for validation
    local lib_dir="$INSTALL_PREFIX/lib"
    if LD_LIBRARY_PATH="$lib_dir:${LD_LIBRARY_PATH:-}" "$PYTHON_BIN" -c "import $module" 2>/dev/null; then
        log_debug "Optional module $module: OK"
    else
        log_warning "Optional module $module: NOT AVAILABLE"
        missing_optional+=("$module")
    fi
done

if (( ${#missing_optional[@]} > 0 )); then
    log_warning "Some optional modules are missing: ${missing_optional[*]}"
    log_warning "Python will work but some functionality may be limited"
    log_warning "To enable these modules, install the corresponding -dev packages"
else
    log_info "✓ All optional modules validated successfully"
fi

# Verify pip
PIP_BIN="$INSTALL_PREFIX/bin/pip${PYTHON_MAJOR_MINOR}"
if ! validate_file_exists "$PIP_BIN" "pip not found"; then
    exit 1
fi

PIP_VERSION=$("$PIP_BIN" --version 2>&1)
log_info "pip available: $PIP_VERSION"

# =============================================================================
# DOCUMENT BUILD INFO
# =============================================================================

log_info "Documenting build information..."
cat > "$INSTALL_PREFIX/.build-info" <<EOF
CPython Build Information
=========================

Version: $PYTHON_VERSION
Build Number: $BUILD_NUMBER
Distribution: $DISTRO
Build Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Build Host: $(hostname)

System Libraries:
$(dpkg -l | grep -E "libssl-dev|libsqlite3-dev|liblzma-dev|libbz2-dev|libffi-dev" | awk '{print $2 ": " $3}')

Configure Flags:
  --prefix=$INSTALL_PREFIX
  --enable-optimizations
  --with-lto
  --enable-shared
  --with-system-ffi
  --enable-loadable-sqlite-extensions

Validated Modules:
$(for mod in "${MODULES_TO_CHECK[@]}"; do echo "  - $mod"; done)
EOF

log_info "Build info saved to $INSTALL_PREFIX/.build-info"

# Include Python LICENSE (PSF)
log_info "Copying Python LICENSE..."
if [[ -f "LICENSE" ]]; then
    if ! sudo cp LICENSE "$INSTALL_PREFIX/LICENSE"; then
        log_error "Failed to copy LICENSE (sudo required)"
        exit 1
    fi
    log_info "LICENSE copied"
else
    log_warning "LICENSE not found in source code"
fi

# =============================================================================
# STEP 5: PACKAGE ARTIFACT
# =============================================================================

log_step 5 5 "Packaging artifact"

cd /opt || exit 1
if ! sudo tar czf "$ARTIFACT_PATH" "python-$PYTHON_VERSION"; then
    log_error "Failed to create tarball"
    exit 1
fi

# Adjust artifact permissions
if ! sudo chown vagrant:vagrant "$ARTIFACT_PATH" 2>/dev/null; then
    CURRENT_USER=$(whoami)
    if ! sudo chown "$CURRENT_USER:$CURRENT_USER" "$ARTIFACT_PATH" 2>/dev/null; then
        log_warning "Could not adjust artifact permissions (may require sudo)"
    fi
fi

if [[ ! -r "$ARTIFACT_PATH" ]]; then
    log_error "Artifact created but not readable"
    exit 1
fi

ARTIFACT_SIZE=$(du -h "$ARTIFACT_PATH" | cut -f1)
log_info "Artifact created: $ARTIFACT_PATH ($ARTIFACT_SIZE)"

# Generate SHA256 checksum
log_info "Generating SHA256 checksum..."
cd "$ARTIFACT_DIR" || exit 1
sha256sum "$ARTIFACT_NAME" > "$ARTIFACT_NAME.sha256"

CHECKSUM=$(cut -d' ' -f1 "$ARTIFACT_NAME.sha256")
log_info "Checksum: $CHECKSUM"

# =============================================================================
# MARK BUILD COMPLETE
# =============================================================================

# Mark build as complete
mark_operation_complete "build_cpython_${PYTHON_VERSION}_${BUILD_NUMBER}" \
    "version=$PYTHON_VERSION" \
    "build_number=$BUILD_NUMBER" \
    "artifact=$ARTIFACT_NAME" \
    "size=$ARTIFACT_SIZE" \
    "checksum=$CHECKSUM"

# =============================================================================
# FINAL SUMMARY
# =============================================================================

echo ""
log_header "Build completed successfully" 73
log_info "Artifact: $ARTIFACT_PATH"
log_info "Checksum: $ARTIFACT_PATH.sha256"
log_info "Size:     $ARTIFACT_SIZE"
echo ""
log_info "Next steps:"
log_info "  1. Validate artifact: ./validate_build.sh $ARTIFACT_NAME"
log_info "  2. Publish to GitHub Releases (manual or with gh CLI)"
log_info "  3. Update artifacts/ARTIFACTS.md"
echo ""
log_info "Build metadata saved in: $INSTALL_PREFIX/.build-info"
log_separator 73
