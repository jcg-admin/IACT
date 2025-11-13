---
title: Agent Documentation
date: 2025-11-13
domain: ai
status: active
---

# Agent Documentation

This directory contains SDLC documentation for AI agents developed in the project.

## Directory Structure

Following the project's standard documentation pattern (similar to `backend/`, `frontend/`):

```
docs/agent/
├── README.md                    # This file
├── arquitectura/                # High-Level Design (HLD) and ADRs
├── diseno_detallado/           # Low-Level Design (LLD)
├── planificacion_y_releases/   # Planning, issues, and release tracking
├── requisitos/                  # Requirements and feasibility studies
└── gobernanza/                  # Governance documents and constitution updates
```

## Current Agents

### ShellScriptAnalysisAgent

Agent specialized in analyzing shell scripts for constitutional compliance, quality, and security.

**Issue ID**: FEATURE-SHELL-ANALYSIS-001

**Documentation**:
- Planning: `planificacion_y_releases/issue_shell_script_analysis_agent.md`
- Feasibility: `requisitos/feasibility_shell_script_analysis_agent.md`
- HLD: `arquitectura/hld_shell_script_analysis_agent.md`
- ADRs: `arquitectura/adrs_shell_script_analysis_agent.md`
- LLD: `diseno_detallado/lld_shell_script_analysis_agent.md`
- Constitution Update: `gobernanza/constitution_update_proposal.md`

**Status**: Implementation Phase (TDD GREEN)

**Traceability**: All documentation follows SDLC methodology with Auto-CoT and Self-Consistency techniques.

## Naming Conventions

- All filenames use underscores (`_`), not hyphens (`-`)
- Follow pattern: `{type}_{agent_name}.md`
- Examples:
  - `issue_shell_script_analysis_agent.md`
  - `hld_shell_script_analysis_agent.md`
  - `lld_shell_script_analysis_agent.md`

## Adding New Agents

When creating documentation for a new agent:

1. **Planning Phase**: Create issue in `planificacion_y_releases/`
2. **Feasibility Phase**: Create feasibility study in `requisitos/`
3. **Design Phase**:
   - HLD and ADRs in `arquitectura/`
   - LLD in `diseno_detallado/`
   - Constitution updates (if any) in `gobernanza/`
4. **Implementation, Testing, Deployment**: Document as per SDLC process

## References

- SDLC Methodology: `docs/scripts/sdlc-agent-guide.md`
- Agent Constitution: `docs/gobernanza/agentes/constitution.md`
- TDD Guidelines: `docs/gobernanza/agentes/tdd-feature-agent.md`
