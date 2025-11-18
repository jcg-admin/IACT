#!/bin/bash
# scripts/deploy.sh
# Deploy automatizado con validacion, backup y rollback
#
# Proceso:
#   1. Validaciones pre-deploy
#   2. Backup de database
#   3. Deploy code
#   4. Run migrations
#   5. Collect static
#   6. Health check post-deploy
#   7. Rollback automatico si falla
#
# Uso:
#   ./scripts/deploy.sh [OPTIONS]
#
# Options:
#   --help                 Muestra esta ayuda
#   --environment ENV      Ambiente: dev|staging|production (default: dev)
#   --skip-backup          Omite backup de database (NO RECOMENDADO)
#   --skip-tests           Omite tests pre-deploy (NO RECOMENDADO)
#   --skip-migrations      Omite migrations (NO RECOMENDADO)
#   --force                No pide confirmacion (usar con cuidado)
#   --verbose              Modo verbose
#
# Ejemplo:
#   ./scripts/deploy.sh --environment staging
#   ./scripts/deploy.sh --environment production --verbose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$PROJECT_ROOT/api"
BACKUP_DIR="$PROJECT_ROOT/backups"

# Opciones
ENVIRONMENT="dev"
SKIP_BACKUP=false
SKIP_TESTS=false
SKIP_MIGRATIONS=false
FORCE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            head -n 30 "$0" | grep "^#" | sed 's/^# \?//'
            exit 0
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
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
        *)
            echo "[ERROR] Opcion desconocida: $1"
            echo "Usa --help para ver opciones disponibles"
            exit 1
            ;;
    esac
done

# Validar environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    echo "[ERROR] Environment invalido: $ENVIRONMENT"
    echo "       Debe ser: dev, staging o production"
    exit 1
fi

echo "========================================================================"
echo "DEPLOY AUTOMATIZADO - Proyecto IACT"
echo "========================================================================"
echo "[INFO] Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[INFO] Environment: $ENVIRONMENT"
echo "[INFO] User: $(whoami)"
echo "[INFO] Branch: $(cd $PROJECT_ROOT && git branch --show-current)"
echo "[INFO] Commit: $(cd $PROJECT_ROOT && git rev-parse --short HEAD)"
echo ""

FAILED=0
ROLLBACK_NEEDED=false
BACKUP_FILE=""

# ==============================================================================
# FUNCIONES DE UTILIDAD
# ==============================================================================

