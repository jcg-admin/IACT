#!/bin/bash
set -euo pipefail

# =============================================================================
# POSTGRESQL DATABASE SETUP - Configuración de base de datos de aplicación
# =============================================================================
# Descripción: Crea y configura base de datos PostgreSQL para aplicación
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
DJANGO_DB_NAME="${DJANGO_DB_NAME:-iact_analytics}"
DJANGO_DB_USER="${DJANGO_DB_USER:-django_user}"
DJANGO_DB_PASSWORD="${DJANGO_DB_PASSWORD:-django_pass}"
DB_PASSWORD="${DB_PASSWORD:-postgrespass123}"

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
    db_count=$(PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -tAc "SELECT COUNT(*) FROM pg_database WHERE datname='$DJANGO_DB_NAME';" 2>/dev/null)

    [ "$db_count" -eq 1 ]
}

# Verifica si usuario existe (idempotente)
user_exists() {
    local user_count
    user_count=$(PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -tAc "SELECT COUNT(*) FROM pg_user WHERE usename='$DJANGO_DB_USER';" 2>/dev/null)

    [ "$user_count" -eq 1 ]
}

# Verifica si extensión existe (idempotente)
extension_exists() {
    local extension="$1"
    local ext_count
    ext_count=$(PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -d "$DJANGO_DB_NAME" -tAc "SELECT COUNT(*) FROM pg_extension WHERE extname='$extension';" 2>/dev/null)

    [ "$ext_count" -eq 1 ]
}

# -----------------------------------------------------------------------------
# Funciones de configuración - Idempotentes y sin fallas silenciosas
# -----------------------------------------------------------------------------

# Espera a que PostgreSQL esté listo (idempotente)
wait_for_service() {
    local current="$1"
    local total="$2"
    local max_wait=60
    local counter=0

    iact_log_step "$current" "$total" "Esperando servicio PostgreSQL"

    while [ "$counter" -lt "$max_wait" ]; do
        if PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "SELECT 1;" >/dev/null 2>&1; then
            iact_log_success "PostgreSQL disponible después de ${counter}s"
            return 0
        fi

        sleep 1
        counter=$((counter + 1))

        if [ $((counter % 10)) -eq 0 ]; then
            iact_log_info "Esperando PostgreSQL... ${counter}s/${max_wait}s"
        fi
    done

    iact_log_error "PostgreSQL no respondió después de ${max_wait}s"
    return 1
}

# Crea base de datos (idempotente)
create_db() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Creando base de datos: $DJANGO_DB_NAME"

    # Verificar si ya existe
    if db_exists; then
        iact_log_info "Base de datos '$DJANGO_DB_NAME' ya existe"
        return 0
    fi

    iact_log_info "Creando base de datos '$DJANGO_DB_NAME'..."
    if PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "CREATE DATABASE $DJANGO_DB_NAME WITH ENCODING='UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Base de datos '$DJANGO_DB_NAME' creada"
        return 0
    else
        iact_log_error "Error creando base de datos '$DJANGO_DB_NAME'"
        return 1
    fi
}

# Crea usuario de base de datos (idempotente)
create_user() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando usuario: $DJANGO_DB_USER"

    # Verificar si usuario ya existe
    if user_exists; then
        iact_log_info "Usuario '$DJANGO_DB_USER' ya existe, actualizando password..."
        if ! PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "ALTER USER $DJANGO_DB_USER WITH PASSWORD '$DJANGO_DB_PASSWORD';" 2>&1 | tee -a "$(iact_get_log_file)"; then
            iact_log_error "Error actualizando password de '$DJANGO_DB_USER'"
            return 1
        fi
    else
        iact_log_info "Creando usuario '$DJANGO_DB_USER'..."
        if ! PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "CREATE USER $DJANGO_DB_USER WITH PASSWORD '$DJANGO_DB_PASSWORD';" 2>&1 | tee -a "$(iact_get_log_file)"; then
            iact_log_error "Error creando usuario '$DJANGO_DB_USER'"
            return 1
        fi
    fi

    # Otorgar privilegios
    iact_log_info "Otorgando privilegios a '$DJANGO_DB_USER' en '$DJANGO_DB_NAME'..."
    if PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE $DJANGO_DB_NAME TO $DJANGO_DB_USER;" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Privilegios otorgados a '$DJANGO_DB_USER'"
        return 0
    else
        iact_log_error "Error otorgando privilegios"
        return 1
    fi
}

