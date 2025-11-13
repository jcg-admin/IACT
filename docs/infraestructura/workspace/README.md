# Workspace Hamilton LLM Example

Este workspace agrupa los artefactos ejecutables que acompañan la guía de integración Hamilton.

## Ubicación del código

- **Paquete principal**: `infrastructure/workspace/hamilton_llm/`
- **Pruebas asociadas**: `infrastructure/workspace/tests/hamilton_llm/test_driver.py`

El paquete contiene el driver declarativo (`driver.py`), el dataflow (`dataflow.py`) y el cliente LLM determinista (`llm_client.py`).

## Objetivo

1. Demostrar el flujo `Data → Prompt → LLM → $` utilizando el patrón de funciones declarativas de Hamilton.
2. Servir como punto de partida para crear workspaces adicionales orientados a GenAI en la carpeta `infrastructure/workspace/`.

## Cómo ejecutarlo

```bash
python3 -m pytest infrastructure/workspace/tests/hamilton_llm/test_driver.py
```

La prueba valida tanto el linaje del dataflow como el manejo de dependencias ausentes, permitiendo extender el workspace mediante TDD.

Para verificar la alineación estructural del workspace, se expone además `infrastructure/workspace/tests/test_registry.py`, que afirma la presencia de `TEST_SUITES` en el paquete raíz y que el workspace Hamilton queda registrado para futuras automatizaciones.
