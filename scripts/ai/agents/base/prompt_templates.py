#!/usr/bin/env python3
"""
Prompt Templates System

Implements structured, reusable prompt templates with variables for systematic
AI agent prompting. Enables consistency, maintainability, and quality control.

Based on: PromptOps best practices and systematic prompt engineering
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import re
from pathlib import Path


class TemplateType(Enum):
    """Type of prompt template."""
    GATE_VALIDATION = "gate_validation"
    CODE_REVIEW = "code_review"
    TEST_GENERATION = "test_generation"
    ANALYSIS = "analysis"
    VERIFICATION = "verification"
    CHAIN_STEP = "chain_step"


class OutputFormat(Enum):
    """Expected output format."""
    JSON = "json"
    MARKDOWN = "markdown"
    STRUCTURED_TEXT = "structured_text"
    PYTHON_CODE = "python_code"
    BOOLEAN = "boolean"


@dataclass
class TemplateVariable:
    """Variable within a prompt template."""
    name: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    validation: Optional[Callable[[Any], bool]] = None
    example: Optional[str] = None


@dataclass
class PromptTemplate:
    """Structured prompt template with variables."""
    name: str
    template_type: TemplateType
    description: str
    system_prompt: str
    user_prompt_template: str
    variables: List[TemplateVariable]
    output_format: OutputFormat
    constraints: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    post_processing: Optional[Callable[[str], Any]] = None


class PromptTemplateEngine:
    """
    Engine for managing and rendering prompt templates.

    Features:
    - Variable substitution with validation
    - Template inheritance
    - Constraint enforcement
    - Output format specification
    - Example injection
    """

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._register_builtin_templates()

    def _register_builtin_templates(self):
        """Register built-in templates for common tasks."""
        # Gate validation template (with anti-hallucination patterns)
        self.register_template(PromptTemplate(
            name="gate_validation",
            template_type=TemplateType.GATE_VALIDATION,
            description="Template for gate agents validating code/config",
            system_prompt="""You are a specialized validation gate agent.
Your role is to analyze code/configuration and identify violations of project restrictions.

You must:
- Be thorough and catch all violations
- Provide specific line numbers and file paths
- Explain WHY each violation is problematic
- Suggest corrections when applicable

Project Restrictions:
{project_restrictions}

VALIDACIÓN ANTI-ALUCINACIÓN:
- Basarte SOLO en el código proporcionado
- No inventar violaciones que no existan en el código
- Citar líneas específicas para cada violación
- Si no estás seguro, indicar: "Requiere verificación: [aspecto específico]"

NUNCA inventes:
- Nombres de variables que no están en el código
- Números de línea aproximados
- Configuraciones que no ves explícitamente
- Referencias a archivos externos sin confirmar
""",
            user_prompt_template="""Validate the following {target_type}:

Target: {target_path}
Content:
```
{target_content}
```

Specific checks:
{checks_to_perform}

Report any violations found. For each violation provide:
1. Type of violation
2. Exact location (file:line)
3. Description of the issue
4. Impact/risk level
5. Suggested fix

VALIDACIÓN REQUERIDA:
- Citar líneas específicas del código proporcionado
- Basar conclusiones solo en el contenido visible
- Indicar explícitamente si se requiere verificación adicional

Nota: Las violaciones deben ser verificables en el código proporcionado antes de reportar.
""",
            variables=[
                TemplateVariable(
                    name="project_restrictions",
                    description="List of project restrictions to enforce",
                    required=True,
                    example="- NO Redis for sessions\n- NO emojis"
                ),
                TemplateVariable(
                    name="target_type",
                    description="Type of target being validated",
                    required=True,
                    example="Python file"
                ),
                TemplateVariable(
                    name="target_path",
                    description="Path to the file being validated",
                    required=True,
                    example="api/callcentersite/settings.py"
                ),
                TemplateVariable(
                    name="target_content",
                    description="Content to validate",
                    required=True
                ),
                TemplateVariable(
                    name="checks_to_perform",
                    description="Specific validation checks to run",
                    required=True,
                    example="- Check for Redis usage\n- Check for email config"
                )
            ],
            output_format=OutputFormat.STRUCTURED_TEXT,
            constraints=[
                "Must report line numbers",
                "Must categorize violations by severity",
                "Must be deterministic (same input = same output)"
            ]
        ))

        # Test generation template (with anti-hallucination patterns)
        self.register_template(PromptTemplate(
            name="test_generation",
            template_type=TemplateType.TEST_GENERATION,
            description="Template for generating test cases",
            system_prompt="""You are a test generation specialist using TDD methodology.

