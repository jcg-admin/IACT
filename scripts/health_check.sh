#!/bin/bash
# scripts/health_check.sh
# Health check completo del proyecto IACT
#
# Valida:
#   - API backend (Django)
#   - PostgreSQL connectivity
#   - MySQL connectivity
#   - SESSION_ENGINE (MySQL, NO Redis)
#   - Servicios criticos
#
# Uso:
#   ./scripts/health_check.sh [OPTIONS]
#
# Options:
#   --help                 Muestra esta ayuda
#   --verbose              Modo verbose
#   --json                 Output en formato JSON
#
# Ejemplo:
#   ./scripts/health_check.sh
#   ./scripts/health_check.sh --verbose
#   ./scripts/health_check.sh --json > health_status.json

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$PROJECT_ROOT/api"

# Opciones
VERBOSE=false
JSON_OUTPUT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            head -n 25 "$0" | grep "^#" | sed 's/^# \?//'
            exit 0
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            echo "[ERROR] Opcion desconocida: $1"
            echo "Usa --help para ver opciones disponibles"
            exit 1
            ;;
    esac
done

if [ "$JSON_OUTPUT" = false ]; then
    echo "========================================================================"
    echo "HEALTH CHECK - Proyecto IACT"
    echo "========================================================================"
    echo "[INFO] Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "[INFO] Hostname: $(hostname)"
    echo ""
fi

FAILED=0
CHECKS_TOTAL=0
CHECKS_PASSED=0

# JSON output storage
if [ "$JSON_OUTPUT" = true ]; then
    JSON_RESULTS="{"
    JSON_RESULTS="${JSON_RESULTS}\"timestamp\":\"$(date -Iseconds)\","
    JSON_RESULTS="${JSON_RESULTS}\"hostname\":\"$(hostname)\","
    JSON_RESULTS="${JSON_RESULTS}\"checks\":["
    FIRST_CHECK=true
fi

# Helper function para agregar resultado
add_result() {
    local check_name="$1"
    local status="$2"  # "pass" or "fail"
    local message="$3"

    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))

    if [ "$status" = "pass" ]; then
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        if [ "$JSON_OUTPUT" = false ]; then
            echo "[OK] $check_name"
            if [ "$VERBOSE" = true ] && [ ! -z "$message" ]; then
                echo "     $message"
            fi
        fi
    else
        FAILED=$((FAILED + 1))
        if [ "$JSON_OUTPUT" = false ]; then
            echo "[FAIL] $check_name"
            if [ ! -z "$message" ]; then
                echo "       $message"
            fi
        fi
    fi

    if [ "$JSON_OUTPUT" = true ]; then
        if [ "$FIRST_CHECK" = false ]; then
            JSON_RESULTS="${JSON_RESULTS},"
        fi
        JSON_RESULTS="${JSON_RESULTS}{\"name\":\"$check_name\",\"status\":\"$status\",\"message\":\"$message\"}"
        FIRST_CHECK=false
    fi
}

# ==============================================================================
# 1. DJANGO PROJECT EXISTS
# ==============================================================================
if [ "$JSON_OUTPUT" = false ]; then
    echo "[1] Verificando proyecto Django..."
fi

if [ ! -d "$API_DIR/callcentersite" ]; then
    add_result "Django project exists" "fail" "Directorio callcentersite no encontrado"
else
    add_result "Django project exists" "pass" "$API_DIR/callcentersite"
fi

if [ "$JSON_OUTPUT" = false ]; then echo ""; fi

# ==============================================================================
# 2. PYTHON DEPENDENCIES
# ==============================================================================
if [ "$JSON_OUTPUT" = false ]; then
    echo "[2] Verificando dependencias Python..."
fi

cd "$API_DIR/callcentersite" || exit 1

if python -c "import django" 2>/dev/null; then
    DJANGO_VERSION=$(python -c "import django; print(django.get_version())")
    add_result "Django installed" "pass" "Version: $DJANGO_VERSION"
else
    add_result "Django installed" "fail" "Django no esta instalado"
fi

if python -c "import psycopg2" 2>/dev/null; then
    add_result "psycopg2 installed" "pass" "PostgreSQL driver disponible"
else
    add_result "psycopg2 installed" "fail" "psycopg2 no esta instalado"
fi

if python -c "import MySQLdb" 2>/dev/null; then
    add_result "MySQLdb installed" "pass" "MySQL driver disponible"
else
    add_result "MySQLdb installed" "fail" "MySQLdb no esta instalado"
fi

cd "$PROJECT_ROOT" || exit 1

if [ "$JSON_OUTPUT" = false ]; then echo ""; fi

# ==============================================================================
# 3. SESSION_ENGINE VALIDATION (CRITICAL)
# ==============================================================================
if [ "$JSON_OUTPUT" = false ]; then
    echo "[3] Verificando SESSION_ENGINE (CRITICO)..."
fi

SESSION_ENGINE=$(grep -r "SESSION_ENGINE" "$API_DIR/callcentersite" \
    --include="settings*.py" \
    | head -1 \
    | sed "s/.*SESSION_ENGINE.*=.*['\"]\\(.*\\)['\"].*/\\1/" 2>/dev/null || echo "NOT_FOUND")

if [ "$SESSION_ENGINE" = "django.contrib.sessions.backends.db" ]; then
    add_result "SESSION_ENGINE correct" "pass" "Sesiones en database (MySQL)"
