# Install prebuilt CPython fallback script

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds. Maintain this plan according to `.agent/PLANS.md`.

## Purpose / Big Picture

Provide a reproducible fallback script that downloads a prebuilt CPython artifact for Ubuntu 20.04 builders. After implementation, operators can run `./install.sh` (symlinked to the new script) to fetch and install the `cpython-3.12.6-ubuntu20.04-build1.tgz` artifact into `/opt/python-3.12.6`, verifying installation by printing the Python version. This offers an alternative when compiling from source is blocked by missing compilers or expired repositories.

## Progress

- [x] (2024-09-27 12:30Z) Add regression tests describing the expected install script behavior (shebang, wget usage, extraction, verification command); confirmed they fail because the script is missing.
- [x] (2024-09-27 12:45Z) Implement `scripts/install_prebuilt_cpython.sh` to satisfy the new tests with configurable artifact/version variables; targeted pytest suite now passes.
- [x] (2024-09-27 12:55Z) Confirmed bootstrap messaging already highlights the symlink; documented fallback via automated tests and noted unrelated suite failures during full pytest run.
- [x] (2025-11-14 06:12Z) Refactored the install script to source shared logging utilities and adjusted tests to enforce the DRY expectation raised during review feedback.
- [x] (2025-11-14 07:25Z) Added a top-level `scripts/build_cpython.sh` entrypoint that delegates to the infrastructure build script so the Vagrant guidance matches the repository layout; captured coverage with a new pytest module.

## Surprises & Discoveries

- Observation: Full `pytest infrastructure/cpython/tests` currently fails in this repository due to pre-existing missing infrastructure scripts and modules (e.g., validate_build.sh, recovery_plan_parser).
  Evidence: pytest output on 2024-09-27 showing 15 failures unrelated to the new install script.

## Decision Log

- Decision: Allow overriding artifact metadata via environment variables instead of CLI flags to keep script usage simple while remaining configurable.
  Rationale: Bootstrap and user instructions expect a straightforward command; environment overrides avoid breaking existing symlink workflows yet permit custom builds.
  Date/Author: 2024-09-27 / ChatGPT
- Decision: Reuse the repository's shared logging helpers instead of redefining ad-hoc `log_info`/`log_error` functions inside the installer.
  Rationale: Aligns with DRY expectations from reviewers and ensures consistent log formatting across infrastructure scripts.
  Date/Author: 2025-11-14 / ChatGPT
- Decision: Provide a thin executable wrapper in `scripts/` that defers to `infrastructure/cpython/scripts/build_cpython.sh` instead of duplicating the build logic.
  Rationale: Keeps the single source of truth for build operations while satisfying the provisioning instructions that reference `./scripts/build_cpython.sh`.
  Date/Author: 2025-11-14 / ChatGPT

## Outcomes & Retrospective

The install script is now covered by regression tests and passes targeted pytest checks. Running the entire infrastructure suite still fails because this workspace lacks several legacy scripts and parser modules referenced by other tests; these gaps predate the new fallback and remain out of scope for this change.

## Context and Orientation

The provisioning flow resides in `infrastructure/cpython/bootstrap.sh`, which already attempts to symlink `install.sh` to `scripts/install_prebuilt_cpython.sh` if the script exists. Currently, that script is absent, so the symlink step issues a warning. Tests for the bootstrap live in `infrastructure/cpython/tests/`. We will add tests ensuring the presence and key steps of the install script, mirroring the user-provided manual commands. The script should:

1. Download the artifact with `wget` into `/tmp/cpython.tgz` (or a configurable temp location).
2. Extract into `/opt/python-<version>` with `sudo tar -xzf ... --strip-components=1`.
3. Print the installed Python version using the extracted interpreter.

We should allow overriding the artifact URL, install prefix, and version/build via environment variables so the script remains maintainable.

## Plan of Work

1. Create a new test module `infrastructure/cpython/tests/test_install_prebuilt_script.py`. The tests will assert that `scripts/install_prebuilt_cpython.sh` exists, is executable, contains a shebang, and references the commands `wget`, `tar -xzf`, and `bin/python3 --version`. Another test will verify that default configuration variables in the script match the documented artifact (version `3.12.6`, build `build1`, Ubuntu `20.04`).
2. Run `pytest infrastructure/cpython/tests/test_install_prebuilt_script.py` and observe failures because the script does not yet exist (Red phase).
3. Implement `scripts/install_prebuilt_cpython.sh` as a Bash script using `set -euo pipefail`, declaring configurable defaults (artifact URL, version, build number, install prefix, temp file). The script should download with retry logic, extract, adjust permissions, and finally execute `/opt/python-<version>/bin/python3 --version`. Ensure the script is executable (`chmod +x`).
4. Optionally update bootstrap tests or script to mention the fallback only if necessary for coverage (e.g., ensure symlink step logs success once script exists). No major bootstrap changes required beyond ensuring the script path resolves.
5. Re-run the targeted pytest module to confirm tests pass (Green). Follow with the full `pytest infrastructure/cpython/tests` suite to ensure no regressions.
6. Refactor if needed for clarity (e.g., shared utility functions in the script), keeping tests green.

## Concrete Steps

1. Working directory: `/workspace/IACT---project`. Command: `pytest infrastructure/cpython/tests/test_install_prebuilt_script.py` (expected failure: file missing).
2. Create `scripts/install_prebuilt_cpython.sh` with executable permissions. Re-run the same pytest command (expected pass).
3. Execute `pytest infrastructure/cpython/tests` to cover the broader suite.

## Validation and Acceptance

Acceptance criteria: Running `pytest infrastructure/cpython/tests` succeeds, and manually invoking `./scripts/install_prebuilt_cpython.sh --dry-run` (if implemented) or `./install.sh` after provisioning downloads and installs the artifact, outputting `Python 3.12.6`. For repository validation, ensure tests assert the presence of commands matching the manual instructions. Documentation or log messages should reflect the new capability.

## Idempotence and Recovery

The script should be safe to re-run: it can skip download if the artifact exists locally (optional) or overwrite by default while backing up existing installations. Tests will not execute the script but only assert its content, maintaining idempotence in the repository state. If the download fails, the script exits non-zero, leaving partial directories removable via `sudo rm -rf /opt/python-<version>`.

## Artifacts and Notes

- Pytest (targeted):
      $ pytest infrastructure/cpython/tests/test_install_prebuilt_script.py
      ... 3 passed in 0.03s
- Pytest (full suite - expected pre-existing failures):
      $ pytest infrastructure/cpython/tests
      ... 15 failed, 47 passed (missing legacy scripts/modules)

## Interfaces and Dependencies

- Shell environment with `wget`, `tar`, and `sudo` available inside the builder VM.
- Artifact naming convention `cpython-<version>-ubuntu20.04-<build>.tgz`. The script should construct URLs accordingly and expose override variables (`ARTIFACT_URL`, `PYTHON_VERSION`, `BUILD_ID`, `INSTALL_PREFIX`).
