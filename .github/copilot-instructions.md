# GitHub Copilot Instructions - IACT Project

## Repository Overview

This is the **IACT (Intelligent Analytics for Call Centers)** project - a monolithic Django 5 application for call center analytics with PostgreSQL and MariaDB databases. The project is in active development with a strong focus on documentation-driven development, AI-powered SDLC agents, and automated governance.

**Current State**: The repository is in consolidation phase, aligning code with extensive documentation. Some features are documented but not yet implemented (marked as [PLANIFICADO] vs [IMPLEMENTADO] in docs).

## Project Architecture

### Tech Stack

- **Backend**: Django 5.x (Python 3.11+)
- **Databases**: 
  - PostgreSQL 15 (analytics, port 15432)
  - MariaDB (IVR read-only, port 13306)
- **Frontend**: React/JavaScript (in `ui/` directory)
- **Infrastructure**: Vagrant + VirtualBox for local development
- **AI/LLM**: Multi-provider support (Claude, ChatGPT, Hugging Face models)
- **CI/CD**: GitHub Actions (25+ workflows)

### Directory Structure

```
IACT---project/
├── .agent/                      # Agent definitions for GitHub Copilot custom agents
│   ├── agents/                  # Agent markdown files (my_agent, gitops_agent, etc.)
│   └── PLANS.md                 # ExecPlan template system
├── .github/
│   ├── copilot/                 # Copilot custom agents configuration
│   │   ├── agents.json          # Custom agents manifest (5 agents)
│   │   └── README.md            # Usage guide
│   ├── agents/                  # Agent documentation (30+ agents)
│   ├── workflows/               # 25+ CI/CD workflows
│   └── copilot_instructions.md  # Legacy instructions (outdated)
├── api/                         # Django backend
│   └── callcentersite/          # Main Django project
│       ├── manage.py
│       └── callcentersite/      # Settings and main app
├── ui/                          # React frontend
├── infrastructure/              # Infrastructure as Code
│   ├── vagrant/                 # Vagrantfile for databases
│   ├── cpython/                 # Custom CPython builder
│   └── devcontainer/            # VS Code devcontainer config
├── scripts/                     # Utility scripts (200+ files)
│   ├── coding/ai/               # SDLC agents (Python)
│   │   ├── sdlc/                # SDLC agents (planner, design, testing, etc.)
│   │   ├── automation/          # Automation agents (coherence, metrics, etc.)
│   │   └── agents/base/         # Prompting techniques
│   ├── ci/                      # CI/CD scripts
│   └── infrastructure/          # Infrastructure scripts
├── docs/                        # Extensive documentation (1000+ files)
│   ├── ai/                      # AI/LLM documentation
│   ├── desarrollo/              # Development guides
│   ├── gobernanza/              # Governance and processes
│   └── operaciones/             # Operations runbooks
├── tests/                       # Test suites
└── schemas/                     # JSON schemas

Key files:
- .constitucion.yaml            # Automation principles (5 principles, 6 rules)
- .pre-commit-config.yaml       # Pre-commit hooks (Black, flake8, etc.)
- README.md                     # Main documentation entry point
```

## Core Principles (La Constitución)

The project follows 5 core automation principles defined in `.constitucion.yaml`:

1. **R1 - Idempotencia**: All operations must be idempotent
2. **R2 - Sin Emojis**: No emojis in automation outputs (text-only)
3. **R3 - Verificación**: All changes must be verified
4. **R4 - Documentación**: All changes must be documented
5. **R5 - Trazabilidad**: Complete traceability of changes

**CRITICAL**: When generating any automation script or output, follow these principles strictly.

## Development Guidelines

### Code Style & Formatting

- **Python**: Black formatter (line length: 100), flake8 linter
- **JavaScript**: ESLint, Prettier
- **Git**: Conventional commits format
- **Pre-commit hooks**: Installed and enforced (`pre-commit run --all-files`)

### Testing Strategy

- **Python**: pytest with coverage requirements
- **Backend Tests**: Located in `api/callcentersite/*/tests/`
- **Frontend Tests**: Jest/React Testing Library in `ui/`
- **Test Pyramid**: Unit > Integration > E2E (see `.github/workflows/test-pyramid.yml`)

