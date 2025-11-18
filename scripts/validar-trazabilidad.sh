#!/bin/bash

################################################################################
# Script: validar-trazabilidad.sh
# Descripción: Valida la trazabilidad entre artefactos de requisitos
# Autor: Claude Code (Sonnet 4.5)
# Fecha: 2025-11-17
# Versión: 1.0.0
# Basado en: ADR-GOB-009 - Trazabilidad entre Artefactos de Requisitos
################################################################################

set -euo pipefail

# Configuración
REQUISITOS_DIR="docs/gobernanza/requisitos"
VERBOSE=0
COLOR=1

# Colores (si está en terminal)
if [[ -t 1 ]] && [[ "$COLOR" == "1" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
    BOLD='\033[1m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
    BOLD=''
fi

# Arrays para tracking
declare -A IDS_EXISTENTES
declare -A REFERENCIAS_A_IDS
declare -A IDS_DUPLICADOS
declare -A IDS_HUERFANOS
declare -A IDS_SIN_REFERENCIAS_A_OTROS

# Contadores
TOTAL_IDS=0
TOTAL_REFERENCIAS=0
ERRORES=0
WARNINGS=0

################################################################################
# Funciones de utilidad
################################################################################

print_usage() {
    cat << EOF
Uso: $(basename "$0") [OPCIONES]

Valida la trazabilidad entre artefactos de requisitos según ADR-GOB-009.

OPCIONES:
    -h, --help              Mostrar esta ayuda
    -v, --verbose           Modo verbose (mostrar detalles)
    -d, --dir DIR           Directorio de requisitos (default: docs/gobernanza/requisitos)
    --no-color              Desactivar colores en output

PATRONES DE IDs VÁLIDOS:
    RN-DOMINIO-###          Reglas de Negocio (ej: RN-BACK-001)
    RNEG-DOMINIO-###        Requerimientos de Negocio (ej: RNEG-BACK-001)
    UC-DOMINIO-###          Casos de Uso (ej: UC-BACK-001)
    RF-DOMINIO-###          Requisitos Funcionales (ej: RF-BACK-005)
    RNF-DOMINIO-###         Atributos de Calidad (ej: RNF-BACK-005)

DOMINIOS VÁLIDOS:
    BACK, FRONT, DEVOPS, QA, AI, GOB

EXIT CODES:
    0 - Todo correcto
    1 - Errores encontrados
    2 - Uso incorrecto

EJEMPLOS:
    $(basename "$0")                              # Validación estándar
    $(basename "$0") -v                           # Con detalles
    $(basename "$0") -d docs/requisitos           # Directorio custom

BASADO EN:
    ADR-GOB-009: Trazabilidad entre Artefactos de Requisitos

EOF
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
    WARNINGS=$((WARNINGS + 1))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
    ERRORES=$((ERRORES + 1))
}

log_verbose() {
    if [[ "$VERBOSE" == "1" ]]; then
        echo -e "${BLUE}[VERBOSE]${NC} $*"
    fi
}

################################################################################
# Funciones principales
################################################################################

# Validar formato de ID
validar_formato_id() {
    local id="$1"
    # Patrón: TIPO-DOMINIO-###
    # TIPO: RN, RNEG, UC, RF, RNF
    # DOMINIO: BACK, FRONT, DEVOPS, QA, AI, GOB
    # ###: 001-999
    if [[ "$id" =~ ^(RN|RNEG|UC|RF|RNF)-(BACK|FRONT|DEVOPS|QA|AI|GOB)-[0-9]{3}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Extraer ID del frontmatter o título del archivo
extraer_id_de_archivo() {
    local archivo="$1"
    local id=""

    # Intentar extraer de frontmatter (línea "id: XXX")
    id=$(grep -m 1 "^id: " "$archivo" 2>/dev/null | sed 's/^id: *//' || echo "")

    # Si no está en frontmatter, buscar en el nombre del archivo
    if [[ -z "$id" ]]; then
        local basename=$(basename "$archivo" .md)
        # Buscar patrón TIPO-DOMINIO-### en el nombre
        id=$(echo "$basename" | grep -oE "(RN|RNEG|UC|RF|RNF)-(BACK|FRONT|DEVOPS|QA|AI|GOB)-[0-9]{3}" || echo "")
    fi

    # Si no está en nombre, buscar en título (# TIPO-DOMINIO-###: ...)
    if [[ -z "$id" ]]; then
        id=$(grep -m 1 "^# " "$archivo" | grep -oE "(RN|RNEG|UC|RF|RNF)-(BACK|FRONT|DEVOPS|QA|AI|GOB)-[0-9]{3}" || echo "")
    fi

    echo "$id"
}

# Escanear todos los archivos y extraer IDs existentes
escanear_ids_existentes() {
    log_info "Escaneando IDs existentes en ${REQUISITOS_DIR}..."

    if [[ ! -d "$REQUISITOS_DIR" ]]; then
        log_error "Directorio no existe: $REQUISITOS_DIR"
        exit 2
    fi

    while IFS= read -r archivo; do
        local id=$(extraer_id_de_archivo "$archivo")

        if [[ -n "$id" ]]; then
            if validar_formato_id "$id"; then
                if [[ -n "${IDS_EXISTENTES[$id]:-}" ]]; then
                    # ID duplicado
                    IDS_DUPLICADOS[$id]="${IDS_EXISTENTES[$id]} | $archivo"
                    log_verbose "ID duplicado encontrado: $id"
                else
                    IDS_EXISTENTES[$id]="$archivo"
                    TOTAL_IDS=$((TOTAL_IDS + 1))
                    log_verbose "ID encontrado: $id en $archivo"
                fi
            else
                log_warning "Formato de ID inválido en $archivo: $id"
            fi
        fi
    done < <(find "$REQUISITOS_DIR" -type f -name "*.md")

    log_success "IDs existentes encontrados: $TOTAL_IDS"
}

# Extraer todas las referencias a IDs en archivos
extraer_referencias() {
    log_info "Extrayendo referencias entre artefactos..."

    while IFS= read -r archivo; do
        # Buscar referencias a IDs en el contenido (formato: RN-BACK-001, UC-FRONT-010, etc.)
        local referencias=$(grep -oE "(RN|RNEG|UC|RF|RNF)-(BACK|FRONT|DEVOPS|QA|AI|GOB)-[0-9]{3}" "$archivo" | sort -u || true)

        while IFS= read -r ref_id; do
            if [[ -n "$ref_id" ]]; then
                # Guardar referencia
                local key="${archivo}||${ref_id}"
                REFERENCIAS_A_IDS[$key]="1"
                TOTAL_REFERENCIAS=$((TOTAL_REFERENCIAS + 1))
                log_verbose "Referencia: $archivo -> $ref_id"
            fi
        done <<< "$referencias"
    done < <(find "$REQUISITOS_DIR" -type f -name "*.md")

    log_success "Referencias totales encontradas: $TOTAL_REFERENCIAS"
}

# Validar que todas las referencias apuntan a IDs existentes
validar_referencias() {
    log_info "Validando referencias..."

    local referencias_rotas=0

    for key in "${!REFERENCIAS_A_IDS[@]}"; do
        local archivo="${key%%||*}"
        local ref_id="${key##*||}"

        # Verificar que el ID referenciado existe
        if [[ -z "${IDS_EXISTENTES[$ref_id]:-}" ]]; then
            log_error "Referencia rota: $ref_id mencionado en $(basename "$archivo") pero no existe"
            referencias_rotas=$((referencias_rotas + 1))
        fi
    done

    if [[ "$referencias_rotas" -eq 0 ]]; then
        log_success "Todas las referencias son válidas"
    else
        log_error "Total de referencias rotas: $referencias_rotas"
    fi
}

# Detectar IDs duplicados
validar_duplicados() {
    log_info "Validando IDs duplicados..."

    local hay_duplicados=0
    if [[ "${!IDS_DUPLICADOS[@]}" ]]; then
        for id in "${!IDS_DUPLICADOS[@]}"; do
            if [[ -n "$id" ]]; then
                hay_duplicados=1
                log_error "ID duplicado: $id aparece en múltiples archivos:"
                IFS='|' read -ra archivos <<< "${IDS_DUPLICADOS[$id]}"
                for archivo in "${archivos[@]}"; do
                    echo -e "  ${RED}→${NC} $(basename "$archivo")"
                done
            fi
        done
    fi

    if [[ "$hay_duplicados" -eq 0 ]]; then
        log_success "No hay IDs duplicados"
    fi
}

# Detectar artefactos huérfanos (sin referencias desde otros)
detectar_huerfanos() {
    log_info "Detectando artefactos huérfanos..."

    # Para cada ID existente, verificar si es referenciado por otros
    for id in "${!IDS_EXISTENTES[@]}"; do
        local es_referenciado=0
        local archivo_propio="${IDS_EXISTENTES[$id]}"

        for key in "${!REFERENCIAS_A_IDS[@]}"; do
            local archivo="${key%%||*}"
            local ref_id="${key##*||}"

            # Si otro archivo (no el propio) referencia este ID
            if [[ "$ref_id" == "$id" ]] && [[ "$archivo" != "$archivo_propio" ]]; then
                es_referenciado=1
                break
            fi
        done

        if [[ "$es_referenciado" -eq 0 ]]; then
            IDS_HUERFANOS[$id]="${IDS_EXISTENTES[$id]}"
        fi
    done

    local hay_huerfanos=0
    if [[ "${!IDS_HUERFANOS[@]}" ]]; then
        for id in "${!IDS_HUERFANOS[@]}"; do
            if [[ -n "$id" ]]; then
                hay_huerfanos=1
                log_warning "Artefacto huérfano: $id en $(basename "${IDS_HUERFANOS[$id]}") - no hay referencias desde otros artefactos"
            fi
        done
    fi

    if [[ "$hay_huerfanos" -eq 0 ]]; then
        log_success "No hay artefactos huérfanos"
    fi
}

# Detectar artefactos que no referencian a otros
detectar_sin_referencias_salientes() {
    log_info "Detectando artefactos sin referencias a otros..."

    for id in "${!IDS_EXISTENTES[@]}"; do
        local archivo="${IDS_EXISTENTES[$id]}"
        local tiene_referencias=0

        for key in "${!REFERENCIAS_A_IDS[@]}"; do
            local archivo_ref="${key%%||*}"
            local ref_id="${key##*||}"

            # Si este archivo referencia a otro ID (no a sí mismo)
            if [[ "$archivo_ref" == "$archivo" ]] && [[ "$ref_id" != "$id" ]]; then
                tiene_referencias=1
                break
            fi
        done

        if [[ "$tiene_referencias" -eq 0 ]]; then
            # Casos de uso y requisitos funcionales DEBEN referenciar a otros
            if [[ "$id" =~ ^(UC|RF|RNF)- ]]; then
                log_warning "Artefacto sin referencias a otros: $id ($(basename "$archivo")) - debería referenciar RN, RNEG, UC o RF relacionados"
                IDS_SIN_REFERENCIAS_A_OTROS[$id]="$archivo"
            fi
        fi
    done

    local hay_sin_refs=0
    if [[ "${!IDS_SIN_REFERENCIAS_A_OTROS[@]}" ]]; then
        hay_sin_refs=1
    fi

    if [[ "$hay_sin_refs" -eq 0 ]]; then
        log_success "Todos los artefactos pertinentes tienen referencias a otros"
    fi
}

# Reporte final
generar_reporte() {
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}           REPORTE DE VALIDACIÓN DE TRAZABILIDAD${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════${NC}"
    # Contar elementos de arrays asociativos de forma segura
    local count_duplicados=0
    local count_huerfanos=0
    local count_sin_refs=0

    if [[ "${!IDS_DUPLICADOS[@]}" ]]; then
        for _ in "${!IDS_DUPLICADOS[@]}"; do
            count_duplicados=$((count_duplicados + 1))
        done
    fi

    if [[ "${!IDS_HUERFANOS[@]}" ]]; then
        for _ in "${!IDS_HUERFANOS[@]}"; do
            count_huerfanos=$((count_huerfanos + 1))
        done
    fi

    if [[ "${!IDS_SIN_REFERENCIAS_A_OTROS[@]}" ]]; then
        for _ in "${!IDS_SIN_REFERENCIAS_A_OTROS[@]}"; do
            count_sin_refs=$((count_sin_refs + 1))
        done
    fi

    echo ""
    echo -e "${BLUE}IDs únicos encontrados:${NC}      $TOTAL_IDS"
    echo -e "${BLUE}Referencias verificadas:${NC}     $TOTAL_REFERENCIAS"
    echo -e "${BLUE}IDs duplicados:${NC}              $count_duplicados"
    echo -e "${BLUE}Artefactos huérfanos:${NC}        $count_huerfanos"
    echo -e "${BLUE}Sin referencias salientes:${NC}   $count_sin_refs"
    echo ""

    if [[ "$ERRORES" -eq 0 ]] && [[ "$WARNINGS" -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}✓ Resultado: EXITOSO${NC}"
        echo -e "${GREEN}  Todos los artefactos están correctamente trazados.${NC}"
        return 0
    elif [[ "$ERRORES" -eq 0 ]]; then
        echo -e "${YELLOW}${BOLD}⚠ Resultado: EXITOSO CON WARNINGS${NC}"
        echo -e "${YELLOW}  Total de warnings: $WARNINGS${NC}"
        echo -e "${YELLOW}  Revisar warnings arriba para mejorar trazabilidad.${NC}"
        return 0
    else
        echo -e "${RED}${BOLD}✗ Resultado: FALLIDO${NC}"
        echo -e "${RED}  Total de errores: $ERRORES${NC}"
        echo -e "${RED}  Total de warnings: $WARNINGS${NC}"
        return 1
    fi
}

################################################################################
# Main
################################################################################

main() {
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                print_usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=1
                shift
                ;;
            -d|--dir)
                REQUISITOS_DIR="$2"
                shift 2
                ;;
            --no-color)
                COLOR=0
                RED=''
                GREEN=''
                YELLOW=''
                BLUE=''
                NC=''
                BOLD=''
                shift
                ;;
            *)
                echo "Opción desconocida: $1"
                print_usage
                exit 2
                ;;
        esac
    done

    echo -e "${BOLD}Validando trazabilidad de requisitos...${NC}"
    echo ""

    # Ejecutar validaciones
    escanear_ids_existentes
    extraer_referencias
    echo ""
    validar_referencias
    validar_duplicados
    detectar_huerfanos
    detectar_sin_referencias_salientes

    # Generar reporte
    generar_reporte
    return $?
}

# Ejecutar
main "$@"
