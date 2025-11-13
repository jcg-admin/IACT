# Workspace Hamilton LLM Example

Este workspace agrupa los artefactos ejecutables que acompañan la guía de integración Hamilton.

## Ubicación del código

- **Paquete principal**: `infrastructure/workspace/hamilton_llm/`
- **Pruebas asociadas**: `scripts/coding/tests/ai/examples/test_hamilton_llm_example.py`

El paquete contiene el driver declarativo (`driver.py`), el dataflow (`dataflow.py`) y el cliente LLM determinista (`llm_client.py`).

## Objetivo

1. Demostrar el flujo `Data → Prompt → LLM → $` utilizando el patrón de funciones declarativas de Hamilton.
2. Servir como punto de partida para crear workspaces adicionales orientados a GenAI en la carpeta `infrastructure/workspace/`.

## Cómo ejecutarlo

```bash
python3 -m pytest scripts/coding/tests/ai/examples/test_hamilton_llm_example.py
```

La prueba valida tanto el linaje del dataflow como el manejo de dependencias ausentes, permitiendo extender el workspace mediante TDD.
