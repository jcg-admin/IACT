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