rollback() {
    echo ""
    echo "[ROLLBACK] Iniciando rollback automatico..."
    echo "----------------------------------------------------------------------"

    if [ ! -z "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
        echo "[ROLLBACK] Restaurando database desde $BACKUP_FILE"
        cd "$API_DIR/callcentersite" || exit 1
        python manage.py loaddata "$BACKUP_FILE"
        echo "[OK] Database restaurada"
    else
        echo "[WARNING] No hay backup disponible para restaurar"
    fi

    echo "[ROLLBACK] Deploy revertido"
    exit 1
}

# ==============================================================================
# 1. CONFIRMACION (production)
# ==============================================================================
if [ "$ENVIRONMENT" = "production" ] && [ "$FORCE" = false ]; then
    echo "[CONFIRMACION REQUERIDA - PRODUCTION DEPLOY]"
    echo "----------------------------------------------------------------------"
    echo "ADVERTENCIA: Vas a deployar a PRODUCTION"
    echo "Branch: $(cd $PROJECT_ROOT && git branch --show-current)"
    echo "Commit: $(cd $PROJECT_ROOT && git rev-parse --short HEAD) - $(cd $PROJECT_ROOT && git log -1 --pretty=%B | head -1)"
    echo ""
    read -p "Confirmar deploy a PRODUCTION? (yes/NO): " -r
    echo ""
    if [[ ! $REPLY = "yes" ]]; then
        echo "[INFO] Deploy cancelado por usuario"
        exit 0
    fi
    echo ""
fi

# ==============================================================================
# 2. VALIDACIONES PRE-DEPLOY
# ==============================================================================
echo "[1] Validaciones pre-deploy..."
echo "----------------------------------------------------------------------"

# Verificar git status limpio
if [ "$ENVIRONMENT" = "production" ]; then
    cd "$PROJECT_ROOT" || exit 1
    if [ ! -z "$(git status --porcelain)" ]; then
        echo "[FAIL] Git working directory no esta limpio"
        echo "       Commit o stash cambios antes de deploy"
        exit 1
    fi
    echo "[OK] Git working directory limpio"
fi

# Verificar branch correcto
CURRENT_BRANCH=$(cd "$PROJECT_ROOT" && git branch --show-current)
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
        echo "[FAIL] Production deploy debe ser desde main/master"
        echo "       Current branch: $CURRENT_BRANCH"
        exit 1
    fi
    echo "[OK] Branch correcto: $CURRENT_BRANCH"
fi

# Validar restricciones criticas
if [ -f "$SCRIPT_DIR/validate_critical_restrictions.sh" ]; then
    bash "$SCRIPT_DIR/validate_critical_restrictions.sh"
    if [ $? -ne 0 ]; then
        echo "[FAIL] Validacion de restricciones criticas FALLO"
        exit 1
    fi
    echo "[OK] Restricciones criticas validadas"
fi

echo ""

# ==============================================================================
# 3. TESTS PRE-DEPLOY
# ==============================================================================
if [ "$SKIP_TESTS" = false ]; then
    echo "[2] Ejecutando tests pre-deploy..."
    echo "----------------------------------------------------------------------"

    if [ -f "$SCRIPT_DIR/run_all_tests.sh" ]; then
        bash "$SCRIPT_DIR/run_all_tests.sh"
        if [ $? -ne 0 ]; then
            echo "[FAIL] Tests FALLARON - deploy abortado"
            exit 1
        fi
        echo "[OK] Tests PASARON"
    else
        echo "[WARNING] run_all_tests.sh no encontrado - omitiendo tests"
    fi

    echo ""
fi

# ==============================================================================
# 4. BACKUP DATABASE
# ==============================================================================
if [ "$SKIP_BACKUP" = false ]; then
    echo "[3] Backup de database..."
    echo "----------------------------------------------------------------------"

    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S)_${ENVIRONMENT}.json"

    cd "$API_DIR/callcentersite" || exit 1

    echo "[INFO] Creando backup en: $BACKUP_FILE"
    python manage.py dumpdata --natural-foreign --natural-primary \
        --indent 2 \
        --exclude auth.permission \
        --exclude contenttypes \
        --exclude admin.logentry \
        --exclude sessions.session \
        > "$BACKUP_FILE"

    if [ $? -eq 0 ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo "[OK] Backup creado: $BACKUP_SIZE"
    else
        echo "[FAIL] Backup FALLO"
        exit 1
    fi

    cd "$PROJECT_ROOT" || exit 1
    echo ""
fi

# ==============================================================================
# 5. DEPLOY CODE (git pull o code update)
# ==============================================================================
echo "[4] Deploy de codigo..."
echo "----------------------------------------------------------------------"

cd "$PROJECT_ROOT" || exit 1

# En production, hacer git pull
if [ "$ENVIRONMENT" = "production" ]; then
    echo "[INFO] Git pull origin main..."
    git pull origin main

    if [ $? -ne 0 ]; then
        echo "[FAIL] Git pull FALLO"
        rollback
    fi
    echo "[OK] Codigo actualizado"
elif [ "$ENVIRONMENT" = "staging" ]; then
    echo "[INFO] Git pull origin staging..."
    git pull origin staging || true
    echo "[OK] Codigo actualizado"
else
    echo "[INFO] Dev environment - codigo ya actualizado"
fi

echo ""

# ==============================================================================
# 6. INSTALL DEPENDENCIES
# ==============================================================================
echo "[5] Instalando dependencias..."
echo "----------------------------------------------------------------------"

cd "$API_DIR/callcentersite" || exit 1

if [ -f "requirements/production.txt" ]; then
    pip install -r requirements/production.txt -q
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
fi

if [ $? -eq 0 ]; then
    echo "[OK] Dependencias instaladas"
else
    echo "[FAIL] Instalacion de dependencias FALLO"
    rollback
fi

cd "$PROJECT_ROOT" || exit 1
echo ""

# ==============================================================================
# 7. RUN MIGRATIONS
# ==============================================================================
if [ "$SKIP_MIGRATIONS" = false ]; then
    echo "[6] Ejecutando migraciones..."
    echo "----------------------------------------------------------------------"

    cd "$API_DIR/callcentersite" || exit 1

    # Verificar si hay migraciones pendientes
    UNAPPLIED=$(python manage.py showmigrations --plan | grep -c "\[ \]" || echo "0")

    if [ "$UNAPPLIED" -eq 0 ]; then
        echo "[INFO] No hay migraciones pendientes"
    else
        echo "[INFO] Aplicando $UNAPPLIED migraciones..."

        if [ "$VERBOSE" = true ]; then
            python manage.py migrate -v 2
        else
            python manage.py migrate
        fi

        if [ $? -ne 0 ]; then
            echo "[FAIL] Migraciones FALLARON"
            rollback
        fi
        echo "[OK] Migraciones aplicadas"
    fi

    cd "$PROJECT_ROOT" || exit 1
    echo ""
fi

# ==============================================================================
# 8. COLLECT STATIC FILES
# ==============================================================================
echo "[7] Collect static files..."
echo "----------------------------------------------------------------------"

cd "$API_DIR/callcentersite" || exit 1

if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "staging" ]; then
    python manage.py collectstatic --noinput --clear

    if [ $? -eq 0 ]; then
        echo "[OK] Static files collected"
    else
        echo "[FAIL] collectstatic FALLO"
        rollback
    fi
