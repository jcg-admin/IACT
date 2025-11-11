"""
SDLCPlannerAgent - Fase 1: Planning

Responsabilidad: Analizar feature requests y generar issues/tickets completos
con user stories, acceptance criteria, story points y requisitos técnicos.

Inputs:
- feature_request (texto libre o URL a issue)
- project_context (opcional)
- backlog (opcional)

Outputs:
- Issue/ticket formateado (GitHub Issue)
- User story completa
- Acceptance criteria
- Story points estimation
- Priority recommendation
- Technical requirements identificados
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .sdlc_base import SDLCAgent, SDLCPhaseResult


class SDLCPlannerAgent(SDLCAgent):
    """
    Agente para la fase de Planning del SDLC.

    Convierte feature requests en issues bien estructurados siguiendo
    estándares de user stories, estimación y priorización.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="SDLCPlannerAgent",
            phase="planning",
            config=config
        )
        self.llm_provider = self.get_config("llm_provider", "anthropic")
        self.model = self.get_config("model", "claude-3-5-sonnet-20241022")

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Guardrails específicos para Planning phase.

        El PlannerAgent no genera código, solo documentación de planificación,
        por lo que los guardrails de constitution no aplican estrictamente.
        """
        errors = []

        # Validar que se generó un issue
        if "issue_title" not in output_data:
            errors.append("No se generó título de issue")

        if "issue_body" not in output_data:
            errors.append("No se generó cuerpo de issue")

        # Validar que hay acceptance criteria
        if "acceptance_criteria" not in output_data or not output_data["acceptance_criteria"]:
            errors.append("No se generaron acceptance criteria")

        # Validar estimación
        story_points = output_data.get("story_points", 0)
        if story_points <= 0:
            errors.append("Story points inválidos")

        return errors

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que exista un feature request."""
        errors = []

        if "feature_request" not in input_data:
            errors.append("Falta 'feature_request' en input")

        feature_request = input_data.get("feature_request", "")
        if not feature_request or not feature_request.strip():
            errors.append("'feature_request' está vacío")

        # TODO: Validar API key cuando se implemente integración LLM real
        # Por ahora usa heurísticas sin LLM
        # if self.llm_provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        #     errors.append("Falta ANTHROPIC_API_KEY en variables de entorno")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la fase de Planning.

        Args:
            input_data: {
                "feature_request": str,  # Descripción del feature
                "project_context": str,  # Contexto del proyecto (opcional)
                "backlog": List[Dict],   # Backlog actual (opcional)
            }

        Returns:
            Dict con issue, user story, acceptance criteria, story points, etc.
        """
        feature_request = input_data["feature_request"]
        project_context = input_data.get("project_context", "")
        backlog = input_data.get("backlog", [])

        self.logger.info(f"Analizando feature request: {feature_request[:100]}...")

        # Analizar project context
        context_analysis = self._analyze_project_context(project_context)

        # Generar user story con LLM
        user_story = self._generate_user_story(
            feature_request,
            context_analysis,
            backlog
        )

        # Extraer componentes
        title = user_story.get("title", "")
        description = user_story.get("description", "")
        acceptance_criteria = user_story.get("acceptance_criteria", [])
        story_points = user_story.get("story_points", 0)
        priority = user_story.get("priority", "P2")
        technical_requirements = user_story.get("technical_requirements", [])
        dependencies = user_story.get("dependencies", [])

        # Generar issue body formateado (GitHub)
        issue_body = self._format_github_issue(
            description=description,
            acceptance_criteria=acceptance_criteria,
            technical_requirements=technical_requirements,
            story_points=story_points,
            priority=priority,
            dependencies=dependencies
        )

        # Guardar artefactos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        issue_filename = f"ISSUE_{timestamp}.md"
        issue_path = self.save_artifact(issue_body, issue_filename)

        # Crear resultado de fase
        phase_result = self.create_phase_result(
            decision="go",  # Planning siempre es go
            confidence=0.85,
            artifacts=[str(issue_path)],
            recommendations=[
                f"Issue generado: {title}",
                f"Story points estimados: {story_points}",
                f"Prioridad recomendada: {priority}",
                "Siguiente fase: Feasibility Analysis"
            ],
            next_steps=[
                "Revisar issue generado",
                "Validar acceptance criteria con stakeholders",
                "Proceder a análisis de viabilidad"
            ]
        )

        return {
            "issue_title": title,
            "issue_body": issue_body,
            "issue_path": str(issue_path),
            "user_story": user_story,
            "story_points": story_points,
            "priority": priority,
            "acceptance_criteria": acceptance_criteria,
            "technical_requirements": technical_requirements,
            "dependencies": dependencies,
            "phase_result": phase_result
        }

    def _analyze_project_context(self, project_context: str) -> Dict[str, Any]:
        """
        Analiza el contexto del proyecto.

        Args:
            project_context: Texto con contexto del proyecto

        Returns:
            Análisis estructurado del contexto
        """
        if not project_context:
            # Intentar leer contexto del proyecto
            readme_path = self.project_root / "README.md"
            if readme_path.exists():
                project_context = readme_path.read_text(encoding="utf-8")

        # Análisis básico (sin LLM para eficiencia)
        analysis = {
            "has_context": bool(project_context),
            "tech_stack": self._extract_tech_stack(project_context),
            "patterns": self._extract_patterns(project_context)
        }

        return analysis

    def _extract_tech_stack(self, context: str) -> List[str]:
        """Extrae tecnologías mencionadas en el contexto."""
        tech_keywords = [
            "Django", "React", "PostgreSQL", "Redis", "Celery",
            "Docker", "Terraform", "AWS", "Python", "TypeScript",
            "pytest", "Jest", "GitHub Actions"
        ]

        found_tech = []
        context_lower = context.lower()

        for tech in tech_keywords:
            if tech.lower() in context_lower:
                found_tech.append(tech)

        return found_tech

    def _extract_patterns(self, context: str) -> List[str]:
        """Extrae patrones de diseño mencionados."""
        pattern_keywords = [
            "microservices", "monolith", "event-driven",
            "REST", "GraphQL", "CQRS", "DDD"
        ]

        found_patterns = []
        context_lower = context.lower()

        for pattern in pattern_keywords:
            if pattern.lower() in context_lower:
                found_patterns.append(pattern)

        return found_patterns

    def _generate_user_story(
        self,
        feature_request: str,
        context_analysis: Dict[str, Any],
        backlog: List[Dict]
    ) -> Dict[str, Any]:
        """
        Genera user story completa usando LLM.

        Args:
            feature_request: Request original
            context_analysis: Análisis de contexto
            backlog: Backlog actual

        Returns:
            User story estructurada
        """
        # TODO: Integrar LLM real (Anthropic/OpenAI)
        # Por ahora, implementación simplificada

        # Extraer título simple
        title = self._extract_title(feature_request)

        # Generar descripción en formato user story
        description = f"""# User Story

