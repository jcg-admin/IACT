# Agentes Personalizados - GitHub Copilot

Este repositorio tiene configurados agentes personalizados de GitHub Copilot para automatizar tareas comunes de desarrollo y DevOps.

## Agentes Disponibles

Los siguientes agentes están configurados en `.github/copilot/agents.json`:

- **my_agent** (CodeTasker) - Tareas de programación, depuración y refactorización
- **gitops_agent** - Operaciones Git y gestión de repositorio
- **release_agent** - Gestión de releases y versionado semántico
- **dependency_agent** - Gestión de dependencias y vulnerabilidades
- **security_agent** - Auditorías de seguridad y compliance

## Cómo Usar

Para invocar un agente, usa la sintaxis:

```
@[nombre_agente]: [descripción de la tarea]
```

Ejemplo:
```
@my_agent: Implementa una función de autenticación JWT en Python
```

## Documentación

- **Configuración de agentes**: [.github/copilot/README.md](.github/copilot/README.md)
- **Guía de onboarding para agentes de código**: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- **Definiciones de agentes (Copilot)**: [.github/agents/](.github/agents/) — Copilot consume estas fichas con formato `<nombre>-agent.agent.md>`
- **Catálogo extendido**: [.agent/agents/](.agent/agents/) — se mantiene para documentación y automatizaciones históricas
- **Guía completa**: [.github/agents/README.md](.github/agents/README.md)

## ExecPlans

When writing complex features or significant refactors, produce an ExecPlan (as described in `.agent/PLANS.md`) before making code changes. Reference the plan during implementation and keep it updated as a living document.
