#!/bin/bash
# validate-docker.sh
#
# Validate Docker Configuration
# Replica: Infrastructure CI / Validate Docker Configuration
#
# Exit codes:
#   0 - Docker config valid
#   1 - Docker config invalid
#   2 - Docker not used (skip)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

log_info "Validating Docker configuration..."

# Check if Docker is used
if [ ! -f "$PROJECT_ROOT/Dockerfile" ] && [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    log_warn "No Docker files found - skipping Docker validation"
    exit 2
fi

CHECKS_PASSED=0
CHECKS_FAILED=0

# Check 1: Validate Dockerfile
if [ -f "$PROJECT_ROOT/Dockerfile" ]; then
    log_info "Found Dockerfile"

    # Check for FROM instruction
    if grep -q "^FROM" "$PROJECT_ROOT/Dockerfile"; then
        log_info "Dockerfile has FROM instruction"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        log_error "Dockerfile missing FROM instruction"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi

    # Check for security best practices
    if grep -q "USER" "$PROJECT_ROOT/Dockerfile"; then
        log_info "Dockerfile uses USER instruction (good practice)"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        log_warn "Dockerfile doesn't use USER instruction (runs as root)"
    fi
fi

# Check 2: Validate docker-compose.yml
if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    log_info "Found docker-compose.yml"

    if command -v docker-compose &> /dev/null; then
        if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" config &> /dev/null; then
            log_info "docker-compose.yml is valid"
            CHECKS_PASSED=$((CHECKS_PASSED + 1))
        else
            log_error "docker-compose.yml is invalid"
            CHECKS_FAILED=$((CHECKS_FAILED + 1))
        fi
    else
        log_warn "docker-compose not installed - skipping validation"
    fi
fi

# Summary
echo ""
log_info "Docker Validation Summary"
log_info "Passed: $CHECKS_PASSED"
log_error "Failed: $CHECKS_FAILED"

if [ $CHECKS_FAILED -eq 0 ]; then
    log_info "Docker configuration is valid"
    exit 0
else
    log_error "Docker configuration has issues"
    exit 1
fi
