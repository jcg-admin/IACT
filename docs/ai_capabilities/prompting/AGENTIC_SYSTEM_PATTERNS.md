---
title: Agentic System Patterns and Best Practices
date: 2025-11-13
domain: general
status: active
---

# Agentic System Patterns and Best Practices

> **Status:** Production notes based on 2024-2025 delivery work with enterprise teams building LLM-driven agents.

Over the last year we have partnered with dozens of product and platform groups that deploy large language model (LLM) agents. The most reliable launches did **not** depend on heavyweight frameworks. Instead, they composed simple patterns, measured continuously, and only increased complexity when it demonstrably improved outcomes. This guide distills those lessons into reusable building blocks for the team.

## What are agents?

"Agent" can mean different things across organizations. Some customers describe fully autonomous systems that run for long periods, chaining multiple tools. Others use the term for guided automations with well-defined workflows. We treat both as *agentic systems* but distinguish between:

- **Workflows:** Predefined code paths where LLM calls and tools are orchestrated deterministically.
- **Agents:** Systems where the LLM dynamically decides which tools to call, how to sequence them, and when to request human input.

Understanding the distinction helps choose the lightest design that still meets business goals.

## When (and when not) to use agents

Start with the simplest possible solution. Multi-step agents consume more tokens, add latency, and can compound mistakes. Prefer single LLM calls augmented with retrieval or examples unless you have evidence that autonomy increases success rates.

Escalate to workflows or agents when:

- Fixed sequences (workflows) improve accuracy by decomposing a task into verifiable steps.
- Dynamic orchestration (agents) is necessary because the number or nature of subtasks cannot be known upfront.
- Human oversight remains available for checkpoints, fallbacks, or escalation.

## When and how to use frameworks

Frameworks such as LangGraph, Amazon Bedrock Agents, Rivet, or Vellum simplify the basics—issuing calls, defining tools, chaining steps. They accelerate prototypes but introduce abstraction layers that can hide prompts and responses, making debugging harder.

Our recommendations:

1. **Prototype directly with the API first.** Many orchestration patterns require fewer than 50 lines of code.
2. **Audit framework assumptions.** Misunderstanding tool schemas or execution order is a common failure mode.
3. **Collapse abstractions when moving to production.** Prefer transparent, composable components over magical orchestration.

Refer to the project cookbook for minimal examples that can be adapted without vendor lock-in.

## Building blocks, workflows, and agents

### Building block: The augmented LLM

Modern agents start with an LLM enhanced with retrieval, tools, and memory. Each model invocation should have:

```text
[Augmented LLM]
├── Retrieval (domain documents, knowledge bases)
├── Tooling (APIs, code execution, search)
├── Memory (session context, persistent logs)
└── Policies (guardrails, stopping criteria)
```

Tailor augmentations to the use case and provide a clear interface that the model can reliably follow—rich descriptions, explicit parameters, and concrete examples.

### Workflow: Prompt chaining

Prompt chaining decomposes work into a deterministic series of LLM calls, optionally inserting programmatic gates that validate intermediate artifacts.

Use it when tasks naturally split into predictable steps—for example, generate marketing copy, review it, translate it. The trade-off is higher latency in exchange for higher accuracy through focused subtasks.

### Workflow: Routing

Routing classifies user intent and directs it to specialized prompts, tools, or even different models. This isolates domain-specific instructions and lets you deploy cost-effective models for easy requests while reserving powerful models for complex cases.

### Workflow: Parallelization

Parallelization runs multiple LLM calls simultaneously. Two common variants:

- **Sectioning:** Independent subtasks processed in parallel.
- **Voting:** Multiple attempts at the same task whose outputs are compared or aggregated.

Choose this when subtasks are independent or when diversity of answers improves confidence (e.g., vulnerability scanning with multiple reviewers).

### Workflow: Orchestrator-workers

An orchestrator LLM breaks down goals into subtasks dynamically and assigns them to worker LLMs. Unlike prompt chaining, the number of steps and required tools emerges from the input. This is useful for large code edits or investigative research where the scope is unknown at the start.

### Workflow: Evaluator-optimizer

One LLM proposes a solution while another critiques it. The loop continues until quality thresholds are met or iteration limits are reached. This mirrors human editorial processes and works when evaluation criteria are clear (translation quality, document completeness, etc.).

### Agents: Autonomous execution

Agents combine planning, tool use, and memory in a loop that continues until completion criteria or stop conditions trigger. Key practices:

- Ground each step with tool feedback (e.g., execution logs, API responses).
- Define checkpoints for human review or early termination.
- Budget tokens and time, enforcing maximum iterations to avoid runaway costs.

Autonomy suits problems where the number of steps cannot be hardcoded—complex coding tasks, investigative research, or support workflows that require branching conversations plus actions.

## Combining and customizing patterns

Patterns are composable. For instance, a routing stage can dispatch to either a prompt chain or an orchestrator-worker agent. Measure each addition; remove complexity that does not move success metrics. Instrument latency, cost, and quality so you can decide objectively when extra orchestration is justified.

## Summary: Principles for reliable agents

1. **Stay simple.** Only add autonomy when single-call prompts fail to hit targets.
2. **Expose the plan.** Make the agent's reasoning and steps transparent for debuggability.
3. **Engineer the agent-computer interface (ACI).** Treat tool definitions like UI design—clear parameters, examples, and safeguards.

## Appendix 1 – Agents in practice

### Customer support

Customer support blends conversational flows with actions such as fetching order data or issuing refunds. Agent fit indicators include:

- Tool integrations for CRM, order history, and knowledge bases.
- Programmatic actions with clear success criteria (ticket updates, refund execution).
- Natural opportunities for human oversight when escalations are required.

Successful teams often price agents by resolved ticket to align incentives with outcome quality.

### Coding agents

Software engineering is a high-leverage domain because:

- Automated tests provide objective ground truth for correctness.
- Agents can iterate using test failures as feedback.
- The problem space is structured, letting the agent plan modifications precisely.

Benchmarks such as SWE-bench Verified show agents solving real GitHub issues from pull request descriptions, but human review still ensures architectural alignment and non-functional requirements.

## Appendix 2 – Prompt engineering your tools

Tool definitions deserve the same rigor as prompts.

1. **Select ergonomic formats.** Prefer representations the model has seen frequently (markdown over JSON for code) and avoid error-prone requirements such as manual diff headers.
2. **Provide rich docstrings.** Include examples, edge cases, and parameter semantics so the LLM understands how and when to use each tool.
3. **Test and iterate.** Observe tool usage in the workbench, then refine descriptions to prevent recurring mistakes.
4. **Poka-yoke critical operations.** Shape parameters so that invalid combinations are impossible or obvious (e.g., enforce absolute file paths to avoid path drift).

Expect to invest heavily here—optimizing tools often delivers larger gains than tuning the top-level prompt. Treat tool UX as a first-class part of the agent architecture.
