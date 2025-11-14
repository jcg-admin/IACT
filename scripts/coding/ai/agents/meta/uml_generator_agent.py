#!/usr/bin/env python3
"""
UML Diagram Generator Agent

Generates UML diagrams from requirements and code.

Supports both heuristic-based generation (using AST parsing)
and LLM-based generation for higher quality diagrams.

Diagram Types Supported:
- Class diagrams (from code structure)
- Sequence diagrams (from interactions)
- Component diagrams (from architecture)
- Activity diagrams (from workflows)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import ast
import re
import logging

# Import DiagramType from validation agent (shared enum)
from scripts.coding.ai.agents.meta.uml_validation_agent import DiagramType

# Import LLMGenerator for AI-powered generation
try:
    from scripts.coding.ai.generators.llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logging.warning("LLMGenerator not available, will use heuristics only")

logger = logging.getLogger(__name__)

# Constants
GENERATION_METHOD_LLM = "llm"
GENERATION_METHOD_HEURISTIC = "heuristic"


@dataclass
class UMLGenerationResult:
    """Result of UML diagram generation."""
    success: bool
    diagram_type: DiagramType
    plantuml_code: str
    generation_method: str  # "heuristic" or "llm"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'diagram_type': self.diagram_type.value,
            'plantuml_code': self.plantuml_code,
            'generation_method': self.generation_method,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


class UMLGeneratorAgent:
    """
    Agent that generates UML diagrams from requirements and code.

    Supports:
    1. Heuristic generation using AST parsing
    2. LLM-based generation for higher quality
    3. Automatic fallback to heuristics if LLM fails
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.

        Args:
            config: Configuration dict with optional keys:
                - llm_provider: "anthropic" or "openai"
                - model: Model name (e.g., "claude-sonnet-4-5-20250929")
                - use_llm: Boolean to enable/disable LLM usage
        """
        self.name = "UMLGeneratorAgent"
        self.config = config or {}
        self.llm_generator = None

        # Initialize LLMGenerator if configured and available
        if self.config and LLM_AVAILABLE:
            try:
                # Initialize LLMGenerator (API key validation happens at runtime)
                self.llm_generator = LLMGenerator(config=self.config)
                llm_provider = self.config.get('llm_provider', 'anthropic')
                logger.info(f"LLMGenerator initialized with {llm_provider}")
            except Exception as e:
                logger.error(f"Failed to initialize LLMGenerator: {e}")
                self.llm_generator = None
        elif self.config and not LLM_AVAILABLE:
            logger.warning("LLM configuration provided but LLMGenerator not available")

    def generate_class_diagram(
        self,
        code: Optional[str] = None,
        requirements: Optional[str] = None
    ) -> UMLGenerationResult:
        """
        Generate a class diagram from code or requirements.

        Args:
            code: Python code to analyze
            requirements: Text requirements describing classes

        Returns:
            UMLGenerationResult with PlantUML code
        """
        # Validate input
        input_text = code or requirements
        if not input_text or not input_text.strip():
            return UMLGenerationResult(
                success=False,
                diagram_type=DiagramType.CLASS,
                plantuml_code="",
                generation_method=GENERATION_METHOD_HEURISTIC,
                error_message="Empty input: code or requirements required"
            )

        # Determine generation method
        use_llm = self.config.get('use_llm', False) and self.llm_generator is not None

        if use_llm:
            try:
                result = self._generate_class_diagram_with_llm(input_text)
                # Validate LLM result
                if result and self._is_valid_plantuml(result):
                    return UMLGenerationResult(
                        success=True,
                        diagram_type=DiagramType.CLASS,
                        plantuml_code=result,
                        generation_method=GENERATION_METHOD_LLM
                    )
                else:
                    logger.warning("LLM returned invalid PlantUML, falling back to heuristics")
            except Exception as e:
                logger.error(f"LLM generation failed: {e}, falling back to heuristics")

        # Use heuristic generation
        try:
            plantuml = self._generate_class_diagram_heuristic(input_text)
            return UMLGenerationResult(
                success=True,
                diagram_type=DiagramType.CLASS,
                plantuml_code=plantuml,
                generation_method=GENERATION_METHOD_HEURISTIC
            )
        except Exception as e:
            logger.error(f"Heuristic generation failed: {e}")
            return UMLGenerationResult(
                success=False,
                diagram_type=DiagramType.CLASS,
                plantuml_code="",
                generation_method=GENERATION_METHOD_HEURISTIC,
                error_message=str(e)
            )

    def generate_sequence_diagram(
        self,
        requirements: str,
        code: Optional[str] = None
    ) -> UMLGenerationResult:
        """
        Generate a sequence diagram from interaction description.

        Args:
            requirements: Text describing interactions
            code: Optional code to analyze

        Returns:
            UMLGenerationResult with PlantUML code
        """
        # Validate input
        if not requirements or not requirements.strip():
            return UMLGenerationResult(
                success=False,
                diagram_type=DiagramType.SEQUENCE,
                plantuml_code="",
                generation_method=GENERATION_METHOD_HEURISTIC,
                error_message="Empty requirements"
            )

        # Determine generation method
        use_llm = self.config.get('use_llm', False) and self.llm_generator is not None

        if use_llm:
            try:
                result = self._generate_sequence_diagram_with_llm(requirements)
                if result and self._is_valid_plantuml(result):
                    return UMLGenerationResult(
                        success=True,
                        diagram_type=DiagramType.SEQUENCE,
                        plantuml_code=result,
                        generation_method=GENERATION_METHOD_LLM
                    )
                else:
                    logger.warning("LLM returned invalid PlantUML, falling back to heuristics")
            except Exception as e:
                logger.error(f"LLM generation failed: {e}, falling back to heuristics")

        # Use heuristic generation
        try:
            plantuml = self._generate_sequence_diagram_heuristic(requirements)
            return UMLGenerationResult(
                success=True,
                diagram_type=DiagramType.SEQUENCE,
                plantuml_code=plantuml,
                generation_method=GENERATION_METHOD_HEURISTIC
            )
        except Exception as e:
            logger.error(f"Heuristic generation failed: {e}")
            return UMLGenerationResult(
                success=False,
                diagram_type=DiagramType.SEQUENCE,
                plantuml_code="",
                generation_method=GENERATION_METHOD_HEURISTIC,
                error_message=str(e)
            )

    def generate_component_diagram(
        self,
        requirements: str,
        code: Optional[str] = None
    ) -> UMLGenerationResult:
        """
        Generate a component diagram from architecture description.

        Args:
            requirements: Text describing architecture
            code: Optional code to analyze

        Returns:
            UMLGenerationResult with PlantUML code
        """
        # Validate input
        if not requirements or not requirements.strip():
            return UMLGenerationResult(
                success=False,
                diagram_type=DiagramType.COMPONENT,
                plantuml_code="",
                generation_method=GENERATION_METHOD_HEURISTIC,
                error_message="Empty requirements"
            )

        # Determine generation method
        use_llm = self.config.get('use_llm', False) and self.llm_generator is not None

        if use_llm:
            try:
                result = self._generate_component_diagram_with_llm(requirements)
                if result and self._is_valid_plantuml(result):
                    return UMLGenerationResult(
                        success=True,
                        diagram_type=DiagramType.COMPONENT,
                        plantuml_code=result,
                        generation_method=GENERATION_METHOD_LLM
                    )
                else:
                    logger.warning("LLM returned invalid PlantUML, falling back to heuristics")
            except Exception as e:
                logger.error(f"LLM generation failed: {e}, falling back to heuristics")

        # Use heuristic generation
        try:
            plantuml = self._generate_component_diagram_heuristic(requirements)
            return UMLGenerationResult(
                success=True,
                diagram_type=DiagramType.COMPONENT,
                plantuml_code=plantuml,
                generation_method=GENERATION_METHOD_HEURISTIC
            )
        except Exception as e:
            logger.error(f"Heuristic generation failed: {e}")
            return UMLGenerationResult(
                success=False,
                diagram_type=DiagramType.COMPONENT,
                plantuml_code="",
                generation_method=GENERATION_METHOD_HEURISTIC,
                error_message=str(e)
            )

    def generate_activity_diagram(
        self,
        requirements: str
    ) -> UMLGenerationResult:
        """
        Generate an activity diagram from workflow description.

        Args:
            requirements: Text describing workflow

        Returns:
            UMLGenerationResult with PlantUML code
        """
        # Validate input
        if not requirements or not requirements.strip():
            return UMLGenerationResult(
                success=False,
                diagram_type=DiagramType.ACTIVITY,
                plantuml_code="",
                generation_method=GENERATION_METHOD_HEURISTIC,
                error_message="Empty requirements"
            )

        # Determine generation method
        use_llm = self.config.get('use_llm', False) and self.llm_generator is not None

        if use_llm:
            try:
                result = self._generate_activity_diagram_with_llm(requirements)
                if result and self._is_valid_plantuml(result):
                    return UMLGenerationResult(
                        success=True,
                        diagram_type=DiagramType.ACTIVITY,
                        plantuml_code=result,
                        generation_method=GENERATION_METHOD_LLM
                    )
                else:
                    logger.warning("LLM returned invalid PlantUML, falling back to heuristics")
            except Exception as e:
                logger.error(f"LLM generation failed: {e}, falling back to heuristics")

        # Use heuristic generation
        try:
            plantuml = self._generate_activity_diagram_heuristic(requirements)
            return UMLGenerationResult(
                success=True,
                diagram_type=DiagramType.ACTIVITY,
                plantuml_code=plantuml,
                generation_method=GENERATION_METHOD_HEURISTIC
            )
        except Exception as e:
            logger.error(f"Heuristic generation failed: {e}")
            return UMLGenerationResult(
                success=False,
                diagram_type=DiagramType.ACTIVITY,
                plantuml_code="",
                generation_method=GENERATION_METHOD_HEURISTIC,
                error_message=str(e)
            )

    # Heuristic Generation Methods

    def _generate_class_diagram_heuristic(self, input_text: str) -> str:
        """
        Generate class diagram using AST parsing.

        Args:
            input_text: Python code or requirements

        Returns:
            PlantUML code
        """
        plantuml_lines = ["@startuml"]

        # Try to parse as Python code
        try:
            tree = ast.parse(input_text)
            classes = self._extract_classes_from_ast(tree)

            for class_info in classes:
                plantuml_lines.append(f"class {class_info['name']} {{")

                # Add attributes
                for attr in class_info.get('attributes', []):
                    plantuml_lines.append(f"    +{attr}")

                # Add methods
                for method in class_info.get('methods', []):
                    plantuml_lines.append(f"    +{method}()")

                plantuml_lines.append("}")

                # Add inheritance
                if class_info.get('bases'):
                    for base in class_info['bases']:
                        plantuml_lines.append(f"{base} <|-- {class_info['name']}")

        except SyntaxError:
            # Not valid Python, try to extract from requirements text
            classes = self._extract_classes_from_text(input_text)
            for class_name in classes:
                plantuml_lines.append(f"class {class_name} {{")
                plantuml_lines.append("}")

        plantuml_lines.append("@enduml")
        return "\n".join(plantuml_lines)

    def _generate_sequence_diagram_heuristic(self, requirements: str) -> str:
        """
        Generate sequence diagram from interaction description.

        Args:
            requirements: Text describing interactions

        Returns:
            PlantUML code
        """
        plantuml_lines = ["@startuml"]

        # Extract participants
        participants = self._extract_participants_from_text(requirements)
        for participant in participants:
            plantuml_lines.append(f"participant {participant}")

        # Extract interactions (simple heuristic)
        lines = requirements.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for patterns like "X calls Y" or "X -> Y"
            if ' calls ' in line.lower() or ' call ' in line.lower():
                parts = re.split(r'\s+calls?\s+', line, flags=re.IGNORECASE)
                if len(parts) == 2:
                    sender = parts[0].strip()
                    receiver = parts[1].strip()
                    plantuml_lines.append(f"{sender} -> {receiver}: request")
            elif ' receives ' in line.lower():
                parts = re.split(r'\s+receives?\s+', line, flags=re.IGNORECASE)
                if len(parts) == 2:
                    receiver = parts[0].strip()
                    sender = parts[1].split()[-1] if parts[1].split() else "System"
                    plantuml_lines.append(f"{sender} -> {receiver}: message")
            elif ' returns ' in line.lower():
                parts = re.split(r'\s+returns?\s+', line, flags=re.IGNORECASE)
                if len(parts) >= 1:
                    sender = parts[0].strip().split()[-1] if parts[0].strip().split() else "System"
                    plantuml_lines.append(f"{sender} --> User: response")

        # If no interactions found, create a simple flow
        if len(plantuml_lines) == 1 + len(participants):
            if len(participants) >= 2:
                plantuml_lines.append(f"{participants[0]} -> {participants[1]}: request")
                plantuml_lines.append(f"{participants[1]} --> {participants[0]}: response")

        plantuml_lines.append("@enduml")
        return "\n".join(plantuml_lines)

    def _generate_component_diagram_heuristic(self, requirements: str) -> str:
        """
        Generate component diagram from architecture description.

        Args:
            requirements: Text describing architecture

        Returns:
            PlantUML code
        """
        plantuml_lines = ["@startuml"]

        # Extract components from text
        components = self._extract_components_from_text(requirements)

        for component in components:
            # Skip IACT-restricted components
            if 'redis' in component.lower():
                continue
            if 'email' in component.lower() and 'service' in component.lower():
                continue

            plantuml_lines.append(f"component [{component}]")

        # Add common relationships
        if len(components) >= 2:
            # Frontend -> Backend pattern
            frontend = next((c for c in components if 'frontend' in c.lower() or 'ui' in c.lower()), None)
            backend = next((c for c in components if 'api' in c.lower() or 'backend' in c.lower() or 'gateway' in c.lower()), None)
            if frontend and backend:
                plantuml_lines.append(f"[{frontend}] --> [{backend}]")

            # Backend -> Database pattern
            database = next((c for c in components if 'database' in c.lower() or 'db' in c.lower()), None)
            if backend and database:
                plantuml_lines.append(f"[{backend}] --> [{database}]")

        plantuml_lines.append("@enduml")
        return "\n".join(plantuml_lines)

    def _generate_activity_diagram_heuristic(self, requirements: str) -> str:
        """
        Generate activity diagram from workflow description.

        Args:
            requirements: Text describing workflow

        Returns:
            PlantUML code
        """
        plantuml_lines = ["@startuml", "start"]

        # Extract steps from workflow
        lines = requirements.split('\n')
        for line in lines:
            line = line.strip()
            if not line or ':' in line[:20]:  # Skip titles
                continue

            # Remove numbering (1., 2., etc.)
            line = re.sub(r'^\d+\.\s*', '', line)

            # Check for conditional logic
            if line.lower().startswith('if '):
                condition = line[3:].strip()
                plantuml_lines.append(f"if ({condition}) then (yes)")
            elif line.lower().startswith('else'):
                plantuml_lines.append("else (no)")
            elif line:
                # Regular activity
                plantuml_lines.append(f":{line};")

        plantuml_lines.append("stop")
        plantuml_lines.append("@enduml")
        return "\n".join(plantuml_lines)

    # LLM Generation Methods

    def _generate_class_diagram_with_llm(self, input_text: str) -> str:
        """Generate class diagram using LLM."""
        prompt = f"""Generate a PlantUML class diagram from the following code or requirements.