**Como** usuario del sistema IACT
**Quiero** {feature_request.strip()}
**Para** mejorar la funcionalidad y experiencia del sistema

## Descripción Detallada

{feature_request}

## Contexto Técnico

Tech stack detectado: {', '.join(context_analysis.get('tech_stack', [])) or 'No especificado'}
Patrones: {', '.join(context_analysis.get('patterns', [])) or 'No especificado'}
"""

        # Generar acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(feature_request)

        # Estimar story points (simplificado)
        story_points = self._estimate_story_points(
            feature_request,
            acceptance_criteria
        )

        # Determinar prioridad
        priority = self._determine_priority(feature_request)

        # Identificar requisitos técnicos
        technical_requirements = self._identify_technical_requirements(
            feature_request,
            context_analysis
        )

        # Identificar dependencias
        dependencies = self._identify_dependencies(feature_request, backlog)

        return {
            "title": title,
            "description": description,
            "acceptance_criteria": acceptance_criteria,
            "story_points": story_points,
            "priority": priority,
            "technical_requirements": technical_requirements,
            "dependencies": dependencies
        }

    def _extract_title(self, feature_request: str) -> str:
        """Extrae/genera un título conciso."""
        # Tomar primera oración o primeras 60 caracteres
        first_line = feature_request.split('\n')[0].strip()

        if len(first_line) > 60:
            title = first_line[:57] + "..."
        else:
            title = first_line

        return title

    def _generate_acceptance_criteria(self, feature_request: str) -> List[str]:
        """Genera acceptance criteria básicos."""
        # Simplificado - en producción usar LLM
        criteria = [
            "El feature está implementado según especificación",
            "Tests unitarios cubren funcionalidad principal",
            "Tests de integración validan flujo completo",
            "Documentación está actualizada",
            "Code review aprobado por arquitecto"
        ]

        # Agregar criterios específicos si detectamos palabras clave
        if "autenticación" in feature_request.lower() or "auth" in feature_request.lower():
            criteria.insert(0, "Sistema de autenticación funciona correctamente")
            criteria.insert(1, "Validación de credenciales implementada")

        if "api" in feature_request.lower():
            criteria.insert(0, "API endpoints documentados en OpenAPI/Swagger")
            criteria.insert(1, "Validación de inputs implementada")

        return criteria

    def _estimate_story_points(
        self,
        feature_request: str,
        acceptance_criteria: List[str]
    ) -> int:
        """
        Estima story points basándose en complejidad.

        Fibonacci: 1, 2, 3, 5, 8, 13, 21
        """
        # Heurística simple (en producción usar LLM)
        complexity_score = 0

        # Longitud del request
        if len(feature_request) > 500:
            complexity_score += 3
        elif len(feature_request) > 200:
            complexity_score += 2
        else:
            complexity_score += 1

        # Número de acceptance criteria
        if len(acceptance_criteria) > 10:
            complexity_score += 5
        elif len(acceptance_criteria) > 5:
            complexity_score += 3
        else:
            complexity_score += 1

        # Keywords que indican complejidad
        complex_keywords = [
            "integración", "migración", "arquitectura", "security",
            "performance", "refactor", "legacy"
        ]
        for keyword in complex_keywords:
            if keyword in feature_request.lower():
                complexity_score += 2

        # Mapear a Fibonacci
        if complexity_score <= 2:
            return 1
        elif complexity_score <= 4:
            return 2
        elif complexity_score <= 6:
            return 3
        elif complexity_score <= 9:
            return 5
        elif complexity_score <= 13:
            return 8
        elif complexity_score <= 18:
            return 13
        else:
            return 21

    def _determine_priority(self, feature_request: str) -> str:
        """
        Determina prioridad del feature.

        P0: Critical
        P1: High
        P2: Medium
        P3: Low
        """
        request_lower = feature_request.lower()

        # P0: Critical keywords
        if any(kw in request_lower for kw in ["critical", "security", "vulnerabilidad", "crash", "down"]):
            return "P0"

        # P1: High priority
        if any(kw in request_lower for kw in ["urgent", "blocker", "important", "compliance"]):
            return "P1"

        # P3: Low priority
        if any(kw in request_lower for kw in ["nice to have", "enhancement", "refactor", "cleanup"]):
            return "P3"

        # Default: P2 Medium
        return "P2"

    def _identify_technical_requirements(
        self,
        feature_request: str,
        context_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identifica requisitos técnicos."""
        requirements = []

        request_lower = feature_request.lower()

        # Backend requirements
        if "api" in request_lower or "backend" in request_lower:
            requirements.append("Django REST API endpoint")
            requirements.append("Serializers y validación")
            requirements.append("Tests de API (pytest)")

        # Frontend requirements
        if "ui" in request_lower or "frontend" in request_lower or "interface" in request_lower:
            requirements.append("React component")
            requirements.append("State management")
            requirements.append("Tests de componente (Jest)")

        # Database
        if "database" in request_lower or "modelo" in request_lower or "model" in request_lower:
            requirements.append("Django models")
            requirements.append("Migrations")
            requirements.append("Database indexes")

        # Authentication/Authorization
        if "auth" in request_lower or "permisos" in request_lower:
            requirements.append("Authentication/Authorization")
            requirements.append("Permission checks")
            requirements.append("Audit logging")

        return requirements

    def _identify_dependencies(
        self,
        feature_request: str,
        backlog: List[Dict]
    ) -> List[str]:
        """Identifica dependencias con otros issues."""
        dependencies = []

        # Análisis simplificado
        # En producción, usar LLM para analizar similitud semántica con backlog

        request_lower = feature_request.lower()

        # Dependencias comunes
        if "api" in request_lower and backlog:
            dependencies.append("Requiere API base configurada")

        if "auth" in request_lower or "login" in request_lower:
            dependencies.append("Requiere sistema de autenticación")

        return dependencies

    def _format_github_issue(
        self,
        description: str,
        acceptance_criteria: List[str],
        technical_requirements: List[str],
        story_points: int,
        priority: str,
        dependencies: List[str]
    ) -> str:
        """
        Formatea issue para GitHub.

        Args:
            description: Descripción completa
            acceptance_criteria: Lista de criterios de aceptación
            technical_requirements: Requisitos técnicos
            story_points: Estimación
            priority: Prioridad
            dependencies: Dependencias

        Returns:
            Markdown formateado para GitHub Issue
        """
        issue = f"""{description}

## Acceptance Criteria

"""
        for i, criterion in enumerate(acceptance_criteria, 1):
            issue += f"{i}. [ ] {criterion}\n"

        issue += f"""
## Technical Requirements

"""
        for req in technical_requirements:
            issue += f"- {req}\n"

        if dependencies:
            issue += f"""
## Dependencies

"""
            for dep in dependencies:
                issue += f"- {dep}\n"

        issue += f"""
## Estimation

**Story Points**: {story_points}
**Priority**: {priority}

## Labels

`feature` `{priority.lower()}` `story-points-{story_points}`

---

*Generado por SDLCPlannerAgent*
*Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return issue
