# GitHub Actions Workflow Audit

## Inventory
| Workflow | Triggers | Jobs | Cache (actions/cache) | Explicit permissions |
| --- | --- | ---: | :---: | :---: |
| actionlint.yml | push, pull_request, workflow_dispatch | 1 | No | Yes |
| agents-ci.yml | push, pull_request, workflow_dispatch | 7 | No | No |
| backend-ci.yml | push, pull_request | 6 | Yes | No |
| code-quality.yml | pull_request, workflow_dispatch | 1 | No | No |
| codeql.yml | push, pull_request, schedule | 1 | No | No |
| dependency-review.yml | pull_request | 1 | No | No |
| deploy.yml | push, workflow_dispatch | 7 | No | No |
| docs-validation.yml | pull_request, push | 6 | No | No |
| docs.yml | push, pull_request, workflow_dispatch | 3 | No | Yes |
| emoji-validation.yml | pull_request, push | 1 | No | No |
| frontend-ci.yml | push, pull_request | 8 | No | No |
| incident-response.yml | workflow_dispatch | 5 | No | No |
| infrastructure-ci.yml | push, pull_request | 7 | No | No |
| lint.yml | pull_request, push | 1 | No | No |
| meta-architecture-check.yml | pull_request, push, workflow_dispatch | 2 | No | No |
| migrations.yml | pull_request, push | 5 | No | No |
| pr-review.yml | issue_comment | 1 | No | Yes |
| python_ci.yml | push, pull_request, workflow_dispatch | 5 | No | No |
| release.yml | push, workflow_dispatch | 7 | No | Yes |
| requirements_index.yml | push, pull_request, workflow_dispatch | 1 | No | Yes |
| requirements_validate_traceability.yml | pull_request, push, workflow_dispatch | 1 | No | No |
| security-scan.yml | push, pull_request, schedule | 11 | No | No |
| sync-docs.yml | schedule, workflow_dispatch | 2 | No | No |
| test-pyramid.yml | push, pull_request, schedule | 3 | No | No |
| validate-guides.yml | pull_request, push, workflow_dispatch | 5 | No | No |

## Quick findings
- Total workflows: 25.
- Workflows with `workflow_dispatch`: 13/25.
- Missing `workflow_dispatch`: backend-ci.yml, codeql.yml, dependency-review.yml, docs-validation.yml, emoji-validation.yml, frontend-ci.yml, infrastructure-ci.yml, lint.yml, migrations.yml, pr-review.yml, security-scan.yml, test-pyramid.yml
- Missing `push` trigger: code-quality.yml, dependency-review.yml, incident-response.yml, pr-review.yml, sync-docs.yml
- Missing `pull_request` trigger: deploy.yml, incident-response.yml, pr-review.yml, release.yml, sync-docs.yml
- Lacking explicit top-level `permissions`: agents-ci.yml, backend-ci.yml, code-quality.yml, codeql.yml, dependency-review.yml, deploy.yml, docs-validation.yml, emoji-validation.yml, frontend-ci.yml, incident-response.yml, infrastructure-ci.yml, lint.yml, meta-architecture-check.yml, migrations.yml, python_ci.yml, requirements_validate_traceability.yml, security-scan.yml, sync-docs.yml, test-pyramid.yml, validate-guides.yml
- Workflows without `actions/cache`: actionlint.yml, agents-ci.yml, code-quality.yml, codeql.yml, dependency-review.yml, deploy.yml, docs-validation.yml, docs.yml, emoji-validation.yml, frontend-ci.yml, incident-response.yml, infrastructure-ci.yml, lint.yml, meta-architecture-check.yml, migrations.yml, pr-review.yml, python_ci.yml, release.yml, requirements_index.yml, requirements_validate_traceability.yml, security-scan.yml, sync-docs.yml, test-pyramid.yml, validate-guides.yml

