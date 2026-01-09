
# Guia de Funciones Utils

Referencia completa de todas las funciones disponibles en el directorio utils/.

---

## Indice

1. [core.sh - Funciones Core](#coresh---funciones-core)
2. [database.sh - Funciones de Base de Datos](#databasesh---funciones-de-base-de-datos)
3. [logging.sh - Sistema de Logging](#loggingsh---sistema-de-logging)
4. [network.sh - Funciones de Red](#networksh---funciones-de-red)
5. [provisioning.sh - Orquestacion](#provisioningsh---orquestacion)
6. [system.sh - Configuracion del Sistema](#systemsh---configuracion-del-sistema)
7. [validation.sh - Validaciones](#validationsh---validaciones)
8. [Ejemplos de Uso](#ejemplos-de-uso)

---

## core.sh - Funciones Core

Funciones fundamentales para manejo de servicios, paquetes, archivos y directorios.

### Service Management

#### start_service

Inicia un servicio systemd.

Sintaxis:
```bash
start_service SERVICE_NAME
```

Retorna:
- 0 si exitoso
- 1 si falla

Ejemplo:
```bash
if ! start_service mariadb; then
    log_error "Failed to start MariaDB"
    return 1
fi
```

#### stop_service

Detiene un servicio systemd.

Sintaxis:
```bash
stop_service SERVICE_NAME
```

Ejemplo:
```bash
stop_service apache2
```

#### restart_service

Reinicia un servicio systemd.

Sintaxis:
```bash
restart_service SERVICE_NAME
```

Ejemplo:
```bash
restart_service postgresql
```

#### enable_service

Habilita un servicio para inicio automatico.

Sintaxis:
```bash
enable_service SERVICE_NAME
```

Ejemplo:
```bash
enable_service mariadb
```

### Package Management

#### install_package

Instala un paquete solo si no esta instalado (idempotente).

Sintaxis:
```bash
install_package PACKAGE_NAME
```

Retorna:
- 0 si ya instalado o instalacion exitosa
- 1 si falla

Ejemplo:
```bash
install_package apache2
install_package php7.4
```

Ventajas:
- No reinstala paquetes existentes
- Mas rapido en re-provisioning
- Idempotente

#### is_package_installed

Verifica si un paquete esta instalado.

Sintaxis:
```bash
is_package_installed PACKAGE_NAME
```

Retorna:
- 0 si instalado
- 1 si no instalado

Ejemplo:
```bash
if is_package_installed apache2; then
    log_info "Apache already installed"
else
    install_package apache2
fi
```

### Directory Management

#### ensure_dir

Crea un directorio si no existe.

Sintaxis:
```bash
ensure_dir DIRECTORY_PATH
```

Retorna:
- 0 si directorio existe o se creo exitosamente
- 1 si falla

Ejemplo:
```bash
ensure_dir /var/log/myapp
ensure_dir /etc/myapp/conf.d
```

### File Management

#### backup_file

Crea backup con timestamp de un archivo.

Sintaxis:
```bash
backup_file FILE_PATH
```

Formato del backup:
```
archivo.backup.YYYYMMDD_HHMMSS
```

Retorna:
- 0 si exitoso
- 1 si archivo no existe o falla

Ejemplo:
```bash
# Backup antes de modificar
backup_file /etc/mysql/my.cnf

# Ahora es seguro modificar
sed -i 's/old/new/' /etc/mysql/my.cnf
```

Resultado:
```
/etc/mysql/my.cnf
/etc/mysql/my.cnf.backup.20260101_153045
/etc/mysql/my.cnf.backup.20260102_091230
```

### Command Checking

#### command_exists

Verifica si un comando existe en el sistema.

Sintaxis:
```bash
command_exists COMMAND_NAME
```

Retorna:
- 0 si existe
- 1 si no existe

Ejemplo:
```bash
if command_exists mysql; then
    log_info "MySQL client available"
else
    install_package mysql-client
fi
```

---

## database.sh - Funciones de Base de Datos

Funciones para trabajar con MySQL/MariaDB y PostgreSQL.

### MySQL/MariaDB Functions

#### mysql_wait_ready

Espera hasta que MySQL/MariaDB este listo para aceptar conexiones.

Sintaxis:
```bash
mysql_wait_ready TIMEOUT
```

Parametros:
- TIMEOUT: segundos a esperar (default: 30)

Retorna:
- 0 si esta listo
- 1 si timeout

Ejemplo:
```bash
if ! mysql_wait_ready 30; then
    log_error "MySQL did not start within 30 seconds"
    return 1
fi
```

#### mysql_database_exists

Verifica si una base de datos existe.

Sintaxis:
```bash
mysql_database_exists DB_NAME USER PASSWORD
```

Parametros:
- DB_NAME: nombre de la base de datos
- USER: usuario de MySQL
- PASSWORD: password del usuario

Retorna:
- 0 si existe
- 1 si no existe

Ejemplo:
```bash
if mysql_database_exists "mydb" "root" "rootpass"; then
    log_info "Database already exists"
else
    mysql_create_database "mydb" "utf8mb4" "utf8mb4_unicode_ci" "root" "rootpass"
fi
```

#### mysql_create_database

Crea una base de datos MySQL.

Sintaxis:
```bash
mysql_create_database DB_NAME CHARSET COLLATION USER PASSWORD
```

Parametros:
- DB_NAME: nombre de la base de datos
- CHARSET: character set (ej: utf8mb4)
- COLLATION: collation (ej: utf8mb4_unicode_ci)
- USER: usuario de MySQL
- PASSWORD: password del usuario

Ejemplo:
```bash
mysql_create_database "ivr_legacy" "utf8mb4" "utf8mb4_unicode_ci" "root" "rootpass123"
```

#### mysql_create_user

Crea un usuario MySQL.

Sintaxis:
```bash
mysql_create_user USERNAME PASSWORD HOST ADMIN_USER ADMIN_PASSWORD
```

Parametros:
- USERNAME: nombre del usuario a crear
- PASSWORD: password del usuario
- HOST: host desde donde puede conectar (% = cualquier host)
- ADMIN_USER: usuario admin para crear el usuario
- ADMIN_PASSWORD: password del usuario admin

Ejemplo:
```bash
mysql_create_user "django_user" "django_pass" "%" "root" "rootpass123"
```

#### mysql_grant_privileges

Otorga privilegios a un usuario.

Sintaxis:
```bash
mysql_grant_privileges DB_NAME USERNAME HOST ADMIN_USER ADMIN_PASSWORD
```

Ejemplo:
```bash
mysql_grant_privileges "ivr_legacy" "django_user" "%" "root" "rootpass123"
```

### PostgreSQL Functions

#### postgres_wait_ready

Espera hasta que PostgreSQL este listo.

Sintaxis:
```bash
postgres_wait_ready TIMEOUT
```

Ejemplo:
```bash
postgres_wait_ready 30
```

#### postgres_database_exists

Verifica si una base de datos existe.

Sintaxis:
```bash
postgres_database_exists DB_NAME
```

Retorna:
- 0 si existe
- 1 si no existe

Ejemplo:
```bash
if ! postgres_database_exists "iact_analytics"; then
    postgres_create_database "iact_analytics"
fi
```

#### postgres_create_database

Crea una base de datos PostgreSQL.

Sintaxis:
```bash
postgres_create_database DB_NAME
```

Ejemplo:
```bash
postgres_create_database "iact_analytics"
```

#### postgres_create_user

Crea un usuario PostgreSQL.

Sintaxis:
```bash
postgres_create_user USERNAME PASSWORD
```

Ejemplo:
```bash
postgres_create_user "django_user" "django_pass"
```

#### postgres_grant_privileges

Otorga privilegios a un usuario.

Sintaxis:
```bash
postgres_grant_privileges DB_NAME USERNAME
```

Ejemplo:
```bash
postgres_grant_privileges "iact_analytics" "django_user"
```

---

## logging.sh - Sistema de Logging

Funciones para logging consistente en todos los scripts.

### Log Levels

#### log_info

Log informativo (nivel INFO).

Sintaxis:
```bash
log_info "mensaje"
```

Formato de salida:
```
[2026-01-01 15:30:45] [INFO] mensaje
```

Ejemplo:
```bash
log_info "Starting installation"
log_info "Package version: ${VERSION}"
```

#### log_success

Log de operacion exitosa (nivel SUCCESS).

Sintaxis:
```bash
log_success "mensaje"
```

Ejemplo:
```bash
log_success "Installation completed"
log_success "Database created successfully"
```

#### log_error

Log de error (nivel ERROR).

Sintaxis:
```bash
log_error "mensaje"
```

Ejemplo:
```bash
if ! install_package apache2; then
    log_error "Failed to install Apache"
    return 1
fi
```

#### log_warn

Log de advertencia (nivel WARN).

Sintaxis:
```bash
log_warn "mensaje"
```

Ejemplo:
```bash
if [[ ! -f "$config_file" ]]; then
    log_warn "Config file not found, using defaults"
fi
```

#### log_fatal

Log de error fatal (nivel FATAL) y termina ejecucion.

Sintaxis:
```bash
log_fatal "mensaje"
```

Comportamiento:
- Escribe mensaje con nivel FATAL
- Ejecuta exit 1

Ejemplo:
```bash
if [[ $EUID -ne 0 ]]; then
    log_fatal "This script must be run as root"
fi
```

#### log_header

Encabezado de seccion.

Sintaxis:
```bash
log_header "titulo"
```

Ejemplo:
```bash
log_header "MariaDB Installation"
```

### Timer Functions

#### start_timer

Inicia un temporizador.

Sintaxis:
```bash
start_timer
```

Ejemplo:
```bash
start_timer

# ... operaciones ...

elapsed=$(show_elapsed)
log_info "Operation took ${elapsed}"
```

#### show_elapsed

Muestra tiempo transcurrido desde start_timer.

Sintaxis:
```bash
elapsed=$(show_elapsed)
```

Retorna:
- String con tiempo en formato "Xm Ys"

Ejemplo:
```bash
start_timer
install_package mariadb-server
elapsed=$(show_elapsed)
log_success "Installation completed in ${elapsed}"
```

---

## network.sh - Funciones de Red

Funciones para operaciones de red, descargas y verificacion de conectividad.

### Downloads

#### download_with_retry

Descarga un archivo con reintentos automaticos.

Sintaxis:
```bash
download_with_retry URL DEST_FILE [RETRIES]
```

Parametros:
- URL: URL del archivo a descargar
- DEST_FILE: ruta donde guardar el archivo
- RETRIES: numero de reintentos (default: 3)

Retorna:
- 0 si exitoso
- 1 si falla despues de todos los reintentos

Comportamiento:
- Intenta descargar con curl
- Si falla, espera con delay exponencial
- Reintenta hasta RETRIES veces
- Logs de progreso

Ejemplo:
```bash
download_with_retry "https://github.com/vrana/adminer/releases/download/v4.8.1/adminer-4.8.1.php" "/tmp/adminer.php" 3
```

### Wait Functions

#### wait_for_url

Espera hasta que una URL responda.

Sintaxis:
```bash
wait_for_url URL TIMEOUT
```

Parametros:
- URL: URL a verificar
- TIMEOUT: segundos a esperar

Retorna:
- 0 si URL responde
- 1 si timeout

Ejemplo:
```bash
if ! wait_for_url "http://localhost" 30; then
    log_error "HTTP service did not start"
    return 1
fi
```

#### wait_for_port

Espera hasta que un puerto este escuchando.

Sintaxis:
```bash
wait_for_port HOST PORT TIMEOUT
```

Parametros:
- HOST: hostname o IP
- PORT: numero de puerto
- TIMEOUT: segundos a esperar

Ejemplo:
```bash
wait_for_port "192.168.56.10" 3306 30
```

#### is_port_listening

Verifica si un puerto esta escuchando en localhost.

Sintaxis:
```bash
is_port_listening PORT
```

Retorna:
- 0 si esta escuchando
- 1 si no esta escuchando

Ejemplo:
```bash
if is_port_listening 80; then
    log_info "Port 80 is listening"
else
    log_error "Port 80 is not listening"
fi
```

---

## provisioning.sh - Orquestacion

Funciones para orquestacion del proceso de aprovisionamiento.

### Initialization

#### init_all

Inicializa el sistema de logging y provisioning.

Sintaxis:
```bash
init_all
```

Debe llamarse al inicio de cada bootstrap script.

Ejemplo:
```bash
#!/bin/bash
source /vagrant/utils/provisioning.sh

init_all
```

#### run_all

Ejecuta una lista de pasos de provisioning.

Sintaxis:
```bash
run_all "step1" "step2" "step3" ...
```

Ejemplo:
```bash
steps=(
    "step_system"
    "step_install"
    "step_setup"
)

if ! run_all "${steps[@]}"; then
    log_error "Provisioning failed"
    exit 1
fi
```

### Step Functions

#### step_header

Muestra encabezado de componente.

Sintaxis:
```bash
step_header "COMPONENT" "DESCRIPTION"
```

Ejemplo:
```bash
step_header "MariaDB" "MariaDB 11.4 Database Server"
```

#### step_install

Define paso de instalacion.

Ejemplo:
```bash
step_install() {
    source /vagrant/provisioners/mariadb/install.sh
    main
}
```

#### step_setup

Define paso de configuracion.

Ejemplo:
```bash
step_setup() {
    source /vagrant/provisioners/mariadb/setup.sh
    main
}
```

#### step_system

Define paso de preparacion del sistema.

Ejemplo:
```bash
step_system() {
    source /vagrant/utils/system.sh
    main
}
```

### Results

#### show_results

Muestra resumen de resultados.

Sintaxis:
```bash
show_results "COMPONENT" "IP" "PORT" "STATUS"
```

Ejemplo:
```bash
show_results "MariaDB" \
    "IP: 192.168.56.10" \
    "Port: 3306" \
    "Status: Running"
```

#### show_connection_info

Muestra informacion de conexion.

Sintaxis:
```bash
show_connection_info "TYPE" "HOST" "PORT" "DATABASE" "USER"
```

Ejemplo:
```bash
show_connection_info \
    "MariaDB" \
    "192.168.56.10" \
    "3306" \
    "ivr_legacy" \
    "django_user"
```

---

## system.sh - Configuracion del Sistema

Funciones para preparacion del sistema operativo.

### main

Funcion principal que ejecuta todas las configuraciones del sistema.

Pasos:
1. update_system - Actualiza indices de paquetes
2. install_essentials - Instala herramientas basicas
3. configure_timezone - Configura zona horaria
4. configure_locale - Configura locale
5. cleanup_system - Limpia paquetes innecesarios

Ejemplo:
```bash
source /vagrant/utils/system.sh
main
```

---

## validation.sh - Validaciones

Funciones para validacion de datos y estado del sistema.

### File Validation

#### validate_file_exists

Valida que un archivo existe.

Sintaxis:
```bash
validate_file_exists FILE_PATH
```

Retorna:
- 0 si existe
- 1 si no existe (con mensaje de error)

Ejemplo:
```bash
if ! validate_file_exists "/etc/mysql/my.cnf"; then
    log_error "Config file not found"
    return 1
fi
```

#### validate_dir_exists

Valida que un directorio existe.

Sintaxis:
```bash
validate_dir_exists DIR_PATH
```

Ejemplo:
```bash
validate_dir_exists /var/log/myapp
```

### Variable Validation

#### require_vars

Valida que variables estan definidas.

Sintaxis:
```bash
require_vars VAR1 VAR2 VAR3 ...
```

Comportamiento:
- Verifica que cada variable esta definida y no vacia
- Si alguna falta, muestra error y termina con exit 1

Ejemplo:
```bash
require_vars DB_NAME DB_USER DB_PASSWORD

# Si alguna variable no esta definida, el script termina aqui
log_info "All required variables are set"
```

#### validate_root

Verifica que el script se ejecuta como root.

Sintaxis:
```bash
validate_root
```

Retorna:
- 0 si es root
- 1 si no es root

Ejemplo:
```bash
if ! validate_root; then
    log_fatal "This script must be run as root"
fi
```

---

## Ejemplos de Uso

### Ejemplo 1: Instalacion con reintentos y backup

```bash
#!/bin/bash
source /vagrant/utils/core.sh
source /vagrant/utils/logging.sh
source /vagrant/utils/network.sh
source /vagrant/utils/validation.sh

# Validar permisos
validate_root || exit 1

# Validar variables
require_vars APP_NAME APP_VERSION

# Crear directorio
ensure_dir /var/log/myapp

# Descargar con reintentos
download_with_retry "https://example.com/app-${APP_VERSION}.tar.gz" "/tmp/app.tar.gz" 3

# Backup de configuracion existente
if validate_file_exists /etc/myapp/config.yml; then
    backup_file /etc/myapp/config.yml
fi

# Instalar paquetes
install_package nginx
install_package php7.4

# Configurar servicios
enable_service nginx
start_service nginx

# Esperar a que este listo
wait_for_port localhost 80 30

log_success "Installation completed"
```

### Ejemplo 2: Configuracion de base de datos

```bash
#!/bin/bash
source /vagrant/utils/database.sh
source /vagrant/utils/logging.sh
source /vagrant/utils/validation.sh

# Variables
DB_NAME="myapp"
DB_USER="app_user"
DB_PASSWORD="app_pass"

# Esperar a que MariaDB este listo
if ! mysql_wait_ready 30; then
    log_error "MariaDB not ready"
    exit 1
fi

# Crear base de datos si no existe
if ! mysql_database_exists "$DB_NAME" "root" "rootpass"; then
    mysql_create_database "$DB_NAME" "utf8mb4" "utf8mb4_unicode_ci" "root" "rootpass"
    log_success "Database created"
else
    log_info "Database already exists"
fi

# Crear usuario si no existe
if ! mysql_user_exists "$DB_USER" "root" "rootpass"; then
    mysql_create_user "$DB_USER" "$DB_PASSWORD" "%" "root" "rootpass"
    mysql_grant_privileges "$DB_NAME" "$DB_USER" "%" "root" "rootpass"
    log_success "User created and privileges granted"
else
    log_info "User already exists"
fi
```

### Ejemplo 3: Script de bootstrap completo

```bash
#!/bin/bash
set -euo pipefail

# Cargar utilidades
source /vagrant/utils/provisioning.sh

# Inicializar
init_all

# Definir pasos
step_system() {
    source /vagrant/utils/system.sh
    main
}

step_install() {
    source /vagrant/provisioners/myapp/install.sh
    main
}

step_setup() {
    source /vagrant/provisioners/myapp/setup.sh
    main
}

# Variables
export APP_NAME="MyApp"
export APP_VERSION="1.0.0"

# Ejecutar pasos
steps=(
    "step_system"
    "step_install"
    "step_setup"
)

if ! run_all "${steps[@]}"; then
    log_error "Provisioning failed"
    exit 1
fi

# Mostrar resultados
show_results "MyApp" \
    "Version: ${APP_VERSION}" \
    "Status: Running" \
    "URL: http://192.168.56.10"

log_success "MyApp provisioning completed successfully"
```

---

## Convenciones y Mejores Practicas

### Manejo de errores

Siempre verificar retorno de funciones:
```bash
# MAL
install_package apache2

# BIEN
if ! install_package apache2; then
    log_error "Failed to install Apache"
    return 1
fi
```

### Logging

Usar niveles apropiados:
```bash
log_info    # Informacion general
log_success # Operaciones exitosas
log_warn    # Advertencias
log_error   # Errores recuperables
log_fatal   # Errores fatales (termina script)
```

### Validaciones

Validar antes de operar:
```bash
# Validar variables
require_vars DB_NAME DB_USER DB_PASSWORD

# Validar permisos
validate_root || exit 1

# Validar archivos
if ! validate_file_exists "$config_file"; then
    log_error "Config file not found"
    return 1
fi
```

### Backups

Siempre hacer backup antes de modificar:
```bash
backup_file /etc/mysql/my.cnf
sed -i 's/old/new/' /etc/mysql/my.cnf
```

### Idempotencia

Usar funciones idempotentes:
```bash
# Idempotente
install_package apache2  # No reinstala si ya existe
ensure_dir /var/log/app  # No falla si ya existe

# No idempotente (evitar)
apt-get install -y apache2  # Siempre reinstala
mkdir /var/log/app          # Falla si existe
```

---

## Troubleshooting

### Funcion no encontrada

Error:
```
command not found: install_package
```

Solucion:
```bash
# Cargar el script correcto
source /vagrant/utils/core.sh
```

### Permisos

Error:
```
Permission denied
```

Solucion:
```bash
# Verificar que se ejecuta como root
validate_root || exit 1
```

### Variables no definidas

Error:
```
unbound variable: DB_NAME
```

Solucion:
```bash
# Definir variables antes de require_vars
export DB_NAME="mydb"
export DB_USER="user"
export DB_PASSWORD="pass"

require_vars DB_NAME DB_USER DB_PASSWORD
```

---

## Referencias

- Documentacion de Bash: https://www.gnu.org/software/bash/manual/
- Systemd: https://www.freedesktop.org/wiki/Software/systemd/
- Vagrant: https://www.vagrantup.com/docs

EOFUTILS

cat /tmp/iact-refactoring/docs/reference/utils-guide.md
Output

# Guia de Funciones Utils

Referencia completa de todas las funciones disponibles en el directorio utils/.

---

## Indice

1. [core.sh - Funciones Core](#coresh---funciones-core)
2. [database.sh - Funciones de Base de Datos](#databasesh---funciones-de-base-de-datos)
3. [logging.sh - Sistema de Logging](#loggingsh---sistema-de-logging)
4. [network.sh - Funciones de Red](#networksh---funciones-de-red)
5. [provisioning.sh - Orquestacion](#provisioningsh---orquestacion)
6. [system.sh - Configuracion del Sistema](#systemsh---configuracion-del-sistema)
7. [validation.sh - Validaciones](#validationsh---validaciones)
8. [Ejemplos de Uso](#ejemplos-de-uso)

---

## core.sh - Funciones Core

Funciones fundamentales para manejo de servicios, paquetes, archivos y directorios.

### Service Management

#### start_service

Inicia un servicio systemd.

Sintaxis:
```bash
start_service SERVICE_NAME
```

Retorna:
- 0 si exitoso
- 1 si falla

Ejemplo:
```bash
if ! start_service mariadb; then
    log_error "Failed to start MariaDB"
    return 1
fi
```

#### stop_service

Detiene un servicio systemd.

Sintaxis:
```bash
stop_service SERVICE_NAME
```

Ejemplo:
```bash
stop_service apache2
```

#### restart_service

Reinicia un servicio systemd.

Sintaxis:
```bash
restart_service SERVICE_NAME
```

Ejemplo:
```bash
restart_service postgresql
```

#### enable_service

Habilita un servicio para inicio automatico.

Sintaxis:
```bash
enable_service SERVICE_NAME
```

Ejemplo:
```bash
enable_service mariadb
```

### Package Management

#### install_package

Instala un paquete solo si no esta instalado (idempotente).

Sintaxis:
```bash
install_package PACKAGE_NAME
```

Retorna:
- 0 si ya instalado o instalacion exitosa
- 1 si falla

Ejemplo:
```bash
install_package apache2
install_package php7.4
```

Ventajas:
- No reinstala paquetes existentes
- Mas rapido en re-provisioning
- Idempotente

#### is_package_installed

Verifica si un paquete esta instalado.

Sintaxis:
```bash
is_package_installed PACKAGE_NAME
```

Retorna:
- 0 si instalado
- 1 si no instalado

Ejemplo:
```bash
if is_package_installed apache2; then
    log_info "Apache already installed"
else
    install_package apache2
fi
```

### Directory Management

#### ensure_dir

Crea un directorio si no existe.

Sintaxis:
```bash
ensure_dir DIRECTORY_PATH
```

Retorna:
- 0 si directorio existe o se creo exitosamente
- 1 si falla

Ejemplo:
```bash
ensure_dir /var/log/myapp
ensure_dir /etc/myapp/conf.d
```

### File Management

#### backup_file

Crea backup con timestamp de un archivo.

Sintaxis:
```bash
backup_file FILE_PATH
```

Formato del backup:
```
archivo.backup.YYYYMMDD_HHMMSS
```

Retorna:
- 0 si exitoso
- 1 si archivo no existe o falla

Ejemplo:
```bash
# Backup antes de modificar
backup_file /etc/mysql/my.cnf

# Ahora es seguro modificar
sed -i 's/old/new/' /etc/mysql/my.cnf
```

Resultado:
```
/etc/mysql/my.cnf
/etc/mysql/my.cnf.backup.20260101_153045
/etc/mysql/my.cnf.backup.20260102_091230
```

### Command Checking

#### command_exists

Verifica si un comando existe en el sistema.

Sintaxis:
```bash
command_exists COMMAND_NAME
```

Retorna:
- 0 si existe
- 1 si no existe

Ejemplo:
```bash
if command_exists mysql; then
    log_info "MySQL client available"
else
    install_package mysql-client
fi
```

---

## database.sh - Funciones de Base de Datos

Funciones para trabajar con MySQL/MariaDB y PostgreSQL.

### MySQL/MariaDB Functions

#### mysql_wait_ready

Espera hasta que MySQL/MariaDB este listo para aceptar conexiones.

Sintaxis:
```bash
mysql_wait_ready TIMEOUT
```

Parametros:
- TIMEOUT: segundos a esperar (default: 30)

Retorna:
- 0 si esta listo
- 1 si timeout

Ejemplo:
```bash
if ! mysql_wait_ready 30; then
    log_error "MySQL did not start within 30 seconds"
    return 1
fi
```

#### mysql_database_exists

Verifica si una base de datos existe.

Sintaxis:
```bash
mysql_database_exists DB_NAME USER PASSWORD
```

Parametros:
- DB_NAME: nombre de la base de datos
- USER: usuario de MySQL
- PASSWORD: password del usuario

Retorna:
- 0 si existe
- 1 si no existe

Ejemplo:
```bash
if mysql_database_exists "mydb" "root" "rootpass"; then
    log_info "Database already exists"
else
    mysql_create_database "mydb" "utf8mb4" "utf8mb4_unicode_ci" "root" "rootpass"
fi
```

#### mysql_create_database

Crea una base de datos MySQL.

Sintaxis:
```bash
mysql_create_database DB_NAME CHARSET COLLATION USER PASSWORD
```

Parametros:
- DB_NAME: nombre de la base de datos
- CHARSET: character set (ej: utf8mb4)
- COLLATION: collation (ej: utf8mb4_unicode_ci)
- USER: usuario de MySQL
- PASSWORD: password del usuario

Ejemplo:
```bash
mysql_create_database "ivr_legacy" "utf8mb4" "utf8mb4_unicode_ci" "root" "rootpass123"
```

#### mysql_create_user

Crea un usuario MySQL.

Sintaxis:
```bash
mysql_create_user USERNAME PASSWORD HOST ADMIN_USER ADMIN_PASSWORD
```

Parametros:
- USERNAME: nombre del usuario a crear
- PASSWORD: password del usuario
- HOST: host desde donde puede conectar (% = cualquier host)
- ADMIN_USER: usuario admin para crear el usuario
- ADMIN_PASSWORD: password del usuario admin

Ejemplo:
```bash
mysql_create_user "django_user" "django_pass" "%" "root" "rootpass123"
```

#### mysql_grant_privileges

Otorga privilegios a un usuario.

Sintaxis:
```bash
mysql_grant_privileges DB_NAME USERNAME HOST ADMIN_USER ADMIN_PASSWORD
```

Ejemplo:
```bash
mysql_grant_privileges "ivr_legacy" "django_user" "%" "root" "rootpass123"
```

### PostgreSQL Functions

#### postgres_wait_ready

Espera hasta que PostgreSQL este listo.

Sintaxis:
```bash
postgres_wait_ready TIMEOUT
```

Ejemplo:
```bash
postgres_wait_ready 30
```

#### postgres_database_exists

Verifica si una base de datos existe.

Sintaxis:
```bash
postgres_database_exists DB_NAME
```

Retorna:
- 0 si existe
- 1 si no existe

Ejemplo:
```bash
if ! postgres_database_exists "iact_analytics"; then
    postgres_create_database "iact_analytics"
fi
```

#### postgres_create_database

Crea una base de datos PostgreSQL.

Sintaxis:
```bash
postgres_create_database DB_NAME
```

Ejemplo:
```bash
postgres_create_database "iact_analytics"
```

#### postgres_create_user

Crea un usuario PostgreSQL.

Sintaxis:
```bash
postgres_create_user USERNAME PASSWORD
```

Ejemplo:
```bash
postgres_create_user "django_user" "django_pass"
```

#### postgres_grant_privileges

Otorga privilegios a un usuario.

Sintaxis:
```bash
postgres_grant_privileges DB_NAME USERNAME
```

Ejemplo:
```bash
postgres_grant_privileges "iact_analytics" "django_user"
```

---

## logging.sh - Sistema de Logging

Funciones para logging consistente en todos los scripts.

### Log Levels

#### log_info

Log informativo (nivel INFO).

Sintaxis:
```bash
log_info "mensaje"
```

Formato de salida:
```
[2026-01-01 15:30:45] [INFO] mensaje
```

Ejemplo:
```bash
log_info "Starting installation"
log_info "Package version: ${VERSION}"
```

#### log_success

Log de operacion exitosa (nivel SUCCESS).

Sintaxis:
```bash
log_success "mensaje"
```

Ejemplo:
```bash
log_success "Installation completed"
log_success "Database created successfully"
```

#### log_error

Log de error (nivel ERROR).

Sintaxis:
```bash
log_error "mensaje"
```

Ejemplo:
```bash
if ! install_package apache2; then
    log_error "Failed to install Apache"
    return 1
fi
```

#### log_warn

Log de advertencia (nivel WARN).

Sintaxis:
```bash
log_warn "mensaje"
```

Ejemplo:
```bash
if [[ ! -f "$config_file" ]]; then
    log_warn "Config file not found, using defaults"
fi
```

#### log_fatal

Log de error fatal (nivel FATAL) y termina ejecucion.

Sintaxis:
```bash
log_fatal "mensaje"
```

Comportamiento:
- Escribe mensaje con nivel FATAL
- Ejecuta exit 1

Ejemplo:
```bash
if [[ $EUID -ne 0 ]]; then
    log_fatal "This script must be run as root"
fi
```

#### log_header

Encabezado de seccion.

Sintaxis:
```bash
log_header "titulo"
```

Ejemplo:
```bash
log_header "MariaDB Installation"
```

### Timer Functions

#### start_timer

Inicia un temporizador.

Sintaxis:
```bash
start_timer
```

Ejemplo:
```bash
start_timer

# ... operaciones ...

elapsed=$(show_elapsed)
log_info "Operation took ${elapsed}"
```

#### show_elapsed

Muestra tiempo transcurrido desde start_timer.

Sintaxis:
```bash
elapsed=$(show_elapsed)
```

Retorna:
- String con tiempo en formato "Xm Ys"

Ejemplo:
```bash
start_timer
install_package mariadb-server
elapsed=$(show_elapsed)
log_success "Installation completed in ${elapsed}"
```

---

## network.sh - Funciones de Red

Funciones para operaciones de red, descargas y verificacion de conectividad.

### Downloads

#### download_with_retry

Descarga un archivo con reintentos automaticos.

Sintaxis:
```bash
download_with_retry URL DEST_FILE [RETRIES]
```

Parametros:
- URL: URL del archivo a descargar
- DEST_FILE: ruta donde guardar el archivo
- RETRIES: numero de reintentos (default: 3)

Retorna:
- 0 si exitoso
- 1 si falla despues de todos los reintentos

Comportamiento:
- Intenta descargar con curl
- Si falla, espera con delay exponencial
- Reintenta hasta RETRIES veces
- Logs de progreso

Ejemplo:
```bash
download_with_retry "https://github.com/vrana/adminer/releases/download/v4.8.1/adminer-4.8.1.php" "/tmp/adminer.php" 3
```

### Wait Functions

#### wait_for_url

Espera hasta que una URL responda.

Sintaxis:
```bash
wait_for_url URL TIMEOUT
```

Parametros:
- URL: URL a verificar
- TIMEOUT: segundos a esperar

Retorna:
- 0 si URL responde
- 1 si timeout

Ejemplo:
```bash
if ! wait_for_url "http://localhost" 30; then
    log_error "HTTP service did not start"
    return 1
fi
```

#### wait_for_port

Espera hasta que un puerto este escuchando.

Sintaxis:
```bash
wait_for_port HOST PORT TIMEOUT
```

Parametros:
- HOST: hostname o IP
- PORT: numero de puerto
- TIMEOUT: segundos a esperar

Ejemplo:
```bash
wait_for_port "192.168.56.10" 3306 30
```

#### is_port_listening

Verifica si un puerto esta escuchando en localhost.

Sintaxis:
```bash
is_port_listening PORT
```

Retorna:
- 0 si esta escuchando
- 1 si no esta escuchando

Ejemplo:
```bash
if is_port_listening 80; then
    log_info "Port 80 is listening"
else
    log_error "Port 80 is not listening"
fi
```

---

## provisioning.sh - Orquestacion

Funciones para orquestacion del proceso de aprovisionamiento.

### Initialization

#### init_all

Inicializa el sistema de logging y provisioning.

Sintaxis:
```bash
init_all
```

Debe llamarse al inicio de cada bootstrap script.

Ejemplo:
```bash
#!/bin/bash
source /vagrant/utils/provisioning.sh

init_all
```

#### run_all

Ejecuta una lista de pasos de provisioning.

Sintaxis:
```bash
run_all "step1" "step2" "step3" ...
```

Ejemplo:
```bash
steps=(
    "step_system"
    "step_install"
    "step_setup"
)

if ! run_all "${steps[@]}"; then
    log_error "Provisioning failed"
    exit 1
fi
```

### Step Functions

#### step_header

Muestra encabezado de componente.

Sintaxis:
```bash
step_header "COMPONENT" "DESCRIPTION"
```

Ejemplo:
```bash
step_header "MariaDB" "MariaDB 11.4 Database Server"
```

#### step_install

Define paso de instalacion.

Ejemplo:
```bash
step_install() {
    source /vagrant/provisioners/mariadb/install.sh
    main
}
```

#### step_setup

Define paso de configuracion.

Ejemplo:
```bash
step_setup() {
    source /vagrant/provisioners/mariadb/setup.sh
    main
}
```

#### step_system

Define paso de preparacion del sistema.

Ejemplo:
```bash
step_system() {
    source /vagrant/utils/system.sh
    main
}
```

### Results

#### show_results

Muestra resumen de resultados.

Sintaxis:
```bash
show_results "COMPONENT" "IP" "PORT" "STATUS"
```

Ejemplo:
```bash
show_results "MariaDB" \
    "IP: 192.168.56.10" \
    "Port: 3306" \
    "Status: Running"
```

#### show_connection_info

Muestra informacion de conexion.

Sintaxis:
```bash
show_connection_info "TYPE" "HOST" "PORT" "DATABASE" "USER"
```

Ejemplo:
```bash
show_connection_info \
    "MariaDB" \
    "192.168.56.10" \
    "3306" \
    "ivr_legacy" \
    "django_user"
```

---

## system.sh - Configuracion del Sistema

Funciones para preparacion del sistema operativo.

### main

Funcion principal que ejecuta todas las configuraciones del sistema.

Pasos:
1. update_system - Actualiza indices de paquetes
2. install_essentials - Instala herramientas basicas
3. configure_timezone - Configura zona horaria
4. configure_locale - Configura locale
5. cleanup_system - Limpia paquetes innecesarios

Ejemplo:
```bash
source /vagrant/utils/system.sh
main
```

---

## validation.sh - Validaciones

Funciones para validacion de datos y estado del sistema.

### File Validation

#### validate_file_exists

Valida que un archivo existe.

Sintaxis:
```bash
validate_file_exists FILE_PATH
```

Retorna:
- 0 si existe
- 1 si no existe (con mensaje de error)

Ejemplo:
```bash
if ! validate_file_exists "/etc/mysql/my.cnf"; then
    log_error "Config file not found"
    return 1
fi
```

#### validate_dir_exists

Valida que un directorio existe.

Sintaxis:
```bash
validate_dir_exists DIR_PATH
```

Ejemplo:
```bash
validate_dir_exists /var/log/myapp
```

### Variable Validation

#### require_vars

Valida que variables estan definidas.

Sintaxis:
```bash
require_vars VAR1 VAR2 VAR3 ...
```

Comportamiento:
- Verifica que cada variable esta definida y no vacia
- Si alguna falta, muestra error y termina con exit 1

Ejemplo:
```bash
require_vars DB_NAME DB_USER DB_PASSWORD

# Si alguna variable no esta definida, el script termina aqui
log_info "All required variables are set"
```

#### validate_root

Verifica que el script se ejecuta como root.

Sintaxis:
```bash
validate_root
```

Retorna:
- 0 si es root
- 1 si no es root

Ejemplo:
```bash
if ! validate_root; then
    log_fatal "This script must be run as root"
fi
```

---

## Ejemplos de Uso

### Ejemplo 1: Instalacion con reintentos y backup

```bash
#!/bin/bash
source /vagrant/utils/core.sh
source /vagrant/utils/logging.sh
source /vagrant/utils/network.sh
source /vagrant/utils/validation.sh

# Validar permisos
validate_root || exit 1

# Validar variables
require_vars APP_NAME APP_VERSION

# Crear directorio
ensure_dir /var/log/myapp

# Descargar con reintentos
download_with_retry "https://example.com/app-${APP_VERSION}.tar.gz" "/tmp/app.tar.gz" 3

# Backup de configuracion existente
if validate_file_exists /etc/myapp/config.yml; then
    backup_file /etc/myapp/config.yml
fi

# Instalar paquetes
install_package nginx
install_package php7.4

# Configurar servicios
enable_service nginx
start_service nginx

# Esperar a que este listo
wait_for_port localhost 80 30

log_success "Installation completed"
```

### Ejemplo 2: Configuracion de base de datos

```bash
#!/bin/bash
source /vagrant/utils/database.sh
source /vagrant/utils/logging.sh
source /vagrant/utils/validation.sh

# Variables
DB_NAME="myapp"
DB_USER="app_user"
DB_PASSWORD="app_pass"

# Esperar a que MariaDB este listo
if ! mysql_wait_ready 30; then
    log_error "MariaDB not ready"
    exit 1
fi

# Crear base de datos si no existe
if ! mysql_database_exists "$DB_NAME" "root" "rootpass"; then
    mysql_create_database "$DB_NAME" "utf8mb4" "utf8mb4_unicode_ci" "root" "rootpass"
    log_success "Database created"
else
    log_info "Database already exists"
fi

# Crear usuario si no existe
if ! mysql_user_exists "$DB_USER" "root" "rootpass"; then
    mysql_create_user "$DB_USER" "$DB_PASSWORD" "%" "root" "rootpass"
    mysql_grant_privileges "$DB_NAME" "$DB_USER" "%" "root" "rootpass"
    log_success "User created and privileges granted"
else
    log_info "User already exists"
fi
```

### Ejemplo 3: Script de bootstrap completo

```bash
#!/bin/bash
set -euo pipefail

# Cargar utilidades
source /vagrant/utils/provisioning.sh

# Inicializar
init_all

# Definir pasos
step_system() {
    source /vagrant/utils/system.sh
    main
}

step_install() {
    source /vagrant/provisioners/myapp/install.sh
    main
}

step_setup() {
    source /vagrant/provisioners/myapp/setup.sh
    main
}

# Variables
export APP_NAME="MyApp"
export APP_VERSION="1.0.0"

# Ejecutar pasos
steps=(
    "step_system"
    "step_install"
    "step_setup"
)

if ! run_all "${steps[@]}"; then
    log_error "Provisioning failed"
    exit 1
fi

# Mostrar resultados
show_results "MyApp" \
    "Version: ${APP_VERSION}" \
    "Status: Running" \
    "URL: http://192.168.56.10"

log_success "MyApp provisioning completed successfully"
```

---

## Convenciones y Mejores Practicas

### Manejo de errores

Siempre verificar retorno de funciones:
```bash
# MAL
install_package apache2

# BIEN
if ! install_package apache2; then
    log_error "Failed to install Apache"
    return 1
fi
```

### Logging

Usar niveles apropiados:
```bash
log_info    # Informacion general
log_success # Operaciones exitosas
log_warn    # Advertencias
log_error   # Errores recuperables
log_fatal   # Errores fatales (termina script)
```

### Validaciones

Validar antes de operar:
```bash
# Validar variables
require_vars DB_NAME DB_USER DB_PASSWORD

# Validar permisos
validate_root || exit 1

# Validar archivos
if ! validate_file_exists "$config_file"; then
    log_error "Config file not found"
    return 1
fi
```

### Backups

Siempre hacer backup antes de modificar:
```bash
backup_file /etc/mysql/my.cnf
sed -i 's/old/new/' /etc/mysql/my.cnf
```

### Idempotencia

Usar funciones idempotentes:
```bash
# Idempotente
install_package apache2  # No reinstala si ya existe
ensure_dir /var/log/app  # No falla si ya existe

# No idempotente (evitar)
apt-get install -y apache2  # Siempre reinstala
mkdir /var/log/app          # Falla si existe
```

---

## Troubleshooting

### Funcion no encontrada

Error:
```
command not found: install_package
```

Solucion:
```bash
# Cargar el script correcto
source /vagrant/utils/core.sh
```

### Permisos

Error:
```
Permission denied
```

Solucion:
```bash
# Verificar que se ejecuta como root
validate_root || exit 1
```

### Variables no definidas

Error:
```
unbound variable: DB_NAME
```

Solucion:
```bash
# Definir variables antes de require_vars
export DB_NAME="mydb"
export DB_USER="user"
export DB_PASSWORD="pass"

require_vars DB_NAME DB_USER DB_PASSWORD
```

---

## Referencias

- Documentacion de Bash: https://www.gnu.org/software/bash/manual/
- Systemd: https://www.freedesktop.org/wiki/Software/systemd/
- Vagrant: https://www.vagrantup.com/docs