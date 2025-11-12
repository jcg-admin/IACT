# Documentation Management

Gestión y sincronización de documentación del proyecto.

## Módulos

- `sync_agent.py` - Sincroniza documentación entre repositorios
- `document_splitter.py` - Divide documentos grandes en módulos

## Uso

```python
from scripts.ai.documentation.sync_agent import DocumentationSyncAgent

agent = DocumentationSyncAgent()
result = agent.sync()
```
