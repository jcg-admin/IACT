#!/bin/bash

# ============================================================================
# DATABASE CONNECTIVITY CONFIGURATION SCRIPT
# ============================================================================
# Propósito: Configurar conectividad para MariaDB y PostgreSQL
# Uso: bash fix_db_connectivity.sh
# ============================================================================

# Cargar utilidades
source utils/logging.sh
source utils/validation.sh
source utils/common.sh

# Variables configurables con valores por defecto
DB_MARIADB_NAME="${DB_MARIADB_NAME:-ivr_legacy}"
DB_PG_NAME="${DB_PG_NAME:-iact_analytics}"
DB_USER="${DB_USER:-django_user}"
DB_PASS="${DB_PASS:-django_pass}"

# Rutas de configuración
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MARIADB_CONFIG_DIR="/etc/mysql/mariadb.conf.d"
PG_VERSION=$(psql -V 2>/dev/null | awk '{print $3}' | cut -d. -f1-2)
POSTGRESQL_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"

# Función de validación de prerequisitos
validate_prerequisites() {
    log_header "Validando Prerequisitos"
    
    # Validar sistema operativo
    validate_ubuntu_version || {
        log_error "Sistema operativo no compatible. Se requiere Ubuntu 20.04, 22.04 o 24.04"
            return 1
    }
    
    # Validar permisos sudo
    validate_sudo || {
        log_error "Se requiere acceso sudo sin contraseña"
        return 1
    }
    
    # Validar comandos necesarios
    local required_commands=(
        "mysql" "psql" "systemctl" 
        "sed" "grep" "cp" "sudo"
    )
    validate_commands_exist "${required_commands[@]}" || {
        log_error "Faltan comandos requeridos"
        return 1
    }
    
    log_success "Prerequisitos del sistema validados"
    return 0
}

# Función de backup de configuraciones originales
backup_original_configs() {
    log_header "Creando Backups de Configuraciones"
    
    local backup_dir="/tmp/db_config_backup_$(date +%Y%m%d_%H%M%S)"
    create_directory "$backup_dir"
    
    # Backup de configuraciones MariaDB
    if [[ -f "$MARIADB_CONFIG_DIR/50-server.cnf" ]]; then
        cp "$MARIADB_CONFIG_DIR/50-server.cnf" "$backup_dir/50-server.cnf.orig"
        log_info "Backup de configuración MariaDB creado"
    fi
    
    # Backup de configuraciones PostgreSQL
    if [[ -f "$POSTGRESQL_CONFIG_DIR/pg_hba.conf" ]]; then
        cp "$POSTGRESQL_CONFIG_DIR/pg_hba.conf" "$backup_dir/pg_hba.conf.orig"
        log_info "Backup de pg_hba.conf creado"
    fi
    
    if [[ -f "$POSTGRESQL_CONFIG_DIR/postgresql.conf" ]]; then
        cp "$POSTGRESQL_CONFIG_DIR/postgresql.conf" "$backup_dir/postgresql.conf.orig"
        log_info "Backup de postgresql.conf creado"
    fi
    
    log_success "Backups de configuración completados en $backup_dir"
}

# Función para configurar MariaDB
configure_mariadb() {
    log_header "Configurando MariaDB"
    
    # Copiar configuración
    sudo cp "$SCRIPT_DIR/config/mariadb/50-server.cnf" "$MARIADB_CONFIG_DIR/50-server.cnf"
    
    # Ejecutar scripts SQL
    sudo mysql < "$SCRIPT_DIR/config/sql/databases.sql" || {
        log_error "Falló la creación de bases de datos en MariaDB"
        return 1
    }
    
    sudo mysql < "$SCRIPT_DIR/config/sql/users.sql" || {
        log_error "Falló la configuración de usuarios en MariaDB"
        return 1
    }
    
    # Reiniciar servicio
    sudo systemctl restart mariadb || {
        log_error "No se pudo reiniciar MariaDB"
        return 1
    }
    
    log_success "Configuración de MariaDB completada"
    return 0
}

