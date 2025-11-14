#!/usr/bin/env bash
# scripts/utils/colors.sh
# Terminal color constants (DEPRECATED - use logging.sh)

if [ -t 1 ]; then
    export COLOR_RED='\033[0;31m'
    export COLOR_GREEN='\033[0;32m'
    export COLOR_YELLOW='\033[0;33m'
    export COLOR_BLUE='\033[0;34m'
    export COLOR_RESET='\033[0m'
else
    export COLOR_RED=''
    export COLOR_GREEN=''
    export COLOR_YELLOW=''
    export COLOR_BLUE=''
    export COLOR_RESET=''
fi