Your role is to generate comprehensive test cases that:
- Cover happy path, edge cases, and error cases
- Follow pytest conventions
- Include clear assertions with messages
- Use appropriate mocking for dependencies
- Follow project testing standards

Agent Type: {agent_type}
Testing Framework: pytest

VALIDACIÓN ANTI-ALUCINACIÓN:
- Generar código sintácticamente correcto para pytest
- No inventar APIs o funciones que no existen
- Basar imports en librerías estándar conocidas
- Si una función específica no está definida, indicar: "# TODO: Definir función [nombre]"

NUNCA inventes:
- Métodos de librerías que no existen
- Sintaxis incorrecta de pytest
- Configuraciones de mocking inexistentes
- Imports de módulos no estándar sin verificar
""",
            user_prompt_template="""Generate test cases for the following component:

Component: {component_name}
Type: {component_type}

Requirements:
{requirements}

Expected Behavior:
{expected_behavior}

Generate complete test methods including:
1. Setup code (fixtures, mocks)
2. Test execution
3. Assertions with descriptive messages
4. Teardown if needed

Follow this structure:
```python
def test_{test_name}(self, {fixtures}):
    \"\"\"Test: {description}\"\"\"
    # Setup
    {setup_code}

    # Execute
    {execution_code}

    # Assert
    {assertions}
```

VALIDACIÓN REQUERIDA:
- Código sintácticamente válido para pytest
- Imports correctos y verificables
- Assertions con mensajes descriptivos
- Manejo de mocks apropiado

Nota: Validar sintaxis y funcionalidad en entorno de desarrollo antes de usar en producción.
""",
            variables=[
                TemplateVariable(
                    name="agent_type",
                    description="Type of agent (gate/chain)",
                    required=True,
                    example="gate"
                ),
                TemplateVariable(
                    name="component_name",
                    description="Name of component being tested",
                    required=True,
                    example="DBRouterGate"
                ),
                TemplateVariable(
                    name="component_type",
                    description="Type of component",
                    required=True,
                    example="validation gate"
                ),
                TemplateVariable(
                    name="requirements",
                    description="Requirements to test",
                    required=True
                ),
                TemplateVariable(
                    name="expected_behavior",
                    description="Expected behavior specification",
                    required=True
                )
            ],
            output_format=OutputFormat.PYTHON_CODE,
            constraints=[
                "Must follow pytest conventions",
                "Must include docstrings",
                "Must have clear assertion messages"
            ]
        ))

        # Code review template (with anti-hallucination patterns)
        self.register_template(PromptTemplate(
            name="code_review",
            template_type=TemplateType.CODE_REVIEW,
            description="Template for code review analysis",
            system_prompt="""You are an expert code reviewer.

Review focus areas:
{review_focus}

Project restrictions to check:
{project_restrictions}

Provide constructive feedback on:
- Code quality and maintainability
- Security vulnerabilities
- Performance issues
- Compliance with project restrictions
- Best practices violations

VALIDACIÓN ANTI-ALUCINACIÓN:
- Basar comentarios SOLO en el código proporcionado
- Citar líneas específicas para cada issue
- No asumir comportamiento no visible en el código
- Indicar "Requiere verificación" si algo no está claro

NUNCA inventes:
- Vulnerabilidades sin evidencia en el código
- Referencias a archivos externos no proporcionados
- Comportamiento de librerías sin verificar
- Métricas de performance sin mediciones reales
""",
            user_prompt_template="""Review the following code:

File: {file_path}
Language: {language}

Code:
```{language}
{code_content}
```

Context:
{context}

Provide review in this format:

## Summary
[High-level assessment]

## Issues Found
[List each issue with severity: HIGH/MEDIUM/LOW and specific line numbers]