INPUT:
```
{input_text}
```

REQUIREMENTS:
1. Generate valid PlantUML syntax
2. Include @startuml and @enduml tags
3. Extract classes with attributes and methods
4. Show relationships between classes
5. Use proper UML notation
6. DO NOT include Redis or Email services (IACT constraints)

RESPONSE FORMAT:
Return ONLY the PlantUML code, no explanation.

Example:
@startuml
class User {{
    +id: int
    +name: string
    +getProfile()
}}
@enduml

Generate the PlantUML class diagram:"""

        response = self.llm_generator._call_llm(prompt)
        return self._extract_plantuml_from_response(response)

    def _generate_sequence_diagram_with_llm(self, requirements: str) -> str:
        """Generate sequence diagram using LLM."""
        prompt = f"""Generate a PlantUML sequence diagram from the following interaction description.

INTERACTION:
```
{requirements}
```

REQUIREMENTS:
1. Generate valid PlantUML syntax
2. Include @startuml and @enduml tags
3. Identify participants
4. Show message flows with arrows (->)
5. Include return messages (-->)
6. DO NOT include Redis or Email services (IACT constraints)

RESPONSE FORMAT:
Return ONLY the PlantUML code, no explanation.

Example:
@startuml
participant User
participant System

User -> System: request
System --> User: response
@enduml

