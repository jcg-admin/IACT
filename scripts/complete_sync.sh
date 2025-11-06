#!/bin/bash
# Script para completar sincronización de ramas - GitOpsAgent
# Generado: 2025-11-05
# Estado: Ramas locales sincronizadas, pendiente push al remoto

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== GitOpsAgent: Completar Sincronización de Ramas ===${NC}"
echo ""
echo "Estado actual:"
echo "  - Ramas locales: SINCRONIZADAS con develop"
echo "  - Ramas remotas: DESACTUALIZADAS (pendiente push)"
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
echo ""
echo "Ramas a actualizar:"
echo "  - docs (282 commits adelante del remoto)"
echo "  - devcontainer (351 commits adelante del remoto)"
echo "  - main (463 commits adelante del remoto)"
echo ""
echo "Total de cambios por rama:"
echo "  - 22 archivos modificados"
echo "  - +122,747 líneas nuevas (marco integrado, agentes BA, metodología)"
echo ""

if confirm "¿Deseas hacer push de estas ramas?"; then
    echo "Pushing docs..."
    git checkout docs
    git push -u origin docs || {
        echo -e "${RED}Error: Push de docs falló${NC}"
        echo "Verifica permisos o ejecuta manualmente:"
        echo "  git checkout docs && git push -u origin docs"
    }

    echo "Pushing devcontainer..."
    git checkout devcontainer
    git push -u origin devcontainer || {
        echo -e "${RED}Error: Push de devcontainer falló${NC}"
        echo "Verifica permisos o ejecuta manualmente:"
        echo "  git checkout devcontainer && git push -u origin devcontainer"
    }

    echo "Pushing main..."
    git checkout main
    git push -u origin main || {
        echo -e "${RED}Error: Push de main falló${NC}"
        echo "Verifica permisos o ejecuta manualmente:"
        echo "  git checkout main && git push -u origin main"
    }

    echo -e "${GREEN}Push completado (o documentados errores)${NC}"
else
    echo -e "${YELLOW}Push omitido${NC}"
fi

echo ""

# 2. Eliminación de ramas feature/* remotas
echo -e "${YELLOW}Paso 2: Eliminación de ramas feature/* remotas${NC}"
echo "Las siguientes ramas feature serán eliminadas del remoto:"
echo "  - feature/analyze-meeting-notes-format-17-14-21"
echo "  - feature/analyze-meeting-notes-format-17-24-38"
echo "  - feature/analyze-meeting-notes-format-17-33-10"
echo "  - feature/analyze-meeting-notes-format-17-51-53"
echo "  - feature/config-devcontainr"
echo "  - feature/create-new-develop-branch-devconta-16-53-42"
echo "  - feature/create-new-develop-branch-devconta-17-04-55"
echo "  - feature/update-documentation-structure-20-07-56"
echo "  - feature/update-documentation-structure-and-style-19-05-16"
echo ""

if confirm "¿Deseas eliminar estas ramas remotas?"; then
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
        git push origin --delete "$branch" 2>&1 || echo -e "${YELLOW}Nota: No se pudo eliminar $branch (puede estar ya eliminada)${NC}"
    done

    echo -e "${GREEN}Ramas feature eliminadas${NC}"
else
    echo -e "${YELLOW}Eliminación de ramas feature omitida${NC}"
fi

echo ""

# 3. Eliminación de rama claude/* remota obsoleta
echo -e "${YELLOW}Paso 3: Eliminación de rama claude/* remota obsoleta${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Rama actual: $CURRENT_BRANCH"
echo ""
echo "Rama claude obsoleta a eliminar:"
echo "  - claude/code-session-setup-011CUiWCQiZowE28eEmsTxVJ"
echo ""
echo "Nota: La rama claude/move-processes-to-governance ya fue eliminada"
echo ""

if confirm "¿Deseas eliminar esta rama remota?"; then
    echo "Eliminando claude/code-session-setup-011CUiWCQiZowE28eEmsTxVJ..."
    git push origin --delete claude/code-session-setup-011CUiWCQiZowE28eEmsTxVJ 2>&1 || {
        echo -e "${YELLOW}Nota: No se pudo eliminar (puede estar ya eliminada)${NC}"
    }

    echo -e "${YELLOW}Nota: La rama $CURRENT_BRANCH no se eliminó (es la rama actual de trabajo)${NC}"
    echo -e "${YELLOW}Elimínala manualmente después de hacer merge a develop${NC}"
    echo -e "${GREEN}Ramas claude eliminadas${NC}"
else
    echo -e "${YELLOW}Eliminación de ramas claude omitida${NC}"
fi

echo ""

# 4. Limpieza de referencias locales
echo -e "${YELLOW}Paso 4: Limpieza de referencias locales${NC}"
echo "Actualizando referencias remotas..."
git fetch --prune origin

echo ""
echo -e "${GREEN}=== Verificación Final ===${NC}"
echo ""
echo -e "${BLUE}Ramas remotas actuales:${NC}"
git branch -r | sort

echo ""
echo -e "${BLUE}Estadísticas:${NC}"
REMOTE_BRANCHES=$(git branch -r | wc -l)
echo "  Total de ramas remotas: $REMOTE_BRANCHES"
echo "  Objetivo: 4 (develop, docs, devcontainer, main)"

if [ "$REMOTE_BRANCHES" -eq 4 ]; then
    echo -e "${GREEN}  Estado: OK - Estructura correcta${NC}"
elif [ "$REMOTE_BRANCHES" -gt 4 ]; then
    echo -e "${YELLOW}  Estado: Ramas adicionales detectadas ($REMOTE_BRANCHES total)${NC}"
    echo -e "${YELLOW}  Ramas sobrantes:${NC}"
    git branch -r | grep -v -E '(develop|docs|devcontainer|main)$' | sed 's/^/    /'
else
    echo -e "${RED}  Estado: Faltan ramas principales${NC}"
fi

echo ""
echo -e "${GREEN}=== Proceso Completado ===${NC}"
echo ""
echo "Siguiente paso:"
echo "  1. Cambiar a develop: git checkout develop"
echo "  2. Si todo está correcto, eliminar rama de trabajo:"
echo "     git push origin --delete $CURRENT_BRANCH"
echo "     git branch -D $CURRENT_BRANCH"
echo ""
echo "Para más detalles, consulta:"
echo "  - Runbook: docs/devops/runbooks/merge_y_limpieza_ramas.md"
echo "  - Registro: docs/qa/registros/2025_11_05_merge_ramas_gitops.md"
