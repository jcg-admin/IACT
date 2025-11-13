#!/bin/bash
# scripts/ai/examples/example_ci_integration.sh
# Ejemplo: Integración con CI/CD (GitHub Actions, GitLab CI, etc)

set -e

# Este script está diseñado para ejecutarse en CI
# Valida y ejecuta generación de tests solo si:
# 1. Cobertura actual < objetivo
# 2. Hay archivos nuevos o modificados sin tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$AI_DIR/../.." && pwd)"
API_DIR="$PROJECT_ROOT/api/callcentersite"

echo "=========================================="
echo "  CI/CD TEST GENERATION"
echo "=========================================="
echo ""

# Verificar si estamos en CI
if [ -z "$CI" ]; then
    echo "WARNING: No se detectó entorno CI"
    echo "         Variables CI esperadas: CI=true"
    echo ""
fi

# 1. Analizar cobertura actual
echo "[1/5] Analizando cobertura actual..."
cd "$API_DIR"

if ! pytest --cov=callcentersite --cov-report=json --cov-report=term-missing -q; then
    echo "ERROR: Tests fallaron"
    exit 1
fi

COVERAGE_FILE="coverage.json"
if [ ! -f "$COVERAGE_FILE" ]; then
    echo "ERROR: No se generó coverage.json"
    exit 1
fi

CURRENT_COVERAGE=$(python3 -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])")
TARGET_COVERAGE=85

echo "  Cobertura actual: ${CURRENT_COVERAGE}%"
echo "  Objetivo:         ${TARGET_COVERAGE}%"
echo ""

# 2. Decidir si generar tests
if (( $(echo "$CURRENT_COVERAGE >= $TARGET_COVERAGE" | bc -l) )); then
    echo "[2/5] Cobertura suficiente - No se requiere generación"
    echo "      Saliendo..."
    exit 0
else
    echo "[2/5] Cobertura insuficiente - Iniciando generación"
    GAP=$(echo "$TARGET_COVERAGE - $CURRENT_COVERAGE" | bc)
    echo "      Gap: ${GAP}%"
fi
echo ""

# 3. Validar API key
echo "[3/5] Validando credenciales..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY no configurada"
    echo "       Configurar en CI secrets"
    exit 1
fi
echo "  API Key configurada: OK"
echo ""

# 4. Ejecutar generación
echo "[4/5] Generando tests automáticamente..."
cd "$AI_DIR"

# Configuración para CI
CONFIG_FILE=$(mktemp /tmp/ci_test_gen_XXXXX.json)
cat > "$CONFIG_FILE" << EOF
{
  "save_results": true,
  "output_dir": "output/test_generation_ci",
  "agents": {
    "coverage_analyzer": {
      "min_coverage": $TARGET_COVERAGE,
      "threshold_low": 70
    },
    "test_planner": {
      "max_tests_per_run": 5
    },
    "llm_generator": {
      "llm_provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.3
    },
    "syntax_validator": {
      "run_mypy": true,
      "run_ruff": true,
      "run_black": true
    },
    "test_runner": {
      "timeout": 300
    },
    "coverage_verifier": {
      "min_coverage_increase": 5.0
    },
    "pr_creator": {
      "enabled": true,
      "auto_assign": true,
      "labels": ["bot-generated-tests", "ci-generated", "needs-review"],
      "draft": true
    }
  }
}
EOF

if python3 test_generation_orchestrator.py \
    --project-path "$API_DIR" \
    --config "$CONFIG_FILE"; then

    echo ""
    echo "[5/5] Generación exitosa"

    # Leer resultados
    RESULT_FILE="output/test_generation_ci/07_PRCreator.json"
    if [ -f "$RESULT_FILE" ]; then
        PR_URL=$(python3 -c "import json; print(json.load(open('$RESULT_FILE')).get('pr_url', 'N/A'))")
        echo ""
        echo "=========================================="
        echo "  RESULTADO"
        echo "=========================================="
        echo "Pull Request: $PR_URL"
        echo ""
        echo "ACCIÓN REQUERIDA:"
        echo "  1. Revisar tests generados"
        echo "  2. Validar que tests sean relevantes"
        echo "  3. Aprobar y mergear PR"
    fi

    rm -f "$CONFIG_FILE"
    exit 0
else
    echo ""
    echo "[5/5] Generación fallida"
    echo "      Ver logs para detalles"

    rm -f "$CONFIG_FILE"
    exit 1
fi
