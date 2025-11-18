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

    run_test "verify_required_scripts aprueba con scripts presentes" test_verify_required_scripts_succeeds_when_files_exist || tests_failed=$((tests_failed + 1))
    tests_run=$((tests_run + 1))

    run_test "verify_required_scripts detecta scripts dinámicos faltantes" test_verify_required_scripts_detects_missing_dynamic_step || tests_failed=$((tests_failed + 1))
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

    local status=0

    "$@" "$fixture_dir" || status=$?

    rm -rf "$fixture_dir"

    return "$status"
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

create_stub_script() {
    local path="$1"

    cat <<'SCRIPT' > "$path"
#!/usr/bin/env bash
exit 0
SCRIPT
    chmod +x "$path"
}

prepare_required_scripts() {
    local root="$1"
    local -a names=(
        system_prepare.sh
        mariadb_install.sh
        postgres_install.sh
        setup_mariadb_database.sh
        setup_postgres_database.sh
    )

    local name
    for name in "${names[@]}"; do
        create_stub_script "$root/scripts/$name"
    done
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
    assert_equals 'script:'"${_fixture_dir}"'/scripts/system_prepare.sh' "${steps[4]}" 'Ruta de script de sistema incorrecta' || return 1
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

test_verify_required_scripts_succeeds_when_files_exist() {
    with_bootstrap_environment __test_verify_required_scripts_succeeds_impl
}

__test_verify_required_scripts_succeeds_impl() {
    local fixture_dir="$1"

    prepare_required_scripts "$fixture_dir"

    if ! verify_required_scripts; then
        printf 'ERROR: verify_required_scripts debería aprobar cuando existen todos los scripts\n' >&2
        return 1
    fi

    return 0
}

test_verify_required_scripts_detects_missing_dynamic_step() {
    with_bootstrap_environment __test_verify_required_scripts_detects_missing_impl
}

__test_verify_required_scripts_detects_missing_impl() {
    local fixture_dir="$1"

    prepare_required_scripts "$fixture_dir"

    define_database_steps() {
        printf '%s\n' \
            "script:$fixture_dir/scripts/mariadb_install.sh" \
            "script:$fixture_dir/scripts/postgres_install.sh" \
            "script:$fixture_dir/scripts/setup_mariadb_database.sh" \
            "script:$fixture_dir/scripts/setup_postgres_database.sh" \
            "script:$fixture_dir/scripts/custom-migration.sh"
    }

    local output
    if output=$(verify_required_scripts 2>&1); then
        printf 'ERROR: verify_required_scripts debió fallar ante script dinámico faltante\n' >&2
        printf '%s\n' "$output" >&2
        return 1
    fi

    assert_contains 'Script faltante' "$output" 'Debe reportar el script faltante' || return 1
    assert_contains 'custom-migration.sh' "$output" 'Debe incluir el nombre del script dinámico faltante' || return 1

    return 0
}

main "$@"
