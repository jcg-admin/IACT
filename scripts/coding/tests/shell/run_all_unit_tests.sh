#!/bin/bash
# tests/shell/run_all_unit_tests.sh
# Runs all unit tests for shell scripts

set -euo pipefail

readonly TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running all shell unit tests..."
echo "========================================"
echo ""

failed=0
passed=0

for test_file in "$TEST_DIR/unit"/test_*.sh; do
    if [ -f "$test_file" ]; then
        echo "Running: $(basename "$test_file")"
        if bash "$test_file"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        echo ""
    fi
done

echo "========================================"
echo "SUMMARY"
echo "========================================"
echo "Passed: $passed"
echo "Failed: $failed"
echo ""

if [ $failed -eq 0 ]; then
    echo "ALL TESTS PASSED"
    exit 0
else
    echo "SOME TESTS FAILED"
    exit 1
fi
