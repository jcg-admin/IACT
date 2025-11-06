#!/bin/bash
# Script para limpiar ramas obsoletas del repositorio
# Fecha: 2025-11-05
# Autor: Claude Code

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Limpieza de Ramas Obsoletas ===${NC}"
echo ""

# Verificar que estamos en un repositorio git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: No estamos en un repositorio git${NC}"
    exit 1
fi

# Función para confirmar acción
confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    return 0
}

# 1. Push de ramas principales actualizadas
echo -e "${YELLOW}Paso 1: Push de ramas principales actualizadas${NC}"
echo "Las siguientes ramas necesitan ser pusheadas al remoto:"
echo "  - docs"
echo "  - devcontainer"
echo "  - main"
echo ""

if confirm "¿Deseas hacer push de estas ramas?"; then
    echo "Pushing docs..."
    git checkout docs
    git push -u origin docs || echo -e "${RED}Warning: Push de docs falló (puede requerir permisos)${NC}"

    echo "Pushing devcontainer..."
    git checkout devcontainer
    git push -u origin devcontainer || echo -e "${RED}Warning: Push de devcontainer falló (puede requerir permisos)${NC}"

    echo "Pushing main..."
    git checkout main
    git push -u origin main || echo -e "${RED}Warning: Push de main falló (puede requerir permisos)${NC}"

    echo -e "${GREEN}Push completado${NC}"
else
    echo -e "${YELLOW}Push omitido${NC}"
fi

echo ""

# 2. Eliminación de ramas feature/* remotas
echo -e "${YELLOW}Paso 2: Eliminación de ramas feature/* remotas${NC}"
echo "Las siguientes ramas feature serán eliminadas del remoto:"
git branch -r | grep 'origin/feature/' | sed 's/origin\//  - /'
echo ""

if confirm "¿Deseas eliminar estas ramas remotas?"; then
    git fetch origin

    # Array de ramas feature a eliminar
    FEATURE_BRANCHES=(
        "feature/analyze-meeting-notes-format-17-14-21"
        "feature/analyze-meeting-notes-format-17-24-38"
        "feature/analyze-meeting-notes-format-17-33-10"
        "feature/analyze-meeting-notes-format-17-51-53"
        "feature/config-devcontainr"
        "feature/create-new-develop-branch-devconta-16-53-42"
        "feature/create-new-develop-branch-devconta-17-04-55"
        "feature/update-documentation-structure-20-07-56"
        "feature/update-documentation-structure-and-style-19-05-16"
    )

    for branch in "${FEATURE_BRANCHES[@]}"; do
        echo "Eliminando $branch..."
        git push origin --delete "$branch" 2>&1 || echo -e "${RED}Warning: No se pudo eliminar $branch${NC}"
    done

    echo -e "${GREEN}Ramas feature eliminadas${NC}"
else
    echo -e "${YELLOW}Eliminación de ramas feature omitida${NC}"
fi

echo ""

# 3. Eliminación de ramas claude/* remotas (excepto la actual)
echo -e "${YELLOW}Paso 3: Eliminación de ramas claude/* remotas${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Rama actual: $CURRENT_BRANCH"
echo ""
echo "Las siguientes ramas claude serán eliminadas del remoto:"
git branch -r | grep 'origin/claude/' | grep -v "$CURRENT_BRANCH" | sed 's/origin\//  - /'
echo ""

if confirm "¿Deseas eliminar estas ramas remotas?"; then
    # Array de ramas claude a eliminar (excepto la actual)
    CLAUDE_BRANCHES=(
        "claude/code-session-setup-011CUiWCQiZowE28eEmsTxVJ"
        "claude/move-processes-to-governance-011CUo5agwqzpkLdiCqwPKNs"
    )

    for branch in "${CLAUDE_BRANCHES[@]}"; do
        echo "Eliminando $branch..."
        git push origin --delete "$branch" 2>&1 || echo -e "${RED}Warning: No se pudo eliminar $branch${NC}"
    done

    echo -e "${YELLOW}Nota: La rama $CURRENT_BRANCH no se eliminó (es la rama actual)${NC}"
    echo -e "${YELLOW}Elimínala manualmente después de hacer merge${NC}"
    echo -e "${GREEN}Ramas claude eliminadas${NC}"
else
    echo -e "${YELLOW}Eliminación de ramas claude omitida${NC}"
fi

echo ""

# 4. Limpieza de ramas locales
echo -e "${YELLOW}Paso 4: Limpieza de ramas locales${NC}"
echo "Las siguientes ramas locales serán eliminadas:"
git branch | grep -E '(feature/|claude/)' | grep -v "$CURRENT_BRANCH" | sed 's/^/  - /'
echo ""

if confirm "¿Deseas eliminar estas ramas locales?"; then
    git branch | grep -E '(feature/|claude/)' | grep -v "$CURRENT_BRANCH" | while read branch; do
        branch=$(echo "$branch" | xargs)  # trim whitespace
        echo "Eliminando rama local: $branch"
        git branch -D "$branch" 2>&1 || echo -e "${RED}Warning: No se pudo eliminar $branch${NC}"
    done

    echo -e "${GREEN}Ramas locales eliminadas${NC}"
else
    echo -e "${YELLOW}Eliminación de ramas locales omitida${NC}"
fi

echo ""

# 5. Verificación final
echo -e "${YELLOW}Paso 5: Verificación final${NC}"
echo "Actualizando referencias remotas..."
git fetch --prune origin

echo ""
echo -e "${GREEN}=== Ramas remotas restantes ===${NC}"
git branch -r | sort

echo ""
echo -e "${GREEN}=== Ramas locales restantes ===${NC}"
git branch | sort

echo ""
echo -e "${GREEN}=== Limpieza completada ===${NC}"
echo ""
echo "Estado final del repositorio:"
echo "  Ramas remotas: $(git branch -r | wc -l)"
echo "  Ramas locales: $(git branch | wc -l)"
echo ""
echo -e "${YELLOW}Recuerda:${NC}"
echo "  1. Cambiar a develop: git checkout develop"
echo "  2. Si todo está correcto, eliminar esta rama de trabajo:"
echo "     git push origin --delete $CURRENT_BRANCH"
echo "     git branch -D $CURRENT_BRANCH"
