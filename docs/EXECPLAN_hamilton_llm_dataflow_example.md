# ExecPlan: Implementar ejemplo Hamilton para pipeline Data→Prompt→LLM con TDD

Esta ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` deben mantenerse al día conforme avance el trabajo. Se rige por las pautas de `.agent/PLANS.md`.

## Purpose / Big Picture

Queremos que cualquier integrante del proyecto pueda ejecutar un ejemplo mínimo de Hamilton que modele el flujo `Data → Prompt → LLM → $`, incorporando las ideas de ritmo de desarrollo para aplicaciones ML tradicionales versus LLM y la necesidad de buenas prácticas de ingeniería. El entregable será un paquete en `scripts/coding/ai/examples/` con un driver Hamilton (o equivalente declarativo) ejecutable vía pytest para que se observe el dataflow, junto con pruebas unitarias que fallen antes de implementar el código. El ejemplo debe exponer, mediante funciones declarativas, cómo se integran datos, plantillas de prompt, clientes LLM simulados y validaciones.

## Progress

- [x] (2025-11-19 10:00Z) ExecPlan creado y alcance documentado.
- [x] (2025-11-19 10:25Z) Pruebas unitarias que describen el dataflow Hamilton deseado creadas en scripts/coding/tests/ai/examples/test_hamilton_llm_example.py.
- [x] (2025-11-19 11:05Z) Implementación del ejemplo Hamilton (driver, dataflow y cliente LLM) con pruebas pasando.
- [x] (2025-11-19 11:20Z) Documentación actualizada (guía Hamilton e índice general) y validaciones ejecutadas.
- [x] (2025-11-13 11:05Z) Refactor del driver para exponer Builder/Driver/DictResult estilo apache/hamilton y ampliación de pruebas.
- [x] (2025-11-19 11:40Z) Reubicación del paquete Hamilton a `infrastructure/workspace/hamilton_llm` y actualización de referencias documentales.

## Surprises & Discoveries

- Observación: Para aislar el error de falta de pricing fue necesario provisionar dependencias intermedias en la prueba negativa; Hamilton evalúa nodos siguiendo el orden de las firmas.
  Evidence: `test_driver_reports_missing_inputs` ahora injecta idea, domain_data y edge_cases antes de omitir `pricing_policy`.
- Observación: El shimming del Builder requiere exponer adaptadores encadenables; reutilizamos un DictResult idéntico al de apache/hamilton para mantener compatibilidad conceptual.
  Evidence: `test_custom_adapter_transforms_execution_result` valida la transformación de resultados.

## Decision Log

- Decision: Escalar el estimador de tokens al 75 % del prompt más un amortiguador fijo para edge cases, garantizando un costo determinista alineado a la guía.
  Rationale: El largo del prompt supera los 150 tokens; sin escalar no se alcanzaba el valor esperado de 120 tokens.
  Date/Author: 2025-11-19 / coding-agent
- Decision: Mantener un shim local (Builder/Driver/DictResult) compatible con la API oficial para no depender de instalaciones externas en CI.
  Rationale: El entorno del repositorio no permite `pip install`; replicar la interfaz pública permite migrar a la librería real sin reescribir pruebas.
  Date/Author: 2025-11-13 / coding-agent
- Decision: Trasladar el ejemplo Hamilton al árbol `infrastructure/workspace` para alinearlo con la organización de entornos ejecutables y facilitar su descubrimiento desde infraestructura.
  Rationale: El ejemplo sirve como workspace autocontenible; ubicarlo junto al resto de utilidades de infraestructura responde a la retroalimentación del stakeholder y mantiene la separación documentación/código.
  Date/Author: 2025-11-19 / coding-agent

## Outcomes & Retrospective

El ejemplo Hamilton quedó implementado con cobertura de pruebas dedicada y documentación cruzada.
La refactorización reciente alinea la API con `github.com/apache/hamilton`, facilitando reemplazar el shim por la dependencia real.
Las pruebas de documentación existentes siguen fallando por deuda histórica; se documentó la nueva ruta en `docs/index.md` y en la guía de gobierno para facilitar futuras remediaciones.

## Context and Orientation

El repositorio organiza scripts de agentes en `scripts/coding/ai/` y pruebas correspondientes en `scripts/coding/tests/`. La guía `docs/gobernanza/ai/HAMILTON_FRAMEWORK_INTEGRACION_SDLC.md` solicita como siguiente paso incorporar ejemplos de código Hamilton usando TDD. Actualmente no existe un paquete que demuestre un dataflow Hamilton; tampoco tenemos dependencias a `sf-hamilton`. Implementaremos un micro-driver declarativo interno inspirado en Hamilton, suficiente para ejecutar funciones nombradas según los nodos del grafo y resolver dependencias mediante introspección. Las pruebas se ubicarán en `scripts/coding/tests/ai/examples/` para mantener la correspondencia.

El ejemplo debe incluir:
1. Una representación explícita de la diferencia entre flujos de desarrollo ML tradicional y LLM, ya sea en docstrings o constantes que puedan inspeccionarse desde las pruebas.
2. Un pipeline `Data → Prompt → LLM → Cost` compuesto por funciones declarativas donde los nombres son los outputs y los argumentos las dependencias.
3. Un cliente LLM simulado que acepte prompts y devuelva una respuesta determinística (evitamos llamadas externas).
4. Validaciones que reflejen habilidades SWE: pruebas unitarias, modularidad y reutilización.

## Plan of Work

1. Crear paquete `infrastructure/workspace/hamilton_llm/` con archivos `__init__.py`, `dataflow.py` y `llm_client.py`. `dataflow.py` contendrá funciones declarativas (topic, prompt_template, prompt, llm_response, business_value, cost_estimate). `llm_client.py` expondrá una clase `MockLLMClient` parametrizable. Documentar en docstrings las diferencias de ritmo de desarrollo.
2. Implementar micro driver en `infrastructure/workspace/hamilton_llm/driver.py` que resuelva dependencias mediante inspección de firmas, exponiendo además un `Builder` y adaptadores `DictResult` compatibles con la API oficial. La ejecución debe aceptar configuración base (`with_config`) y adaptadores encadenables.
3. Escribir pruebas TDD en `scripts/coding/tests/ai/examples/test_hamilton_llm_example.py` que:
   - Construyan el driver con el módulo `dataflow`.
   - Injecten entradas (por ejemplo, `idea`, `domain_data`, `pricing_policy`).
   - Verifiquen que `llm_response` y `business_value` devuelvan valores esperados.
   - Aseguren que el grafo solo ejecuta nodos necesarios y que la metadata sobre ritmo de desarrollo está presente.
4. Ejecutar pytest y observar fallo (Red).
5. Implementar código real en los módulos descritos, asegurando cobertura >80 % mediante pruebas que ejerciten rutas principales, errores controlados (por ejemplo, dependencia faltante) y adaptadores personalizados.
6. Re-ejecutar pytest (Green) y refactorizar si procede.
7. Actualizar `docs/gobernanza/ai/HAMILTON_FRAMEWORK_INTEGRACION_SDLC.md` en la sección de próximos pasos para referenciar el nuevo ejemplo y añadir entrada en `docs/index.md` si corresponde.
8. Documentar en el ExecPlan las decisiones, sorpresas y resultados. Incluir instrucciones de validación (`python3 -m pytest scripts/coding/tests/ai/examples/test_hamilton_llm_example.py`).
9. Mantener el shim alineado con apache/hamilton agregando pruebas de Builder y adaptadores para evitar regresiones.

## Concrete Steps

1. Añadir pruebas fallidas: crear archivo de test y ejecutar `python3 -m pytest scripts/coding/tests/ai/examples/test_hamilton_llm_example.py` desde la raíz del repo.
2. Implementar paquetes y funciones según el plan, escribir docstrings que recojan la narrativa de ritmo de desarrollo y habilidades SWE.
3. Añadir pruebas de Builder/adaptadores (`test_custom_adapter_transforms_execution_result`, `test_builder_requires_modules_before_building`) antes de implementar el shim.
4. Ejecutar pytest nuevamente hasta que pase y revisar cobertura si se añade reporte.
5. Actualizar documentación cruzada e índice.
6. Registrar decisiones y sorpresas en el ExecPlan conforme aparezcan.

## Validation and Acceptance

- `python3 -m pytest scripts/coding/tests/ai/examples/test_hamilton_llm_example.py` debe pasar, mostrando que el driver ejecuta correctamente el dataflow y que la metadata esperada está disponible.
- `python3 -m pytest docs/qa/testing/test_documentation_alignment.py` debe continuar pasando, confirmando integridad documental.
- La documentación Hamilton debe mencionar explícitamente el nuevo ejemplo.

## Idempotence and Recovery

El driver declarativo resolverá dependencias determinísticamente, por lo que ejecutar el pipeline múltiples veces produce el mismo resultado dado que el cliente LLM es determinista. Si un nodo falla por dependencia faltante, el driver debe generar una excepción clara (`MissingDependencyError`). Las pruebas pueden re-ejecutarse sin efectos secundarios. En caso de fallo durante la implementación, eliminar archivos nuevos y volver a ejecutar pytest dejará el entorno limpio.

## Artifacts and Notes

Salida relevante de validaciones más recientes:

- `python3 -m pytest scripts/coding/tests/ai/examples/test_hamilton_llm_example.py`

      scripts/coding/tests/ai/examples/test_hamilton_llm_example.py .....

- `python3 -m pytest docs/qa/testing/test_documentation_alignment.py` (sigue fallando por deuda documental heredada)

      docs/qa/testing/test_documentation_alignment.py::test_hamilton_framework_integration_doc_is_published PASSED
      docs/qa/testing/test_documentation_alignment.py::test_readme_acknowledges_absence_of_root_makefile FAILED

## Interfaces and Dependencies

- `infrastructure/workspace/hamilton_llm/driver.py` definirá:
      class Builder:
          def with_modules(self, *modules: ModuleType | str) -> Builder
          def with_config(self, config: Mapping[str, Any]) -> Builder
          def with_adapters(self, *adapters: Callable[[Mapping[str, Any]], Any]) -> Builder
          def build(self) -> Driver

      class Driver:
          def execute(self, targets: Sequence[str], inputs: Mapping[str, Any] | None = None) -> Any

      class DictResult:
          def __call__(self, results: Mapping[str, Any]) -> Mapping[str, Any]

  Incluir excepción `MissingDependencyError` y motor interno para resolver dependencias por nombre de función.

- `infrastructure/workspace/hamilton_llm/dataflow.py` definirá funciones:
      def idea() -> str: ...  # documented with pacing insight
      def domain_data() -> dict[str, Any]: ...
      def prompt_template(idea: str, domain_data: dict[str, Any]) -> str: ...
      def llm_prompt(prompt_template: str) -> str: ...
      def llm_response(llm_prompt: str, llm_client: MockLLMClient) -> str: ...
      def business_value(llm_response: str, pricing_policy: dict[str, Any]) -> dict[str, Any]: ...
      def cost_estimate(llm_response: str, pricing_policy: dict[str, Any]) -> float: ...

- `infrastructure/workspace/hamilton_llm/llm_client.py` definirá:
      class MockLLMClient:
          def __init__(self, price_per_1k_tokens: float, response_catalog: Mapping[str, str]): ...
          def complete(self, prompt: str) -> str: ...

Este conjunto permitirá demostrar el flujo `Data → Prompt → LLM → $`.
