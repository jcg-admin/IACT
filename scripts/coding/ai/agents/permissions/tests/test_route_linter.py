"""
Tests para Route Lint Agent (TDD)

Estos tests se escribieron ANTES de implementar el código completo,
siguiendo la metodología Test-Driven Development.

Cobertura:
- Detección de ViewSets sin permisos
- Aceptación de ViewSets con required_permissions
- Aceptación de ViewSets con PermisoMixin
- Exclusión de tests y migrations
- Exclusión de ViewSets base/abstractos
- Manejo de errores de sintaxis
- Formato de output
"""

import pytest
from pathlib import Path
from textwrap import dedent

# Import del agent a testear
from scripts.coding.ai.agents.permissions.route_linter import (
    RouteLintAgent,
    Violation,
    LintResult
)


class TestRouteLinterBasics:
    """Tests básicos de funcionalidad."""

    @pytest.fixture
    def agent(self):
        """Fixture: Agente de prueba."""
        return RouteLintAgent(verbose=False)

    def test_agent_initialization(self, agent):
        """Test: Agente se inicializa correctamente."""
        assert agent.name == "route-lint"
        assert agent.prompt_path.name == "route-lint.md"
        assert agent.stats.total_viewsets == 0

    def test_project_root_detection(self, agent):
        """Test: Detecta correctamente el project root."""
        root = agent.get_project_root()
        assert root.exists()
        assert (root / "api" / "callcentersite").exists()


class TestViewSetDetection:
    """Tests de detección de ViewSets."""

    @pytest.fixture
    def agent(self):
        return RouteLintAgent(verbose=False)

    def test_detects_viewset_without_permissions(self, agent, tmp_path):
        """
        Test: Detecta ViewSet sin permisos.

        Caso: ViewSet básico sin required_permissions ni PermisoMixin.
        Esperado: Violación detectada.
        """
        # Arrange: Crear archivo de prueba
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets
            from .models import Reporte

            class ReporteViewSet(viewsets.ModelViewSet):
                '''ViewSet sin permisos - DEBE SER DETECTADO'''
                queryset = Reporte.objects.all()
                serializer_class = ReporteSerializer
        """))

        # Act: Analizar archivo
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 1, "Debe detectar 1 violación"
        assert violations[0].class_name == "ReporteViewSet"
        assert violations[0].severity in ["high", "medium", "low"]
        assert "required_permissions" in violations[0].suggestion

    def test_accepts_viewset_with_required_permissions(self, agent, tmp_path):
        """
        Test: Acepta ViewSet con required_permissions.

        Caso: ViewSet con atributo required_permissions válido.
        Esperado: Sin violaciones.
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class ReporteViewSet(viewsets.ModelViewSet):
                required_permissions = ['sistema.reportes.ivr.ver']
                queryset = Reporte.objects.all()
                serializer_class = ReporteSerializer
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 0, "No debe detectar violaciones"

    def test_accepts_viewset_with_permiso_mixin(self, agent, tmp_path):
        """
        Test: Acepta ViewSet con PermisoMixin.

        Caso: ViewSet que hereda de PermisoMixin.
        Esperado: Sin violaciones.
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets
            from apps.permissions.mixins import PermisoMixin

            class ReporteViewSet(PermisoMixin, viewsets.ModelViewSet):
                queryset = Reporte.objects.all()
                serializer_class = ReporteSerializer
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 0, "PermisoMixin debe ser válido"

    def test_rejects_empty_required_permissions(self, agent, tmp_path):
        """
        Test: Rechaza lista vacía de permisos.

        Caso: required_permissions = []
        Esperado: Violación detectada.
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class ReporteViewSet(viewsets.ModelViewSet):
                required_permissions = []  # VACÍO - INVÁLIDO
                queryset = Reporte.objects.all()
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 1, "Lista vacía debe ser violación"


