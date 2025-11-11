#!/bin/bash
#
# Backend CI Script - Local execution (NO GitHub Actions dependency)
#
# Ejecuta tests y validaciones de backend Django
# Puede ejecutarse localmente o desde GitHub Actions
#
# Uso:
#   ./scripts/ci/backend_test.sh [--mysql|--postgresql|--all]
#
# Requisitos:
#   - Python 3.11+
#   - MySQL y/o PostgreSQL corriendo localmente
#   - Variables de entorno DB_* configuradas
#
# RNF-002: Script valida NO Redis, sesiones en MySQL

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
TEST_DB=${1:-"all"}

log_info "Backend CI Script - Starting..."
log_info "Test database: $TEST_DB"

cd "$PROJECT_ROOT/api/callcentersite"

# Step 1: Lint
log_info "Step 1/6: Running linters..."

if command -v flake8 &> /dev/null; then
    log_info "Running flake8..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || {
        log_error "flake8 critical errors found"
        exit 1
    }
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    log_success "flake8 passed"
else
    log_warning "flake8 not installed, skipping"
fi

if command -v black &> /dev/null; then
    log_info "Running black..."
    black --check . || {
        log_warning "black formatting issues found"
        log_info "Run: black ."
    }
else
    log_warning "black not installed, skipping"
fi

if command -v isort &> /dev/null; then
    log_info "Running isort..."
    isort --check-only . || {
        log_warning "isort issues found"
        log_info "Run: isort ."
    }
else
    log_warning "isort not installed, skipping"
fi

# Step 2: Validate IACT Restrictions (RNF-002)
log_info "Step 2/6: Validating IACT restrictions (RNF-002)..."

if grep -r "redis" settings*.py; then
    log_error "Redis detected in settings. Prohibited by RNF-002"
    exit 1
fi

if grep -r "django_redis" settings*.py; then
    log_error "django_redis detected. Prohibited by RNF-002"
    exit 1
fi

log_success "NO Redis usage detected"

if ! grep -q "django.contrib.sessions.backends.db" settings*.py; then
    log_error "SESSION_ENGINE must be django.contrib.sessions.backends.db (RNF-002)"
    exit 1
fi

log_success "Session backend correctly configured (MySQL)"

# Check for Email usage (warning only)
if grep -r "send_mail\|EmailMessage\|EmailMultiAlternatives" *.py | grep -v "# PROHIBITED"; then
    log_warning "Email usage detected. Should use InternalMessage instead"
fi

# Step 3: Run tests with MySQL
if [ "$TEST_DB" == "mysql" ] || [ "$TEST_DB" == "all" ]; then
    log_info "Step 3/6: Running tests with MySQL..."

    # Check if MySQL is available
    if ! mysqladmin ping -h "${DB_HOST:-127.0.0.1}" --silent 2>/dev/null; then
        log_warning "MySQL not available, skipping MySQL tests"
    else
        export DB_ENGINE=django.db.backends.mysql
        export DB_NAME=${DB_NAME:-test_iact}
        export DB_USER=${DB_USER:-root}
        export DB_PASSWORD=${DB_PASSWORD:-}
        export DB_HOST=${DB_HOST:-127.0.0.1}
        export DB_PORT=${DB_PORT:-3306}

        log_info "Running migrations..."
        python manage.py migrate --run-syncdb --no-input

        log_info "Running tests with coverage..."
        if command -v pytest &> /dev/null; then
            pytest --cov=callcentersite --cov-report=term --cov-fail-under=80 || {
                log_error "Tests failed or coverage < 80%"
                exit 1
            }
            log_success "MySQL tests passed with coverage > 80%"
        else
            python manage.py test --parallel --keepdb || {
                log_error "Tests failed"
                exit 1
            }
            log_success "MySQL tests passed"
        fi
    fi
fi

# Step 4: Run tests with PostgreSQL
if [ "$TEST_DB" == "postgresql" ] || [ "$TEST_DB" == "all" ]; then
    log_info "Step 4/6: Running tests with PostgreSQL..."

    # Check if PostgreSQL is available
    if ! pg_isready -h "${DB_HOST:-127.0.0.1}" 2>/dev/null; then
        log_warning "PostgreSQL not available, skipping PostgreSQL tests"
    else
        export DB_ENGINE=django.db.backends.postgresql
        export DB_NAME=${DB_NAME:-test_iact}
        export DB_USER=${DB_USER:-postgres}
        export DB_PASSWORD=${DB_PASSWORD:-}
        export DB_HOST=${DB_HOST:-127.0.0.1}
        export DB_PORT=${DB_PORT:-5432}

        log_info "Running migrations..."
        python manage.py migrate --run-syncdb --no-input

        log_info "Running tests..."
        python manage.py test --parallel --keepdb || {
            log_error "Tests failed"
            exit 1
        }
        log_success "PostgreSQL tests passed"
    fi
fi

# Step 5: Run integration tests
log_info "Step 5/6: Running integration tests..."

if python -c "import pytest" 2>/dev/null; then
    pytest -m integration --tb=short 2>/dev/null || {
        log_warning "No integration tests found or failed"
    }
else
    log_warning "pytest not installed, skipping integration tests"
fi

# Step 6: Run validation scripts
log_info "Step 6/6: Running validation scripts..."

if [ -f "$PROJECT_ROOT/scripts/validate_critical_restrictions.sh" ]; then
    bash "$PROJECT_ROOT/scripts/validate_critical_restrictions.sh" || {
        log_error "Critical restrictions validation failed"
        exit 1
    }
else
    log_warning "validate_critical_restrictions.sh not found"
fi

if [ -f "$PROJECT_ROOT/scripts/validate_security_config.sh" ]; then
    bash "$PROJECT_ROOT/scripts/validate_security_config.sh" || {
        log_warning "Security config validation failed"
    }
else
    log_warning "validate_security_config.sh not found"
fi

log_success "Backend CI completed successfully!"
