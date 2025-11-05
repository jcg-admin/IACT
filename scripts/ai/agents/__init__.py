"""
Agentes especializados para generación automática de tests.

Este paquete contiene 7 agentes especializados que siguen el principio
de responsabilidad única (SRP) para generar tests automáticamente:

1. CoverageAnalyzer - Analiza gaps de cobertura
2. TestPlanner - Planifica tests a generar
3. LLMGenerator - Genera código con LLM
4. SyntaxValidator - Valida sintaxis y estilo
5. TestRunner - Ejecuta tests
6. CoverageVerifier - Verifica incremento de cobertura
7. PRCreator - Crea Pull Request

Cada agente tiene una única responsabilidad y puede ser testeado,
modificado y reusado de forma independiente.
"""

from .base import Agent, AgentResult, AgentStatus, Pipeline
from .coverage_analyzer import CoverageAnalyzer
from .test_planner import TestPlanner
from .llm_generator import LLMGenerator
from .syntax_validator import SyntaxValidator
from .test_runner import TestRunner
from .coverage_verifier import CoverageVerifier
from .pr_creator import PRCreator

__all__ = [
    "Agent",
    "AgentResult",
    "AgentStatus",
    "Pipeline",
    "CoverageAnalyzer",
    "TestPlanner",
    "LLMGenerator",
    "SyntaxValidator",
    "TestRunner",
    "CoverageVerifier",
    "PRCreator",
]

__version__ = "1.0.0"
