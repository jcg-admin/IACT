#!/bin/bash
# scripts/ai/examples/example_single_file.sh
# Ejemplo: Generar tests para un solo archivo específico

set -e

# Configuración
TARGET_FILE="$1"
if [ -z "$TARGET_FILE" ]; then
    echo "Uso: $0 <archivo_python>"
    echo ""
    echo "Ejemplo:"
    echo "  $0 api/callcentersite/app/models.py"
    exit 1
fi

if [ ! -f "$TARGET_FILE" ]; then
    echo "ERROR: Archivo no existe: $TARGET_FILE"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Generando tests para: $TARGET_FILE"
echo ""

# Crear configuración temporal
CONFIG_FILE=$(mktemp /tmp/test_gen_XXXXX.json)
cat > "$CONFIG_FILE" << EOF
{
  "save_results": true,
  "output_dir": "output/test_generation_single",
  "agents": {
    "coverage_analyzer": {
      "target_files": ["$TARGET_FILE"],
      "min_coverage": 85,
      "threshold_low": 0
    },
    "test_planner": {
      "max_tests_per_run": 1,
      "focus_on_target": true
    },
    "llm_generator": {
      "llm_provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    },
    "syntax_validator": {
      "run_mypy": false
    },
    "test_runner": {},
    "coverage_verifier": {
      "min_coverage_increase": 5.0
    },
    "pr_creator": {
      "enabled": false
    }
  }
}
EOF

# Ejecutar
cd "$AI_DIR"
python3 test_generation_orchestrator.py \
    --project-path "$(dirname "$TARGET_FILE")" \
    --config "$CONFIG_FILE"

# Limpiar
rm -f "$CONFIG_FILE"

echo ""
echo "Tests generados en: output/test_generation_single/"
