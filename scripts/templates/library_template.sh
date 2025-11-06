#!/usr/bin/env sh
# library-name.sh - Biblioteca de funciones utilitarias
#
# Este archivo debe ser sourced, no ejecutado:
#   . ./library-name.sh
#
# Funciones exportadas:
#   - log_info(message)      : Log mensaje informativo
#   - log_error(message)     : Log mensaje de error
#   - require_command(cmd)   : Validar que comando esté disponible
#   - validate_number(input) : Validar que input sea número
#
# Ejemplo de uso:
#   #!/usr/bin/env sh
#   . ./library-name.sh
#   log_info "Script iniciado"
#   require_command "curl"
#
# Nota: Compatible con POSIX sh - no usa local, arrays, ni [[]]

# -----------------------------------------------------------------------------
# FUNCIONES DE LOGGING
# -----------------------------------------------------------------------------

# Log mensaje informativo a stdout
# Argumentos:
#   $* - Mensaje a loggear
# Retorna:
#   0 siempre
log_info() {
    printf '[INFO] %s\n' "$*"
}

# Log mensaje de error a stderr
# Argumentos:
#   $* - Mensaje de error
# Retorna:
#   0 siempre
log_error() {
    printf '[ERROR] %s\n' "$*" >&2
}

# Log mensaje de éxito
# Argumentos:
#   $* - Mensaje de éxito
# Retorna:
#   0 siempre
log_success() {
    printf '[SUCCESS] %s\n' "$*"
}

# Log mensaje de advertencia
# Argumentos:
#   $* - Mensaje de advertencia
# Retorna:
#   0 siempre
log_warning() {
    printf '[WARN] %s\n' "$*" >&2
}

# -----------------------------------------------------------------------------
# FUNCIONES DE VALIDACIÓN
# -----------------------------------------------------------------------------

# Verificar que un comando esté disponible en el sistema
# Argumentos:
#   $1 - Nombre del comando a verificar
# Retorna:
#   0 si comando existe, 1 si no existe
# Ejemplo:
#   require_command "curl" || exit 1
require_command() {
    _cmd="${1:?ERROR: Nombre de comando requerido}"
    if ! command -v "$_cmd" >/dev/null 2>&1; then
        log_error "Comando requerido no encontrado: $_cmd"
        unset _cmd
        return 1
    fi
    unset _cmd
    return 0
}

# Validar que input sea un número entero
# Argumentos:
#   $1 - String a validar
# Retorna:
#   0 si es número válido, 1 si no lo es
# Ejemplo:
#   validate_number "$PORT" || exit 2
validate_number() {
    _input="$1"
    case "$_input" in
        ''|*[!0-9]*)
            log_error "No es un número válido: $_input"
            unset _input
            return 1
            ;;
        *)
            unset _input
            return 0
            ;;
    esac
}

# Validar que input contenga solo caracteres alfanuméricos
# Argumentos:
#   $1 - String a validar
# Retorna:
#   0 si es válido, 1 si contiene caracteres inválidos
# Ejemplo:
#   validate_alphanumeric "$USERNAME" || exit 2
validate_alphanumeric() {
    _input="$1"
    case "$_input" in
        *[!A-Za-z0-9_-]*)
            log_error "Caracteres inválidos en input: $_input"
            unset _input
            return 1
            ;;
        '')
            log_error "Input no puede estar vacío"
            unset _input
            return 1
            ;;
        *)
            unset _input
            return 0
            ;;
    esac
}

# -----------------------------------------------------------------------------
# UTILIDADES DE STRING
# -----------------------------------------------------------------------------

# Eliminar whitespace al inicio y fin de string
# Argumentos:
#   $1 - String a limpiar
# Salida:
#   String limpio a stdout
# Ejemplo:
#   clean=$(trim "  hello  ")
trim() {
    _var="$1"
    # Remover whitespace al inicio
    _var="${_var#"${_var%%[![:space:]]*}"}"
    # Remover whitespace al final
    _var="${_var%"${_var##*[![:space:]]}"}"
    printf '%s' "$_var"
}

# -----------------------------------------------------------------------------
# UTILIDADES DE ARCHIVOS
# -----------------------------------------------------------------------------

# Verificar que archivo existe y es legible
# Argumentos:
#   $1 - Ruta del archivo
# Retorna:
#   0 si archivo existe y es legible, 1 en caso contrario
# Ejemplo:
#   validate_file "/etc/config.yml" || exit 1
validate_file() {
    _file="$1"

    if [ ! -e "$_file" ]; then
        log_error "Archivo no existe: $_file"
        unset _file
        return 1
    fi

    if [ ! -r "$_file" ]; then
        log_error "Archivo no es legible: $_file"
        unset _file
        return 1
    fi

    unset _file
    return 0
}

# -----------------------------------------------------------------------------
# UTILIDADES DE SISTEMA
# -----------------------------------------------------------------------------

# Obtener tipo de sistema operativo
# Salida:
#   Nombre del OS a stdout (Linux, Darwin, etc.)
# Ejemplo:
#   os=$(get_os_type)
get_os_type() {
    uname -s
}

# Verificar si el script está corriendo en Linux
# Retorna:
#   0 si es Linux, 1 si no lo es
# Ejemplo:
#   is_linux && echo "Running on Linux"
is_linux() {
    _os_type=$(get_os_type)
    _result=1
    [ "$_os_type" = "Linux" ] && _result=0
    unset _os_type
    return $_result
}

# Verificar si el script está corriendo como root
# Retorna:
#   0 si es root, 1 si no lo es
# Ejemplo:
#   is_root || { log_error "Requiere root"; exit 1; }
is_root() {
    [ "$(id -u)" -eq 0 ]
}

# -----------------------------------------------------------------------------
# FIN DE BIBLIOTECA
# -----------------------------------------------------------------------------

# Nota: Este archivo puede ser sourced múltiples veces de forma segura
# No tiene efectos secundarios en la carga
