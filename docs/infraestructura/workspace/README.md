# Workspaces de Hamilton

Este directorio agrupa workspaces autocontenidos que acompañan la guía de integración Hamilton y las prácticas de TDD para GenAI.

## Hamilton LLM Example

- **Código**: `infrastructure/workspace/hamilton_llm/`
- **Pruebas**: `infrastructure/workspace/tests/hamilton_llm/test_driver.py`

El paquete contiene el driver declarativo (`driver.py`), el dataflow (`dataflow.py`) y el cliente LLM determinista (`llm_client.py`).

### Objetivo

1. Demostrar el flujo `Data → Prompt → LLM → $` utilizando el patrón de funciones declarativas de Hamilton.
2. Servir como punto de partida para crear workspaces adicionales orientados a GenAI en la carpeta `infrastructure/workspace/`.

### Cómo ejecutarlo

```bash
python3 -m pytest infrastructure/workspace/tests/hamilton_llm/test_driver.py
```

La prueba valida tanto el linaje del dataflow como el manejo de dependencias ausentes, permitiendo extender el workspace mediante TDD.

## Hamilton Language Server (Dev Tools)

- **Código**: `infrastructure/workspace/dev_tools/language_server/hamilton_lsp/`
- **Pruebas**: `infrastructure/workspace/tests/dev_tools/language_server/test_hamilton_lsp.py`

Este workspace replica de forma auto-contenida la estructura del lenguaje de servidores de Apache Hamilton. Incluye un `HamiltonLanguageServer` que puede registrar eventos de apertura/cambio, generar completions, exponer símbolos y enviar visualizaciones DOT sin depender de librerías externas.

### Cómo validarlo

```bash
python3 -m pytest infrastructure/workspace/tests/dev_tools/language_server/test_hamilton_lsp.py
```

Las pruebas cubren el registro de features LSP, la construcción del grafo al abrir documentos, los comandos de visualización y la extracción de símbolos.

## Registro de suites

Para verificar la alineación estructural del workspace, se expone `infrastructure/workspace/tests/test_registry.py`, que afirma la presencia de `TEST_SUITES` en el paquete raíz y que ambos workspaces quedan registrados para futuras automatizaciones.