## Security Concerns
[Security-related findings with evidence from code]

## Suggestions
[Specific improvement recommendations based on visible code]

## Compliance
[Project restrictions compliance check with citations]

VALIDACIÓN REQUERIDA:
- Cada issue debe citar línea específica
- Evidencia basada en código proporcionado
- Indicar explícitamente si se requiere información adicional

Nota: Verificar comportamiento de librerías externas en documentación oficial antes de reportar como issues definitivos.
""",
            variables=[
                TemplateVariable(
                    name="review_focus",
                    description="Specific aspects to focus on",
                    required=True,
                    example="Security, Performance, Django best practices"
                ),
                TemplateVariable(
                    name="project_restrictions",
                    description="Project-specific restrictions",
                    required=True
                ),
                TemplateVariable(
                    name="file_path",
                    description="Path to file being reviewed",
                    required=True
                ),
                TemplateVariable(
                    name="language",
                    description="Programming language",
                    required=True,
                    example="python"
                ),
                TemplateVariable(
                    name="code_content",
                    description="Code to review",
                    required=True
                ),
                TemplateVariable(
                    name="context",
                    description="Additional context",
                    required=False,
                    default="No additional context provided"
                )
            ],
            output_format=OutputFormat.MARKDOWN,
            constraints=[
                "Must categorize by severity",
                "Must be specific with line numbers",
                "Must suggest concrete fixes"
            ]
        ))

        # Analysis template
        self.register_template(PromptTemplate(
            name="code_analysis",
            template_type=TemplateType.ANALYSIS,
            description="Template for code analysis and understanding",
            system_prompt="""You are a code analysis specialist.

Your role is to analyze code and provide detailed insights on:
- Architecture and design patterns
- Data flow
- Dependencies
- Complexity
- Potential issues

Analysis type: {analysis_type}
""",
            user_prompt_template="""Analyze the following code:

File: {file_path}
Purpose: {purpose}

Code:
```
{code_content}
```

Focus on:
{focus_areas}

Provide analysis in this structure:

1. Overview
   - Purpose and functionality
   - Key components

2. Architecture
   - Design patterns used
   - Component interactions

3. Data Flow
   - Input sources
   - Processing steps
   - Output destinations

4. Dependencies
   - External dependencies
   - Internal dependencies

5. Complexity Analysis
   - Cyclomatic complexity
   - Areas of concern

6. Recommendations
   - Improvements
   - Refactoring suggestions
