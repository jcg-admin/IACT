#!/usr/bin/env bash
# scripts/utils/logging.sh
# Shared logging utilities
# Usage: source scripts/utils/logging.sh

# Enable colors if terminal supports it
if [ -t 1 ]; then
    readonly RED='\033[0;31m'
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[0;33m'
    readonly BLUE='\033[0;34m'
    readonly NC='\033[0m' # No Color
else
    readonly RED=''
    readonly GREEN=''
    readonly YELLOW=''
    readonly BLUE=''
    readonly NC=''
fi

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_debug() {
    if [ "${DEBUG:-0}" = "1" ]; then
        echo -e "${BLUE}[DEBUG]${NC} $*" >&2
    fi
}

# Log with timestamp
log_timestamp() {
    local level="$1"
    shift
    local timestamp=$(date -Iseconds)
    echo "[$timestamp] [$level] $*"
}

# Log to file
log_to_file() {
    local logfile="$1"
    shift
    echo "[$(date -Iseconds)] $*" >> "$logfile"
}

# Progress bar
progress_bar() {
    local current="$1"
    local total="$2"
    local width=50

    local percent=$((current * 100 / total))
    local filled=$((current * width / total))

    printf "\r["
    printf "%${filled}s" | tr ' ' '='
    printf "%$((width - filled))s" | tr ' ' ' '
    printf "] %3d%%" "$percent"
}