Generate the PlantUML sequence diagram:"""

        response = self.llm_generator._call_llm(prompt)
        return self._extract_plantuml_from_response(response)

    def _generate_component_diagram_with_llm(self, requirements: str) -> str:
        """Generate component diagram using LLM."""
        prompt = f"""Generate a PlantUML component diagram from the following architecture description.

ARCHITECTURE:
```
{requirements}
```

REQUIREMENTS:
1. Generate valid PlantUML syntax
2. Include @startuml and @enduml tags
3. Identify system components
4. Show dependencies between components
5. Use component notation: component [Name]
6. DO NOT include Redis or Email services (IACT constraints - these are NOT allowed)

RESPONSE FORMAT:
Return ONLY the PlantUML code, no explanation.

Example:
@startuml
component [Frontend]
component [API Gateway]
database [Database]

[Frontend] --> [API Gateway]
[API Gateway] --> [Database]
@enduml

Generate the PlantUML component diagram:"""

        response = self.llm_generator._call_llm(prompt)
        return self._extract_plantuml_from_response(response)

    def _generate_activity_diagram_with_llm(self, requirements: str) -> str:
        """Generate activity diagram using LLM."""
        prompt = f"""Generate a PlantUML activity diagram from the following workflow description.

WORKFLOW:
```
{requirements}
```

