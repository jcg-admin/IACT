"""
TestPlanner Agent

Responsabilidad: Planificar qué tests generar basado en gaps de cobertura.
Input: Lista de targets con baja cobertura
Output: Plan detallado de tests a generar
"""

import ast
import inspect
from pathlib import Path
from typing import Any, Dict, List

# Legacy import - base moved to scripts.ai.shared.agent_base


class TestPlanner(Agent):
    """
    Agente especializado en planificación de tests.

    Analiza el código fuente y decide:
    - Qué funciones/clases necesitan tests
    - Qué casos edge testear
    - Prioridad de generación
    - Estimación de esfuerzo
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="TestPlanner", config=config)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan targets priorizados."""
        errors = []

        if "prioritized_targets" not in input_data:
            errors.append("Falta 'prioritized_targets' en input")

        if "project_path" not in input_data:
            errors.append("Falta 'project_path' en input")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la planificación de tests."""
        targets = input_data["prioritized_targets"]
        project_path = Path(input_data["project_path"])
        max_tests = self.get_config("max_tests_per_run", 5)

        self.logger.info(f"Planificando tests para {len(targets)} targets")

        # Seleccionar top N targets
        selected_targets = targets[:max_tests]

        # Planificar tests para cada target
        test_plans = []
        for target in selected_targets:
            plan = self._plan_for_file(target, project_path)
            if plan:
                test_plans.append(plan)

        return {
            "test_plans": test_plans,
            "total_planned": len(test_plans),
            "estimated_coverage_increase": self._estimate_coverage_increase(
                test_plans
            )
        }

    def _plan_for_file(
        self,
        target: Dict[str, Any],
        project_path: Path
    ) -> Dict[str, Any]:
        """
        Crea plan de tests para un archivo específico.

        Args:
            target: Información del target con baja cobertura
            project_path: Ruta del proyecto

        Returns:
            Plan de tests para el archivo
        """
        filepath = Path(target["file"])
        full_path = project_path / filepath

        if not full_path.exists():
            self.logger.warning(f"Archivo no existe: {full_path}")
            return None

        # Leer y parsear el código
        try:
            with open(full_path) as f:
                source_code = f.read()

            tree = ast.parse(source_code)
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)

        except Exception as e:
            self.logger.error(f"Error parseando {filepath}: {e}")
            return None

        # Identificar qué necesita tests
        test_candidates = self._identify_test_candidates(
            functions,
            classes,
            target.get("missing_lines", [])
        )

        # Generar casos de prueba
        test_cases = []
        for candidate in test_candidates:
            cases = self._generate_test_cases(candidate, source_code)
            test_cases.extend(cases)

        return {
            "source_file": str(filepath),
            "test_file": self._get_test_file_path(filepath),
            "current_coverage": target["current_coverage"],
            "test_candidates": test_candidates,
            "test_cases": test_cases,
            "estimated_new_lines": len(test_cases) * 8,  # ~8 líneas por test
            "priority": target.get("rank", 999)
        }

    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extrae funciones del AST."""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Ignorar métodos privados y dunder
                if node.name.startswith('_') and not node.name.startswith('__test'):
                    continue

                functions.append({
                    "name": node.name,
                    "type": "function",
                    "lineno": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "returns": self._get_return_annotation(node),
                    "docstring": ast.get_docstring(node) or ""
                })

        return functions

    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extrae clases del AST."""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if not item.name.startswith('_') or item.name == '__init__':
                            methods.append({
                                "name": item.name,
                                "lineno": item.lineno,
                                "args": [arg.arg for arg in item.args.args][1:]  # Skip self
                            })

                classes.append({
                    "name": node.name,
                    "type": "class",
                    "lineno": node.lineno,
                    "methods": methods,
                    "docstring": ast.get_docstring(node) or ""
                })

        return classes

    def _get_return_annotation(self, node: ast.FunctionDef) -> str:
        """Obtiene anotación de tipo de retorno."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return "Any"

    def _identify_test_candidates(
        self,
        functions: List[Dict[str, Any]],
        classes: List[Dict[str, Any]],
        missing_lines: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Identifica qué funciones/clases necesitan tests.

        Args:
            functions: Lista de funciones encontradas
            classes: Lista de clases encontradas
            missing_lines: Líneas sin cobertura

        Returns:
            Lista de candidatos para generar tests
        """
        candidates = []

        # Funciones en líneas sin cobertura
        for func in functions:
            if func["lineno"] in missing_lines or any(
                func["lineno"] <= line <= func["lineno"] + 10
                for line in missing_lines
            ):
                candidates.append({
                    "type": "function",
                    "name": func["name"],
                    "signature": self._build_signature(func),
                    "docstring": func["docstring"],
                    "complexity": "medium"
                })

        # Métodos de clases
        for cls in classes:
            for method in cls["methods"]:
                if method["lineno"] in missing_lines:
                    candidates.append({
                        "type": "method",
                        "class": cls["name"],
                        "name": method["name"],
                        "signature": f"{cls['name']}.{method['name']}",
                        "docstring": cls["docstring"],
                        "complexity": "medium"
                    })

        return candidates

    def _build_signature(self, func: Dict[str, Any]) -> str:
        """Construye la firma de una función."""
        args_str = ", ".join(func["args"])
        return_type = func.get("returns", "Any")
        return f"{func['name']}({args_str}) -> {return_type}"

    def _generate_test_cases(
        self,
        candidate: Dict[str, Any],
        source_code: str
    ) -> List[Dict[str, Any]]:
        """
        Genera casos de prueba para un candidato.

        Args:
            candidate: Función/método candidato
            source_code: Código fuente completo

        Returns:
            Lista de casos de prueba a generar
        """
        test_cases = []

        # Caso básico: happy path
        test_cases.append({
            "name": f"test_{candidate['name']}_happy_path",
            "type": "happy_path",
            "description": f"Test del caso normal de {candidate['name']}",
            "priority": "high"
        })

        # Casos edge según complejidad
        if candidate.get("complexity") in ["medium", "high"]:
            test_cases.append({
                "name": f"test_{candidate['name']}_edge_cases",
                "type": "edge_case",
                "description": f"Test de casos límite de {candidate['name']}",
                "priority": "medium"
            })

        # Casos de error
        test_cases.append({
            "name": f"test_{candidate['name']}_error_handling",
            "type": "error",
            "description": f"Test de manejo de errores de {candidate['name']}",
            "priority": "medium"
        })

        return test_cases

    def _get_test_file_path(self, source_file: Path) -> str:
        """
        Determina la ruta del archivo de tests.

        Args:
            source_file: Ruta del archivo fuente

        Returns:
            Ruta del archivo de tests correspondiente
        """
        # Estrategia: tests/test_<nombre>.py
        filename = f"test_{source_file.stem}.py"
        return f"tests/{filename}"

    def _estimate_coverage_increase(
        self,
        test_plans: List[Dict[str, Any]]
    ) -> float:
        """
        Estima el incremento de cobertura esperado.

        Args:
            test_plans: Lista de planes de tests

        Returns:
            Porcentaje estimado de incremento
        """
        if not test_plans:
            return 0.0

        # Heurística simple: 5-10% por plan
        base_increase = len(test_plans) * 5
        return min(base_increase, 20)  # Cap at 20%

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Valida que los planes sean razonables."""
        errors = []

        test_plans = output_data.get("test_plans", [])

        if not test_plans:
            errors.append("No se generó ningún plan de tests")

        for plan in test_plans:
            if not plan.get("test_cases"):
                errors.append(f"Plan sin casos: {plan.get('source_file')}")

            if len(plan.get("test_cases", [])) > 20:
                errors.append(
                    f"Demasiados casos ({len(plan['test_cases'])}) "
                    f"para {plan.get('source_file')}"
                )

        return errors
