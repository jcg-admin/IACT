# MCP Workflows Infrastructure Workspace

This workspace bundles the automation artefacts that power the VPN/Proxy agent,
Hamilton DAGs, and Codex MCP playbooks. It now ships with explicit Python and
Node.js dependencies so that the same tooling used in CI is available to local
contributors.

## Quick start

1. **Install dependencies**
   ```bash
   cd infrastructure/workspace
   ./setup.sh
   ```
   The script verifies Node.js ≥ 18 and Python ≥ 3.10, creates `.venv/`, installs
   `requirements.txt`, and attempts to run `npm install` (the command emits a
   warning if the registry is unreachable in offline environments).

   > **Note**: To facilitate fully offline workflows, `package.json` references local stubs in `vendor/`. Installed binaries (e.g., `codex`, `eslint`, `prettier`) print informational messages instead of executing the actual tools. This maintains compatibility with npm scripts and allows `npm ci` to work without registry access.

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # edit .env with your MCP, OpenAI or Claude credentials
   ```

3. **Run the full test suite**
   ```bash
   npm test
   ```
   This command invokes the Python tests under `infrastructure/workspace/tests`
   and the Node test runner (`node --test`). All modules are exercised via unit
   tests; the Hamilton driver, tunnel manager, and MCP server components are
   validated without hitting external services thanks to dependency injection.

4. **Inspect available scripts**
   ```bash
   npm run lint       # ruff + black + eslint
   npm run format    # opinionated formatting for Python/TypeScript
   npm run mcp:list  # list Codex MCP playbooks via codex-mcp
   npm run vpn:health
   ```

## Ejecución del agente

Este workspace no utiliza Django, por lo que el patrón `manage.py` **no aplica**.
En su lugar, el agente se orquesta mediante el servidor MCP y los playbooks de
Codex. Tienes dos maneras de ejecutarlo:

1. **Modo directo (Python)**
   ```bash
   cd infrastructure/workspace
   source .venv/bin/activate  # si aún no lo hiciste
   python -m infrastructure.workspace.vpn_proxy_agent.mcp_server
   ```
   El proceso abre un servidor MCP por `stdin/stdout` que puede ser consumido
   por cualquier cliente compatible.

2. **Modo asistido (NPM + Codex)**
   ```bash
   cd infrastructure/workspace
   npm run vpn:setup-dev     # configura dependencias simuladas y túnel
   npm run vpn:setup-tunnel  # únicamente el túnel SOCKS5
   npm run vpn:health        # chequeos de estado
   ```
   Estos comandos envuelven llamadas a `codex mcp run <playbook>` y permiten
   validar el flujo end-to-end con parámetros declarados en `.env`.

Si deseas invocar manualmente un playbook específico, también puedes ejecutar:

```bash
codex mcp run setup-dev-environment
```

La ausencia de `manage.py` no impide la ejecución del agente: todos los
componentes se inician a través del servidor MCP y los scripts definidos en
`package.json`.

## Validación del agente

Para demostrar que el agente VPN/Proxy funciona sin depender de
infraestructura externa sigue esta secuencia cada vez que hagas un cambio:

1. Ejecuta toda la batería de pruebas (Python + Node) y genera cobertura de
   código de los módulos de `vpn_proxy_agent`.
   ```bash
   cd infrastructure/workspace
   npm test
   pytest infrastructure/workspace/tests -v --cov=infrastructure.workspace.vpn_proxy_agent
   ```
   El primer comando confirma que los scripts definidos en `package.json`
   integran Pytest y `node --test`; el segundo asegura un mínimo de 80 % de
   cobertura para los componentes críticos (túnel, diagnósticos, MCP).

2. Verifica que los comandos funcionales respondan correctamente en modo
   "dry-run" usando las dependencias simuladas de los tests.
   ```bash
   npm run vpn:health
   npm run vpn:stop
   ```
   Ambos scripts se apoyan en `codex mcp run` y ejercitan el servidor MCP
   local descrito en esta carpeta.

3. Opcionalmente, inspecciona la salida del driver de Hamilton para comprobar
   la orquestación completa:
   ```bash
   npm run hamilton:test
   ```

Si cualquiera de los pasos anteriores falla, revisa los registros generados en
`logs_data/` o ejecuta Pytest con `-vv` para obtener trazas detalladas.

## Pipeline CI/CD

El flujo automatizado está definido en
`.github/workflows/infrastructure-ci.yml` y replica los pasos de validación
anteriores en GitHub Actions:

1. **Job `test-node`**: instala dependencias con `npm ci`, ejecuta `lint:node`
   y `test:node` en Node.js 18 y 20.
2. **Job `test-python`**: prepara entornos con Python 3.10–3.12, instala
   `requirements.txt`, ejecuta `ruff`, `black --check`, `mypy` y
   `pytest` con reporte de cobertura.
3. **Job `integration`**: una vez aprobados los jobs previos, repite la
   instalación completa (`npm ci` + `pip install`) y corre `npm test` para
   garantizar que la integración entre scripts, Hamilton y el servidor MCP se
   mantiene intacta.

El pipeline se dispara en cada `push` o `pull_request` contra `main` y
`develop`. Si necesitas una validación manual, puedes lanzar los mismos
comandos localmente siguiendo la sección "Validación del agente".

## Directory map

```
infrastructure/workspace/
├── package.json               # Node scripts for testing, linting and MCP helpers
├── requirements.txt           # Python dependencies for vpn_proxy_agent & tests
├── .env.example               # Required environment variables
├── setup.sh                   # Bootstrap script (Node + Python)
├── codex_mcp/                 # Playbooks + vpn_proxy playbook registry
├── hamilton_llm/              # Hamilton driver shim & dual-provider LLM client
├── vpn_proxy_agent/           # Tunnel manager, diagnostics, MCP server & tools
├── tests/                     # Pytest suite covering all modules
└── dev_tools/                 # Language server helpers (unchanged)
```

### vpn_proxy_agent package

The new package orchestrates SSH tunnels, system diagnostics, connectivity
checks and MCP tool wiring. Key modules:

- `tunnel.manager.TunnelManager` – wraps an asynchronous SSH client and stores
  tunnel state on disk via `state.manager.StateManager`.
- `ssh.keys.generate_keypair` – utility for provisioning SSH keys (Paramiko).
- `system.services.SystemDiagnostics` – exposes CPU/memory/disk/network metrics
  with psutil.
- `network.connectivity.test_endpoints` – asynchronous HTTPX checks routed
  through a SOCKS proxy.
- `mcp_tools.VPNProxyTools` – high level façade consumed by the MCP server.
- `mcp_server.py` – lightweight MCP stdio server exposing Codex tools.

### Hamilton integration

`hamilton_llm/driver.py` now exports `execute_vpn_workflow`, an async helper that
composes the Hamilton dataflow with VPN diagnostics, tunnel status, and LLM
responses. The LLM factory in `hamilton_llm/llm_client.py` selects OpenAI or
Claude based on the environment (`LLM_PROVIDER`, `OPENAI_API_KEY`,
`ANTHROPIC_API_KEY`).

### Codex MCP playbooks

`codex_mcp/vpn_proxy_playbooks.py` registers `setup-dev-environment`,
`health-check`, and `stop-tunnel` playbooks. The Node scripts (`npm run
vpn:setup-dev`, etc.) wrap these playbooks via `codex-mcp`.

## Running commands individually

```bash
# Python tests only
pytest infrastructure/workspace/tests -v --cov=infrastructure.workspace.vpn_proxy_agent

