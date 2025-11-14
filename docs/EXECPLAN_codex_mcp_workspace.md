# ExecPlan: Integrar playbooks Codex MCP en el workspace de infraestructura

Esta ExecPlan es un documento vivo; debe actualizarse durante la implementación según `.agent/PLANS.md`.

## Purpose / Big Picture

Incorporar un workspace autocontenible que documente y codifique la integración de Codex CLI como servidor MCP, junto con playbooks para sistemas mono-agente y multi-agente que usan el Agents SDK. La meta es que el repositorio disponga de artefactos reproducibles (código + pruebas + documentación) que muestren cómo orquestar estos agentes sin depender de llamadas externas durante la ejecución de CI.

## Progress

- [x] (2025-11-20 15:30Z) ExecPlan creado con alcance inicial y validaciones esperadas.
- [x] (2025-11-20 16:05Z) Pruebas TDD escritas en `infrastructure/workspace/tests/codex_mcp/test_playbooks.py` y actualización del registro estructural.
- [x] (2025-11-20 16:30Z) Implementación del módulo `infrastructure/workspace/codex_mcp/` con blueprints declarativos.
- [x] (2025-11-20 16:45Z) Documentación y registros actualizados (`docs/index.md`, `docs/infraestructura/workspace/README.md`, `docs/infraestructura/workspace/codex_mcp.md`, `infrastructure/workspace/__init__.py`).
- [x] (2025-11-20 17:00Z) Validaciones ejecutadas (`pytest` del workspace completo y prueba documental dirigida) con resultados documentados.

## Surprises & Discoveries

- Ajuste requerido: las instrucciones de los agentes deben incluir exactamente la cadena `"sandbox": "workspace-write"` con espacios para cumplir la política documentada y las expectativas de los tests.
  Evidence: Primera ejecución de las pruebas falló hasta normalizar el formato de la cadena Codex MCP.

## Decision Log

- Decision: Representar servidores y agentes como dataclasses inmutables y construir playbooks declarativos en lugar de scripts ejecutables.
  Rationale: Evita dependencias externas (`openai-agents`, `codex`) durante la ejecución de CI, pero mantiene la trazabilidad de configuraciones y handoffs descrita por el stakeholder.
  Date/Author: 2025-11-20 / coding-agent

## Outcomes & Retrospective

- El workspace Codex MCP quedó alineado al árbol `infrastructure/workspace/` con documentación y pruebas TDD.
- La guía de infraestructura refleja la disponibilidad del nuevo playbook junto a Hamilton y Dev Tools.
- Restan correr las validaciones finales del plan antes de cerrarlo.

## Context and Orientation

La guía entregada por el stakeholder describe paso a paso cómo levantar Codex CLI como servidor MCP, definir agentes especializados y orquestar flujos mono y multi-agente con el Agents SDK, incluyendo requisitos de entorno y trazabilidad. Actualmente el repositorio no refleja estos playbooks; sí cuenta con un workspace Hamilton (`infrastructure/workspace/hamilton_llm`) y herramientas de lenguaje (`infrastructure/workspace/dev_tools`).

Integraremos el contenido en `infrastructure/workspace/codex_mcp/` como código Python basado en dataclasses que represente la configuración declarativa de servidores y agentes. Las pruebas vivirán en `infrastructure/workspace/tests/codex_mcp/`, siguiendo el patrón de TDD establecido.

## Plan of Work

1. Crear pruebas unitarias que describan:
   - La configuración del servidor MCP (`command`, `args`, timeout) y su asociación a los agentes.
   - El contenido crítico de las instrucciones (por ejemplo, `approval-policy`, `workspace-write`, uso del `RECOMMENDED_PROMPT_PREFIX`).
   - La secuencia de handoffs y artefactos requeridos en el flujo multi-agente.
2. Implementar dataclasses y funciones en `infrastructure/workspace/codex_mcp/playbooks.py` expuestas vía `__init__.py`.
3. Registrar el nuevo workspace en `infrastructure.workspace.TEST_SUITES` y exportarlo en `__all__`.
4. Actualizar documentación relevante (`docs/infraestructura/workspace/README.md`, índice general y guías de gobernanza si aplica).
5. Ejecutar pytest sobre el nuevo paquete y las pruebas de documentación pertinentes.
6. Completar las secciones de progreso, decisiones y hallazgos del ExecPlan.

## Concrete Steps

1. Añadir archivo `infrastructure/workspace/tests/codex_mcp/test_playbooks.py` con casos para servidor, agentes y handoffs.
2. Ejecutar `python3 -m pytest infrastructure/workspace/tests/codex_mcp/test_playbooks.py` para observar el fallo inicial (Red).
3. Implementar `infrastructure/workspace/codex_mcp/__init__.py` y `playbooks.py` satisfaciendo los tests.
4. Ajustar `infrastructure/workspace/__init__.py` y `infrastructure/workspace/tests/test_registry.py` para registrar el workspace.
5. Actualizar documentación y volver a ejecutar las suites relevantes (Green) antes de refactorizar.

## Validation and Acceptance

Se considerará completo cuando:
- `python3 -m pytest infrastructure/workspace/tests/codex_mcp/test_playbooks.py` pase sin fallos.
- `python3 -m pytest infrastructure/workspace/tests` incluya el workspace Codex sin romper las suites existentes.
- La documentación de infraestructura describa el workspace y la guía de gobierno enlace el recurso cuando corresponda.

## Idempotence and Recovery

Los playbooks serán representaciones declarativas sin efectos secundarios. Ejecutar las pruebas no generará archivos externos ni requerirá conexiones a servicios. Ante fallos, basta con revertir cambios en el módulo y reejecutar `pytest`.

## Artifacts and Notes

- `python3 -m pytest infrastructure/workspace/tests/codex_mcp/test_playbooks.py`
- `python3 -m pytest infrastructure/workspace/tests`
- `python3 -m pytest docs/qa/testing/test_documentation_alignment.py::test_hamilton_framework_integration_doc_is_published`

## Interfaces and Dependencies

El módulo expondrá funciones y dataclasses puramente locales, sin dependencias externas al repositorio. Se espera que otras herramientas puedan consumir la metadata retornada para generar scripts reales si así se decide en el futuro.
