---
name: CodeInspectorAgent
description: Escanea código backend, frontend e infraestructura para planificar actualizaciones de documentación.
---

# Documentation Code Inspector Agent

El `CodeInspectorAgent` (`scripts/coding/ai/documentation/sync_agent.py`) es la fase Planner del pipeline de sincronización documental. Recorre los dominios `api/`, `ui/` e `infrastructure/`, detecta componentes implementados y compara el estado real con los directorios de documentación existentes.

## Capacidades

- Descubre apps de Django (modelos, vistas, serializers, tests) y módulos React, incluyendo metadatos útiles para documentar.
- Analiza documentación vigente en `docs/` para identificar archivos inexistentes, desactualizados o correctos.
- Genera un `inspection_plan` con acciones `create`, `update` y `ok`, priorizadas por dominio.
- Expone estadísticas agregadas (componentes totales, docs faltantes, docs desactualizadas).
- Permite parametrizar dominios a inspeccionar y rutas raíz mediante configuración.

## Entradas y Salidas

- **Entradas**
  - `domains`: lista de dominios a evaluar (por defecto `api`, `ui`, `infrastructure`).
  - Configuración vía `project_root`, `docs_root` y flags específicos.
- **Salidas**
  - `discovered_components`: estructura con apps, módulos y servicios encontrados.
  - `existing_docs`: documentación ya presente en cada dominio.
  - `inspection_plan`: acciones sugeridas para creación/actualización.
  - Métricas de inspección (`stats`).

## Uso

```python
from scripts.coding.ai.documentation.sync_agent import CodeInspectorAgent

agent = CodeInspectorAgent({"project_root": Path.cwd()})
result = agent.run({"domains": ["api", "ui"]})
print(result["inspection_plan"]["create"])
```

## Validaciones Relacionadas

- Ejecutar `agent.validate_input({"domains": [...]})` para confirmar rutas antes de orquestar.
- Integrar su salida con `DocumentationEditorAgent`, `ConsistencyVerifierAgent` y `SyncReporterAgent` dentro del pipeline de sincronización.
