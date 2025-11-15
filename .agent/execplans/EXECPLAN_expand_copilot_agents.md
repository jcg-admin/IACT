# Expandir agentes de Copilot para cubrir todas las definiciones disponibles

Este ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` deben mantenerse actualizadas según `.agent/PLANS.md`.

## Purpose / Big Picture

Tras esta actualización, cualquier persona podrá invocar desde GitHub Copilot a todos los agentes especializados documentados en `.agent/agents/`, sin tener que recordar rutas ni activar manualmente cada ficha. El usuario comprobará el resultado revisando que `@nombre_agente` esté disponible en la lista de agentes sugeridos por Copilot y verificando que cada entrada enlaza con su markdown de instrucciones.

## Progress

- [x] (2025-11-15 17:46Z) Redactado el ExecPlan inicial y confirmado el objetivo con la documentación existente.
- [x] (2025-11-15 17:48Z) Inventario actualizado de agentes en `.agent/agents/` y clasificación preliminar por categorías.
- [x] (2025-11-15 17:55Z) Definición de descripciones concisas para cada agente pendiente y mapeo al archivo correspondiente.
- [x] (2025-11-15 17:56Z) Actualización de `.github/copilot/agents.json` con todas las entradas requeridas, manteniendo consistencia JSON.
- [x] (2025-11-15 17:57Z) Validación estructural (`python3 -m json.tool`) y verificación de existencia de archivos referenciados.
- [x] (2025-11-15 17:58Z) Registro del resultado final en `Outcomes & Retrospective` y cierre del plan.

## Surprises & Discoveries

- Ninguna aún.

## Decision Log

- (2025-11-15) Se decidió mantener el formato `snake_case` para los identificadores en `agents.json`, siguiendo las entradas actuales y evitando ambigüedades entre mayúsculas/minúsculas.
- (2025-11-15) Las entradas de `agents.json` se ordenaron por categoría funcional (dominio, proveedores, automatización, SDLC, meta, calidad, documentación y TDD) para facilitar su descubrimiento.

## Outcomes & Retrospective

La ampliación de `agents.json` habilita 37 agentes adicionales (dominio, proveedores, automatización, SDLC, meta, calidad, documentación y TDD) sin perder las definiciones existentes. La validación con `python3 -m json.tool` y el barrido mediante `jq` confirmaron tanto la sintaxis como la existencia de cada archivo de instrucciones. Con esto, Copilot puede ofrecer un catálogo completo alineado con la documentación y los ExecPlans vigentes.

## Context and Orientation

Actualmente `./.github/copilot/agents.json` solo registra cinco agentes (`my_agent`, `gitops_agent`, `release_agent`, `dependency_agent`, `security_agent`). Sin embargo, `.agent/agents/` contiene más de treinta definiciones markdown para agentes de dominios (ApiAgent, UiAgent, etc.), proveedores LLM (ClaudeAgent, ChatGPTAgent, HuggingFaceAgent) y automatización (Automation_*). La documentación consolidada en `.github/agents/README.md` y `.agent/agents/README.md` describe el alcance de cada uno pero no los expone en la configuración activa de Copilot.

## Plan of Work

Primero se listarán todos los archivos markdown en `.agent/agents/` que representen agentes (excluyendo `README.md`). Después se agruparán por categorías para redactar descripciones claras en español, reutilizando los resúmenes presentes en la documentación existente. A continuación se ampliará la matriz `agents` en `.github/copilot/agents.json`, respetando el orden lógico (por categorías) y manteniendo las entradas ya presentes. Finalmente se validará el JSON y se ejecutará un script sencillo con `jq` o bucle shell para asegurar que cada ruta apuntada existe.

## Concrete Steps

1. `ls .agent/agents` y, si es necesario, filtrar con `sed` o `python` para obtener los nombres sin la extensión `.md`.
2. Revisar la documentación de referencia (`.github/agents/*.md`, `.agent/agents/README.md`) para extraer una frase descriptiva por agente.
3. Editar `.github/copilot/agents.json` añadiendo objetos con los campos `name`, `description` e `instructions` para cada agente pendiente. Mantener indentación de dos espacios y ordenar por grupos lógicos (SDLC, automatización, dominio, proveedores, meta, calidad, TDD, documentación, etc.).
4. Ejecutar `cat .github/copilot/agents.json | python3 -m json.tool` para validar la sintaxis.
5. Ejecutar `for agent in $(jq -r '.agents[].instructions' .github/copilot/agents.json); do [ -f "$agent" ] && echo "[OK] $agent" || echo "[MISSING] $agent"; done` para asegurar que no haya referencias rotas.
6. Actualizar este ExecPlan, marcando el progreso alcanzado y documentando hallazgos o decisiones adicionales.

## Validation and Acceptance

La actualización se considerará exitosa cuando:

- El comando `python3 -m json.tool` confirme que `agents.json` es válido.
- El bucle de verificación reporte `[OK]` para cada ruta de instrucciones.
- El `Progress` del plan indique todas las tareas como completadas.
- `Outcomes & Retrospective` documente que Copilot ahora cuenta con todas las entradas esperadas.

## Idempotence and Recovery

Las modificaciones al JSON son idempotentes: repetir el proceso sólo reemplazará el contenido con las mismas entradas. En caso de error, se puede restaurar el archivo ejecutando `git checkout -- .github/copilot/agents.json` y reiniciando desde el paso de inventario.

## Artifacts and Notes

- Capturar, en caso necesario, ejemplos breves de las descripciones redactadas para reutilizarlas en documentación futura.

## Interfaces and Dependencies

- Archivo de configuración: `.github/copilot/agents.json`.
- Definiciones de agentes: `.agent/agents/*.md`.
- Documentación de referencia: `.github/agents/*.md` y `.agent/agents/README.md`.
- Herramientas CLI: `python3`, `jq` (preinstalado en la imagen base) para verificación.
