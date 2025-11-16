# Integrar el agente Implementation Planner y sus restricciones obligatorias

Este plan detalla cómo propagar las instrucciones personalizadas "implementation-planner" en los artefactos maestros del catálogo de agentes y documentación, garantizando que cualquier ficha o guía que lo consuma conozca las reglas de TDD, cobertura ≥80 %, commits convencionales y definición operativa de alucinaciones.

## Objetivo
- Registrar la ficha `.github/agents/implementation-planner-agent.agent.md` con la plantilla de etiquetas `<Goals>`, `<Limitations>`, `<WhatToAdd>`, `<StepsToFollow>`, `<Validation>`.
- Exponer el agente en `.github/copilot/agents.json` para que Copilot lo pueda invocar.
- Actualizar los índices (`AGENTS_IMPLEMENTATION_MAP.md`, `.github/agents/README.md`) para reflejar la existencia del agente y las restricciones que arrastra.
- Conectar los playbooks temáticos (p. ej., `docs/mobile/ejemplos-mobile.md`) con las mismas reglas para que al solicitar prompts quede claro cómo prevenir alucinaciones.

## Alcance
- Solo documentación; no se modifica código ejecutable.
- No se referencian rutas frágiles dentro de las fichas (la ficha del agente explica procesos y políticas).
- Se debe incluir en cada artefacto la referencia a TDD, cobertura, Conventional Commits y gestión rigurosa de alucinaciones.

## Pasos
1. **Inventario**: revisar catálogos existentes y confirmar ausencia del agente `implementation-planner`.
2. **Ficha**: redactar archivo `.github/agents/implementation-planner-agent.agent.md` incluyendo:
   - Objetivos: planificar entregas con especificaciones detalladas.
   - Limitaciones: respetar metodología TDD, cobertura, convenciones y documentación de decisiones.
   - Qué añadir: high-level details sobre análisis, plantillas, uso de meta-prompts y prevención de alucinaciones.
   - BuildInstructions / Steps con énfasis en Red→Green→Refactor y métricas.
   - Validaciones: comprobar planes vs. pipelines, listas anti-alucinación, verificación cruzada.
3. **Catálogo Copilot**: agregar entrada en `.github/copilot/agents.json` con descripción y ruta de instrucciones.
4. **Mapas**: añadir fila/sección en `AGENTS_IMPLEMENTATION_MAP.md` bajo "Agentes Definidos en Markdown" e incluir mención en `.github/agents/README.md` dentro del catálogo.
5. **Playbook móvil**: insertar recordatorio para que los prompts usen Implementation Planner como orquestador de restricciones.
6. **Validación**:
   - `python3 -m json.tool .github/copilot/agents.json`.
   - Revisar manualmente cada archivo modificado para confirmar etiquetas y menciones.

## Resultados esperados
- Copilot puede seleccionar Implementation Planner como agente especializado en planes técnicos.
- Toda guía relevante subraya las mismas restricciones obligatorias.
- Se reduce riesgo de alucinaciones gracias al enlace entre meta-prompts y la ficha del agente.
