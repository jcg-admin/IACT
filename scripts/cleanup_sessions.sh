#!/bin/bash
# scripts/cleanup_sessions.sh
# Limpieza de tabla django_session en MySQL
#
# Elimina sesiones expiradas y muestra estadisticas.
# NOTA: Solo elimina sesiones EXPIRADAS, no afecta sesiones activas.
#
# Uso:
#   ./scripts/cleanup_sessions.sh [OPTIONS]
#
# Options:
#   --help                 Muestra esta ayuda
#   --dry-run              Muestra que se haria sin ejecutar
#   --force                No pide confirmacion
#   --verbose              Modo verbose
#   --days N               Elimina sesiones expiradas hace N dias (default: 7)
#
# Ejemplo:
#   ./scripts/cleanup_sessions.sh --dry-run
#   ./scripts/cleanup_sessions.sh --force
#   ./scripts/cleanup_sessions.sh --days 30

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$PROJECT_ROOT/api"

# Opciones
DRY_RUN=false
FORCE=false
VERBOSE=false
DAYS=7

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            head -n 25 "$0" | grep "^#" | sed 's/^# \?//'
            exit 0
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --days)
            DAYS="$2"
            shift 2
            ;;
        *)
            echo "[ERROR] Opcion desconocida: $1"
            echo "Usa --help para ver opciones disponibles"
            exit 1
            ;;
    esac
done

echo "========================================================================"
echo "CLEANUP DJANGO SESSIONS - Proyecto IACT"
echo "========================================================================"
echo "[INFO] Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[INFO] Modo: $([ "$DRY_RUN" = true ] && echo "DRY-RUN (no ejecuta)" || echo "EJECUCION REAL")"
echo ""

cd "$API_DIR/callcentersite" || exit 1

# ==============================================================================
# 1. ESTADISTICAS ANTES DE CLEANUP
# ==============================================================================
echo "[1] Obteniendo estadisticas de sesiones..."
echo "----------------------------------------------------------------------"

SESSION_COUNT_BEFORE=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings')
django.setup()
from django.contrib.sessions.models import Session
print(Session.objects.count())
" 2>/dev/null)

