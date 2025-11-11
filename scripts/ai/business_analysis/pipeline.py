"""
Business Analysis Pipeline

Pipeline completo de generación de análisis de negocio que orquesta
todos los agentes especializados en secuencia.

Flujo del Pipeline:
1. BusinessAnalysisGenerator: Genera análisis inicial completo
2. TraceabilityMatrixGenerator: Crea matrices RTM y análisis de gaps
3. CompletenessValidator: Valida completitud del análisis
4. DocumentSplitter: Divide en módulos si el documento es muy grande (opcional)
5. TemplateGenerator: Genera plantillas adicionales (opcional)

Configuración:
- Flexible: permite habilitar/deshabilitar agentes
- Configurable: parámetros específicos por agente
- Robusto: manejo de errores por agente
- Trazable: logs detallados de cada paso
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import Pipeline
from .business_analysis_generator import BusinessAnalysisGenerator
from .traceability_matrix_generator import TraceabilityMatrixGenerator
from .completeness_validator import CompletenessValidator
from .document_splitter import DocumentSplitter
from .template_generator import TemplateGenerator


class BusinessAnalysisPipeline:
    """
    Pipeline especializado para generación de análisis de negocio.

    Orquesta la ejecución de múltiples agentes en secuencia para
    generar documentación completa de análisis de negocio.

    Características:
    - Ejecución secuencial de agentes
    - Propagación de datos entre agentes
    - Configuración flexible por agente
    - Manejo de errores robusto
    - Generación de reportes de ejecución
    - Guardado automático de resultados
    """

    def __init__(
        self,
        output_dir: Path,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa el pipeline.

        Args:
            output_dir: Directorio de salida para resultados
            config: Configuración del pipeline y agentes
        """
        self.output_dir = Path(output_dir)
        self.config = config or {}

        # Crear directorio de salida
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configuración de agentes
        self.enable_splitter = self.config.get("split_large_docs", True)
        self.enable_templates = self.config.get("generate_templates", False)

        # Construir lista de agentes
        self.agents = self._build_agent_list()

        # Crear pipeline base
        self.pipeline = Pipeline(
            name="BusinessAnalysisPipeline",
            agents=self.agents
        )

    def _build_agent_list(self) -> List[Any]:
        """
        Construye lista de agentes según configuración.

        Returns:
            Lista de agentes a ejecutar
        """
        agents = []

        # Agente 1: BusinessAnalysisGenerator (obligatorio)
        agents.append(
            BusinessAnalysisGenerator(
                config=self.config.get("generator", {})
            )
        )

        # Agente 2: TraceabilityMatrixGenerator (obligatorio)
        agents.append(
            TraceabilityMatrixGenerator(
                config=self.config.get("traceability", {})
            )
        )

        # Agente 3: CompletenessValidator (obligatorio)
        agents.append(
            CompletenessValidator(
                config=self.config.get("validator", {})
            )
        )

        # Agente 4: DocumentSplitter (opcional)
        if self.enable_splitter:
            agents.append(
                DocumentSplitter(
                    config=self.config.get("splitter", {})
                )
            )

        # Agente 5: TemplateGenerator (opcional)
        if self.enable_templates:
            agents.append(
                TemplateGenerator(
                    config=self.config.get("templates", {})
                )
            )

        return agents

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo.

        Args:
            input_data: Datos de entrada para el pipeline

        Returns:
            Diccionario con resultados del pipeline
        """
        print(f"\n{'='*60}")
        print(f"  Business Analysis Pipeline")
        print(f"{'='*60}\n")

        print(f"Componente: {input_data.get('component_name', 'N/A')}")
        print(f"Dominio: {input_data.get('domain', 'N/A')}")
        print(f"Agentes: {len(self.agents)}")
        print(f"Salida: {self.output_dir}\n")

        # Ejecutar pipeline
        result = self.pipeline.execute(input_data)

        # Procesar resultados
        if result["status"] == "success":
            print(f"\n{'='*60}")
            print(f"  Pipeline Completado Exitosamente")
            print(f"{'='*60}\n")

            self._print_summary(result)
            self._save_results(result)

        elif result["status"] == "failed":
            print(f"\n{'='*60}")
            print(f"  Pipeline Falló")
            print(f"{'='*60}\n")

            print(f"Agente que falló: {result['failed_agent']}")
            print(f"Errores: {result['errors']}")
            print(f"Agentes completados: {len(result.get('completed_agents', []))}")

        elif result["status"] == "blocked":
            print(f"\n{'='*60}")
            print(f"  Pipeline Bloqueado")
            print(f"{'='*60}\n")

            print(f"Agente bloqueado: {result['blocked_agent']}")
            print(f"Razones: {result['errors']}")

        return result

    def _print_summary(self, result: Dict[str, Any]) -> None:
        """
        Imprime resumen de ejecución.

        Args:
            result: Resultado del pipeline
        """
        data = result.get("data", {})

        print("Artefactos Generados:")
        print(f"  - Procesos: {data.get('processes_count', 0)}")
        print(f"  - Reglas de Negocio: {data.get('business_rules_count', 0)}")
        print(f"  - Casos de Uso: {data.get('use_cases_count', 0)}")
        print(f"  - Requisitos Funcionales: {data.get('requirements_functional_count', 0)}")
        print(f"  - Requisitos No Funcionales: {data.get('requirements_nonfunctional_count', 0)}")

        # Métricas de trazabilidad
        if "traceability_index" in data:
            print(f"\nMétricas de Calidad:")
            print(f"  - Índice de Trazabilidad: {data['traceability_index']:.1%}")
            print(f"  - Índice de Cobertura: {data.get('coverage_index', 0):.1%}")

        # Completitud
        if "completeness_percentage" in data:
            print(f"  - Completitud: {data['completeness_percentage']:.1%}")
            print(f"  - Estado: {'COMPLETO' if data.get('is_complete') else 'INCOMPLETO'}")

        # Documentos generados
        if "document" in data:
            doc_lines = len(data['document'].split('\n'))
            print(f"\nDocumento Principal:")
            print(f"  - Líneas: {doc_lines}")
            print(f"  - Tamaño: {len(data['document'])} bytes")

        # Módulos (si se dividió)
        if "modules" in data:
            print(f"\nMódulos Generados:")
            print(f"  - Cantidad: {data.get('module_count', 0)}")
            print(f"  - Promedio: {data.get('average_module_size_lines', 0)} líneas/módulo")

    def _save_results(self, result: Dict[str, Any]) -> None:
        """
        Guarda resultados en disco.

        Args:
            result: Resultado del pipeline
        """
        data = result.get("data", {})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Guardar documento principal
        if "document" in data:
            doc_path = self.output_dir / f"analisis_completo_{timestamp}.md"
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(data["document"])
            print(f"\nDocumento guardado: {doc_path}")

        # Guardar matriz RTM
        if "rtm_document" in data:
            rtm_path = self.output_dir / f"matriz_trazabilidad_{timestamp}.md"
            with open(rtm_path, 'w', encoding='utf-8') as f:
                f.write(data["rtm_document"])
            print(f"Matriz RTM guardada: {rtm_path}")

        # Guardar checklist de completitud
        if "checklist_document" in data:
            checklist_path = self.output_dir / f"checklist_completitud_{timestamp}.md"
            with open(checklist_path, 'w', encoding='utf-8') as f:
                f.write(data["checklist_document"])
            print(f"Checklist guardado: {checklist_path}")

        # Guardar módulos (si se dividió)
        if "modules" in data and "master_index" in data:
            modules_dir = self.output_dir / f"modulos_{timestamp}"
            modules_dir.mkdir(exist_ok=True)

            # Guardar índice maestro
            index_path = modules_dir / "00_indice_maestro.md"
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(data["master_index"])

            # Guardar cada módulo
            for module in data["modules"]:
                module_path = modules_dir / module["filename"]
                with open(module_path, 'w', encoding='utf-8') as f:
                    f.write(module["content"])

            print(f"Módulos guardados en: {modules_dir}")

        # Guardar plantillas (si se generaron)
        if "template_content" in data:
            template_path = self.output_dir / f"plantilla_{data.get('template_type', 'template')}_{timestamp}.md"
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(data["template_content"])
            print(f"Plantilla guardada: {template_path}")

        # Guardar resultados del pipeline
        self.pipeline.save_results(self.output_dir / f"pipeline_results_{timestamp}")
        print(f"Resultados del pipeline: {self.output_dir}/pipeline_results_{timestamp}/")


def create_business_analysis_pipeline(
    output_dir: Path,
    config: Optional[Dict[str, Any]] = None
) -> BusinessAnalysisPipeline:
    """
    Factory function para crear pipeline de análisis de negocio.

    Args:
        output_dir: Directorio de salida
        config: Configuración del pipeline

    Returns:
        Instancia de BusinessAnalysisPipeline

    Example:
        >>> config = {
        ...     "generator": {
        ...         "domain": "Seguridad",
        ...         "include_procedures": True,
        ...         "include_nfr": True
        ...     },
        ...     "traceability": {
        ...         "min_traceability_index": 0.95,
        ...         "min_coverage_index": 0.90
        ...     },
        ...     "validator": {
        ...         "min_completeness": 0.95,
        ...         "strict_mode": False
        ...     },
        ...     "split_large_docs": True,
        ...     "splitter": {
        ...         "max_lines": 1000,
        ...         "min_lines": 200
        ...     },
        ...     "generate_templates": False
        ... }
        >>>
        >>> pipeline = create_business_analysis_pipeline(
        ...     output_dir=Path("output/analisis"),
        ...     config=config
        ... )
        >>>
        >>> input_data = {
        ...     "component_name": "Sistema de Recuperación de Contraseña",
        ...     "domain": "Seguridad",
        ...     "business_objective": "Permitir recuperación segura de acceso",
        ...     "stakeholders": [
        ...         {"rol": "Usuario", "interes": "Proceso simple y rápido"},
        ...         {"rol": "Admin Seguridad", "interes": "Trazabilidad completa"}
        ...     ]
        ... }
        >>>
        >>> result = pipeline.execute(input_data)
    """
    return BusinessAnalysisPipeline(output_dir=output_dir, config=config)
