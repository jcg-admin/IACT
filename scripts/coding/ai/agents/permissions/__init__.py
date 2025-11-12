"""
Permission Analysis Agents

Agentes especializados en análisis y validación del sistema de permisos IACT.

Componentes:
- BasePermissionAgent: Clase base para todos los agentes
- RouteLintAgent: Verifica que ViewSets tengan required_permissions
- AuditValidatorAgent: Valida contrato de auditoría
- CoverageAnalyzerAgent: Analiza cobertura de tests de permisos
"""

from .base import BasePermissionAgent

__all__ = ['BasePermissionAgent']