# Crea extensiones de PostgreSQL (idempotente)
create_extensions() {
    local current="$1"
    local total="$2"
    local extensions="pg_trgm unaccent"
    local created=0
    local skipped=0

    iact_log_step "$current" "$total" "Configurando extensiones de PostgreSQL"

    for extension in $extensions; do
        if extension_exists "$extension"; then
            iact_log_info "Extensión '$extension' ya existe"
            skipped=$((skipped + 1))
        else
            iact_log_info "Creando extensión '$extension'..."
            if PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -d "$DJANGO_DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS $extension;" 2>&1 | tee -a "$(iact_get_log_file)"; then
                iact_log_success "Extensión '$extension' creada"
                created=$((created + 1))
            else
                iact_log_warning "No se pudo crear extensión '$extension' (puede no estar disponible)"
            fi
        fi
    done

    iact_log_info "Extensiones creadas: $created, ya existían: $skipped"
    iact_log_success "Configuración de extensiones completada"
    return 0
}

# Verifica configuración de base de datos (idempotente)
verify_setup() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando configuración de PostgreSQL"

    # Verificar que la base de datos existe
    if ! db_exists; then
        iact_log_error "Base de datos '$DJANGO_DB_NAME' no existe"
        return 1
    fi
    iact_log_success "Base de datos '$DJANGO_DB_NAME' existe"

    # Verificar que el usuario existe
    if ! user_exists; then
        iact_log_error "Usuario '$DJANGO_DB_USER' no existe"
        return 1
    fi
    iact_log_success "Usuario '$DJANGO_DB_USER' existe"

    # Probar conexión con el usuario
    iact_log_info "Probando conexión con usuario '$DJANGO_DB_USER'..."
    if PGPASSWORD="$DJANGO_DB_PASSWORD" psql -U "$DJANGO_DB_USER" -h localhost -d "$DJANGO_DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        iact_log_success "Conexión con '$DJANGO_DB_USER' exitosa"
    else
        iact_log_error "No se puede conectar con usuario '$DJANGO_DB_USER'"
        return 1
    fi

    # Verificar extensiones
    local extensions="pg_trgm unaccent"
    local missing=""

    for extension in $extensions; do
        if extension_exists "$extension"; then
            iact_log_success "Extensión '$extension' disponible"
        else
            iact_log_warning "Extensión '$extension' no disponible"
            if [ -z "$missing" ]; then
                missing="$extension"
            else
                missing="$missing $extension"
            fi
        fi
    done

    if [ -n "$missing" ]; then
        iact_log_warning "Extensiones faltantes: $missing"
        iact_log_info "Algunas funcionalidades pueden no estar disponibles"
    fi

    return 0
}

# Muestra información de configuración
show_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de configuración"

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "          CONFIGURACION DE BASE DE DATOS POSTGRESQL"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "Base de datos: $DJANGO_DB_NAME"
    printf '%s\n' "Usuario: $DJANGO_DB_USER"
    printf '%s\n' "Password: $DJANGO_DB_PASSWORD"
    printf '\n'
    printf '%s\n' "Comando de conexión:"
    printf '%s\n' "  PGPASSWORD='$DJANGO_DB_PASSWORD' psql -U $DJANGO_DB_USER -h localhost -d $DJANGO_DB_NAME"
    printf '\n'
    printf '%s\n' "Encoding: UTF8"
    printf '%s\n' "LC_COLLATE: en_US.UTF-8"
    printf '%s\n' "LC_CTYPE: en_US.UTF-8"
    printf '\n'
    printf '%s\n' "Extensiones instaladas:"
    printf '%s\n' "  - pg_trgm (búsqueda de texto)"
    printf '%s\n' "  - unaccent (normalización de texto)"
    printf '\n'
    printf '%s\n' "Desde aplicación Django:"
    printf '%s\n' "  'ENGINE': 'django.db.backends.postgresql'"
    printf '%s\n' "  'NAME': '$DJANGO_DB_NAME'"
    printf '%s\n' "  'USER': '$DJANGO_DB_USER'"
    printf '%s\n' "  'PASSWORD': '$DJANGO_DB_PASSWORD'"
    printf '%s\n' "  'HOST': 'localhost'"
    printf '%s\n' "  'PORT': '5432'"
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
        iact_log_error "Error esperando servicio PostgreSQL"
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

step_create_extensions() {
    local current="$1"
    local total="$2"

    if ! create_extensions "$current" "$total"; then
        iact_log_error "Error creando extensiones"
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
        iact_log_success "Configuración de PostgreSQL completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Base de datos '$DJANGO_DB_NAME' lista para usar"
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
    iact_log_header "POSTGRESQL DATABASE SETUP - VAGRANT"
    iact_log_info "Configurando base de datos de aplicación: $DJANGO_DB_NAME"
    iact_log_info "Context: $(iact_get_context)"

    local total_steps=6
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
    run_step step_create_extensions
    run_step step_verify
    run_step step_show_info

    # Mostrar resultados finales
    show_results "$total_steps" "$failed_count" "$failed_list"
}

# Ejecutar main
main "$@"