REQUIREMENTS:
1. Generate valid PlantUML syntax
2. Include @startuml and @enduml tags
3. Start with 'start' and end with 'stop'
4. Show activities with :activity;
5. Include decision points with if/then/else
6. Show workflow flow

RESPONSE FORMAT:
Return ONLY the PlantUML code, no explanation.

Example:
@startuml
start
:Enter credentials;
if (Valid?) then (yes)
    :Create session;
else (no)
    :Show error;
endif
stop
@enduml

Generate the PlantUML activity diagram:"""

        response = self.llm_generator._call_llm(prompt)
        return self._extract_plantuml_from_response(response)

    # Helper Methods

    def _extract_classes_from_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class information from AST."""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'attributes': [],
                    'methods': [],
                    'bases': [base.id for base in node.bases if isinstance(base, ast.Name)]
                }

                # Extract methods and attributes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info['methods'].append(item.name)

                        # Extract attributes from __init__
                        if item.name == '__init__':
                            for stmt in ast.walk(item):
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute):
                                            if isinstance(target.value, ast.Name) and target.value.id == 'self':
                                                class_info['attributes'].append(target.attr)

                classes.append(class_info)

        return classes

    def _extract_classes_from_text(self, text: str) -> List[str]:
        """Extract class names from text requirements."""
        classes = []

        # Look for patterns like "User entity", "User class", etc.
        patterns = [
            r'\b([A-Z][a-zA-Z]+)\s+(?:entity|class|model|object)',
            r'class\s+([A-Z][a-zA-Z]+)',
            r'\b([A-Z][a-zA-Z]+)(?:\s+has|\s+contains)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            classes.extend(matches)

        return list(set(classes))  # Remove duplicates

    def _extract_participants_from_text(self, text: str) -> List[str]:
        """Extract participant names from text."""
        participants = []

        # Common participant patterns
        words = text.split()
        for word in words:
            # Capitalized words are likely participants
            if word and word[0].isupper() and word.isalpha():
                participants.append(word)

        # Add common participants if found
        common = ['User', 'System', 'Controller', 'Service', 'Database']
        for participant in common:
            if participant.lower() in text.lower() and participant not in participants:
                participants.append(participant)

        # Remove duplicates while preserving order
        seen = set()
        unique_participants = []
        for p in participants:
            if p not in seen:
                seen.add(p)
                unique_participants.append(p)

        return unique_participants[:10]  # Limit to 10 participants

    def _extract_components_from_text(self, text: str) -> List[str]:
        """Extract component names from text."""
        components = []

        # Look for component patterns
        patterns = [
            r'([A-Z][a-zA-Z\s]+)(?:\s+\([^)]+\))?',  # "Frontend (React)"
            r'\-\s+([A-Z][a-zA-Z\s]+)',  # "- Frontend"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                component = match.strip()
                if len(component) > 2 and len(component) < 50:
                    components.append(component)

        # Remove duplicates
        return list(set(components))[:15]  # Limit to 15 components

    def _extract_plantuml_from_response(self, response: str) -> str:
        """Extract PlantUML code from LLM response."""
        # Remove markdown code blocks if present
        response = re.sub(r'```(?:plantuml)?\s*', '', response)
        response = response.strip()

        # If response already has @startuml/@enduml, return as-is
        if '@startuml' in response and '@enduml' in response:
            return response

        # Check if response looks like valid PlantUML content
        # (should have UML keywords like class, component, participant, etc.)
        uml_keywords = ['class', 'component', 'participant', 'actor', 'database',
                        '->', '-->', 'start', 'stop', 'if', 'endif']

        if not any(keyword in response.lower() for keyword in uml_keywords):
            # Response doesn't look like valid PlantUML
            return response  # Return as-is without wrapping

        # Otherwise, wrap the response
        return f"@startuml\n{response}\n@enduml"

    def _is_valid_plantuml(self, plantuml_code: str) -> bool:
        """Validate PlantUML syntax."""
        if not plantuml_code or not plantuml_code.strip():
            return False

        # Must contain @startuml and @enduml
        if '@startuml' not in plantuml_code or '@enduml' not in plantuml_code:
            return False

        # @startuml must come before @enduml
        start_idx = plantuml_code.index('@startuml')
        end_idx = plantuml_code.index('@enduml')
        if start_idx >= end_idx:
            return False

        return True
