"""
Agentes especializados para generación automática de tests y análisis de negocio.

Este paquete contiene dos categorías de agentes:

## Agentes de Generación de Tests (7 agentes)

Siguen el principio de responsabilidad única (SRP) para generar tests automáticamente:

1. CoverageAnalyzer - Analiza gaps de cobertura
2. TestPlanner - Planifica tests a generar
3. LLMGenerator - Genera código con LLM
4. SyntaxValidator - Valida sintaxis y estilo
5. TestRunner - Ejecuta tests
6. CoverageVerifier - Verifica incremento de cobertura
7. PRCreator - Crea Pull Request

## Agentes de Análisis de Negocio (5 agentes)

Generan documentación completa de análisis de negocio siguiendo estándares
ISO 29148:2018, BABOK v3 y UML 2.5:

1. BusinessAnalysisGenerator - Genera análisis completo (Procesos → UC → Requisitos)
2. TraceabilityMatrixGenerator - Genera matrices RTM y análisis de gaps
3. CompletenessValidator - Valida completitud con checklist
4. TemplateGenerator - Genera plantillas personalizables
5. DocumentSplitter - Divide documentos grandes en módulos

Pipeline:
- BusinessAnalysisPipeline - Orquesta todos los agentes de análisis

Cada agente tiene una única responsabilidad y puede ser testeado,
modificado y reusado de forma independiente.
"""

# Base
from .base import Agent, AgentResult, AgentStatus, Pipeline

# Agentes de Generación de Tests
from .coverage_analyzer import CoverageAnalyzer
from .test_planner import TestPlanner
from .llm_generator import LLMGenerator
from .syntax_validator import SyntaxValidator
from .test_runner import TestRunner
from .coverage_verifier import CoverageVerifier
from .pr_creator import PRCreator

# Agentes de Análisis de Negocio
from .business_analysis_generator import BusinessAnalysisGenerator
from .traceability_matrix_generator import TraceabilityMatrixGenerator
from .completeness_validator import CompletenessValidator
from .template_generator import TemplateGenerator
from .document_splitter import DocumentSplitter
from .business_analysis_pipeline import (
    BusinessAnalysisPipeline,
    create_business_analysis_pipeline
)

__all__ = [
    # Base
    "Agent",
    "AgentResult",
    "AgentStatus",
    "Pipeline",
    # Agentes de Tests
    "CoverageAnalyzer",
    "TestPlanner",
    "LLMGenerator",
    "SyntaxValidator",
    "TestRunner",
    "CoverageVerifier",
    "PRCreator",
    # Agentes de Análisis de Negocio
    "BusinessAnalysisGenerator",
    "TraceabilityMatrixGenerator",
    "CompletenessValidator",
    "TemplateGenerator",
    "DocumentSplitter",
    "BusinessAnalysisPipeline",
    "create_business_analysis_pipeline",
]

__version__ = "1.1.0"