### Database Architecture

**Two-database setup** (managed via Vagrant):

1. **PostgreSQL** (analytics)
   - Host: 127.0.0.1:15432
   - Database: iact_analytics
   - Purpose: Django models, analytics data
   - Migrations: `python manage.py migrate`

2. **MariaDB** (IVR - read-only)
   - Host: 127.0.0.1:13306
   - Database: ivr_data
   - Purpose: Legacy IVR data (no migrations)
   - Access: Via Django database router

**IMPORTANT**: Never run migrations on MariaDB. Use PostgreSQL for all Django models.

### Environment Setup

1. **Virtual environment**: Python 3.11+ required
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. **Dependencies**: 
   - Backend: No root requirements.txt (use `api/callcentersite/pyproject.toml`)
   - Frontend: `ui/package.json`
   - Docs: `docs/requirements.txt` (MkDocs)

3. **Databases**: Start with `vagrant up` in root or `infrastructure/vagrant/`

4. **Environment variables**: Create `.env` in root with DB credentials (see README.md)

### Common Commands

```bash
# Backend
cd api/callcentersite
python manage.py runserver
python manage.py migrate
python manage.py test

# Frontend
cd ui
npm install
npm run dev

# Database
vagrant up                    # Start databases
vagrant ssh postgres          # Connect to PostgreSQL VM
vagrant ssh mariadb           # Connect to MariaDB VM

# Pre-commit
pre-commit install
pre-commit run --all-files

# CI local testing
./scripts/ci-local.sh
```

## AI Agents & Automation

### GitHub Copilot Custom Agents

**5 custom agents configured** in `.github/copilot/agents.json`:

1. **my_agent** (CodeTasker) - Programming tasks, debugging, refactoring
2. **gitops_agent** - Git operations, branch synchronization
3. **release_agent** - Semantic versioning, changelog generation
4. **dependency_agent** - Dependency updates, CVE scanning
5. **security_agent** - Security audits, STRIDE analysis

**Usage**: `@my_agent: [task description]`

### Python SDLC Agents

**30+ agents** implemented in `scripts/coding/ai/`:

- **SDLC Agents** (`scripts/coding/ai/sdlc/`): Planning, feasibility, design, testing, deployment
- **Automation Agents** (`scripts/coding/ai/automation/`): Coherence analysis, PDCA, metrics, schema validation
- **Base Techniques** (`scripts/coding/ai/agents/base/`): Auto-CoT, self-consistency, tree-of-thoughts

**Multi-LLM Support**: Agents auto-detect available providers:
- Anthropic (Claude) - via `ANTHROPIC_API_KEY`
- OpenAI (GPT) - via `OPENAI_API_KEY`
- Hugging Face - via `HF_LOCAL_MODEL_PATH` or `HF_MODEL_ID`

See `docs/ai/CONFIGURACION_API_KEYS.md` for setup.

## CI/CD Workflows

**25+ GitHub Actions workflows** in `.github/workflows/`:

### Critical Workflows
- **backend-ci.yml**: Django tests, migrations check
- **frontend-ci.yml**: React tests, build verification
- **security-scan.yml**: Bandit, safety, gitleaks
- **test-pyramid.yml**: Multi-level test orchestration
- **release.yml**: Semantic versioning, changelog generation
- **deploy.yml**: Deployment automation

### Quality Gates
- **lint.yml**: Black, flake8, ESLint
- **code-quality.yml**: Code coverage, complexity checks
- **meta-architecture-check.yml**: Architecture compliance
- **emoji-validation.yml**: Enforces R2 (no emojis)

### Documentation
- **docs.yml**: MkDocs build and deployment
- **docs-validation.yml**: Markdown linting, link checking
- **sync-docs.yml**: Documentation synchronization

## Documentation System

**Massive documentation** (1000+ files in `docs/`):

### Key Documentation Areas

