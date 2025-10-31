#!/usr/bin/env bash
set -euo pipefail

main() {
    local tests_run=0
    local tests_failed=0

    run_test "build_bootstrap_steps trims definitions" test_build_bootstrap_steps_trims || tests_failed=$((tests_failed + 1))
    tests_run=$((tests_run + 1))

    run_test "execute_installation_script propaga fallos" test_execute_installation_script_failure || tests_failed=$((tests_failed + 1))
    tests_run=$((tests_run + 1))

    run_test "run_bootstrap_steps reporta fallos de funciones" test_run_bootstrap_steps_reports_failures || tests_failed=$((tests_failed + 1))
    tests_run=$((tests_run + 1))

    printf "Pruebas ejecutadas: %d\n" "$tests_run"

    if [[ "$tests_failed" -gt 0 ]]; then
        printf "Pruebas fallidas: %d\n" "$tests_failed" >&2
        return 1
    fi

    printf "Todas las pruebas pasaron\n"
    return 0
}

run_test() {
    local description="$1"
    local function_name="$2"

    printf -- "- %s..." "$description"
    if "$function_name"; then
        printf " ok\n"
        return 0
    else
        printf " fallo\n" >&2
        return 1
    fi
}

setup_fixture() {
    local fixture_dir
    fixture_dir="$(mktemp -d)"

    mkdir -p "$fixture_dir/scripts" "$fixture_dir/utils" "$fixture_dir/logs"

    cat <<'STUB' > "$fixture_dir/utils/core.sh"
#!/usr/bin/env bash
iact_source_module() { return 0; }
iact_init_logging() { :; }
iact_log_step() { :; }
iact_log_info() { :; }
iact_log_error() { printf '%s\n' "$*" >&2; }
iact_log_success() { :; }
iact_get_log_file() { printf '%s\n' "${IACT_TEST_LOG_FILE:-/tmp/iact-test.log}"; }
iact_get_context() { printf 'test\n'; }
STUB

    printf '%s\n' "$fixture_dir"
}

source_bootstrap_as_library() {
    local fixture_dir="$1"

    export IACT_BOOTSTRAP_MODE="library"
    export IACT_BOOTSTRAP_TEST_ROOT="$fixture_dir"
    export IACT_TEST_LOG_FILE="$fixture_dir/logs/bootstrap.log"

    # shellcheck disable=SC1091
    source "$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)/bootstrap.sh"
}

with_bootstrap_environment() {
    local fixture_dir
    fixture_dir=$(setup_fixture)

    source_bootstrap_as_library "$fixture_dir"

    if ! setup_environment; then
        printf 'ERROR: setup_environment falló durante la preparación del fixture\n' >&2
        rm -rf "$fixture_dir"
        return 1
    fi

    "$@" "$fixture_dir"

    rm -rf "$fixture_dir"
}

assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"

    if [[ "$expected" != "$actual" ]]; then
        printf 'ERROR: %s\nEsperado: %s\nActual: %s\n' "$message" "$expected" "$actual" >&2
        return 1
    fi
    return 0
}

assert_contains() {
    local needle="$1"
    local haystack="$2"
    local message="$3"

    if [[ "$haystack" != *"$needle"* ]]; then
        printf 'ERROR: %s\nNo se encontró "%s" en:\n%s\n' "$message" "$needle" "$haystack" >&2
        return 1
    fi
    return 0
}

test_build_bootstrap_steps_trims() {
    with_bootstrap_environment __test_build_bootstrap_steps_trims_impl
}

__test_build_bootstrap_steps_trims_impl() {
    local _fixture_dir="$1"
    local -a steps

    readarray -t steps < <(build_bootstrap_steps all)

    local last_index=$(( ${#steps[@]} - 1 ))

    assert_equals 'func:display_bootstrap_header' "${steps[0]}" 'Primer paso incorrecto' || return 1
    assert_equals 'script:'"${_fixture_dir}"'/scripts/system-prepare.sh' "${steps[4]}" 'Ruta de script de sistema incorrecta' || return 1
    assert_equals 'func:display_access_information' "${steps[last_index]}" 'Último paso incorrecto' || return 1
    return 0
}

test_execute_installation_script_failure() {
    with_bootstrap_environment __test_execute_installation_script_failure_impl
}

__test_execute_installation_script_failure_impl() {
    local fixture_dir="$1"
    local failing_script="$fixture_dir/scripts/fail.sh"

    cat <<'SCRIPT' > "$failing_script"
#!/usr/bin/env bash
exit 3
SCRIPT
    chmod +x "$failing_script"

    local status=0

    if execute_installation_script "$failing_script" 1 1; then
        printf 'ERROR: Se esperaba fallo de execute_installation_script\n' >&2
        return 1
    else
        status=$?
    fi

    assert_equals '3' "$status" 'Código de salida propagado' || return 1
    return 0
}

test_run_bootstrap_steps_reports_failures() {
    with_bootstrap_environment __test_run_bootstrap_steps_reports_failures_impl
}

__test_run_bootstrap_steps_reports_failures_impl() {
    successful_step() { return 0; }
    failing_step() { return 1; }

    local output
    if output=$(run_bootstrap_steps 'func:successful_step' 'func:failing_step' 2>&1); then
        printf 'ERROR: run_bootstrap_steps debió fallar\n' >&2
        return 1
    fi

    assert_contains 'failing_step' "$output" 'El resumen debe incluir el paso fallido' || return 1
    return 0
}

main "$@"
