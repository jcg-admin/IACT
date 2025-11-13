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
3. **Walk the Hamilton dataflow end to end**:
   ```bash
   pytest infrastructure/workspace/tests/hamilton_llm/test_driver.py \
       --maxfail=1 -k hamilton_builder_executes_llm_business_flow -vv
   ```
   Pytest executes the declarative pipeline and prints the captured plan to the
   console. The Hamilton shim in `hamilton_llm/` mirrors the public API of the
   real `hamilton` package without requiring external installs. Step-by-step
   output demonstrates the execution order, configuration overrides and adapter
   chaining you would observe inside the official Hamilton UI.
4. **Review Codex MCP playbooks** in `codex_mcp/playbooks.py`. They describe the
   declarative configuration passed to the Codex CLI (`npx codex mcp`). Optional
   dependencies (`openai-agents`, `openai`) are listed inside the module under
   `ENVIRONMENT_SETUP` instead of a requirements file because installing them is
   only necessary when exercising the Codex workflow.
5. **Language server tooling** (`dev_tools/language_server/`) exposes utilities
   used by the internal development environment. They rely solely on the Python
   standard library and therefore do not require extra dependencies.

> **Why you do not see a browser UI**
>
> The Hamilton demo is purposely console-first to keep the repository
> dependency-light. When you run the test target above pytest prints the
> executed nodes and their order. Connecting the same modules to a browser UI is
> possible (for example by embedding the driver inside a FastAPI app), but the
> repository keeps that integration out of scope to avoid shipping additional
> JavaScript tooling or backend frameworks.

### Visualising the pipeline on the command line

Run the snippet below to print the resolved nodes and the resulting business
package exactly as the tests assert:

```bash
python - <<'PY'
from infrastructure.workspace.hamilton_llm import dataflow, driver
from infrastructure.workspace.hamilton_llm.llm_client import MockLLMClient

mock = MockLLMClient(
    price_per_1k_tokens=0.4,
    response_catalog={dataflow.DATAFLOW_LABEL: "Use Hamilton declarative functions to guard prompts."},
)

pipeline = (
    driver.Builder()
    .with_modules(dataflow)
    .with_config({"pricing_policy": {"price_per_1k_tokens": 0.4, "safety_multiplier": 1.15}})
    .build()
)

result = pipeline.execute(
    ["business_value", "cost_estimate"],
    {
        "idea": "AI copilots for compliance analysts",
        "domain_data": {
            "data": "archived compliance tickets",
            "ui": "browser extension",
            "business_process": "regulatory audit",
        },
        "edge_cases": [
            "Input state space",
            "Guard against prompt injection",
            "Domain expertise",
            "Evaluation",
            "Cost/GPUs",
        ],
        "llm_client": mock,
    },
)

print("Execution order:", pipeline.execution_log)
print("Business payload:", result["business_value"]["llm_plan"])
print("Estimated cost:", result["cost_estimate"])
PY
```

The script mirrors the pytest fixture and produces terminal output such as:

```
Execution order: ['pace_of_development', 'prompt_template', 'llm_prompt', 'llm_response', 'prompt_token_estimate', 'business_value', 'cost_estimate']
Business payload: Use Hamilton declarative functions to guard prompts.
Estimated cost: 0.0552
```

## Bootstrapping a clean virtual environment

The modules in this directory run on standard library primitives, but the test
suite and Codex integrations expect a handful of optional dependencies. When
working inside a fresh virtual environment run the following commands:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install pytest
```

Install the Codex/OpenAI extras only if you plan to exercise the MCP playbooks:

```bash
pip install openai-agents openai python-dotenv
```

Create a `.env` file at the project root and load it via `python-dotenv` to make
the API keys available to the workflows:

```bash
OPENAI_API_KEY=sk-your-api-key
```

The Hamilton driver example and developer tooling modules continue to operate
without additional packages beyond what ships with CPython.

### Capturing a requirements snapshot (optional)

When teams want to reproduce the exact versions used during an experiment they
can materialise a temporary `requirements.txt` from the active environment
without committing it to source control:

```bash
pip install openai-agents openai python-dotenv  # only if Codex integrations are needed
pip freeze --exclude-editable > infrastructure/workspace/requirements.txt
```

The generated file documents the state of your virtual environment at that
moment (suitable for sharing in an issue or attaching to a pipeline artifact),
while keeping the repository source clean. Delete the file afterwards if it is
only needed for local troubleshooting:

```bash
rm infrastructure/workspace/requirements.txt
```

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
