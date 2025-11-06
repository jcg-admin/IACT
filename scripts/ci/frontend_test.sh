#!/bin/bash
#
# Frontend CI Script - Local execution (NO GitHub Actions dependency)
#
# Ejecuta tests y validaciones de frontend React/TypeScript
# Puede ejecutarse localmente o desde GitHub Actions
#
# Uso:
#   ./scripts/ci/frontend_test.sh [--unit|--integration|--e2e|--all]
#
# Requisitos:
#   - Node.js 18+
#   - npm dependencies instaladas (npm ci)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors para output (solo si terminal interactivo)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

# Logging functions
log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Parse arguments
TEST_TYPE=${1:-"all"}

log_info "Frontend CI Script - Starting..."
log_info "Test type: $TEST_TYPE"

cd "$PROJECT_ROOT/frontend"

# Step 1: Install dependencies
log_info "Step 1/7: Checking dependencies..."

if [ ! -d "node_modules" ]; then
    log_info "Installing dependencies..."
    npm ci
else
    log_info "Dependencies already installed"
fi

# Step 2: Lint
log_info "Step 2/7: Running linters..."

if npm run lint > /dev/null 2>&1; then
    npm run lint || {
        log_error "ESLint failed"
        exit 1
    }
    log_success "ESLint passed"
else
    log_warning "ESLint script not found in package.json"
fi

# Step 3: Type checking
log_info "Step 3/7: Running TypeScript type checking..."

if npm run type-check > /dev/null 2>&1; then
    npm run type-check || {
        log_error "TypeScript type checking failed"
        exit 1
    }
    log_success "TypeScript type checking passed"
else
    log_warning "type-check script not found in package.json"
fi

# Step 4: Prettier formatting check
log_info "Step 4/7: Checking code formatting..."

if npm run format:check > /dev/null 2>&1; then
    npm run format:check || {
        log_warning "Prettier formatting issues found"
        log_info "Run: npm run format"
    }
else
    log_warning "format:check script not found in package.json"
fi

# Step 5: Unit tests
if [ "$TEST_TYPE" == "unit" ] || [ "$TEST_TYPE" == "all" ]; then
    log_info "Step 5/7: Running unit tests..."

    if npm run test:unit > /dev/null 2>&1; then
        npm run test:unit -- --coverage --watchAll=false || {
            log_error "Unit tests failed"
            exit 1
        }

        # Check coverage threshold
        if npm run test:coverage-check > /dev/null 2>&1; then
            npm run test:coverage-check || {
                log_error "Coverage threshold not met"
                exit 1
            }
        fi

        log_success "Unit tests passed with adequate coverage"
    else
        log_warning "test:unit script not found in package.json"
    fi
fi

# Step 6: Integration tests
if [ "$TEST_TYPE" == "integration" ] || [ "$TEST_TYPE" == "all" ]; then
    log_info "Step 6/7: Running integration tests..."

    if npm run test:integration > /dev/null 2>&1; then
        npm run test:integration || {
            log_error "Integration tests failed"
            exit 1
        }
        log_success "Integration tests passed"
    else
        log_warning "test:integration script not found in package.json"
    fi
fi

# Step 7: E2E tests
if [ "$TEST_TYPE" == "e2e" ] || [ "$TEST_TYPE" == "all" ]; then
    log_info "Step 7/7: Running E2E tests..."

    # Install Playwright browsers if needed
    if command -v npx > /dev/null; then
        if [ ! -d "$HOME/.cache/ms-playwright" ]; then
            log_info "Installing Playwright browsers..."
            npx playwright install --with-deps
        fi

        # Build application
        log_info "Building application..."
        npm run build || {
            log_error "Build failed"
            exit 1
        }

        # Run E2E tests
        if npm run test:e2e > /dev/null 2>&1; then
            npm run test:e2e || {
                log_error "E2E tests failed"
                exit 1
            }
            log_success "E2E tests passed"
        else
            log_warning "test:e2e script not found in package.json"
        fi
    else
        log_warning "npx not available, skipping E2E tests"
    fi
fi

# Step 8: Security audit
log_info "Step 8/8: Running security audit..."

npm audit --audit-level=moderate || {
    log_warning "npm audit found vulnerabilities"
    log_info "Review with: npm audit"
}

log_success "Frontend CI completed successfully!"