1. **AI/LLM** (`docs/ai/`):
   - `SDLC_AGENTS_GUIDE.md` - SDLC agents usage
   - `CONFIGURACION_API_KEYS.md` - LLM provider setup
   - `FINE_TUNING_TINYLLAMA.md` - Model fine-tuning

2. **Development** (`docs/desarrollo/`):
   - `agentes_automatizacion.md` - Automation agents
   - `arquitectura_agentes_especializados.md` - Agent architecture

3. **Governance** (`docs/gobernanza/`):
   - Process definitions
   - Quality standards
   - Compliance requirements

4. **Operations** (`docs/operaciones/`):
   - Runbooks for common tasks
   - Troubleshooting guides

5. **AI Capabilities** (`docs/ai_capabilities/`):
   - `prompting/PROMPT_TECHNIQUES_CATALOG.md` - 120+ prompting techniques
   - `orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md` - Multi-agent orchestration
   - `orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md` - Context/memory management

### Documentation Tools

- **MkDocs**: Static site generation (`mkdocs serve`)
- **Markdown linting**: Via `.markdownlint.json`
- **Link checking**: Automated in CI

## ExecPlans System

**ExecPlans** are living documents for complex features (see `.agent/PLANS.md`):

- Template-based planning approach
- Track implementation progress
- Link code to requirements
- Found in `docs/plans/` and root directory

**When to create an ExecPlan**: For any complex feature or significant refactor.