elif [[ "$SESSION_ENGINE" == *"redis"* ]] || [[ "$SESSION_ENGINE" == *"cache"* ]]; then
    add_result "SESSION_ENGINE correct" "fail" "RNF-002 VIOLADO: Sesiones en $SESSION_ENGINE (debe ser database)"
else
    add_result "SESSION_ENGINE correct" "fail" "SESSION_ENGINE no encontrado o incorrecto: $SESSION_ENGINE"
fi

if [ "$JSON_OUTPUT" = false ]; then echo ""; fi

# ==============================================================================
# 4. DATABASE CONNECTIVITY
# ==============================================================================
if [ "$JSON_OUTPUT" = false ]; then
    echo "[4] Verificando conectividad a bases de datos..."
fi

cd "$API_DIR/callcentersite" || exit 1

# PostgreSQL check
if python manage.py check --database default 2>/dev/null; then
    add_result "PostgreSQL connectivity" "pass" "Conexion a PostgreSQL exitosa"
else
    add_result "PostgreSQL connectivity" "fail" "No se puede conectar a PostgreSQL"
fi

# MySQL check (si existe configuracion)
if grep -q "mysql" "*/settings*.py" 2>/dev/null; then
    if python manage.py check --database mysql 2>/dev/null; then
        add_result "MySQL connectivity" "pass" "Conexion a MySQL exitosa"
    else
        add_result "MySQL connectivity" "fail" "No se puede conectar a MySQL"
    fi
fi

cd "$PROJECT_ROOT" || exit 1

if [ "$JSON_OUTPUT" = false ]; then echo ""; fi

# ==============================================================================
# 5. MIGRATIONS STATUS
# ==============================================================================
if [ "$JSON_OUTPUT" = false ]; then
    echo "[5] Verificando estado de migraciones..."
fi

cd "$API_DIR/callcentersite" || exit 1

UNAPPLIED=$(python manage.py showmigrations --plan | grep -c "\[ \]" || echo "0")

if [ "$UNAPPLIED" -eq 0 ]; then
    add_result "Migrations applied" "pass" "Todas las migraciones aplicadas"
else
    add_result "Migrations applied" "fail" "$UNAPPLIED migraciones pendientes"
fi

cd "$PROJECT_ROOT" || exit 1

if [ "$JSON_OUTPUT" = false ]; then echo ""; fi

# ==============================================================================
# 6. DJANGO SESSION TABLE SIZE
# ==============================================================================
if [ "$JSON_OUTPUT" = false ]; then
    echo "[6] Verificando tamano de tabla django_session..."
fi

cd "$API_DIR/callcentersite" || exit 1

SESSION_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings')
django.setup()
from django.contrib.sessions.models import Session
print(Session.objects.count())
" 2>/dev/null || echo "ERROR")

if [ "$SESSION_COUNT" = "ERROR" ]; then
    add_result "Session table size" "fail" "No se pudo obtener count de sesiones"
elif [ "$SESSION_COUNT" -gt 100000 ]; then
    add_result "Session table size" "fail" "CRITICO: $SESSION_COUNT sesiones (> 100K) - ejecutar cleanup_sessions.sh"
elif [ "$SESSION_COUNT" -gt 50000 ]; then
    add_result "Session table size" "pass" "WARNING: $SESSION_COUNT sesiones (> 50K) - considerar cleanup"
else
    add_result "Session table size" "pass" "$SESSION_COUNT sesiones activas"
fi

cd "$PROJECT_ROOT" || exit 1

if [ "$JSON_OUTPUT" = false ]; then echo ""; fi

# ==============================================================================
# RESUMEN
# ==============================================================================
if [ "$JSON_OUTPUT" = true ]; then
    JSON_RESULTS="${JSON_RESULTS}],"
    JSON_RESULTS="${JSON_RESULTS}\"summary\":{"
    JSON_RESULTS="${JSON_RESULTS}\"total\":${CHECKS_TOTAL},"
    JSON_RESULTS="${JSON_RESULTS}\"passed\":${CHECKS_PASSED},"
    JSON_RESULTS="${JSON_RESULTS}\"failed\":${FAILED},"
    if [ $FAILED -eq 0 ]; then
        JSON_RESULTS="${JSON_RESULTS}\"status\":\"healthy\""
    else
        JSON_RESULTS="${JSON_RESULTS}\"status\":\"unhealthy\""
    fi
    JSON_RESULTS="${JSON_RESULTS}}"
    JSON_RESULTS="${JSON_RESULTS}}"
    echo "$JSON_RESULTS" | python -m json.tool 2>/dev/null || echo "$JSON_RESULTS"
else
    echo "========================================================================"
    echo "RESUMEN HEALTH CHECK"
    echo "========================================================================"
    echo "[INFO] Checks totales: $CHECKS_TOTAL"
    echo "[INFO] Checks pasados: $CHECKS_PASSED"
    echo "[INFO] Checks fallidos: $FAILED"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo "[OK] SISTEMA SALUDABLE"
        echo ""
        exit 0
    else
        echo "[FAIL] SISTEMA NO SALUDABLE - $FAILED checks fallaron"
        echo ""
        echo "Acciones recomendadas:"
        echo "  - Verificar logs: tail -f /var/log/iact/*.log"
        echo "  - Verificar bases de datos: ./scripts/verificar_servicios.md"
        echo "  - Limpiar sesiones: ./scripts/cleanup_sessions.sh"
        echo ""
        exit 1
    fi
fi