class TestViewSetExclusions:
    """Tests de exclusión de ViewSets."""

    @pytest.fixture
    def agent(self):
        return RouteLintAgent(verbose=False)

    def test_ignores_non_viewset_classes(self, agent, tmp_path):
        """
        Test: Ignora clases que no son ViewSets.

        Caso: Clase regular que no hereda de ViewSet.
        Esperado: Sin violaciones (clase ignorada).
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            class RegularClass:
                '''Clase regular, NO es ViewSet'''
                def some_method(self):
                    pass
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 0, "Clases no-ViewSet deben ser ignoradas"

    def test_ignores_base_viewsets(self, agent, tmp_path):
        """
        Test: Ignora ViewSets base/abstractos.

        Caso: ViewSet con 'Base' en el nombre.
        Esperado: Sin violaciones (ViewSet base ignorado).
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class BaseViewSet(viewsets.ModelViewSet):
                '''ViewSet base - NO requiere permisos'''
                pass
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 0, "ViewSets base deben ser ignorados"

    def test_ignores_abstract_viewsets(self, agent, tmp_path):
        """
        Test: Ignora ViewSets con Meta abstract.

        Caso: ViewSet con class Meta: abstract = True.
        Esperado: Sin violaciones.
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class AbstractViewSet(viewsets.ModelViewSet):
                class Meta:
                    abstract = True
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 0, "ViewSets abstractos deben ser ignorados"

    def test_detects_multiple_viewsets(self, agent, tmp_path):
        """
        Test: Detecta múltiples ViewSets en un archivo.

        Caso: Archivo con 3 ViewSets, 1 sin permisos.
        Esperado: 1 violación detectada.
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets
            from apps.permissions.mixins import PermisoMixin

            class ViewSet1(PermisoMixin, viewsets.ModelViewSet):
                pass  # OK

            class ViewSet2(viewsets.ModelViewSet):
                required_permissions = ['sistema.test.ver']  # OK

            class ViewSet3(viewsets.ModelViewSet):
                pass  # VIOLATION
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 1, "Debe detectar solo 1 violación"
        assert violations[0].class_name == "ViewSet3"


class TestFileExclusions:
    """Tests de exclusión de archivos."""

    @pytest.fixture
    def agent(self):
        return RouteLintAgent(verbose=False)

    def test_excludes_test_files(self, agent, tmp_path):
        """
        Test: Excluye archivos de tests.

        Caso: Archivo con 'test' en el path.
        Esperado: Archivo no analizado.
        """
        # Arrange: Crear estructura con tests
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        view_file = test_dir / "test_views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class TestViewSet(viewsets.ModelViewSet):
                pass  # Test fixture, no debe ser analizado
        """))

        # Act
        files = agent._find_view_files(tmp_path)

        # Assert
        assert len(files) == 0, "Archivos de test deben ser excluidos"

    def test_excludes_migrations(self, agent, tmp_path):
        """
        Test: Excluye archivos en migrations/.

        Caso: views.py dentro de carpeta migrations/.
        Esperado: Archivo no analizado.
        """
        # Arrange
        migrations_dir = tmp_path / "migrations"
        migrations_dir.mkdir()
        view_file = migrations_dir / "views.py"
        view_file.write_text("# Migration file")

        # Act
        files = agent._find_view_files(tmp_path)

        # Assert
        assert len(files) == 0, "Migrations deben ser excluidas"


class TestErrorHandling:
    """Tests de manejo de errores."""

    @pytest.fixture
    def agent(self):
        return RouteLintAgent(verbose=False)

    def test_handles_syntax_errors_gracefully(self, agent, tmp_path):
        """
        Test: Maneja errores de sintaxis sin fallar.

        Caso: Archivo con sintaxis Python inválida.
        Esperado: Sin crash, archivo skip con warning.
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class BrokenViewSet(viewsets.ModelViewSet
                # Falta cerrar paréntesis - SYNTAX ERROR
                pass
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 0, "Syntax error debe ser manejado gracefully"

    def test_handles_unreadable_files(self, agent, tmp_path):
        """
        Test: Maneja archivos no legibles.

        Caso: Archivo que no se puede leer.
        Esperado: Sin crash, archivo skip.
        """
        # Arrange: Crear archivo
        view_file = tmp_path / "views.py"
        view_file.write_text("content")

        # Simular archivo no legible (permisos)
        import os
        os.chmod(view_file, 0o000)

        try:
            # Act
            violations = agent._analyze_file(view_file, tmp_path)

            # Assert
            assert len(violations) == 0
        finally:
            # Cleanup: Restaurar permisos
            os.chmod(view_file, 0o644)


class TestOutputFormat:
    """Tests del formato de salida."""

    @pytest.fixture
    def agent(self):
        return RouteLintAgent(verbose=False)

    def test_violation_dataclass_structure(self, agent):
        """
        Test: Violación tiene estructura esperada.

        Verifica que Violation tenga todos los campos requeridos.
        """
        # Arrange & Act
        violation = Violation(
            file="test.py",
            line=42,
            class_name="TestViewSet",
            issue="No permissions",
            severity="high",
            suggestion="Add permissions"
        )

        # Assert
        assert violation.file == "test.py"
        assert violation.line == 42
        assert violation.class_name == "TestViewSet"
        assert violation.severity == "high"

    def test_lint_result_json_serializable(self, agent, tmp_path):
        """
        Test: LintResult es serializable a JSON.

        Caso: Resultado completo del análisis.
        Esperado: JSON válido.
        """
        # Arrange: Crear proyecto mock
        api_dir = tmp_path / "api" / "callcentersite"
        api_dir.mkdir(parents=True)

        view_file = api_dir / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class TestViewSet(viewsets.ModelViewSet):
                pass
        """))

        # Act
        result = agent.analyze_viewsets(tmp_path)

        # Assert: Debe ser convertible a JSON
        import json
        from dataclasses import asdict

        json_str = json.dumps(asdict(result), default=str)
        assert json_str
        assert "status" in json_str
        assert "violations" in json_str

    def test_text_report_format(self, agent, tmp_path):
        """
        Test: Reporte de texto tiene formato esperado.

        Caso: Generar reporte legible.
        Esperado: Contiene secciones esperadas.
        """
        # Arrange
        api_dir = tmp_path / "api" / "callcentersite"
        api_dir.mkdir(parents=True)

        view_file = api_dir / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class TestViewSet(viewsets.ModelViewSet):
                pass
        """))

        # Act
        result = agent.analyze_viewsets(tmp_path)
        report = agent.generate_report(result, format="text")

        # Assert
        assert "Route Lint Gate" in report
        assert "Analyzed:" in report
        assert "ViewSets:" in report
        assert "Coverage:" in report
        assert ("PASS" in report) or ("FAIL" in report)


