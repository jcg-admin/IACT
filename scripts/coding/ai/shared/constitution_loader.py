"""
Constitution Loader - Carga y valida adherencia a constitution para agentes AI.

Este módulo proporciona utilidades para que los agentes AI carguen y
validen sus decisiones contra los principios definidos en la constitution.

Trazabilidad:
    - Constitution: docs/gobernanza/agentes/constitution.md
    - Fase 4: Integración con Agentes AI
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging


class ConstitutionPrinciple:
    """Representa un principio individual de la constitution."""

    def __init__(self, number: int, name: str, description: str, rules: List[str]):
        """
        Inicializa un principio.

        Args:
            number: Número del principio (1-12)
            name: Nombre del principio
            description: Descripción del principio
            rules: Lista de reglas del principio
        """
        self.number = number
        self.name = name
        self.description = description
        self.rules = rules

    def __str__(self) -> str:
        """Representación en string del principio."""
        return f"Principio {self.number}: {self.name}"


class Constitution:
    """
    Constitution para agentes AI.

    Carga y proporciona acceso a los principios fundamentales que
    guían las decisiones de los agentes AI.
    """

    def __init__(self, constitution_path: Optional[Path] = None):
        """
        Inicializa la constitution.

        Args:
            constitution_path: Ruta al archivo de constitution.
                             Si no se especifica, usa la ubicación por defecto.
        """
        if constitution_path is None:
            # Ubicación por defecto relativa a este archivo
            base_dir = Path(__file__).parent.parent.parent  # Raíz del proyecto
            constitution_path = base_dir / "docs" / "gobernanza" / "agentes" / "constitution.md"

        self.constitution_path = constitution_path
        self.principles: Dict[int, ConstitutionPrinciple] = {}
        self.logger = logging.getLogger("constitution_loader")
        self._load_constitution()

    def _load_constitution(self) -> None:
        """Carga la constitution desde el archivo markdown."""
        if not self.constitution_path.exists():
            self.logger.warning(f"Constitution no encontrada en {self.constitution_path}")
            return

        with open(self.constitution_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extraer principios usando regex
        # Buscar secciones que empiecen con "### N. "
        principle_pattern = r'### (\d+)\.\s+(.+?)\n\n\*\*Principio\*\*:\s+(.+?)(?=\n###|\Z)'

        matches = re.finditer(principle_pattern, content, re.DOTALL)

        for match in matches:
            number = int(match.group(1))
            name = match.group(2).strip()
            description = match.group(3).strip()

            # Extraer reglas del principio (listas, puntos importantes)
            principle_text = match.group(0)
            rules = self._extract_rules(principle_text)

            principle = ConstitutionPrinciple(
                number=number,
                name=name,
                description=description,
                rules=rules
            )

            self.principles[number] = principle

        self.logger.info(f"Constitution cargada: {len(self.principles)} principios")

    def _extract_rules(self, text: str) -> List[str]:
        """
        Extrae reglas importantes del texto de un principio.

        Args:
            text: Texto del principio

        Returns:
            Lista de reglas extraídas
        """
        rules = []

        # Extraer ítems de listas
        list_items = re.findall(r'^\s*[-*]\s+(.+)$', text, re.MULTILINE)
        rules.extend([item.strip() for item in list_items])

        # Extraer texto en negrita (reglas importantes)
        bold_items = re.findall(r'\*\*([^*]+)\*\*', text)
        rules.extend([item.strip() for item in bold_items if len(item) > 10])

        # Remover duplicados manteniendo orden
        seen = set()
        unique_rules = []
        for rule in rules:
            if rule not in seen:
                seen.add(rule)
                unique_rules.append(rule)

        return unique_rules[:10]  # Limitar a 10 reglas más importantes

    def get_principle(self, number: int) -> Optional[ConstitutionPrinciple]:
        """
        Obtiene un principio por su número.

        Args:
            number: Número del principio (1-12)

        Returns:
            ConstitutionPrinciple o None si no existe
        """
        return self.principles.get(number)

    def get_all_principles(self) -> List[ConstitutionPrinciple]:
        """
        Obtiene todos los principios.

        Returns:
            Lista de todos los principios
        """
        return sorted(self.principles.values(), key=lambda p: p.number)

    def get_quality_principle(self) -> Optional[ConstitutionPrinciple]:
        """Obtiene el principio de Calidad sobre Velocidad."""
        return self.get_principle(1)

    def get_standards_principle(self) -> Optional[ConstitutionPrinciple]:
        """Obtiene el principio de Adherencia a Estándares."""
        return self.get_principle(2)

    def get_traceability_principle(self) -> Optional[ConstitutionPrinciple]:
        """Obtiene el principio de Trazabilidad Completa."""
        return self.get_principle(3)

    def get_authority_principle(self) -> Optional[ConstitutionPrinciple]:
        """Obtiene el principio de Límites de Autoridad."""
        return self.get_principle(4)

    def get_documentation_principle(self) -> Optional[ConstitutionPrinciple]:
        """Obtiene el principio de Documentación Obligatoria."""
        return self.get_principle(5)

    def get_testing_principle(self) -> Optional[ConstitutionPrinciple]:
        """Obtiene el principio de Testing y Validación."""
        return self.get_principle(6)


class ConstitutionValidator:
    """
    Validador de adherencia a constitution para agentes.

    Proporciona métodos para que los agentes validen sus decisiones
    y output contra los principios de la constitution.
    """

    def __init__(self, constitution: Constitution):
        """
        Inicializa el validador.

        Args:
            constitution: Constitution cargada
        """
        self.constitution = constitution
        self.logger = logging.getLogger("constitution_validator")

    def validate_quality_over_speed(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Valida adherencia al principio de Calidad sobre Velocidad.

        Args:
            output_data: Datos de salida del agente

        Returns:
            Lista de violaciones (vacía si cumple)
        """
        violations = []

        # Verificar que no hay placeholders
        if self._contains_placeholders(output_data):
            violations.append("Output contiene placeholders (TODO, FIXME, etc.)")

        # Verificar que hay documentación
        if not self._has_documentation(output_data):
            violations.append("Output carece de documentación adecuada")

        return violations

    def validate_traceability(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Valida adherencia al principio de Trazabilidad.

        Args:
            output_data: Datos de salida del agente

        Returns:
            Lista de violaciones (vacía si cumple)
        """
        violations = []

        # Verificar que hay referencias a requisitos
        content = str(output_data)
        has_req = bool(re.search(r'REQ-[A-Z]+-\d+', content))
        has_spec = bool(re.search(r'SPEC-[A-Z]+-\d+', content))
        has_adr = bool(re.search(r'ADR-\d{4}-\d+', content))

        if not (has_req or has_spec or has_adr):
            violations.append("Output carece de trazabilidad a requisitos/specs/ADRs")

        return violations

    def validate_no_emojis(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Valida que no hay emojis en el output.

        Args:
            output_data: Datos de salida del agente

        Returns:
            Lista de violaciones (vacía si cumple)
        """
        violations = []

        content = str(output_data)

        # Patrones de emojis comunes
        emoji_patterns = [
            r'[\U0001F600-\U0001F64F]',  # Emoticons
            r'[\U0001F300-\U0001F5FF]',  # Símbolos
            r'[\U0001F680-\U0001F6FF]',  # Transporte
            r'✅', r'❌', r'⚠️', r'🚀', r'🔧', r'📝'
        ]

        for pattern in emoji_patterns:
            if re.search(pattern, content):
                violations.append(f"Output contiene emojis (prohibidos por GUIA_ESTILO.md)")
                break

        return violations

    def validate_testing(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Valida adherencia al principio de Testing y Validación.

        Args:
            output_data: Datos de salida del agente

        Returns:
            Lista de violaciones (vacía si cumple)
        """
        violations = []

        # Si el output incluye código, debe incluir tests
        if self._contains_code(output_data):
            if not self._contains_tests(output_data):
                violations.append("Código generado sin tests asociados")

        return violations

    def validate_authority_limits(self, action: str, context: Dict[str, Any]) -> bool:
        """
        Valida si una acción está dentro de los límites de autoridad del agente.

        Args:
            action: Acción que el agente quiere realizar
            context: Contexto de la acción

        Returns:
            True si está dentro de autoridad, False si requiere escalación
        """
        # Acciones que requieren escalación humana
        requires_escalation = [
            "modificar_arquitectura",
            "cambiar_esquema_bd",
            "modificar_api_publica",
            "eliminar_codigo",
            "cambiar_seguridad",
            "modificar_dependencias_core",
            "merge_to_main",
            "cambiar_reglas_negocio"
        ]

        return action not in requires_escalation

    def _contains_placeholders(self, data: Dict[str, Any]) -> bool:
        """Verifica si hay placeholders en los datos."""
        content = str(data)
        placeholder_patterns = [r'TODO', r'FIXME', r'XXX', r'HACK', r'\.\.\.']
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in placeholder_patterns)

    def _has_documentation(self, data: Dict[str, Any]) -> bool:
        """Verifica si hay documentación en los datos."""
        content = str(data)
        # Buscar docstrings, comentarios, o secciones de documentación
        doc_patterns = [r'"""', r"'''", r'Args:', r'Returns:', r'## ', r'### ']
        return any(pattern in content for pattern in doc_patterns)

    def _contains_code(self, data: Dict[str, Any]) -> bool:
        """Verifica si los datos contienen código."""
        content = str(data)
        code_patterns = [r'def ', r'class ', r'import ', r'from .* import']
        return any(re.search(pattern, content) for pattern in code_patterns)

    def _contains_tests(self, data: Dict[str, Any]) -> bool:
        """Verifica si los datos contienen tests."""
        content = str(data)
        test_patterns = [r'def test_', r'class Test', r'@pytest', r'assert ']
        return any(re.search(pattern, content) for pattern in test_patterns)

    def validate_all(self, output_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Ejecuta todas las validaciones sobre el output.

        Args:
            output_data: Datos de salida del agente

        Returns:
            Diccionario con violaciones por categoría
        """
        return {
            "quality": self.validate_quality_over_speed(output_data),
            "traceability": self.validate_traceability(output_data),
            "emojis": self.validate_no_emojis(output_data),
            "testing": self.validate_testing(output_data)
        }


def load_constitution(constitution_path: Optional[Path] = None) -> Constitution:
    """
    Función de conveniencia para cargar la constitution.

    Args:
        constitution_path: Ruta opcional al archivo de constitution

    Returns:
        Constitution cargada

    Example:
        >>> from constitution_loader import load_constitution
        >>> constitution = load_constitution()
        >>> quality_principle = constitution.get_quality_principle()
        >>> print(quality_principle.description)
    """
    return Constitution(constitution_path)


def create_validator(constitution: Optional[Constitution] = None) -> ConstitutionValidator:
    """
    Función de conveniencia para crear un validador.

    Args:
        constitution: Constitution opcional (se carga si no se proporciona)

    Returns:
        ConstitutionValidator configurado

    Example:
        >>> from constitution_loader import create_validator
        >>> validator = create_validator()
        >>> violations = validator.validate_no_emojis({"output": "test"})
        >>> assert len(violations) == 0
    """
    if constitution is None:
        constitution = load_constitution()
    return ConstitutionValidator(constitution)
