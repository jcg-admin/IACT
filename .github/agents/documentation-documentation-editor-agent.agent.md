---
name: DocumentationEditorAgent
description: Genera o actualiza archivos Markdown siguiendo el plan emitido por CodeInspectorAgent.
---

# Documentation Editor Agent

`DocumentationEditorAgent` (`scripts/coding/ai/documentation/sync_agent.py`) es la fase Editor del flujo de sincronización. A partir del `inspection_plan`, crea nuevos documentos con metadatos estándar y marca archivos existentes para revisión, permitiendo modo `dry-run` para simulaciones.

## Capacidades

- Valida la presencia del plan y los componentes descubiertos antes de ejecutar.
- Genera contenido Markdown para apps de Django, módulos React e infraestructura utilizando plantillas internas.
- Escribe archivos en `docs/` (o ejecuta en modo `dry_run` reportando qué se generaría).
- Registra estadísticas de documentos creados y actualizados, preservando rutas finales.
- Permite configurar directorios raíz y plantillas mediante parámetros de inicialización.

## Entradas y Salidas

- **Entradas**
  - `inspection_plan`: acciones `create` y `update` generadas por `CodeInspectorAgent`.
  - `discovered_components`: detalle de componentes detectados.
  - Opcionales: `template_dir`, `dry_run` (config).
- **Salidas**
  - `created_docs`: lista de documentos nuevos o simulados.
  - `updated_docs`: componentes marcados para revisión.
  - `files_written`: rutas efectivamente escritas cuando `dry_run=False`.
  - Métricas (`stats`) con conteos de creación/actualización.

## Uso

```python
from scripts.coding.ai.documentation.sync_agent import DocumentationEditorAgent

editor = DocumentationEditorAgent({"project_root": Path.cwd(), "dry_run": True})
result = editor.run({
    "inspection_plan": plan,
    "discovered_components": discovered
})
print(result["stats"], result["created_docs"][0])
```

## Validaciones Relacionadas

- Utilizar `editor.validate_input(...)` antes de ejecutar para detectar configuraciones incompletas.
- Encadenar su salida con `ConsistencyVerifierAgent` para asegurar que los documentos satisfacen las necesidades detectadas.