class TestSeverityDetection:
    """Tests de detección de severidad."""

    @pytest.fixture
    def agent(self):
        return RouteLintAgent(verbose=False)

    def test_high_severity_for_crud_methods(self, agent, tmp_path):
        """
        Test: Severidad alta para métodos CRUD peligrosos.

        Caso: ViewSet con métodos create/update/destroy.
        Esperado: Severidad = "high".
        """
        # Arrange
        view_file = tmp_path / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class DangerousViewSet(viewsets.ModelViewSet):
                def create(self, request):
                    pass  # Método peligroso

                def destroy(self, request, pk=None):
                    pass  # Método peligroso
        """))

        # Act
        violations = agent._analyze_file(view_file, tmp_path)

        # Assert
        assert len(violations) == 1
        assert violations[0].severity == "high"


class TestCoverageCalculation:
    """Tests de cálculo de cobertura."""

    @pytest.fixture
    def agent(self):
        return RouteLintAgent(verbose=False)

    def test_calculates_coverage_correctly(self, agent):
        """
        Test: Calcula cobertura correctamente.

        Caso: 3 ViewSets, 2 con permisos.
        Esperado: Coverage = 66.7%.
        """
        # Arrange
        agent.stats.total_viewsets = 3
        agent.stats.viewsets_with_permissions = 2

        # Act
        coverage = agent._calculate_coverage()

        # Assert
        assert coverage == pytest.approx(66.7, rel=0.1)

    def test_100_percent_coverage_with_no_viewsets(self, agent):
        """
        Test: 100% cobertura si no hay ViewSets.

        Caso: Proyecto sin ViewSets.
        Esperado: Coverage = 100%.
        """
        # Arrange
        agent.stats.total_viewsets = 0
        agent.stats.viewsets_with_permissions = 0

        # Act
        coverage = agent._calculate_coverage()

        # Assert
        assert coverage == 100.0


class TestIntegration:
    """Tests de integración end-to-end."""

    @pytest.fixture
    def agent(self):
        return RouteLintAgent(verbose=False)

    def test_full_analysis_pass(self, agent, tmp_path):
        """
        Test E2E: Análisis completo que pasa.

        Caso: Proyecto con todos los ViewSets con permisos.
        Esperado: Status = "pass", exit code = 0.
        """
        # Arrange: Crear proyecto mock
        api_dir = tmp_path / "api" / "callcentersite"
        api_dir.mkdir(parents=True)

        view_file = api_dir / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets
            from apps.permissions.mixins import PermisoMixin

            class ViewSet1(PermisoMixin, viewsets.ModelViewSet):
                pass

            class ViewSet2(viewsets.ModelViewSet):
                required_permissions = ['sistema.test.ver']
        """))

        # Act
        result = agent.analyze_viewsets(tmp_path)

        # Assert
        assert result.status == "pass"
        assert len(result.violations) == 0
        assert result.coverage_percent == 100.0

    def test_full_analysis_fail(self, agent, tmp_path):
        """
        Test E2E: Análisis completo que falla.

        Caso: Proyecto con ViewSets sin permisos.
        Esperado: Status = "fail", exit code = 1.
        """
        # Arrange
        api_dir = tmp_path / "api" / "callcentersite"
        api_dir.mkdir(parents=True)

        view_file = api_dir / "views.py"
        view_file.write_text(dedent("""
            from rest_framework import viewsets

            class BadViewSet1(viewsets.ModelViewSet):
                pass  # VIOLATION

            class BadViewSet2(viewsets.ModelViewSet):
                pass  # VIOLATION
        """))

        # Act
        result = agent.analyze_viewsets(tmp_path)

        # Assert
        assert result.status == "fail"
        assert len(result.violations) == 2
        assert result.coverage_percent == 0.0


# Markers para pytest
pytestmark = [
    pytest.mark.unit,
    pytest.mark.permissions
]
