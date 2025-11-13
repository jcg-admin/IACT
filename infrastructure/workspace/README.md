# Workspace Infrastructure Modules

This package documents the helper modules located in `infrastructure/workspace/`.
They support local automation experiments (Hamilton-inspired pipelines, Codex MCP
playbooks and language server tooling) and ship intentionally without a dedicated
`requirements.txt`. The modules either re-implement small portions of external
packages for educational purposes or model optional integrations that require the
consumer to decide whether to install the third-party dependency.

## Execution quickstart

1. **Activate the project virtual environment** (see repository root `README.md`).
2. **Run the module tests** to validate the self-contained helpers:
   ```bash
   pytest infrastructure/workspace/tests
   ```
3. **Explore the Hamilton driver example**:
   ```bash
   python -m infrastructure.workspace.tests.hamilton_llm.test_driver
   ```
   The shim in `hamilton_llm/` mirrors the public API of the real `hamilton`
   package without requiring external installs. The tests demonstrate the
   execution order, configuration overrides and adapter chaining.
4. **Review Codex MCP playbooks** in `codex_mcp/playbooks.py`. They describe the
   declarative configuration passed to the Codex CLI (`npx codex mcp`). Optional
   dependencies (`openai-agents`, `openai`) are listed inside the module under
   `ENVIRONMENT_SETUP` instead of a requirements file because installing them is
   only necessary when executing the Codex workflow.
5. **Language server tooling** (`dev_tools/language_server/`) exposes utilities
   used by the internal development environment. They rely solely on the Python
   standard library and therefore do not require extra dependencies.

## Why there is no `requirements.txt`

- **Hamilton example**: the code re-implements the essentials of the Apache
  Hamilton driver so that unit tests run without external packages.
- **Codex MCP integration**: the dependencies depend on the MCP client chosen
  by the operator. The module documents the recommended packages and environment
  variables but does not enforce their installation globally.
- **Developer tools**: rely on the standard library. Pinning versions in a
  separate requirements file would duplicate the repository-level dependency
  management without bringing additional value.

When using the Codex or OpenAI integrations, install the optional packages in
your active environment:

```bash
pip install openai-agents openai python-dotenv
```

Create a `.env` file with the required keys (`OPENAI_API_KEY`, etc.) before
running the workflows.
