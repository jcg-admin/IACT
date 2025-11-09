#!/bin/bash
# Funciones comunes compartidas por todos los scripts
# Constitution compliant utilities

# Colors para output (opcional)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_debug() {
    if [ "${DEBUG:-0}" -eq 1 ]; then
        echo -e "${BLUE}[DEBUG]${NC} $*" >&2
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get project root directory
get_project_root() {
    git rev-parse --show-toplevel 2>/dev/null || pwd
}

# Count files matching pattern
count_files() {
    local pattern="$1"
    local path="${2:-.}"
    find "$path" -type f -name "$pattern" 2>/dev/null | wc -l
}
