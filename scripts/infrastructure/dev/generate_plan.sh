#!/bin/bash
#
# generate_plan.sh - Genera plan de implementación desde especificación
#
# Uso:
#   ./scripts/dev/generate_plan.sh <spec-file> [plan-file]
#
# Descripción:
#   Asiste en la creación de un plan de implementación a partir de una
#   especificación existente. Copia la plantilla y pre-llena campos
#   básicos desde la spec.
#
# Trazabilidad:
#   - Constitution AI: Principio 3 (Trazabilidad Completa)
#   - Plantilla: docs/plantillas/desarrollo/plantilla_plan.md
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TEMPLATE_PATH="docs/plantillas/desarrollo/plantilla_plan.md"
PLANS_DIR="docs/plans"

print_usage() {
    echo "Uso: $0 <spec-file> [plan-file]"
    echo ""
    echo "Argumentos:"
    echo "  spec-file          Ruta a la especificación (ej: docs/specs/auth-jwt.md)"
    echo "  plan-file          Ruta para el plan (opcional, se auto-genera si no se especifica)"
    echo ""
    echo "Opciones:"
    echo "  --help, -h         Mostrar esta ayuda"
    echo ""
    echo "Descripción:"
    echo "  Genera un plan de implementación desde una especificación existente."
    echo "  El plan se crea a partir de la plantilla y se pre-llena con datos de la spec."
    echo ""
    echo "Ejemplos:"
    echo "  $0 docs/specs/auth-jwt.md"
    echo "  $0 docs/specs/auth-jwt.md docs/plans/auth-jwt-implementation.md"
}

extract_metadata() {
    local file="$1"
    local field="$2"

    # Extraer valor del campo del front matter YAML
    local value
    value=$(awk -v field="$field" '
        BEGIN { in_frontmatter=0; }
        /^---$/ { in_frontmatter++; next; }
        in_frontmatter == 1 && $0 ~ "^" field ":" {
            sub("^" field ":[[:space:]]*", "");
            print;
            exit;
        }
    ' "$file")

    echo "$value"
}

extract_title() {
    local file="$1"

    # Buscar primer título H1
    local title
    title=$(grep -m 1 "^# " "$file" | sed 's/^# //')

    echo "$title"
}

generate_plan_filename() {
    local spec_file="$1"

    # Obtener nombre base del archivo spec
    local basename
    basename=$(basename "$spec_file" .md)

    # Generar nombre del plan
    echo "${PLANS_DIR}/${basename}-plan.md"
}

create_plan() {
    local spec_file="$1"
    local plan_file="$2"

    echo -e "${BLUE}Generando plan de implementación...${NC}"
    echo ""

    # Verificar que la spec existe
    if [[ ! -f "$spec_file" ]]; then
        echo -e "${RED}ERROR: Especificación no encontrada: $spec_file${NC}"
        return 1
    fi

    # Verificar que la plantilla existe
    if [[ ! -f "$TEMPLATE_PATH" ]]; then
        echo -e "${RED}ERROR: Plantilla no encontrada: $TEMPLATE_PATH${NC}"
        return 1
    fi

    # Crear directorio de plans si no existe
    mkdir -p "$PLANS_DIR"

    # Verificar si el plan ya existe
    if [[ -f "$plan_file" ]]; then
        echo -e "${YELLOW}ADVERTENCIA: El archivo del plan ya existe: $plan_file${NC}"
        read -p "¿Sobrescribir? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Operación cancelada"
            return 1
        fi
    fi

    # Extraer metadata de la spec
    local spec_id
    spec_id=$(extract_metadata "$spec_file" "id")

    local spec_title
    spec_title=$(extract_title "$spec_file")

    local spec_version
    spec_version=$(extract_metadata "$spec_file" "version")

    local fecha_hoy
    fecha_hoy=$(date +%Y-%m-%d)

    # Copiar plantilla al archivo del plan
    cp "$TEMPLATE_PATH" "$plan_file"

    # Reemplazar placeholders con datos de la spec
    if [[ -n "$spec_id" ]]; then
        # Generar ID del plan basado en spec ID
        local plan_id="${spec_id/SPEC-/PLAN-}"

        # Reemplazar en el archivo
        sed -i "s/id: PLANTILLA-PLAN/id: ${plan_id}/" "$plan_file"
        sed -i "s/\[SPEC-XXX-NNN\]/${spec_id}/g" "$plan_file"
    fi

    if [[ -n "$spec_title" ]]; then
        # Extraer nombre de feature del título (quitar "Especificación de Feature: ")
        local feature_name="${spec_title#Especificación de Feature: }"

        # Reemplazar título
        sed -i "s/\[Nombre de la Feature\]/${feature_name}/g" "$plan_file"
    fi

    # Actualizar fecha de creación
    sed -i "s/fecha_creacion: YYYY-MM-DD/fecha_creacion: ${fecha_hoy}/" "$plan_file"

    # Actualizar fecha en metadata
    sed -i "s/Fecha de Creación: YYYY-MM-DD/Fecha de Creación: ${fecha_hoy}/" "$plan_file"

    echo -e "${GREEN}Plan generado exitosamente: ${plan_file}${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "  1. Abrir el archivo: ${plan_file}"
    echo "  2. Completar secciones marcadas con [...]"
    echo "  3. Agregar tareas detalladas en Fase 1-7"
    echo "  4. Actualizar estimaciones de tiempo"
    echo "  5. Commit: git add ${plan_file} && git commit -m 'docs: agregar plan de implementación'"
    echo ""
    echo "Referencia de spec: ${spec_file}"

    # Abrir archivo en editor si está configurado
    if [[ -n "$EDITOR" ]]; then
        echo ""
        read -p "¿Abrir en editor $EDITOR? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            $EDITOR "$plan_file"
        fi
    fi

    return 0
}

validate_spec() {
    local spec_file="$1"

    echo -e "${BLUE}Validando especificación...${NC}"

    if [[ -f "scripts/dev/validate_spec.sh" ]]; then
        if ./scripts/dev/validate_spec.sh "$spec_file"; then
            echo -e "${GREEN}Especificación válida${NC}"
            return 0
        else
            echo -e "${YELLOW}ADVERTENCIA: Especificación tiene errores${NC}"
            read -p "¿Continuar generando plan de todas formas? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                return 1
            fi
        fi
    else
        echo -e "${YELLOW}ADVERTENCIA: No se puede validar spec (script no encontrado)${NC}"
    fi

    return 0
}

# Script principal
main() {
    if [[ $# -eq 0 ]]; then
        echo -e "${RED}ERROR: Falta argumento${NC}"
        print_usage
        exit 1
    fi

    case "$1" in
        --help|-h)
            print_usage
            exit 0
            ;;
    esac

    local spec_file="$1"
    local plan_file="$2"

    # Auto-generar nombre del plan si no se especificó
    if [[ -z "$plan_file" ]]; then
        plan_file=$(generate_plan_filename "$spec_file")
        echo -e "${BLUE}Auto-generando nombre del plan: ${plan_file}${NC}"
    fi

    # Validar spec (opcional pero recomendado)
    if ! validate_spec "$spec_file"; then
        exit 1
    fi

    # Crear el plan
    if create_plan "$spec_file" "$plan_file"; then
        exit 0
    else
        exit 1
    fi
}

main "$@"
