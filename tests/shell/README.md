# Shell Scripts Testing Framework

Testing framework for shell scripts following SHELL_SCRIPTS_CONSTITUTION.md RULE 4.

## Structure

```
tests/shell/
├── unit/           # Unit tests (no external dependencies)
├── integration/    # Integration tests (module interactions)
└── e2e/           # End-to-end tests (full workflows)
```

## Rules

**RULE 4 (Constitution)**: Tests executable without external dependencies.

- NO internet required
- NO databases required
- NO external APIs
- Use mocks/stubs for external dependencies

## Running Tests

```bash
# Run all unit tests
bash tests/shell/run_all_unit_tests.sh

# Run specific test
bash tests/shell/unit/test_logger.sh

# Run with constitution validation
bash scripts/validation/quality/validate_shell_constitution.sh tests/shell/unit/*.sh
```

## Writing Tests

### Template

```bash
#!/bin/bash
# tests/shell/unit/test_MODULE.sh

set -euo pipefail

# Source module under test
source scripts/lib/MODULE.sh

# Mock external dependencies (RULE 4)
log_info() { echo "INFO: $*"; }
log_error() { echo "ERROR: $*" >&2; }

# Test functions
test_function_name_success() {
    # Setup
    local input="test"

    # Execute
    if function_name "$input"; then
        echo "PASS: test_function_name_success"
        return 0
    else
        echo "FAIL: test_function_name_success"
        return 1
    fi
}

test_function_name_failure() {
    # Test error case
    if function_name ""; then
        echo "FAIL: Should have failed with empty input"
        return 1
    else
        echo "PASS: Correctly failed with empty input"
        return 0
    fi
}

# Run all tests
main() {
    local failed=0

    test_function_name_success || failed=$((failed + 1))
    test_function_name_failure || failed=$((failed + 1))

    if [ $failed -eq 0 ]; then
        echo "ALL TESTS PASSED"
        return 0
    else
        echo "TESTS FAILED: $failed"
        return 1
    fi
}

main
```

## Examples

See:
- `unit/test_logger.sh` - Logger module tests
- `unit/test_validator.sh` - Validator module tests
- `integration/test_hooks_integration.sh` - Git hooks integration

## Constitution Compliance

All test files must comply with:
- RULE 3: Explicit error handling (set -euo pipefail)
- RULE 4: No external dependencies
- RULE 5: Clean Code naming
- RULE 7: Inline documentation