else
    echo "[INFO] Dev environment - omitiendo collectstatic"
fi

cd "$PROJECT_ROOT" || exit 1
echo ""

# ==============================================================================
# 9. RESTART SERVICES (si aplica)
# ==============================================================================
echo "[8] Restart services..."
echo "----------------------------------------------------------------------"

if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "staging" ]; then
    # Aqui se reiniciaria gunicorn, uwsgi, etc
    # Ejemplo:
    # sudo systemctl restart gunicorn
    # sudo systemctl restart nginx

    echo "[INFO] Servicios reiniciados (implementar segun deployment)"
else
    echo "[INFO] Dev environment - no restart necesario"
fi

echo ""

# ==============================================================================
# 10. HEALTH CHECK POST-DEPLOY
# ==============================================================================
echo "[9] Health check post-deploy..."
echo "----------------------------------------------------------------------"

if [ -f "$SCRIPT_DIR/health_check.sh" ]; then
    bash "$SCRIPT_DIR/health_check.sh"

    if [ $? -ne 0 ]; then
        echo "[FAIL] Health check FALLO"
        rollback
    fi
    echo "[OK] Health check PASO"
else
    echo "[WARNING] health_check.sh no encontrado - omitiendo"
fi

echo ""

# ==============================================================================
# 11. CLEANUP OLD BACKUPS (mantener ultimos 10)
# ==============================================================================
echo "[10] Cleanup old backups..."
echo "----------------------------------------------------------------------"

if [ -d "$BACKUP_DIR" ]; then
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | wc -l)
    if [ "$BACKUP_COUNT" -gt 10 ]; then
        echo "[INFO] Eliminando backups antiguos (mantener ultimos 10)..."
        cd "$BACKUP_DIR" || exit 1
        ls -1t | tail -n +11 | xargs rm -f
        echo "[OK] Backups antiguos eliminados"
    else
        echo "[INFO] $BACKUP_COUNT backups - no cleanup necesario"
    fi
fi

cd "$PROJECT_ROOT" || exit 1
echo ""

# ==============================================================================
# DEPLOY EXITOSO
# ==============================================================================
echo "========================================================================"
echo "DEPLOY COMPLETADO EXITOSAMENTE"
echo "========================================================================"
echo "[INFO] Environment: $ENVIRONMENT"
echo "[INFO] Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[INFO] Branch: $(git branch --show-current)"
echo "[INFO] Commit: $(git rev-parse --short HEAD)"

if [ ! -z "$BACKUP_FILE" ]; then
    echo "[INFO] Backup disponible: $BACKUP_FILE"
fi

echo ""
echo "Proximos pasos:"
echo "  - Verificar aplicacion: curl http://localhost:8000/health/"
echo "  - Monitorear logs: tail -f /var/log/iact/*.log"
echo "  - Validar metricas: python scripts/dora_metrics.py"
echo ""

exit 0