## Recommendations
- Add `workflow_dispatch` to workflows that currently only run on PR/push to enable manual runs during incidents or hotfix validation.
- Define explicit, least-privilege `permissions` blocks to avoid default write scopes (e.g., contents: read, pull-requests: write only where needed).
- Introduce dependency caching where missing (pip, npm, etc.) to speed up jobs; most workflows reinstall dependencies from scratch.
- Expand test matrices for Python/Node where appropriate (e.g., backend/agents run single Python 3.11, frontend fixed to Node 18).
- Consider a lightweight security gate (e.g., Semgrep or Trivy) on push to main/develop to complement existing CodeQL and security scans.
- Add concurrency keys to long-running workflows (deploy, incident-response) to prevent overlapping runs per ref/environment.

## Per-workflow issues and gaps
- **actionlint.yml**: Uses explicit permissions and manual trigger is present, but there is no caching and the Docker action is not pinned to a digest.
- **agents-ci.yml**: Lacks an explicit permissions block, requires `CODECOV_TOKEN` to run coverage uploads, and the Bandit step ignores findings by design (`|| true`).
- **backend-ci.yml**: Missing `workflow_dispatch`; no permissions block; database service uses default MySQL root credentials and exposes 3306.
- **code-quality.yml**: Only runs on `pull_request` and `workflow_dispatch` is absent; no explicit permissions; no dependency caching.
- **codeql.yml**: Lacks `workflow_dispatch`; permissions not explicitly narrowed for code scanning upload; no cache for Python setup.
- **dependency-review.yml**: Only trigger is `pull_request`; no manual trigger; permissions block present but default read/write not narrowed to minimal contents/read.
- **deploy.yml**: Does not run on `pull_request`; no permissions block; re-runs full test suite without caching, slowing deployments.
- **docs-validation.yml**: Missing `workflow_dispatch` and explicit permissions; no caching for Python or Sphinx deps.
- **docs.yml**: Triggers are complete and permissions are explicit, but there is no dependency cache and no concurrency control for doc publishes.
- **emoji-validation.yml**: Missing manual trigger; no permissions block; re-installs dependencies every run.
- **frontend-ci.yml**: Missing `workflow_dispatch`; no permissions block; npm/node dependencies are not cached and only Node 18 is covered.
- **incident-response.yml**: Manual-only trigger with no `push`/`pull_request`; lacking permissions block and dependency caching.
- **infrastructure-ci.yml**: Missing `workflow_dispatch` and permissions block; Terraform steps lack a backend/cache and may need environment protection.
- **lint.yml**: Missing `workflow_dispatch` and permissions block; no caching for lint dependencies.
- **meta-architecture-check.yml**: Triggers present, but no permissions block and no dependency caching.
- **migrations.yml**: Missing `workflow_dispatch`; no permissions block; seeds data with inline secrets (`testpass`) and exposes MySQL port 3306.
- **pr-review.yml**: Triggered only by `issue_comment` with no `push`/`pull_request`; permissions are constrained but there is no validation to limit to PR comments; no caching.
- **python_ci.yml**: Triggers present but lacks permissions block; no cache for Python dependencies and no concurrency control.
- **release.yml**: No `pull_request` trigger; permissions rely on defaults; reuses build artifacts without checksum verification.
- **requirements_index.yml**: Triggers present and permissions explicit, but there is no cache and the Python job runs only on a single version.
- **requirements_validate_traceability.yml**: Triggers present but no permissions block; no dependency caching.
- **security-scan.yml**: Missing `workflow_dispatch` and permissions block; no caching and uses broad third-party actions without digests.
- **sync-docs.yml**: Missing `push`/`pull_request` triggers; no permissions block; relies on PAT/SSH secrets without validation and lacks caching.
- **test-pyramid.yml**: Missing `workflow_dispatch`; no permissions block; Python jobs reuse `pip install` without cache and matrix lacks latest versions.
- **validate-guides.yml**: Triggers are complete, but permissions are not explicit and there is no dependency caching.
