"""
PRCreator Agent

Responsabilidad: Crear Pull Request con los tests generados.
Input: Tests verificados
Output: PR creado en GitHub
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .base import Agent


class PRCreator(Agent):
    """
    Agente especializado en creación de Pull Requests.

    Crea un PR con:
    - Tests generados
    - Descripción detallada
    - Métricas de cobertura
    - Label 'bot-generated-tests'
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="PRCreator", config=config)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan tests verificados."""
        errors = []

        if "test_results" not in input_data:
            errors.append("Falta 'test_results' en input")

        if "previous_coverage" not in input_data:
            errors.append("Falta 'previous_coverage' en input")

        if "new_coverage" not in input_data:
            errors.append("Falta 'new_coverage' en input")

        if "project_path" not in input_data:
            errors.append("Falta 'project_path' en input")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la creación del PR."""
        test_results = input_data["test_results"]
        validated_tests = input_data.get("validated_tests", [])
        project_path = Path(input_data["project_path"])
        previous_coverage = input_data["previous_coverage"]
        new_coverage = input_data["new_coverage"]
        coverage_increase = input_data.get("coverage_increase", 0)

        self.logger.info(f"Creando PR con {len(test_results)} tests")

        # Escribir tests al proyecto
        written_files = self._write_tests(
            test_results,
            validated_tests,
            project_path
        )

        # Crear branch
        branch_name = self._create_branch(project_path)

        # Commit tests
        self._commit_tests(
            project_path,
            written_files,
            previous_coverage,
            new_coverage
        )

        # Crear PR description
        pr_body = self._build_pr_body(
            test_results,
            previous_coverage,
            new_coverage,
            coverage_increase,
            input_data.get("file_improvements", [])
        )

        # Crear PR con gh
        pr_url = self._create_pull_request(
            project_path,
            branch_name,
            pr_body
        )

        return {
            "pr_created": pr_url is not None,
            "pr_url": pr_url,
            "branch_name": branch_name,
            "files_added": [str(f) for f in written_files],
            "total_tests_added": len(test_results)
        }

    def _write_tests(
        self,
        test_results: List[Dict[str, Any]],
        validated_tests: List[Dict[str, Any]],
        project_path: Path
    ) -> List[Path]:
        """
        Escribe los tests en el proyecto.

        Args:
            test_results: Tests que pasaron
            validated_tests: Tests con código validado
            project_path: Ruta del proyecto

        Returns:
            Lista de archivos escritos
        """
        written_files = []

        # Mapear test_file a código
        test_code_map = {
            t["test_file"]: t["validated_code"]
            for t in validated_tests
        }

        for result in test_results:
            test_file = result["test_file"]

            if test_file not in test_code_map:
                self.logger.warning(f"No se encontró código para {test_file}")
                continue

            code = test_code_map[test_file]

            # Escribir en el proyecto
            full_path = project_path / test_file
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(code)

            written_files.append(full_path)
            self.logger.info(f"Escrito {full_path}")

        return written_files

    def _create_branch(self, project_path: Path) -> str:
        """
        Crea una nueva branch para los tests.

        Args:
            project_path: Ruta del proyecto

        Returns:
            Nombre de la branch creada
        """
        import time
        timestamp = int(time.time())
        branch_name = f"bot/generated-tests-{timestamp}"

        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            self.logger.info(f"Branch creada: {branch_name}")
            return branch_name

        except Exception as e:
            self.logger.error(f"Error creando branch: {e}")
            return "bot/generated-tests-error"

    def _commit_tests(
        self,
        project_path: Path,
        written_files: List[Path],
        previous_coverage: float,
        new_coverage: float
    ) -> None:
        """
        Hace commit de los tests.

        Args:
            project_path: Ruta del proyecto
            written_files: Archivos a commitear
            previous_coverage: Cobertura previa
            new_coverage: Nueva cobertura
        """
        try:
            # Add files
            for filepath in written_files:
                subprocess.run(
                    ["git", "add", str(filepath)],
                    cwd=project_path,
                    timeout=30
                )

            # Commit
            increase = new_coverage - previous_coverage
            commit_message = (
                f"test: agregar tests generados automáticamente\n\n"
                f"Cobertura: {previous_coverage:.1f}% → {new_coverage:.1f}% "
                f"(+{increase:.1f}%)\n\n"
                f"Tests agregados: {len(written_files)}\n"
                f"Generado automáticamente por LLM Agent Pipeline"
            )

            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            self.logger.info("Commit creado")

        except Exception as e:
            self.logger.error(f"Error en commit: {e}")

    def _build_pr_body(
        self,
        test_results: List[Dict[str, Any]],
        previous_coverage: float,
        new_coverage: float,
        coverage_increase: float,
        file_improvements: List[Dict[str, Any]]
    ) -> str:
        """
        Construye el cuerpo del PR.

        Args:
            test_results: Tests que pasaron
            previous_coverage: Cobertura previa
            new_coverage: Nueva cobertura
            coverage_increase: Incremento
            file_improvements: Mejoras por archivo

        Returns:
            Markdown para el cuerpo del PR
        """
        # Archivos mejorados
        improved_files = [
            f for f in file_improvements
            if f.get("improvement", 0) > 0
        ]

        # Tabla de mejoras
        improvements_table = "| Archivo | Antes | Después | Mejora |\n"
        improvements_table += "|---------|-------|---------|--------|\n"

        for item in improved_files[:10]:  # Top 10
            improvements_table += (
                f"| {item['file']} | "
                f"{item['old_coverage']:.1f}% | "
                f"{item['new_coverage']:.1f}% | "
                f"+{item['improvement']:.1f}% |\n"
            )

        # Tests agregados
        tests_list = "\n".join([
            f"- `{result['test_file']}`"
            for result in test_results[:20]  # Top 20
        ])

        if len(test_results) > 20:
            tests_list += f"\n- ... y {len(test_results) - 20} más"

        body = f"""## Tests Generados Automáticamente por LLM

ESTE PR FUE GENERADO AUTOMÁTICAMENTE. Requiere revisión humana antes de merge.

### Resumen de Cobertura

- Cobertura anterior: **{previous_coverage:.2f}%**
- Cobertura nueva: **{new_coverage:.2f}%**
- Incremento: **+{coverage_increase:.2f}%**

### Archivos Mejorados

{improvements_table}

### Tests Agregados

{tests_list}

### Validaciones Realizadas

- OK: Sintaxis Python válida (AST)
- OK: Lint con ruff
- OK: Formato con black
- OK: Tests ejecutan correctamente
- OK: Incremento de cobertura verificado

### Checklist de Revisión

- [ ] Revisar que los tests sean correctos
- [ ] Verificar que los tests cubran casos relevantes
- [ ] Validar que no haya duplicación con tests existentes
- [ ] Confirmar que los mocks sean apropiados
- [ ] Verificar que los nombres sean descriptivos

### Notas

Los tests fueron generados usando un pipeline de agentes especializados:
1. CoverageAnalyzer - Identificó gaps de cobertura
2. TestPlanner - Planificó tests necesarios
3. LLMGenerator - Generó código con LLM
4. SyntaxValidator - Validó sintaxis y estilo
5. TestRunner - Ejecutó tests
6. CoverageVerifier - Verificó incremento de cobertura
7. PRCreator - Creó este PR

Para más información, consulta: `docs/desarrollo/arquitectura_agentes_especializados.md`
"""

        return body

    def _create_pull_request(
        self,
        project_path: Path,
        branch_name: str,
        pr_body: str
    ) -> str:
        """
        Crea el Pull Request usando gh CLI.

        Args:
            project_path: Ruta del proyecto
            branch_name: Nombre de la branch
            pr_body: Cuerpo del PR

        Returns:
            URL del PR creado o None si falló
        """
        try:
            # Push branch
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Crear PR con gh
            cmd = [
                "gh", "pr", "create",
                "--title", "[BOT] Tests generados automáticamente",
                "--body", pr_body,
                "--label", "bot-generated-tests",
                "--label", "needs-review"
            ]

            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                pr_url = result.stdout.strip()
                self.logger.info(f"PR creado: {pr_url}")
                return pr_url
            else:
                self.logger.error(f"Error creando PR: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"Error en PR creation: {e}")
            return None

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Valida que el PR se haya creado."""
        errors = []

        pr_created = output_data.get("pr_created", False)

        if not pr_created:
            errors.append("No se pudo crear el Pull Request")

        files_added = output_data.get("files_added", [])
        if not files_added:
            errors.append("No se agregaron archivos al PR")

        return errors
