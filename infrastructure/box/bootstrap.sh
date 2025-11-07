#!/bin/bash
set -euo pipefail

# ============================================================================
# BOOTSTRAP INTELIGENTE DEL ENTORNO VAGRANT
# ============================================================================
# Detecta el estado del sistema, instala servicios si es necesario,
# y ejecuta verificación final con trazabilidad.
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/utils"
INSTALL_DIR="${SCRIPT_DIR}/install"
LOG_DIR="${SCRIPT_DIR}/logs"
VERIFY_SCRIPT="${SCRIPT_DIR}/verify_connections.sh"

source "${UTILS_DIR}/logging.sh"
source "${UTILS_DIR}/validation.sh"
source "${UTILS_DIR}/common.sh"

create_directory "$LOG_DIR"
LOG_FILE="${LOG_DIR}/verify_$(date +%Y%m%d_%H%M%S).log"

log_header "BOOTSTRAP DEL ENTORNO"

# Paso 1: Verificar estado actual
log_step 1 "Ejecutando diagnóstico inicial"
if bash "$VERIFY_SCRIPT" | tee "$LOG_FILE" | grep -q "VERIFICACION COMPLETA"; then
    log_success "El entorno ya está correctamente aprovisionado"
else
    log_warn "Se detectaron fallos o servicios incompletos. Ejecutando instalación..."

    # Paso 2: Instalar MariaDB si es necesario
    log_step 2 "Instalando MariaDB si aplica"
    bash "${INSTALL_DIR}/mariadb.sh"

    # Paso 3: Instalar PostgreSQL si es necesario
    log_step 3 "Instalando PostgreSQL si aplica"
    bash "${INSTALL_DIR}/postgresql.sh"

    # Paso 4: Verificación final
    log_step 4 "Ejecutando verificación final"
    bash "$VERIFY_SCRIPT" | tee "$LOG_FILE"

    log_success "Instalación y verificación completadas"
fi

# Paso 5: Mostrar resumen
log_summary_start
log_summary_item "Log guardado en" "$LOG_FILE"
log_summary_item "Fecha" "$(date)"
log_summary_item "Hostname" "$(hostname)"
log_summary_end