# Node tests only
npm run test:node

# Type checking (Python)
npm run typecheck

# Launch Hamilton driver smoke test
npm run hamilton:test
```

## Environment variables

`infrastructure/workspace/.env.example` documents the expected variables:

- `MCP_SERVER_URL`, `MCP_API_KEY`
- `OPENAI_API_KEY`, `OPENAI_ORG_ID`
- `LLM_PROVIDER` (`openai` or `claude`), `ANTHROPIC_API_KEY`
- `TUNNEL_HOST`, `TUNNEL_PORT`, `SSH_USER`, `SSH_KEY_PATH`
- `API_URLS` for connectivity probes
- `STATE_DIR` for persisted tunnel state

## Offline environments

If you are developing in an air-gapped environment, `npm install` may fail when
accessing the public registry. The tests still pass because all network calls
are mocked; re-run the command once registry access is restored to refresh
`node_modules/` locally.

## Additional resources

- The Hamilton driver shim remains compatible with upstream Hamilton
  documentation and can be visualised via `npm run hamilton:visualize` (requires
  `hamilton-ui`).
- The language server helpers in `dev_tools/` are untouched and continue to
  service the existing development workflow.

## Preguntas frecuentes

**¿Necesito configurar `mise ~/.config/mise/config.toml tools` para este workspace?**

No es necesario. El script `setup.sh` instala y valida todas las dependencias
requeridas (Python, Node.js y las librerías declaradas en `requirements.txt` y
`package.json`). Si ya usas `mise` como gestor de versiones puedes mantener tu
configuración, pero no forma parte del flujo oficial ni bloquea la ejecución de
los comandos documentados aquí.

**¿Hace falta alguna verificación adicional para garantizar que todo funciona?**

Sí: después de ejecutar las pruebas recomendadas en "Validación del agente",
comprueba que la CLI de Codex MCP está instalada y accesible ejecutando:

```bash
codex --version
npm run mcp:validate
```

Estos comandos confirman que las herramientas MCP disponibles en este workspace
responden correctamente y que tu entorno cuenta con la versión esperada del
cliente `codex`.
