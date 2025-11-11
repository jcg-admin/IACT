#!/usr/bin/env python3
"""
Route Lint Agent

Verifica que todos los ViewSets de Django REST Framework tengan
protección de permisos granulares.

Propósito:
    - Detectar ViewSets sin required_permissions
    - Detectar ViewSets sin herencia de PermisoMixin
    - Prevenir código sin permisos en producción

Input: Archivos views.py del proyecto
Output: Reporte JSON con violaciones encontradas

Uso:
    python route_linter.py
    python route_linter.py --verbose
    python route_linter.py --json
    python route_linter.py --fix  # (futuro: auto-fix)

Exit codes:
    0: Pass - No violations found
    1: Fail - Violations found
    2: Error - Execution error
"""

import ast
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field

from .base import BasePermissionAgent


@dataclass
class Violation:
    """Representa una violación detectada."""
    file: str
    line: int
    class_name: str
    issue: str
    severity: str
    suggestion: str
    fix_example: Optional[str] = None


@dataclass
class AnalysisStats:
    """Estadísticas del análisis."""
    total_files: int = 0
    total_viewsets: int = 0
    viewsets_with_permissions: int = 0
    viewsets_without_permissions: int = 0


@dataclass
class LintResult:
    """Resultado del análisis completo."""
    agent: str
    timestamp: str
    status: str  # "pass" | "fail"
    duration_seconds: float
    analyzed: AnalysisStats
    coverage_percent: float
    violations: List[Violation] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)


