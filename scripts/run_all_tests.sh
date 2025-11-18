#!/bin/bash
# scripts/run_all_tests.sh
# Ejecuta suite completa de tests: backend, UI, security, coverage
#
# Uso:
#   ./scripts/run_all_tests.sh [OPTIONS]
#
# Options:
#   --help                 Muestra esta ayuda
#   --skip-backend         Omite tests de backend
#   --skip-ui              Omite tests de la interfaz (alias: --skip-frontend)
#   --skip-security        Omite security scan
#   --verbose              Modo verbose
#
# Ejemplo:
#   ./scripts/run_all_tests.sh
#   ./scripts/run_all_tests.sh --skip-ui --verbose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$PROJECT_ROOT/api"
UI_DIR="$PROJECT_ROOT/ui"

# Opciones
SKIP_BACKEND=false
SKIP_UI=false
SKIP_SECURITY=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            head -n 20 "$0" | grep "^#" | sed 's/^# \?//'
            exit 0
            ;;
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-ui|--skip-frontend)
            SKIP_UI=true
            shift
            ;;
        --skip-security)
            SKIP_SECURITY=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "[ERROR] Opcion desconocida: $1"
            echo "Usa --help para ver opciones disponibles"
            exit 1
            ;;
    esac
done

echo "========================================================================"
echo "SUITE COMPLETA DE TESTS - Proyecto IACT"
echo "========================================================================"
echo "[INFO] Directorio del proyecto: $PROJECT_ROOT"
echo ""

FAILED=0
START_TIME=$(date +%s)

# ==============================================================================
# 1. BACKEND TESTS
# ==============================================================================
if [ "$SKIP_BACKEND" = false ]; then
    echo "[1] Ejecutando tests de backend..."
    echo "----------------------------------------------------------------------"

    if [ ! -d "$API_DIR" ]; then
        echo "[FAIL] Directorio $API_DIR no existe"
        FAILED=$((FAILED + 1))
    else
        cd "$API_DIR/callcentersite" || exit 1

        # Ejecutar tests con coverage
        if [ "$VERBOSE" = true ]; then
            pytest --cov=. --cov-report=term --cov-fail-under=80 -v
        else
            pytest --cov=. --cov-report=term --cov-fail-under=80 -q
        fi

        if [ $? -eq 0 ]; then
            echo "[OK] Tests de backend PASARON (coverage >= 80%)"
        else
            echo "[FAIL] Tests de backend FALLARON o coverage < 80%"
            FAILED=$((FAILED + 1))
        fi

        cd "$PROJECT_ROOT" || exit 1
    fi
    echo ""
fi

# ==============================================================================
# 2. UI TESTS
# ==============================================================================
if [ "$SKIP_UI" = false ]; then
    echo "[2] Ejecutando tests de UI..."
    echo "----------------------------------------------------------------------"

    if [ ! -d "$UI_DIR" ]; then
        echo "[WARNING] Directorio $UI_DIR no existe - omitiendo tests de UI"
    else
        cd "$UI_DIR" || exit 1

        # Verificar si package.json existe
        if [ ! -f "package.json" ]; then
            echo "[WARNING] package.json no encontrado - omitiendo tests de UI"
        else
            # Ejecutar tests de UI
            if [ "$VERBOSE" = true ]; then
                npm test -- --verbose
            else
                npm test
            fi

            if [ $? -eq 0 ]; then
                echo "[OK] Tests de UI PASARON"
            else
                echo "[FAIL] Tests de UI FALLARON"
                FAILED=$((FAILED + 1))
            fi
        fi

        cd "$PROJECT_ROOT" || exit 1
    fi
    echo ""
fi

# ==============================================================================
# 3. SECURITY SCAN
# ==============================================================================
if [ "$SKIP_SECURITY" = false ]; then
    echo "[3] Ejecutando security scan..."
    echo "----------------------------------------------------------------------"

    if [ -f "$SCRIPT_DIR/ci/security_scan.sh" ]; then
        bash "$SCRIPT_DIR/ci/security_scan.sh"

        if [ $? -eq 0 ]; then
            echo "[OK] Security scan PASO"
        else
            echo "[FAIL] Security scan FALLO"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "[WARNING] Script security_scan.sh no encontrado - omitiendo"
    fi
    echo ""
fi

# ==============================================================================
# 4. VALIDACIONES CRITICAS
# ==============================================================================
echo "[4] Ejecutando validaciones criticas..."
echo "----------------------------------------------------------------------"

if [ -f "$SCRIPT_DIR/validate_critical_restrictions.sh" ]; then
    bash "$SCRIPT_DIR/validate_critical_restrictions.sh"

    if [ $? -eq 0 ]; then
        echo "[OK] Validaciones criticas PASARON"
    else
        echo "[FAIL] Validaciones criticas FALLARON"
        FAILED=$((FAILED + 1))
    fi
else
    echo "[WARNING] Script validate_critical_restrictions.sh no encontrado"
fi
echo ""

# ==============================================================================
# RESUMEN
# ==============================================================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "========================================================================"
echo "RESUMEN DE TESTS"
echo "========================================================================"
echo "[INFO] Tiempo total: ${DURATION}s"

if [ $FAILED -eq 0 ]; then
    echo "[OK] TODOS LOS TESTS PASARON"
    echo ""
    exit 0
else
    echo "[FAIL] $FAILED test suite(s) FALLARON"
    echo ""
    echo "Para correr individual:"
    echo "  Backend:      ./scripts/ci/backend_test.sh"
    echo "  UI (manual):  npm test (dentro de ./ui/)"
    echo "  Security:     ./scripts/ci/security_scan.sh"
    echo "  Validaciones: ./scripts/validate_critical_restrictions.sh"
    echo ""
    exit 1
fi
