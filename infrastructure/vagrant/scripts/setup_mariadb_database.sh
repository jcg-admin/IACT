#!/bin/bash
set -euo pipefail

# =============================================================================
# MARIADB DATABASE SETUP - Configuración de base de datos de aplicación
# =============================================================================
# Descripción: Crea y configura base de datos MariaDB para aplicación
# Patrón: Funcional, Idempotente, Sin fallas silenciosas, POSIX
# =============================================================================

# -----------------------------------------------------------------------------
# Setup - Configuración inicial
# -----------------------------------------------------------------------------

# Detectar directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Detectar PROJECT_ROOT
if [ -d "/vagrant" ]; then
    PROJECT_ROOT="/vagrant"
else
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
fi

# Configuración de base de datos con valores por defecto
IVR_DB_NAME="${IVR_DB_NAME:-ivr_legacy}"
IVR_DB_USER="${IVR_DB_USER:-django_user}"
IVR_DB_PASSWORD="${IVR_DB_PASSWORD:-django_pass}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"

# Cargar módulos core
if [ ! -f "${PROJECT_ROOT}/utils/core.sh" ]; then
    printf 'ERROR: No se encontró %s/utils/core.sh\n' "$PROJECT_ROOT" >&2
    exit 1
fi

# shellcheck disable=SC1090
. "${PROJECT_ROOT}/utils/core.sh"

# Cargar módulos adicionales
if type "iact_source_module" >/dev/null 2>&1; then
    iact_source_module "validation" || {
        printf 'ADVERTENCIA: No se pudo cargar módulo validation\n' >&2
    }
    iact_source_module "database" || {
        printf 'ADVERTENCIA: No se pudo cargar módulo database\n' >&2
    }
fi

# Inicializar logging
if type "iact_init_logging" >/dev/null 2>&1; then
    iact_init_logging "${SCRIPT_NAME%.sh}"
fi

# -----------------------------------------------------------------------------
# Funciones auxiliares - Idempotentes
# -----------------------------------------------------------------------------

# Verifica si base de datos existe (idempotente)
db_exists() {
    local db_count
    db_count=$(mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT COUNT(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='$IVR_DB_NAME';" 2>/dev/null | tail -n 1)

    [ "$db_count" -eq 1 ]
}

# Verifica si usuario existe (idempotente)
user_exists() {
    local user_count
    user_count=$(mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT COUNT(*) FROM mysql.user WHERE User='$IVR_DB_USER';" 2>/dev/null | tail -n 1)

    [ "$user_count" -gt 0 ]
}

# -----------------------------------------------------------------------------
# Funciones de configuración - Idempotentes y sin fallas silenciosas
# -----------------------------------------------------------------------------

# Espera a que MariaDB esté listo (idempotente)
wait_for_service() {
    local current="$1"
    local total="$2"
    local max_wait=60
    local counter=0

    iact_log_step "$current" "$total" "Esperando servicio MariaDB"

    while [ "$counter" -lt "$max_wait" ]; do
        if mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
            iact_log_success "MariaDB disponible después de ${counter}s"
            return 0
        fi

        sleep 1
        counter=$((counter + 1))

        if [ $((counter % 10)) -eq 0 ]; then
            iact_log_info "Esperando MariaDB... ${counter}s/${max_wait}s"
        fi
    done

    iact_log_error "MariaDB no respondió después de ${max_wait}s"
    return 1
}

# Crea base de datos (idempotente)
create_db() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Creando base de datos: $IVR_DB_NAME"

    # Verificar si ya existe
    if db_exists; then
        iact_log_info "Base de datos '$IVR_DB_NAME' ya existe"
        return 0
    fi

    iact_log_info "Creando base de datos '$IVR_DB_NAME'..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS \`$IVR_DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Base de datos '$IVR_DB_NAME' creada"
        return 0
    else
        iact_log_error "Error creando base de datos '$IVR_DB_NAME'"
        return 1
    fi
}

# Crea usuario de base de datos (idempotente)
create_user() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando usuario: $IVR_DB_USER"

    # Verificar si usuario ya existe
    if user_exists; then
        iact_log_info "Usuario '$IVR_DB_USER' ya existe, actualizando privilegios..."
    else
        iact_log_info "Creando usuario '$IVR_DB_USER'..."
        if ! mysql -u root -p"$DB_ROOT_PASSWORD" -e "CREATE USER IF NOT EXISTS '$IVR_DB_USER'@'%' IDENTIFIED BY '$IVR_DB_PASSWORD';" 2>&1 | tee -a "$(iact_get_log_file)"; then
            iact_log_error "Error creando usuario '$IVR_DB_USER'"
            return 1
        fi
    fi

    # Otorgar privilegios
    iact_log_info "Otorgando privilegios a '$IVR_DB_USER' en '$IVR_DB_NAME'..."
    if ! mysql -u root -p"$DB_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON \`$IVR_DB_NAME\`.* TO '$IVR_DB_USER'@'%';" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error otorgando privilegios"
        return 1
    fi

    iact_log_success "Privilegios otorgados a '$IVR_DB_USER'"

    # Aplicar cambios
    iact_log_info "Aplicando cambios de privilegios..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Privilegios actualizados"
        return 0
    else
        iact_log_error "Error aplicando privilegios"
        return 1
    fi
}

# Verifica configuración de base de datos (idempotente)
verify_setup() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando configuración de MariaDB"

    # Verificar que la base de datos existe
    if ! db_exists; then
        iact_log_error "Base de datos '$IVR_DB_NAME' no existe"
        return 1
    fi
    iact_log_success "Base de datos '$IVR_DB_NAME' existe"

    # Verificar que el usuario existe
    if ! user_exists; then
        iact_log_error "Usuario '$IVR_DB_USER' no existe"
        return 1
    fi
    iact_log_success "Usuario '$IVR_DB_USER' existe"

    # Probar conexión con el usuario
    iact_log_info "Probando conexión con usuario '$IVR_DB_USER'..."
    if mysql -u "$IVR_DB_USER" -p"$IVR_DB_PASSWORD" -e "USE \`$IVR_DB_NAME\`; SELECT 1;" >/dev/null 2>&1; then
        iact_log_success "Conexión con '$IVR_DB_USER' exitosa"
        return 0
    else
        iact_log_error "No se puede conectar con usuario '$IVR_DB_USER'"
        return 1
    fi
}

