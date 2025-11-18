"""
TDD Agent

Automatiza el ciclo Test-Driven Development completo:
- Genera tests desde requisitos
- Ejecuta pytest
- Analiza errores
- Documenta el proceso
- Itera hasta 100% passing

Componentes:
- TDDAgent: Orquestador principal
- TestGenerator: Genera código de tests
- ErrorAnalyzer: Analiza fallos de pytest
- DocGenerator: Genera documentación markdown
"""

from .tdd_agent import TDDAgent

__all__ = ['TDDAgent']