## Git Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Development integration
- **feature/***: Feature branches
- **hotfix/***: Emergency fixes
- **docs**: Documentation updates
- **devcontainer**: DevContainer configuration

### Commit Conventions

Use conventional commits:
```
type(scope): subject

types: feat, fix, docs, style, refactor, test, chore, ci
```

### Pre-commit Checks

- No commits to main/master directly
- Python formatting (Black)
- Linting (flake8, ESLint)
- YAML/JSON validation
- Large file detection (max 1MB)
- No debug statements

## Common Pitfalls & Solutions

### Issue: "Agents not working"
**Solution**: Ensure `.github/copilot/agents.json` exists and references correct agent files in `.agent/agents/`.

### Issue: Database connection errors
**Solution**: Run `vagrant up` to start databases. Check ports 15432 (PostgreSQL) and 13306 (MariaDB).

### Issue: Migration errors on MariaDB
**Solution**: Never run migrations on MariaDB. It's read-only. Only migrate PostgreSQL.

### Issue: Pre-commit hooks failing
**Solution**: Run `pre-commit run --all-files` to see errors. Install with `pip install pre-commit && pre-commit install`.

### Issue: "No module named 'callcentersite'"
**Solution**: You're in wrong directory. Navigate to `api/callcentersite/` before running Django commands.

### Issue: Import errors in SDLC agents
**Solution**: Install agent dependencies: `pip install -r scripts/coding/ai/requirements.txt`.

### Issue: Emoji validation failures
**Solution**: Remove all emojis from automation outputs. This is R2 principle enforcement.

## Best Practices for Agents

### When Adding Features

1. **Check ExecPlans**: Review `docs/plans/` for existing planning documents
2. **Update Documentation**: Document before or alongside implementation
3. **Follow Principles**: Adhere to .constitucion.yaml principles
4. **Run Tests**: `pytest` for Python, `npm test` for JavaScript
5. **Pre-commit**: Ensure hooks pass before committing
6. **CI Validation**: Check GitHub Actions results

### When Debugging

1. **Check Documentation**: Review `docs/operaciones/` for runbooks
2. **Verify Services**: Run `./scripts/verificar_servicios.sh`
3. **Check Logs**: Django logs, workflow logs, agent outputs
4. **Consult Agents**: Use custom agents for specialized tasks

### When Refactoring

1. **Create ExecPlan**: Document refactoring strategy in `.agent/PLANS.md` format
2. **Maintain Tests**: Keep existing tests passing
3. **Update Docs**: Sync documentation with code changes
4. **Verify Architecture**: Run `meta-architecture-check.yml` workflow
5. **Check Coherence**: Use `CoherenceAnalyzerAgent` for validation

## Security Considerations

### Secrets Management

- **Never commit**: API keys, passwords, tokens
- **Use .env**: For local development secrets
- **GitHub Secrets**: For CI/CD secrets
- **Validation**: Gitleaks runs in CI to detect exposed secrets

### Security Scanning

- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Gitleaks**: Secret detection
- **CodeQL**: Code security analysis
- **Dependency Review**: GitHub native scanning

### Database Security

- **Separate credentials**: PostgreSQL vs MariaDB
- **Read-only access**: MariaDB is read-only for safety
- **No production data**: Use synthetic data for development

## Testing Strategy

### Test Pyramid

1. **Unit Tests** (70%)
   - Fast, isolated tests
   - Mock external dependencies
   - Test individual functions/classes

2. **Integration Tests** (20%)
   - Database interactions
   - API endpoint testing
   - Component integration

3. **E2E Tests** (10%)
   - Full user workflows
   - Browser automation
   - Critical path validation

### Running Tests

```bash
# Backend unit tests
cd api/callcentersite
pytest

# Backend with coverage
pytest --cov=. --cov-report=html

# Frontend tests
cd ui
npm test

# Run test pyramid
# Triggered by .github/workflows/test-pyramid.yml
```

## Troubleshooting Common Errors

### Error: "No such file or directory: manage.py"
```bash
# Solution: Navigate to Django project directory
cd api/callcentersite
python manage.py [command]
```

### Error: "django.db.utils.OperationalError: could not connect to server"
```bash
# Solution: Start databases
vagrant up
# Verify databases are running
vagrant status
```

### Error: "Black would reformat"
```bash
# Solution: Run Black formatter
black . --line-length=100
# Or use pre-commit
pre-commit run black --all-files
```

### Error: "Agent not found: @agent_name"
```bash
# Solution: Verify agent configuration
cat .github/copilot/agents.json
# Check agent file exists
ls .agent/agents/[agent_name].md
```

### Error: "ImportError: No module named 'anthropic'"
```bash
# Solution: Install AI agent dependencies
pip install -r scripts/coding/ai/requirements.txt
```

## Performance Considerations

### Database Optimization

- Use `.select_related()` and `.prefetch_related()` for Django ORM
- Index frequently queried fields
- Avoid N+1 queries
- Use database router for read/write separation

### Frontend Performance

- Code splitting in React
- Lazy loading for routes
- Image optimization
- Bundle size monitoring

### CI/CD Performance

- Matrix builds for parallel execution
- Caching dependencies (pip, npm)
- Conditional job execution
- Reusable workflows

## Resources & References

### Internal Documentation
- **Main Index**: `docs/index.md` or `docs/INDEX.md`
- **Setup Guide**: `docs/SETUP.md`
- **Onboarding**: `docs/ONBOARDING.md`
- **Contributing**: `docs/CONTRIBUTING.md`

### Agent Documentation
- **Custom Agents**: `.github/copilot/README.md`
- **Agent Definitions**: `.agent/agents/README.md`
- **SDLC Agents**: `.github/agents/README.md`

### External Resources
- Django 5 Documentation: https://docs.djangoproject.com/en/5.0/
- React Documentation: https://react.dev/
- GitHub Actions: https://docs.github.com/en/actions
- Conventional Commits: https://www.conventionalcommits.org/

## Quick Reference Card

```bash
# Essential Commands Cheatsheet

# Setup
python3.11 -m venv .venv && source .venv/bin/activate
vagrant up
cp .env.example .env  # If exists

# Backend
cd api/callcentersite
python manage.py runserver
python manage.py migrate
python manage.py test

# Frontend
cd ui && npm install && npm run dev

# Quality
pre-commit run --all-files
black . --line-length=100
pytest --cov=.

# Database
vagrant ssh postgres
vagrant ssh mariadb

# Agents
@my_agent: [task]
python scripts/coding/ai/sdlc/testing_agent.py --help

# Docs
cd docs && mkdocs serve
```

---

**Last Updated**: 2025-11-14
**Version**: 1.0.0
**Maintainer**: IACT Project Team

This document is a living guide - update it as the project evolves to keep it relevant and useful for all coding agents.
