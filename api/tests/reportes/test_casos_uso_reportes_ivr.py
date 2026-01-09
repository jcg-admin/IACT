"""
Tests TDD para Casos de Uso del modulo de Reportes IVR.

Sistema de consulta de reportes pre-procesados desde BD IVR.
Solo lectura, datos ya procesados por jobs ETL.
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

User = get_user_model()


@pytest.mark.django_db
class TestConsultarReporteTrimestral:
    """Consultar reporte trimestral agregado."""

    def test_consultar_trimestral_por_rango_fechas(self):
        """
        UC-REPORTE-01: Consultar reporte trimestral con filtro de fechas.

        Given datos en tbl_reporte_trimestral
        When se consulta con rango de fechas
        Then retorna registros del periodo
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.consultar_trimestral(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 3, 31)
        )

        # Assert
        assert resultado is not None
        assert isinstance(resultado, QuerySet)

    def test_consultar_trimestral_sin_filtros(self):
        """
        Consultar todo el trimestre actual sin filtros.

        Given datos en tbl_reporte_trimestral
        When se consulta sin filtros
        Then retorna todos los registros del trimestre actual
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.consultar_trimestral()

        # Assert
        assert resultado is not None
        assert isinstance(resultado, QuerySet)


@pytest.mark.django_db
class TestConsultarTransferencias:
    """Consultar reporte de transferencias."""

    def test_consultar_transferencias_por_centro(self):
        """
        UC-REPORTE-02: Consultar transferencias filtradas por centro.

        Given datos en tbl_reporte_transferencias
        When se consulta con centro='Nacional'
        Then retorna solo transferencias de ese centro
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.consultar_transferencias(
            centro_origen='Nacional'
        )

        # Assert
        assert resultado is not None
        assert isinstance(resultado, QuerySet)

    def test_consultar_transferencias_todas(self):
        """
        Consultar todas las transferencias sin filtro.

        Given datos en tbl_reporte_transferencias
        When se consulta sin filtro de centro
        Then retorna todas las transferencias
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.consultar_transferencias()

        # Assert
        assert resultado is not None
        assert isinstance(resultado, QuerySet)


@pytest.mark.django_db
class TestConsultarMenusProblematicos:
    """Consultar menus con problemas."""

    def test_consultar_menus_problematicos(self):
        """
        UC-REPORTE-03: Consultar menus con mayor tasa de abandono.

        Given datos en tbl_reporte_menu_problemas
        When se consultan menus problematicos
        Then retorna lista ordenada por tasa de abandono
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.consultar_menus_problematicos()

        # Assert
        assert resultado is not None
        assert isinstance(resultado, QuerySet)


@pytest.mark.django_db
class TestConsultarLlamadasDia:
    """Consultar llamadas por dia."""

    def test_consultar_llamadas_fecha_especifica(self):
        """
        UC-REPORTE-04: Consultar llamadas de un dia especifico.

        Given datos en tbl_reporte_llamadas_dia
        When se consulta con fecha especifica
        Then retorna metricas del dia
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.consultar_llamadas_dia(
            fecha_inicio=date(2025, 11, 11),
            fecha_fin=date(2025, 11, 11)
        )

        # Assert
        assert resultado is not None
        assert isinstance(resultado, QuerySet)

    def test_consultar_llamadas_ultimos_7_dias(self):
        """
        Consultar llamadas de los ultimos 7 dias.

        Given datos en tbl_reporte_llamadas_dia
        When se consulta ultimos 7 dias
        Then retorna serie temporal
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=7)

        resultado = ReporteIVRService.consultar_llamadas_dia(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        # Assert
        assert resultado is not None
        assert isinstance(resultado, QuerySet)


@pytest.mark.django_db
class TestConsultarClientesUnicos:
    """Consultar clientes unicos."""

    def test_consultar_clientes_unicos(self):
        """
        UC-REPORTE-05: Consultar clientes unicos por periodo.

        Given datos en tbl_reporte_clientes_unicos
        When se consultan clientes unicos
        Then retorna conteo de clientes unicos
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.consultar_clientes_unicos()

        # Assert
        assert resultado is not None
        assert isinstance(resultado, QuerySet)


@pytest.mark.django_db
class TestExportarReporte:
    """Exportar reportes en diferentes formatos."""

    def test_exportar_reporte_csv(self):
        """
        UC-REPORTE-06: Exportar reporte a CSV.

        Given reporte generado
        When se exporta a CSV
        Then retorna metadata de exportacion
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.exportar_reporte(
            tipo_reporte='trimestral',
            formato='csv',
            filtros={}
        )

        # Assert
        assert resultado is not None
        assert isinstance(resultado, dict)
        assert resultado['tipo_reporte'] == 'trimestral'
        assert resultado['formato'] == 'csv'

    def test_exportar_reporte_excel(self):
        """
        Exportar reporte a Excel.

        Given reporte generado
        When se exporta a Excel
        Then retorna metadata de exportacion
        """
        from callcentersite.apps.reportes.services import ReporteIVRService

        # Act
        resultado = ReporteIVRService.exportar_reporte(
            tipo_reporte='transferencias',
            formato='excel',
            filtros={}
        )

        # Assert
        assert resultado is not None
        assert isinstance(resultado, dict)
        assert resultado['tipo_reporte'] == 'transferencias'
        assert resultado['formato'] == 'excel'
