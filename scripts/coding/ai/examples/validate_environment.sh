#!/bin/bash
# scripts/ai/examples/validate_environment.sh
# Validación exhaustiva del entorno para generación de tests

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo "=========================================="
echo "  VALIDACIÓN DE ENTORNO"
echo "=========================================="
echo ""

# ==============================================================================
# 1. PYTHON Y DEPENDENCIAS
# ==============================================================================
echo -e "${BLUE}[1] Validando Python y dependencias${NC}"
echo ""

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        echo -e "${GREEN}[OK]${NC} Python $PYTHON_VERSION (>= 3.10 requerido)"
    else
        echo -e "${RED}[FAIL]${NC} Python $PYTHON_VERSION (se requiere >= 3.10)"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}[FAIL]${NC} Python 3 no encontrado"
    ERRORS=$((ERRORS + 1))
fi

# pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | awk '{print $2}')
    echo -e "${GREEN}[OK]${NC} pip $PIP_VERSION"
else
    echo -e "${RED}[FAIL]${NC} pip3 no encontrado"
    ERRORS=$((ERRORS + 1))
fi

# Paquetes Python requeridos
REQUIRED_PACKAGES=(
    "pytest:pytest"
    "pytest_cov:pytest-cov"
    "anthropic:anthropic"
    "ruff:ruff"
    "black:black"
    "isort:isort"
)

for pkg_pair in "${REQUIRED_PACKAGES[@]}"; do
    IFS=':' read -r import_name pkg_name <<< "$pkg_pair"

    if python3 -c "import $import_name" 2>/dev/null; then
        VERSION=$(python3 -c "import $import_name; print(getattr($import_name, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}[OK]${NC} $pkg_name ($VERSION)"
    else
        echo -e "${RED}[FAIL]${NC} $pkg_name no encontrado"
        echo "       Instalar: pip install $pkg_name"
        ERRORS=$((ERRORS + 1))
    fi
done

# Paquetes opcionales
OPTIONAL_PACKAGES=(
    "mypy:mypy"
    "hypothesis:hypothesis"
)

for pkg_pair in "${OPTIONAL_PACKAGES[@]}"; do
    IFS=':' read -r import_name pkg_name <<< "$pkg_pair"

    if python3 -c "import $import_name" 2>/dev/null; then
        VERSION=$(python3 -c "import $import_name; print(getattr($import_name, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}[OK]${NC} $pkg_name ($VERSION) [opcional]"
    else
        echo -e "${YELLOW}[WARN]${NC} $pkg_name no encontrado [opcional]"
        WARNINGS=$((WARNINGS + 1))
    fi
done

echo ""

# ==============================================================================
# 2. CONFIGURACIÓN DE API
# ==============================================================================
echo -e "${BLUE}[2] Validando configuración de API${NC}"
echo ""

# ANTHROPIC_API_KEY
if [ -n "$ANTHROPIC_API_KEY" ]; then
    KEY_LENGTH=${#ANTHROPIC_API_KEY}
    if [ "$KEY_LENGTH" -gt 20 ]; then
        MASKED_KEY="${ANTHROPIC_API_KEY:0:10}...${ANTHROPIC_API_KEY: -4}"
        echo -e "${GREEN}[OK]${NC} ANTHROPIC_API_KEY configurada ($MASKED_KEY)"

        # Validar formato
        if [[ "$ANTHROPIC_API_KEY" =~ ^sk-ant-api03- ]]; then
            echo -e "${GREEN}[OK]${NC} Formato de API key válido"
        else
            echo -e "${YELLOW}[WARN]${NC} Formato de API key no estándar"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo -e "${RED}[FAIL]${NC} ANTHROPIC_API_KEY parece inválida (muy corta)"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}[FAIL]${NC} ANTHROPIC_API_KEY no configurada"
    echo "       export ANTHROPIC_API_KEY='sk-ant-api03-...'"
    ERRORS=$((ERRORS + 1))
fi

# Archivo .env (alternativa)
if [ -f "../../.env" ]; then
    if grep -q "ANTHROPIC_API_KEY" ../../.env; then
        echo -e "${GREEN}[OK]${NC} Archivo .env encontrado con ANTHROPIC_API_KEY"
    else
        echo -e "${YELLOW}[INFO]${NC} Archivo .env existe pero sin ANTHROPIC_API_KEY"
    fi
else
    echo -e "${YELLOW}[INFO]${NC} No se encontró archivo .env (opcional)"
fi

echo ""

# ==============================================================================
# 3. HERRAMIENTAS EXTERNAS
# ==============================================================================
echo -e "${BLUE}[3] Validando herramientas externas${NC}"
echo ""

# git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    echo -e "${GREEN}[OK]${NC} git $GIT_VERSION"
else
    echo -e "${RED}[FAIL]${NC} git no encontrado"
    ERRORS=$((ERRORS + 1))
fi

# gh (GitHub CLI)
if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version | head -1 | awk '{print $3}')
    echo -e "${GREEN}[OK]${NC} GitHub CLI $GH_VERSION"

    # Validar autenticación
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} GitHub CLI autenticado"
    else
        echo -e "${YELLOW}[WARN]${NC} GitHub CLI no autenticado (gh auth login)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}[WARN]${NC} GitHub CLI no encontrado (PR creation deshabilitado)"
    echo "       Instalar: https://cli.github.com/"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ==============================================================================
