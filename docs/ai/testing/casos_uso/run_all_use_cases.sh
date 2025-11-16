#!/bin/bash
# Script maestro para ejecutar todos los casos de uso

echo "=========================================="
echo "  CASOS DE USO: AGENTES SDLC"
echo "=========================================="
echo

# Caso 1: Viabilidad
echo "CASO 1: Evaluacion de Viabilidad"
echo "----------------------------------"
python3 test_case1_viabilidad.py 2>&1 | grep -v "Constitution\|INFO\|WARNING\|ERROR"
echo

# Caso 6: UML
echo "CASO 6: Generacion de Diagramas UML"
echo "------------------------------------"
python3 test_case6_uml.py 2>&1 | grep -v "Constitution\|INFO\|WARNING"
echo

# Resumen de artifacts
echo "=========================================="
echo "  ARTIFACTS GENERADOS"
echo "=========================================="
echo
echo "Feasibility Reports:"
ls -1 docs/sdlc_outputs/feasibility/ | tail -3
echo
echo "Design Documents:"
ls -1 docs/sdlc_outputs/design/ | tail -4
echo
echo "Testing Documents:"
ls -1 docs/sdlc_outputs/testing/ | tail -4
echo
echo "Deployment Documents:"
ls -1 docs/sdlc_outputs/deployment/ | tail -5
echo
echo "Orchestration Reports:"
ls -1 docs/sdlc_outputs/orchestration/ | tail -2
echo

echo "=========================================="
echo "  DOCUMENTACION"
echo "=========================================="
echo
echo "Guia completa:"
echo "  docs/ai/SDLC_AGENTS_GUIDE.md"
echo
echo "Casos de uso:"
echo "  docs/ai/CASOS_DE_USO_SDLC.md"
echo
echo "Ejemplos ejecutables:"
echo "  examples/sdlc_pipeline_complete.py"
echo "  examples/sdlc_feasibility_only.py"
echo "  examples/sdlc_compare_providers.py"
echo
echo "=========================================="
