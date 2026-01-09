"""Tests de API REST para reportes IVR."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from callcentersite.apps.reportes.models import (
    ReporteClientesUnicos,
    ReporteLlamadasDia,
    ReporteMenuProblemas,
    ReporteTransferencias,
    ReporteTrimestral,
)

User = get_user_model()


@pytest.mark.django_db
class TestReporteTrimestralAPI:
    """Tests para API REST de reportes trimestrales."""

    def setup_method(self):
        """Configuracion inicial para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_listar_reportes_trimestrales(self):
        """UC-REPORTE-01: Listar reportes trimestrales."""
        # Crear reportes de prueba
        ReporteTrimestral.objects.create(
            trimestre="Q1",
            anio=2025,
            total_llamadas=1000,
            llamadas_atendidas=900,
            llamadas_abandonadas=100,
            tiempo_promedio_espera=45.5,
            tiempo_promedio_atencion=120.0,
            nivel_servicio=90.0,
            tasa_abandono=10.0,
        )
        ReporteTrimestral.objects.create(
            trimestre="Q2",
            anio=2025,
            total_llamadas=1200,
            llamadas_atendidas=1080,
            llamadas_abandonadas=120,
            tiempo_promedio_espera=50.0,
            tiempo_promedio_atencion=115.0,
            nivel_servicio=90.0,
            tasa_abandono=10.0,
        )

        response = self.client.get("/api/v1/reportes/trimestral/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_api_filtrar_reportes_trimestrales_por_anio(self):
        """UC-REPORTE-01: Filtrar reportes trimestrales por anio."""
        ReporteTrimestral.objects.create(
            trimestre="Q1",
            anio=2025,
            total_llamadas=1000,
            llamadas_atendidas=900,
            llamadas_abandonadas=100,
        )
        ReporteTrimestral.objects.create(
            trimestre="Q1",
            anio=2024,
            total_llamadas=800,
            llamadas_atendidas=700,
            llamadas_abandonadas=100,
        )

        response = self.client.get("/api/v1/reportes/trimestral/?anio=2025")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["anio"] == 2025

    def test_api_obtener_reporte_trimestral_detalle(self):
        """UC-REPORTE-01: Obtener detalle de un reporte trimestral."""
        reporte = ReporteTrimestral.objects.create(
            trimestre="Q1",
            anio=2025,
            total_llamadas=1000,
            llamadas_atendidas=900,
            llamadas_abandonadas=100,
            tiempo_promedio_espera=45.5,
            tiempo_promedio_atencion=120.0,
            nivel_servicio=90.0,
            tasa_abandono=10.0,
        )

        response = self.client.get(f"/api/v1/reportes/trimestral/{reporte.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["trimestre"] == "Q1"
        assert response.data["anio"] == 2025
        assert response.data["total_llamadas"] == 1000


@pytest.mark.django_db
class TestReporteTransferenciasAPI:
    """Tests para API REST de reportes de transferencias."""

    def setup_method(self):
        """Configuracion inicial para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_listar_reportes_transferencias(self):
        """UC-REPORTE-02: Listar reportes de transferencias."""
        ReporteTransferencias.objects.create(
            fecha=date.today(),
            centro_origen="Nacional",
            centro_destino="Puebla",
            total_transferencias=50,
            transferencias_exitosas=45,
            transferencias_fallidas=5,
            tiempo_promedio_transferencia=30.0,
            tasa_exito=90.0,
        )

        response = self.client.get("/api/v1/reportes/transferencias/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_api_filtrar_transferencias_por_centro_origen(self):
        """UC-REPORTE-02: Filtrar transferencias por centro de origen."""
        ReporteTransferencias.objects.create(
            fecha=date.today(),
            centro_origen="Nacional",
            centro_destino="Puebla",
            total_transferencias=50,
            transferencias_exitosas=45,
            transferencias_fallidas=5,
        )
        ReporteTransferencias.objects.create(
            fecha=date.today(),
            centro_origen="Puebla",
            centro_destino="Nacional",
            total_transferencias=30,
            transferencias_exitosas=28,
            transferencias_fallidas=2,
        )

        response = self.client.get(
            "/api/v1/reportes/transferencias/?centro_origen=Nacional"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["centro_origen"] == "Nacional"


@pytest.mark.django_db
class TestReporteMenuProblemasAPI:
    """Tests para API REST de reportes de menus problematicos."""

    def setup_method(self):
        """Configuracion inicial para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_listar_menus_problematicos(self):
        """UC-REPORTE-03: Listar menus problematicos."""
        ReporteMenuProblemas.objects.create(
            fecha=date.today(),
            menu_id="M001",
            menu_nombre="Menu Principal",
            veces_accedido=100,
            abandonos=20,
            timeout=5,
            errores=3,
            tasa_abandono=20.0,
            tiempo_promedio_permanencia=15.5,
        )

        response = self.client.get("/api/v1/reportes/menus-problematicos/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_api_filtrar_menus_por_tasa_abandono(self):
        """UC-REPORTE-03: Filtrar menus por tasa de abandono minima."""
        ReporteMenuProblemas.objects.create(
            fecha=date.today(),
            menu_id="M001",
            menu_nombre="Menu Alto Abandono",
            veces_accedido=100,
            abandonos=30,
            tasa_abandono=30.0,
        )
        ReporteMenuProblemas.objects.create(
            fecha=date.today(),
            menu_id="M002",
            menu_nombre="Menu Bajo Abandono",
            veces_accedido=100,
            abandonos=5,
            tasa_abandono=5.0,
        )

        response = self.client.get(
            "/api/v1/reportes/menus-problematicos/?tasa_abandono_minima=20"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["menu_nombre"] == "Menu Alto Abandono"


@pytest.mark.django_db
class TestReporteLlamadasDiaAPI:
    """Tests para API REST de reportes de llamadas por dia."""

    def setup_method(self):
        """Configuracion inicial para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_listar_llamadas_dia(self):
        """UC-REPORTE-04: Listar llamadas por dia."""
        ReporteLlamadasDia.objects.create(
            fecha=date.today(),
            hora=9,
            total_llamadas=50,
            llamadas_atendidas=45,
            llamadas_abandonadas=5,
            tiempo_promedio_espera=30.0,
            tiempo_promedio_atencion=120.0,
            nivel_servicio=90.0,
        )

        response = self.client.get("/api/v1/reportes/llamadas-dia/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_api_filtrar_llamadas_por_hora(self):
        """UC-REPORTE-04: Filtrar llamadas por hora especifica."""
        ReporteLlamadasDia.objects.create(
            fecha=date.today(),
            hora=9,
            total_llamadas=50,
            llamadas_atendidas=45,
            llamadas_abandonadas=5,
        )
        ReporteLlamadasDia.objects.create(
            fecha=date.today(),
            hora=14,
            total_llamadas=80,
            llamadas_atendidas=75,
            llamadas_abandonadas=5,
        )

        response = self.client.get("/api/v1/reportes/llamadas-dia/?hora=9")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["hora"] == 9


@pytest.mark.django_db
class TestReporteClientesUnicosAPI:
    """Tests para API REST de reportes de clientes unicos."""

    def setup_method(self):
        """Configuracion inicial para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_listar_clientes_unicos(self):
        """UC-REPORTE-05: Listar reportes de clientes unicos."""
        ReporteClientesUnicos.objects.create(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 31),
            total_clientes_unicos=500,
            nuevos_clientes=100,
            clientes_recurrentes=400,
            promedio_llamadas_cliente=2.5,
        )

        response = self.client.get("/api/v1/reportes/clientes-unicos/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_api_obtener_detalle_clientes_unicos(self):
        """UC-REPORTE-05: Obtener detalle de reporte de clientes unicos."""
        reporte = ReporteClientesUnicos.objects.create(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 31),
            total_clientes_unicos=500,
            nuevos_clientes=100,
            clientes_recurrentes=400,
            promedio_llamadas_cliente=2.5,
        )

        response = self.client.get(f"/api/v1/reportes/clientes-unicos/{reporte.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_clientes_unicos"] == 500
        assert response.data["nuevos_clientes"] == 100


@pytest.mark.django_db
class TestExportarReporteAPI:
    """Tests para API REST de exportacion de reportes."""

    def setup_method(self):
        """Configuracion inicial para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_exportar_reporte_trimestral_csv(self):
        """UC-REPORTE-06: Exportar reporte trimestral en CSV."""
        # Crear datos de prueba
        ReporteTrimestral.objects.create(
            trimestre="Q1",
            anio=2025,
            total_llamadas=1000,
            llamadas_atendidas=900,
            llamadas_abandonadas=100,
        )

        payload = {
            "tipo_reporte": "trimestral",
            "formato": "csv",
            "filtros": {"anio": 2025},
        }

        response = self.client.post(
            "/api/v1/reportes/exportar/exportar/", data=payload, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["tipo_reporte"] == "trimestral"
        assert response.data["formato"] == "csv"
        assert response.data["total_registros"] >= 0

    def test_api_exportar_reporte_tipo_invalido(self):
        """UC-REPORTE-06: Validar tipo de reporte invalido."""
        payload = {
            "tipo_reporte": "invalido",
            "formato": "csv",
        }

        response = self.client.post(
            "/api/v1/reportes/exportar/exportar/", data=payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data or "tipo_reporte" in response.data