# 4. ESTRUCTURA DEL PROYECTO
# ==============================================================================
echo -e "${BLUE}[4] Validando estructura del proyecto${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$AI_DIR/../.." && pwd)"

# Archivos esenciales
REQUIRED_FILES=(
    "$AI_DIR/test_generation_orchestrator.py"
    "$AI_DIR/agents/base.py"
    "$AI_DIR/agents/coverage_analyzer.py"
    "$AI_DIR/config/test_generation.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}[OK]${NC} $(basename "$file")"
    else
        echo -e "${RED}[FAIL]${NC} Archivo no encontrado: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

# Directorio de tests
if [ -d "$PROJECT_ROOT/api/callcentersite/tests" ]; then
    TEST_COUNT=$(find "$PROJECT_ROOT/api/callcentersite/tests" -name "test_*.py" | wc -l)
    echo -e "${GREEN}[OK]${NC} Directorio de tests existe ($TEST_COUNT tests encontrados)"
else
    echo -e "${YELLOW}[WARN]${NC} Directorio de tests no encontrado"
    WARNINGS=$((WARNINGS + 1))
fi

# pytest.ini o pyproject.toml
if [ -f "$PROJECT_ROOT/api/callcentersite/pytest.ini" ] || [ -f "$PROJECT_ROOT/api/callcentersite/pyproject.toml" ]; then
    echo -e "${GREEN}[OK]${NC} Configuración de pytest encontrada"
else
    echo -e "${YELLOW}[WARN]${NC} No se encontró pytest.ini ni pyproject.toml"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# ==============================================================================
# 5. PERMISOS Y ACCESO
# ==============================================================================
echo -e "${BLUE}[5] Validando permisos y acceso${NC}"
echo ""

# Permisos de escritura
OUTPUT_DIR="$AI_DIR/output"
if [ -d "$OUTPUT_DIR" ]; then
    if [ -w "$OUTPUT_DIR" ]; then
        echo -e "${GREEN}[OK]${NC} Permisos de escritura en output/"
    else
        echo -e "${RED}[FAIL]${NC} Sin permisos de escritura en output/"
        ERRORS=$((ERRORS + 1))
    fi
else
    # Intentar crear
    if mkdir -p "$OUTPUT_DIR" 2>/dev/null; then
        echo -e "${GREEN}[OK]${NC} Directorio output/ creado"
    else
        echo -e "${RED}[FAIL]${NC} No se pudo crear directorio output/"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Repositorio git
if git -C "$PROJECT_ROOT" rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Repositorio git válido"

    # Branch actual
    CURRENT_BRANCH=$(git -C "$PROJECT_ROOT" branch --show-current)
    echo -e "${GREEN}[OK]${NC} Branch actual: $CURRENT_BRANCH"

    # Estado del repo
    if git -C "$PROJECT_ROOT" diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${GREEN}[OK]${NC} Working directory limpio"
    else
        echo -e "${YELLOW}[WARN]${NC} Hay cambios sin commitear"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}[FAIL]${NC} No es un repositorio git válido"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# ==============================================================================
# 6. CONECTIVIDAD
# ==============================================================================
echo -e "${BLUE}[6] Validando conectividad${NC}"
echo ""

# API de Anthropic
if command -v curl &> /dev/null && [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "Probando conexión con API de Anthropic..."

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST https://api.anthropic.com/v1/messages \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{
          "model": "claude-3-5-sonnet-20241022",
          "max_tokens": 1,
          "messages": [{"role": "user", "content": "test"}]
        }' 2>/dev/null)

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "${GREEN}[OK]${NC} Conexión exitosa con API de Anthropic"
    elif [ "$HTTP_CODE" -eq 401 ]; then
        echo -e "${RED}[FAIL]${NC} API key inválida (HTTP 401)"
        ERRORS=$((ERRORS + 1))
    elif [ "$HTTP_CODE" -eq 429 ]; then
        echo -e "${YELLOW}[WARN]${NC} Rate limit alcanzado (HTTP 429)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${YELLOW}[WARN]${NC} Respuesta inesperada de API (HTTP $HTTP_CODE)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}[INFO]${NC} Saltando validación de conectividad (curl no disponible o API key no configurada)"
fi

echo ""

# ==============================================================================
# RESUMEN
# ==============================================================================
echo "=========================================="
echo "  RESUMEN"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}TODO OK${NC} - Entorno completamente configurado"
    echo ""
    echo "Siguientes pasos:"
    echo "  1. ./quickstart.sh demo    # Ejecutar demo"
    echo "  2. ./quickstart.sh basic   # Ejecución básica"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}OK CON ADVERTENCIAS${NC} - El sistema funcionará pero con limitaciones"
    echo ""
    echo "Advertencias: $WARNINGS"
    echo ""
    echo "Puedes continuar, pero considera resolver las advertencias."
    exit 0
else
    echo -e "${RED}FALLO${NC} - Se encontraron problemas críticos"
    echo ""
    echo "Errores: $ERRORS"
    echo "Advertencias: $WARNINGS"
    echo ""
    echo "Resuelve los errores antes de continuar."
    exit 1
fi