# Muestra información de configuración
show_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de configuración"

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "           CONFIGURACION DE BASE DE DATOS MARIADB"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "Base de datos: $IVR_DB_NAME"
    printf '%s\n' "Usuario: $IVR_DB_USER"
    printf '%s\n' "Password: $IVR_DB_PASSWORD"
    printf '\n'
    printf '%s\n' "Comando de conexión:"
    printf '%s\n' "  mysql -u $IVR_DB_USER -p'$IVR_DB_PASSWORD' $IVR_DB_NAME"
    printf '\n'
    printf '%s\n' "Charset: utf8mb4"
    printf '%s\n' "Collation: utf8mb4_unicode_ci"
    printf '\n'
    printf '%s\n' "Desde aplicación Django:"
    printf '%s\n' "  'ENGINE': 'django.db.backends.mysql'"
    printf '%s\n' "  'NAME': '$IVR_DB_NAME'"
    printf '%s\n' "  'USER': '$IVR_DB_USER'"
    printf '%s\n' "  'PASSWORD': '$IVR_DB_PASSWORD'"
    printf '%s\n' "  'HOST': 'localhost'"
    printf '%s\n' "  'PORT': '3306'"
    printf '\n'
    printf '%s\n' "=================================================================="
    printf '\n'

    return 0
}

# -----------------------------------------------------------------------------
# Funciones de paso - Una por paso, con validación explícita
# -----------------------------------------------------------------------------

step_wait_service() {
    local current="$1"
    local total="$2"

    if ! wait_for_service "$current" "$total"; then
        iact_log_error "Error esperando servicio MariaDB"
        return 1
    fi
    return 0
}

step_create_db() {
    local current="$1"
    local total="$2"

    if ! create_db "$current" "$total"; then
        iact_log_error "Error creando base de datos"
        return 1
    fi
    return 0
}

step_create_user() {
    local current="$1"
    local total="$2"

    if ! create_user "$current" "$total"; then
        iact_log_error "Error creando usuario"
        return 1
    fi
    return 0
}

step_verify() {
    local current="$1"
    local total="$2"

    if ! verify_setup "$current" "$total"; then
        iact_log_error "Error verificando configuración"
        return 1
    fi
    return 0
}

step_show_info() {
    local current="$1"
    local total="$2"

    if ! show_info "$current" "$total"; then
        iact_log_error "Error mostrando información"
        return 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# Reporte de resultados - POSIX puro
# -----------------------------------------------------------------------------

show_results() {
    local total="$1"
    local failed_count="$2"
    local failed_list="$3"
    local successful

    printf '\n'

    if [ "$failed_count" -eq 0 ]; then
        iact_log_success "Configuración de MariaDB completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Base de datos '$IVR_DB_NAME' lista para usar"
        return 0
    fi

    successful=$((total - failed_count))

    iact_log_error "Configuración completada con $failed_count error(es):"

    # Mostrar cada fallo (POSIX compatible sin arrays)
    local IFS='|'
    for step in $failed_list; do
        iact_log_error "  - $step"
    done

    iact_log_info "Total pasos ejecutados: $total"
    iact_log_info "Pasos exitosos: $successful"
    return 1
}

# -----------------------------------------------------------------------------
# Main - Composición directa sin abstracciones innecesarias
# -----------------------------------------------------------------------------

main() {
    iact_log_header "MARIADB DATABASE SETUP - VAGRANT"
    iact_log_info "Configurando base de datos de aplicación: $IVR_DB_NAME"
    iact_log_info "Context: $(iact_get_context)"

    local total_steps=5
    local current_step=0
    local failed_count=0
    local failed_list=""

    # Helper para ejecutar paso y registrar fallo sin abortar
    run_step() {
        local step_func="$1"

        current_step=$((current_step + 1))

        if ! "$step_func" "$current_step" "$total_steps"; then
            iact_log_warning "Paso $step_func falló (continuando con siguientes pasos)"

            # Acumular fallos
            if [ -z "$failed_list" ]; then
                failed_list="$step_func"
            else
                failed_list="$failed_list|$step_func"
            fi
            failed_count=$((failed_count + 1))

            return 1
        fi

        return 0
    }

    iact_log_info "Total de pasos a ejecutar: $total_steps"

    # Ejecutar todos los pasos - composición directa
    run_step step_wait_service
    run_step step_create_db
    run_step step_create_user
    run_step step_verify
    run_step step_show_info

    # Mostrar resultados finales
    show_results "$total_steps" "$failed_count" "$failed_list"
}

# Ejecutar main
main "$@"