class RouteLintAgent(BasePermissionAgent):
    """
    Agent que verifica protección de permisos en ViewSets.

    Detecta dos formas válidas de protección:
    1. Atributo required_permissions en la clase
    2. Herencia de PermisoMixin

    Excluye automáticamente:
    - Archivos en migrations/
    - Archivos que contengan 'test' en el path
    - ViewSets abstractos
    - ViewSets base (contienen 'Base' en el nombre)
    """

    # ViewSet base classes a detectar
    VIEWSET_BASES = {
        'ViewSet',
        'ModelViewSet',
        'ReadOnlyModelViewSet',
        'GenericViewSet'
    }

    # Palabras que indican ViewSet base/abstracto (skip)
    BASE_INDICATORS = {'Base', 'Abstract', 'Mixin'}

    def __init__(self, verbose: bool = False):
        super().__init__(
            name="route-lint",
            prompt_path="docs/backend/permisos/promptops/gates/route-lint.md",
            verbose=verbose
        )
        self.stats = AnalysisStats()

    def run(self) -> int:
        """
        Ejecuta el análisis completo.

        Returns:
            Exit code (0 = pass, 1 = fail, 2 = error)
        """
        try:
            self.start_execution()

            # Validar prerequisitos
            self.validate_prerequisites()

            # Obtener project root
            project_root = self.get_project_root()

            # Analizar ViewSets
            result = self.analyze_viewsets(project_root)

            # Log métricas
            self.log_metric("total_viewsets", result.analyzed.total_viewsets)
            self.log_metric("violations", len(result.violations))
            self.log_metric("coverage_percent", result.coverage_percent)

            self.end_execution()

            # Return exit code
            return 0 if result.status == "pass" else 1

        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            return 2

    def analyze_viewsets(self, root_path: Path) -> LintResult:
        """
        Analiza todos los ViewSets del proyecto.

        Args:
            root_path: Ruta raíz del proyecto

        Returns:
            LintResult con violaciones encontradas
        """
        from datetime import datetime

        violations = []

        # Buscar archivos views.py
        view_files = self._find_view_files(root_path)
        self.stats.total_files = len(view_files)

        self.logger.info(f"Found {len(view_files)} view files to analyze")

        # Analizar cada archivo
        for view_file in view_files:
            try:
                file_violations = self._analyze_file(view_file, root_path)
                violations.extend(file_violations)
            except Exception as e:
                self.logger.warning(
                    f"Error analyzing {view_file}: {e}",
                    extra={"file": str(view_file)}
                )

        # Calcular cobertura
        coverage = self._calculate_coverage()

        # Generar resumen por severidad
        summary = self._generate_summary(violations)

        # Determinar status
        status = "pass" if not violations else "fail"

        return LintResult(
            agent=self.name,
            timestamp=datetime.now().isoformat(),
            status=status,
            duration_seconds=self.get_duration(),
            analyzed=self.stats,
            coverage_percent=coverage,
            violations=violations,
            summary=summary
        )

    def _find_view_files(self, root_path: Path) -> List[Path]:
        """
        Encuentra todos los archivos views.py del proyecto.

        Args:
            root_path: Ruta raíz del proyecto

        Returns:
            Lista de paths a archivos views.py
        """
        api_root = root_path / "api" / "callcentersite"

        if not api_root.exists():
            self.logger.warning(f"API root not found: {api_root}")
            return []

        view_files_set = set()

        # Buscar views.py en directorio base Y subdirectorios
        # glob("views.py") busca en dir actual
        # rglob("**/views.py") busca en subdirectorios
        for pattern in ["views.py", "**/views.py"]:
            for view_file in api_root.glob(pattern):
                path_str = str(view_file)

                # Excluir migrations (solo carpeta migrations/)
                if "/migrations/" in path_str or "\\migrations\\" in path_str:
                    self.logger.debug(f"Skipping migration: {view_file}")
                    continue

                # Excluir tests (solo carpetas test/ o tests/ y archivos test_*.py)
                # NO excluir si "test" aparece en cualquier parte del path
                path_parts = view_file.parts
                if any(part in ["test", "tests"] for part in path_parts):
                    self.logger.debug(f"Skipping test directory: {view_file}")
                    continue

                if view_file.name.startswith("test_"):
                    self.logger.debug(f"Skipping test file: {view_file}")
                    continue

                view_files_set.add(view_file)

        return sorted(list(view_files_set))

    def _analyze_file(
        self,
        file_path: Path,
        root_path: Path
    ) -> List[Violation]:
        """
        Analiza un archivo views.py en busca de ViewSets sin permisos.

        Args:
            file_path: Path al archivo a analizar
            root_path: Path raíz del proyecto

        Returns:
            Lista de violaciones encontradas
        """
        violations = []

        # Leer archivo
        try:
            with open(file_path) as f:
                content = f.read()
        except Exception as e:
            self.logger.warning(f"Cannot read {file_path}: {e}")
            return []

        # Parsear AST
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            self.logger.warning(
                f"Syntax error in {file_path}:{e.lineno} - {e.msg}"
            )
            return []

        # Analizar cada clase
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Verificar si es ViewSet
            if not self._is_viewset(node):
                continue

            # Incrementar contador
            self.stats.total_viewsets += 1

            # Verificar si es ViewSet base/abstracto
            if self._is_base_viewset(node):
                self.logger.debug(
                    f"Skipping base ViewSet: {node.name} in {file_path}"
                )
                continue

            # Verificar si tiene permisos
            if self._has_permissions(node):
                self.stats.viewsets_with_permissions += 1
                continue

            # VIOLATION: ViewSet sin permisos
            self.stats.viewsets_without_permissions += 1

            # Crear violación
            relative_path = self._get_relative_path(file_path, root_path)

            violation = Violation(
                file=relative_path,
                line=node.lineno,
                class_name=node.name,
                issue="ViewSet no tiene required_permissions ni hereda PermisoMixin",
                severity=self._determine_severity(node),
                suggestion=self._generate_suggestion(node),
                fix_example=self._generate_fix_example(node)
            )

            violations.append(violation)

            # Log violación
            self.log_violation(
                file=relative_path,
                line=node.lineno,
                severity=violation.severity,
                message=violation.issue,
                class_name=node.name
            )

        return violations

    def _is_viewset(self, node: ast.ClassDef) -> bool:
        """
        Verifica si una clase hereda de algún ViewSet de DRF.

        Args:
            node: Nodo AST de la clase

        Returns:
            True si hereda de ViewSet
        """
        for base in node.bases:
            base_name = None

            if isinstance(base, ast.Attribute):
                # Caso: viewsets.ModelViewSet
                base_name = base.attr
            elif isinstance(base, ast.Name):
                # Caso: ModelViewSet (importado directamente)
                base_name = base.id

            if base_name in self.VIEWSET_BASES:
                return True

        return False

    def _is_base_viewset(self, node: ast.ClassDef) -> bool:
        """
        Verifica si es un ViewSet base/abstracto que no requiere permisos.

        Args:
            node: Nodo AST de la clase

        Returns:
            True si es ViewSet base
        """
        # Verificar nombre
        if any(indicator in node.name for indicator in self.BASE_INDICATORS):
            return True

        # Verificar si tiene Meta con abstract = True
        for item in node.body:
            if isinstance(item, ast.ClassDef) and item.name == "Meta":
                for meta_item in item.body:
                    if isinstance(meta_item, ast.Assign):
                        for target in meta_item.targets:
                            if (isinstance(target, ast.Name) and
                                target.id == "abstract"):
                                return True

        return False

    def _has_permissions(self, node: ast.ClassDef) -> bool:
        """
        Verifica si ViewSet tiene protección de permisos válida.

        Dos formas válidas:
        1. Atributo required_permissions
        2. Herencia de PermisoMixin

        Args:
            node: Nodo AST de la clase

        Returns:
            True si tiene protección de permisos
        """
        # Verificar required_permissions
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if (isinstance(target, ast.Name) and
                        target.id == "required_permissions"):
                        # Verificar que no esté vacío
                        if isinstance(item.value, ast.List):
                            if item.value.elts:  # Lista no vacía
                                return True
                        else:
                            # Asignación dinámica (asumir válida)
                            return True

        # Verificar PermisoMixin en bases
        for base in node.bases:
            base_name = None

            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr

            if base_name == "PermisoMixin":
                return True

        return False

    def _determine_severity(self, node: ast.ClassDef) -> str:
        """
        Determina la severidad de la violación basada en los métodos del ViewSet.

        Args:
            node: Nodo AST de la clase

        Returns:
            "high" | "medium" | "low"
        """
        # Buscar métodos CRUD peligrosos
        dangerous_methods = {'create', 'update', 'partial_update', 'destroy'}
        moderate_methods = {'list', 'retrieve'}

        methods_found = set()

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods_found.add(item.name)

        # Si tiene métodos de escritura, es high severity
        if methods_found & dangerous_methods:
            return "high"

        # Si solo tiene métodos de lectura, es medium
        if methods_found & moderate_methods:
            return "medium"

        # Por defecto, high (puede heredar métodos de ModelViewSet)
        return "high"

    def _generate_suggestion(self, node: ast.ClassDef) -> str:
        """
        Genera sugerencia de corrección basada en el nombre del ViewSet.

        Args:
            node: Nodo AST de la clase

        Returns:
            Sugerencia de capacidad a agregar
        """
        # Extraer nombre base del ViewSet
        class_name = node.name.replace('ViewSet', '')

        # Convertir a snake_case
        import re
        snake_name = re.sub('([A-Z]+)', r'_\1', class_name).lower().strip('_')

        # Generar capacidad sugerida
        suggestion = f"required_permissions = ['sistema.{snake_name}.ver']"

        return suggestion

    def _generate_fix_example(self, node: ast.ClassDef) -> str:
        """
        Genera ejemplo de código corregido.

        Args:
            node: Nodo AST de la clase

        Returns:
            Código de ejemplo con la corrección
        """
        # Obtener bases
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}")
            elif isinstance(base, ast.Name):
                bases.append(base.id)

        bases_str = ", ".join(["PermisoMixin"] + bases)

        # Generar capacidad
        class_name = node.name.replace('ViewSet', '')
        import re
        snake_name = re.sub('([A-Z]+)', r'_\1', class_name).lower().strip('_')

        example = f"""class {node.name}({bases_str}):
    required_permissions = ['sistema.{snake_name}.ver']
    queryset = ...
    serializer_class = ..."""

        return example

    def _get_relative_path(self, file_path: Path, root_path: Path) -> str:
        """
        Obtiene path relativo al root del proyecto.

        Args:
            file_path: Path absoluto del archivo
            root_path: Path raíz del proyecto

        Returns:
            Path relativo como string
        """
        try:
            return str(file_path.relative_to(root_path))
        except ValueError:
            return str(file_path)

    def _calculate_coverage(self) -> float:
        """
        Calcula porcentaje de cobertura de permisos.

        Returns:
            Porcentaje (0-100)
        """
        if self.stats.total_viewsets == 0:
            return 100.0

        coverage = (
            self.stats.viewsets_with_permissions /
            self.stats.total_viewsets
        ) * 100

        return round(coverage, 1)

    def _generate_summary(self, violations: List[Violation]) -> Dict[str, int]:
        """
        Genera resumen de violaciones por severidad.

        Args:
            violations: Lista de violaciones

        Returns:
            Dict con conteo por severidad
        """
        summary = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }

        for violation in violations:
            summary[violation.severity] += 1

        return summary

    def generate_report(self, result: LintResult, format: str = "text") -> str:
        """
        Genera reporte legible del análisis.

        Args:
            result: Resultado del análisis
            format: "text" | "json"

        Returns:
            Reporte formateado
        """
        if format == "json":
            return json.dumps(asdict(result), indent=2, default=str)

        # Formato texto
        lines = []

        # Header
        lines.append("=" * 70)
        lines.append("🔍 Route Lint Gate")
        lines.append("=" * 70)
        lines.append("")

        # Stats
        lines.append("Analyzed:")
        lines.append(f"  Files: {result.analyzed.total_files}")
        lines.append(f"  ViewSets: {result.analyzed.total_viewsets}")
        lines.append(f"  Coverage: {result.coverage_percent}%")
        lines.append("")

        # Status
        if result.status == "pass":
            lines.append("✅ PASS - No violations found")
            lines.append("")
            lines.append(
                f"All {result.analyzed.total_viewsets} ViewSets have "
                "permission protection."
            )
        else:
            lines.append(f"❌ FAIL - {len(result.violations)} violations found")
            lines.append("")

            # Violations
            lines.append("Violations:")
            lines.append("")

            for i, v in enumerate(result.violations, 1):
                lines.append(f"  [{i}] {v.file}:{v.line}")
                lines.append(f"      Class: {v.class_name}")
                lines.append(f"      Issue: {v.issue}")
                lines.append(f"      Severity: {v.severity.upper()}")
                lines.append(f"      Fix: {v.suggestion}")
                lines.append("")

            # Summary
            lines.append(f"Summary: {result.summary}")
            lines.append("")

            # How to fix
            lines.append("To fix:")
            lines.append("1. Add required_permissions to each ViewSet")
            lines.append("2. Or inherit from PermisoMixin")
            lines.append("")
            lines.append("Example:")
            lines.append("  from apps.permissions.mixins import PermisoMixin")
            lines.append("")
            lines.append("  class ReporteViewSet(PermisoMixin, viewsets.ModelViewSet):")
            lines.append("      required_permissions = ['sistema.reportes.ivr.ver']")
            lines.append("      queryset = Reporte.objects.all()")
            lines.append("      serializer_class = ReporteSerializer")

        lines.append("")
        lines.append("=" * 70)
        lines.append(f"Duration: {result.duration_seconds:.2f}s")
        lines.append("=" * 70)

        return "\n".join(lines)


def main():
    """Entry point del agente."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Route Lint Agent - Verifica permisos en ViewSets"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON format'
    )
    args = parser.parse_args()

    # Crear agente
    agent = RouteLintAgent(verbose=args.verbose)

    # Analizar
    project_root = agent.get_project_root()
    result = agent.analyze_viewsets(project_root)

    # Output
    format_type = "json" if args.json else "text"
    print(agent.generate_report(result, format=format_type))

    # Exit code
    sys.exit(0 if result.status == "pass" else 1)


if __name__ == "__main__":
    main()