# Función para configurar PostgreSQL
configure_postgresql() {
    log_header "Configurando PostgreSQL"
    
    # Copiar configuraciones
    sudo cp "$SCRIPT_DIR/config/postgresql/pg_hba.conf" "$POSTGRESQL_CONFIG_DIR/pg_hba.conf"
    sudo cp "$SCRIPT_DIR/config/postgresql/postgresql.conf" "$POSTGRESQL_CONFIG_DIR/postgresql.conf"
    
    # Ejecutar scripts SQL como usuario postgres
    sudo -u postgres psql -f "$SCRIPT_DIR/config/sql/databases.sql" || {
        log_error "Falló la creación de bases de datos en PostgreSQL"
        return 1
    }
    
    sudo -u postgres psql -f "$SCRIPT_DIR/config/sql/users.sql" || {
                
        log_error "Falló la configuración de usuarios en PostgreSQL"

        return 1
    }
    
    # Reiniciar servicio
    sudo systemctl restart postgresql || {
        log_error "No se pudo reiniciar PostgreSQL"
        return 1
    }
    
    log_success "Configuración de PostgreSQL completada"
    return 0
}

# Función de verificación de conectividad
verify_database_connectivity() {
    log_header "Verificando Conectividad de Bases de Datos"
    
    # Verificación de MariaDB
    mysql -h 127.0.0.1 -u "$DB_USER" -p"$DB_PASS" "$DB_MARIADB_NAME" -e "SELECT 1" &>/dev/null || {
        log_error "Falló la conexión a MariaDB con el usuario $DB_USER"
        return 1
    }
    
    # Verificación de PostgreSQL
    PGPASSWORD="$DB_PASS" psql -h 127.0.0.1 -U "$DB_USER" -d "$DB_PG_NAME" -c "SELECT 1" &>/dev/null || {
        log_error "Falló la conexión a PostgreSQL con el usuario $DB_USER"
        return 1
    }
    
    log_success "Verificación de conectividad completada"
    return 0
}

# Función de configuración de firewall (opcional)
configure_firewall() {
    log_header "Configurando Firewall"
    
    # Habilitar puertos para MariaDB y PostgreSQL
    sudo ufw allow 3306/tcp comment 'MariaDB' || {
        log_error "No se pudo abrir puerto 3306 para MariaDB"
        return 1
    }
    
    sudo ufw allow 5432/tcp comment 'PostgreSQL' || {
        log_error "No se pudo abrir puerto 5432 para PostgreSQL"
        return 1
    }
    
    # Recargar firewall
    sudo ufw reload || {
        log_error "No se pudo recargar firewall"
        return 1
    }
    
    log_success "Configuración de firewall completada"
    return 0
}

# Función principal
main() {
    # Limpiar pantalla
    clear
    
    # Validar prerequisitos
    validate_prerequisites || {
        log_error "Prerequisitos no cumplidos. Deteniendo script."
        exit 1
    }
    
    # Crear backups
    backup_original_configs
    
    # Configurar MariaDB
    configure_mariadb || {
        log_error "Falló la configuración de MariaDB"
        exit 1
    }
    
    # Configurar PostgreSQL
    configure_postgresql || {
        log_error "Falló la configuración de PostgreSQL"
        exit 1
    }
    
    # Configurar firewall (opcional)
    configure_firewall
    
    # Verificar conectividad
    verify_database_connectivity || {
        log_error "La verificación de conectividad falló"
        exit 1
    }
    
    # Resumen final
    log_header "RESUMEN DE CONFIGURACIÓN"
    log_info "Bases de datos configuradas:"
    log_info "- MariaDB: $DB_MARIADB_NAME"
    log_info "- PostgreSQL: $DB_PG_NAME"
    log_info "Usuario: $DB_USER"
    
    log_box "Configuración de conectividad completada con éxito"
    
    return 0
}

# Ejecutar función principal
main "$@"