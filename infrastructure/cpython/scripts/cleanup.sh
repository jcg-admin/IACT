#!/bin/bash
#
# cleanup.sh - Limpiar entorno de compilacion de CPython
#
# Referencia: SPEC_INFRA_001
# Proposito: Permitir compilaciones limpias (idempotencia)
#
# Uso:
#   ./cleanup.sh [--all|--build|--artifacts]
#

set -euo pipefail

# Cargar utilidades
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-/vagrant}"

source "$SCRIPT_DIR/../utils/logging.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/logging.sh"

# Configuracion
BUILD_DIR="/tmp/cpython-build"
INSTALL_PREFIX_BASE="/opt"
ARTIFACT_DIR="/vagrant/artifacts/cpython"

show_usage() {
    cat <<EOF
Uso: $0 [opciones]

Opciones:
  --all        Limpiar todo (builds, instalaciones, artifacts)
  --build      Limpiar solo directorios de build temporales
  --artifacts  Limpiar solo artifacts generados
  --install    Limpiar instalaciones en /opt/python-*

Sin argumentos: muestra el estado actual
EOF
    exit 0
}

show_status() {
    log_info "=== Estado del entorno de compilacion ==="
    echo ""

    # Build directory
    if [ -d "$BUILD_DIR" ]; then
        BUILD_SIZE=$(du -sh "$BUILD_DIR" 2>/dev/null | cut -f1 || echo "unknown")
        log_info "Directorio de build: $BUILD_DIR ($BUILD_SIZE)"
        find "$BUILD_DIR" -maxdepth 1 -type d | tail -n +2 | sed 's/^/  /'
    else
        log_info "Directorio de build: no existe"
    fi
    echo ""

    # Instalaciones
    INSTALLS=$(find "$INSTALL_PREFIX_BASE" -maxdepth 1 -type d -name "python-*" 2>/dev/null | wc -l)
    if [ "$INSTALLS" -gt 0 ]; then
        log_info "Instalaciones en $INSTALL_PREFIX_BASE: $INSTALLS"
        find "$INSTALL_PREFIX_BASE" -maxdepth 1 -type d -name "python-*" -exec du -sh {} \; | sed 's/^/  /'
    else
        log_info "Instalaciones: ninguna"
    fi
    echo ""

    # Artifacts
    if [ -d "$ARTIFACT_DIR" ]; then
        ARTIFACT_COUNT=$(find "$ARTIFACT_DIR" -name "*.tgz" 2>/dev/null | wc -l)
        if [ "$ARTIFACT_COUNT" -gt 0 ]; then
            log_info "Artifacts generados: $ARTIFACT_COUNT"
            find "$ARTIFACT_DIR" -name "*.tgz" -exec ls -lh {} \; | awk '{print "  " $9 " (" $5 ")"}'
        else
            log_info "Artifacts: ninguno"
        fi
    else
        log_info "Directorio de artifacts: no existe"
    fi
    echo ""

    log_info "Uso: $0 --all para limpiar todo"
}

cleanup_build() {
    log_info "Limpiando directorios de build..."

    if [ -d "$BUILD_DIR" ]; then
        BUILD_SIZE=$(du -sh "$BUILD_DIR" 2>/dev/null | cut -f1 || echo "unknown")
        log_info "Eliminando $BUILD_DIR ($BUILD_SIZE)..."
        if ! rm -rf "$BUILD_DIR"; then
            log_error "Fallo al eliminar directorio de build"
            return 1
        fi
        log_success "Directorio de build eliminado"
    else
        log_info "Directorio de build no existe (ya limpio)"
    fi
}

cleanup_install() {
    log_info "Limpiando instalaciones..."

    INSTALLS=$(find "$INSTALL_PREFIX_BASE" -maxdepth 1 -type d -name "python-*" 2>/dev/null)

    if [ -z "$INSTALLS" ]; then
        log_info "No hay instalaciones que limpiar"
        return 0
    fi

    for install_dir in $INSTALLS; do
        INSTALL_SIZE=$(du -sh "$install_dir" 2>/dev/null | cut -f1 || echo "unknown")
        log_info "Eliminando $install_dir ($INSTALL_SIZE)..."
        if ! sudo rm -rf "$install_dir"; then
            log_error "Fallo al eliminar $install_dir (permisos sudo requeridos)"
            return 1
        fi
    done

    log_success "Instalaciones eliminadas"
}

cleanup_artifacts() {
    log_info "Limpiando artifacts..."

    if [ ! -d "$ARTIFACT_DIR" ]; then
        log_info "Directorio de artifacts no existe"
        return 0
    fi

    ARTIFACTS=$(find "$ARTIFACT_DIR" -name "*.tgz" -o -name "*.sha256" 2>/dev/null)

    if [ -z "$ARTIFACTS" ]; then
        log_info "No hay artifacts que limpiar"
        return 0
    fi

    ARTIFACT_COUNT=$(echo "$ARTIFACTS" | wc -l)
    log_warn "Se eliminaran $ARTIFACT_COUNT archivos"

    read -p "¿Confirmar eliminacion de artifacts? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cancelado por usuario"
        return 0
    fi

    for artifact in $ARTIFACTS; do
        log_info "Eliminando $artifact..."
        rm -f "$artifact"
    done

    log_success "Artifacts eliminados"
}

cleanup_all() {
    log_info "=== Limpieza completa del entorno ==="
    echo ""

    cleanup_build
    cleanup_install
    cleanup_artifacts

    echo ""
    log_success "=== Limpieza completa finalizada ==="
    log_info "El entorno esta listo para una compilacion limpia"
}

# Main
main() {
    if [ $# -eq 0 ]; then
        show_status
        exit 0
    fi

    case "$1" in
        --help|-h)
            show_usage
            ;;
        --all)
            cleanup_all
            ;;
        --build)
            cleanup_build
            ;;
        --artifacts)
            cleanup_artifacts
            ;;
        --install)
            cleanup_install
            ;;
        *)
            log_error "Opcion invalida: $1"
            show_usage
            ;;
    esac
}

main "$@"
