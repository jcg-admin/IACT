#!/bin/bash
# validate-config.sh
#
# Validate Configuration Files
# Replica: Infrastructure CI / Validate Configuration Files
#
# Exit codes:
#   0 - All configs valid
#   1 - Some configs invalid

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

log_info "Validating configuration files..."

CONFIGS_VALID=0
CONFIGS_INVALID=0

# Check 1: Validate JSON files
log_info "Checking JSON files..."
JSON_FILES=$(find "$PROJECT_ROOT" -type f -name "*.json" ! -path "*/node_modules/*" ! -path "*/.venv/*" ! -path "*/venv/*")

for json_file in $JSON_FILES; do
    if python3 -c "import json; json.load(open('$json_file'))" &> /dev/null; then
        log_info "Valid JSON: $json_file"
        CONFIGS_VALID=$((CONFIGS_VALID + 1))
    else
        log_error "Invalid JSON: $json_file"
        CONFIGS_INVALID=$((CONFIGS_INVALID + 1))
    fi
done

# Check 2: Validate YAML files (if any)
log_info "Checking YAML files..."
YAML_FILES=$(find "$PROJECT_ROOT" -type f \( -name "*.yml" -o -name "*.yaml" \) ! -path "*/node_modules/*" ! -path "*/.venv/*")

if [ -n "$YAML_FILES" ]; then
    for yaml_file in $YAML_FILES; do
        if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" &> /dev/null; then
            log_info "Valid YAML: $yaml_file"
            CONFIGS_VALID=$((CONFIGS_VALID + 1))
        else
            log_error "Invalid YAML: $yaml_file"
            CONFIGS_INVALID=$((CONFIGS_INVALID + 1))
        fi
    done
fi

# Check 3: Validate Django settings
log_info "Checking Django settings..."
cd "$PROJECT_ROOT/api/callcentersite"

if [ -f "callcentersite/settings.py" ]; then
    if python3 -c "from callcentersite import settings" &> /dev/null; then
        log_info "Django settings: Valid"
        CONFIGS_VALID=$((CONFIGS_VALID + 1))
    else
        log_error "Django settings: Invalid"
        CONFIGS_INVALID=$((CONFIGS_INVALID + 1))
    fi
fi

# Summary
echo ""
log_info "Configuration Validation Summary"
log_info "Valid: $CONFIGS_VALID"
log_error "Invalid: $CONFIGS_INVALID"

if [ $CONFIGS_INVALID -eq 0 ]; then
    log_info "All configurations are valid"
    exit 0
else
    log_error "Some configurations are invalid"
    exit 1
fi