""",
            variables=[
                TemplateVariable(
                    name="analysis_type",
                    description="Type of analysis to perform",
                    required=True,
                    example="architecture"
                ),
                TemplateVariable(
                    name="file_path",
                    description="Path to file",
                    required=True
                ),
                TemplateVariable(
                    name="purpose",
                    description="Purpose of the code",
                    required=False,
                    default="Unknown"
                ),
                TemplateVariable(
                    name="code_content",
                    description="Code to analyze",
                    required=True
                ),
                TemplateVariable(
                    name="focus_areas",
                    description="Specific areas to focus on",
                    required=True,
                    example="- Database interactions\n- Permission checks"
                )
            ],
            output_format=OutputFormat.MARKDOWN
        ))

    def register_template(self, template: PromptTemplate):
        """Register a new template."""
        self.templates[template.name] = template
        print(f"[PromptTemplates] Registered template: {template.name}")

    def render(
        self,
        template_name: str,
        variables: Dict[str, Any],
        include_examples: bool = False
    ) -> Dict[str, str]:
        """
        Render a template with provided variables.

        Args:
            template_name: Name of template to use
            variables: Variable values
            include_examples: Whether to include examples in prompt

        Returns:
            Dict with 'system' and 'user' prompts
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]

        # Validate variables
        self._validate_variables(template, variables)

        # Fill in defaults for missing optional variables
        complete_vars = self._complete_variables(template, variables)

        # Render system prompt
        system_prompt = self._render_string(template.system_prompt, complete_vars)

        # Render user prompt
        user_prompt = self._render_string(template.user_prompt_template, complete_vars)

        # Add examples if requested
        if include_examples and template.examples:
            examples_text = self._format_examples(template.examples)
            user_prompt = f"{examples_text}\n\n{user_prompt}"

        # Add constraints
        if template.constraints:
            constraints_text = "\n".join(f"- {c}" for c in template.constraints)
            user_prompt += f"\n\nConstraints:\n{constraints_text}"

        # Add output format specification
        user_prompt += f"\n\nOutput format: {template.output_format.value}"

        return {
            "system": system_prompt,
            "user": user_prompt,
            "template": template
        }

    def _validate_variables(self, template: PromptTemplate, variables: Dict[str, Any]):
        """Validate provided variables against template requirements."""
        # Check required variables
        for var in template.variables:
            if var.required and var.name not in variables:
                raise ValueError(
                    f"Required variable '{var.name}' missing for template '{template.name}'"
                )

            # Run custom validation if provided
            if var.name in variables and var.validation:
                if not var.validation(variables[var.name]):
                    raise ValueError(
                        f"Validation failed for variable '{var.name}'"
                    )

    def _complete_variables(
        self,
        template: PromptTemplate,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fill in defaults for missing optional variables."""
        complete = variables.copy()

        for var in template.variables:
            if var.name not in complete and var.default is not None:
                complete[var.name] = var.default

        return complete

    def _render_string(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render a template string with variables."""
        result = template_str

        # Replace {variable} with values
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(var_value))

        return result

    def _format_examples(self, examples: List[Dict[str, str]]) -> str:
        """Format examples for inclusion in prompt."""
        formatted = ["Examples:"]

        for i, example in enumerate(examples, 1):
            formatted.append(f"\nExample {i}:")
            for key, value in example.items():
                formatted.append(f"{key}:")
                formatted.append(f"{value}")

        return "\n".join(formatted)

    def list_templates(self) -> List[str]:
        """List all registered templates."""
        return list(self.templates.keys())

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get detailed information about a template."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]

        return {
            "name": template.name,
            "type": template.template_type.value,
            "description": template.description,
            "output_format": template.output_format.value,
            "variables": [
                {
                    "name": v.name,
                    "description": v.description,
                    "required": v.required,
                    "default": v.default,
                    "example": v.example
                }
                for v in template.variables
            ],
            "constraints": template.constraints,
            "examples_count": len(template.examples)
        }


def main():
    """Example usage of Prompt Templates."""
    print("Prompt Templates System - Example\n")
    print("=" * 70)

    engine = PromptTemplateEngine()

    # Example 1: Gate validation
    print("\n[Example 1] Gate Validation Template\n")

    gate_vars = {
        "project_restrictions": "- NO Redis for sessions\n- NO emojis\n- IVR database is READ-ONLY",
        "target_type": "Python settings file",
        "target_path": "api/callcentersite/settings.py",
        "target_content": """
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
""",
        "checks_to_perform": "- Check for Redis usage\n- Check for email configuration"
    }

    prompts = engine.render("gate_validation", gate_vars)
    print("System Prompt:")
    print(prompts["system"])
    print("\nUser Prompt:")
    print(prompts["user"][:300] + "...")

    # Example 2: Test generation
    print("\n" + "=" * 70)
    print("[Example 2] Test Generation Template\n")

    test_vars = {
        "agent_type": "gate",
        "component_name": "DBRouterGate",
        "component_type": "validation gate",
        "requirements": "Validate that db_for_write never returns 'ivr'",
        "expected_behavior": "Should detect any code that attempts to write to IVR database"
    }

    prompts = engine.render("test_generation", test_vars)
    print("Template rendered successfully")
    print(f"System prompt length: {len(prompts['system'])} chars")
    print(f"User prompt length: {len(prompts['user'])} chars")

    # Example 3: List all templates
    print("\n" + "=" * 70)
    print("[Example 3] Available Templates\n")

    templates = engine.list_templates()
    print(f"Total templates: {len(templates)}\n")

    for name in templates:
        info = engine.get_template_info(name)
        print(f"Template: {name}")
        print(f"  Type: {info['type']}")
        print(f"  Description: {info['description']}")
        print(f"  Variables: {len(info['variables'])}")
        print(f"  Output: {info['output_format']}")
        print()


if __name__ == "__main__":
    main()