EXPIRED_COUNT=$(python -c "
import django
import os
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings')
django.setup()
from django.contrib.sessions.models import Session
from django.utils import timezone
expired = Session.objects.filter(expire_date__lt=timezone.now())
print(expired.count())
" 2>/dev/null)

OLD_EXPIRED_COUNT=$(python -c "
import django
import os
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings')
django.setup()
from django.contrib.sessions.models import Session
from django.utils import timezone
cutoff = timezone.now() - timedelta(days=$DAYS)
old_expired = Session.objects.filter(expire_date__lt=cutoff)
print(old_expired.count())
" 2>/dev/null)

echo "[INFO] Total sesiones en tabla: $SESSION_COUNT_BEFORE"
echo "[INFO] Sesiones expiradas: $EXPIRED_COUNT"
echo "[INFO] Sesiones expiradas hace >$DAYS dias: $OLD_EXPIRED_COUNT"
echo ""

# Verificar si hay alerta
if [ "$SESSION_COUNT_BEFORE" -gt 100000 ]; then
    echo "[WARNING] CRITICO: Mas de 100K sesiones en tabla!"
    echo "          Se recomienda cleanup inmediato"
    echo ""
elif [ "$SESSION_COUNT_BEFORE" -gt 50000 ]; then
    echo "[WARNING] Mas de 50K sesiones en tabla"
    echo "          Considerar cleanup pronto"
    echo ""
fi

# ==============================================================================
# 2. CONFIRMACION (si no es --force)
# ==============================================================================
if [ "$DRY_RUN" = false ] && [ "$FORCE" = false ]; then
    echo "[CONFIRMACION REQUERIDA]"
    echo "----------------------------------------------------------------------"
    echo "Se eliminaran $OLD_EXPIRED_COUNT sesiones expiradas hace >$DAYS dias"
    echo ""
    read -p "Continuar? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "[INFO] Cleanup cancelado por usuario"
        exit 0
    fi
    echo ""
fi

# ==============================================================================
# 3. EJECUTAR CLEANUP
# ==============================================================================
echo "[2] Ejecutando cleanup..."
echo "----------------------------------------------------------------------"

if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] Se eliminarian $OLD_EXPIRED_COUNT sesiones"
    echo "[DRY-RUN] No se ejecuta nada"
else
    # Usar Django management command
    if [ "$VERBOSE" = true ]; then
        python manage.py clearsessions -v 2
    else
        python manage.py clearsessions
    fi

    if [ $? -eq 0 ]; then
        echo "[OK] Cleanup ejecutado exitosamente"
    else
        echo "[FAIL] Cleanup fallo"
        exit 1
    fi
fi
echo ""

# ==============================================================================
# 4. ESTADISTICAS DESPUES DE CLEANUP
# ==============================================================================
if [ "$DRY_RUN" = false ]; then
    echo "[3] Obteniendo estadisticas post-cleanup..."
    echo "----------------------------------------------------------------------"

    SESSION_COUNT_AFTER=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings')
django.setup()
from django.contrib.sessions.models import Session
print(Session.objects.count())
" 2>/dev/null)

    DELETED=$((SESSION_COUNT_BEFORE - SESSION_COUNT_AFTER))

    echo "[INFO] Sesiones antes: $SESSION_COUNT_BEFORE"
    echo "[INFO] Sesiones despues: $SESSION_COUNT_AFTER"
    echo "[INFO] Sesiones eliminadas: $DELETED"
    echo ""

    # Calcular espacio liberado (aprox 500 bytes por sesion)
    SPACE_MB=$((DELETED * 500 / 1024 / 1024))
    echo "[INFO] Espacio liberado (aprox): ${SPACE_MB}MB"
    echo ""

    # Recomendaciones
    if [ "$SESSION_COUNT_AFTER" -gt 50000 ]; then
        echo "[WARNING] Aun hay $SESSION_COUNT_AFTER sesiones"
        echo "          Considerar ejecutar cleanup con --days mayor"
        echo "          Ejemplo: ./scripts/cleanup_sessions.sh --days 30"
    fi
fi

# ==============================================================================
# 5. TABLA SIZE EN MYSQL (si esta disponible)
# ==============================================================================
if [ "$VERBOSE" = true ] && [ "$DRY_RUN" = false ]; then
    echo "[4] Obteniendo tamano de tabla en MySQL..."
    echo "----------------------------------------------------------------------"

    TABLE_SIZE=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('''
    SELECT
        ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
    FROM information_schema.TABLES
    WHERE table_schema = DATABASE()
    AND table_name = 'django_session'
''')
result = cursor.fetchone()
print(result[0] if result else 'N/A')
" 2>/dev/null)

    echo "[INFO] Tamano tabla django_session: ${TABLE_SIZE}MB"
    echo ""
fi

# ==============================================================================
# RESUMEN Y RECOMENDACIONES
# ==============================================================================
echo "========================================================================"
echo "CLEANUP COMPLETADO"
echo "========================================================================"

if [ "$DRY_RUN" = false ]; then
    echo "[INFO] Sesiones eliminadas: $DELETED"
    echo "[INFO] Sesiones restantes: $SESSION_COUNT_AFTER"
    echo ""

    if [ "$SESSION_COUNT_AFTER" -lt 10000 ]; then
        echo "[OK] Tabla en buen estado"
    fi
fi

echo ""
echo "Recomendaciones:"
echo "  - Ejecutar este script cada 6 horas via cron"
echo "  - Cron entry: 0 */6 * * * $SCRIPT_DIR/cleanup_sessions.sh --force >> /var/log/iact/cleanup.log 2>&1"
echo "  - Monitorear con: ./scripts/health_check.sh"
echo ""

cd "$PROJECT_ROOT" || exit 1

exit 0
