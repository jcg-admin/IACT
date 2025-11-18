"""
Tests TDD para Casos de Uso del módulo de Dashboards.

Sistema de visualización y personalización de dashboards.
Casos de uso implementados siguiendo TDD.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUC020_VerDashboard:
    """
    UC-020: Ver Dashboard.

    Actor: Usuario autenticado
    Precondición: Usuario tiene permiso "sistema.vistas.dashboards.ver"

    Flujo principal:
    1. Sistema recibe solicitud de dashboard
    2. Sistema obtiene configuración del usuario
    3. Sistema agrega datos de widgets configurados
    4. Sistema retorna dashboard con datos actualizados
    """

    def test_ver_dashboard_personal(self):
        """
        UC-020 Escenario 1: Ver dashboard personal con configuración por defecto.

        Given usuario autenticado sin configuración personalizada
        When solicita ver su dashboard
        Then retorna dashboard con widgets por defecto
          And incluye datos actualizados
        """
        # Arrange
        usuario = User.objects.create_user(
            username='test.user',
            password='pass',
            email='test@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService

        # Act
        dashboard = DashboardService.ver_dashboard(usuario_id=usuario.id)

        # Assert
        assert dashboard is not None
        assert 'widgets' in dashboard
        assert isinstance(dashboard['widgets'], list)
        assert len(dashboard['widgets']) > 0
        # Verificar que tiene timestamp
        assert 'last_update' in dashboard

    def test_ver_dashboard_con_widgets_personalizados(self):
        """
        UC-020 Escenario 2: Ver dashboard con widgets personalizados.

        Given usuario con configuración personalizada
        When solicita ver su dashboard
        Then retorna solo widgets configurados
          And respeta el orden definido
        """
        # Arrange
        usuario = User.objects.create_user(
            username='custom.user',
            password='pass',
            email='custom@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService

        # Personalizar primero
        DashboardService.personalizar_dashboard(
            usuario_id=usuario.id,
            widgets=['total_calls', 'avg_duration']
        )

        # Act
        dashboard = DashboardService.ver_dashboard(usuario_id=usuario.id)

        # Assert
        assert len(dashboard['widgets']) == 2
        widget_types = [w['type'] for w in dashboard['widgets']]
        assert 'total_calls' in widget_types
        assert 'avg_duration' in widget_types


@pytest.mark.django_db
class TestUC021_PersonalizarDashboard:
    """
    UC-021: Personalizar Dashboard.

    Actor: Usuario autenticado
    Precondición: Usuario tiene permiso "sistema.vistas.dashboards.personalizar"

    Flujo principal:
    1. Sistema recibe configuración de widgets
    2. Sistema valida que widgets existen
    3. Sistema guarda configuración del usuario
    4. Sistema retorna confirmación
    """

    def test_personalizar_widgets_exitoso(self):
        """
        UC-021 Escenario 1: Personalizar widgets del dashboard.

        Given usuario con dashboard por defecto
        When personaliza la lista de widgets
        Then configuración es guardada
          And próxima vista usa nueva configuración
        """
        # Arrange
        usuario = User.objects.create_user(
            username='custom.user',
            password='pass',
            email='custom@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService

        # Act
        resultado = DashboardService.personalizar_dashboard(
            usuario_id=usuario.id,
            widgets=['total_calls']
        )

        # Assert
        assert resultado is not None
        # Verificar que se guardó
        dashboard = DashboardService.ver_dashboard(usuario_id=usuario.id)
        assert len(dashboard['widgets']) == 1
        assert dashboard['widgets'][0]['type'] == 'total_calls'

    def test_personalizar_orden_widgets(self):
        """
        UC-021 Escenario 2: Cambiar orden de widgets.

        Given usuario con widgets configurados
        When cambia el orden de widgets
        Then nuevo orden es respetado
        """
        # Arrange
        usuario = User.objects.create_user(
            username='reorder.user',
            password='pass',
            email='reorder@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService

        # Act - Orden específico
        DashboardService.personalizar_dashboard(
            usuario_id=usuario.id,
            widgets=['avg_duration', 'total_calls']
        )

        # Assert
        dashboard = DashboardService.ver_dashboard(usuario_id=usuario.id)
        widget_types = [w['type'] for w in dashboard['widgets']]
        assert widget_types == ['avg_duration', 'total_calls']

    def test_personalizar_con_widget_invalido(self):
        """
        UC-021 Escenario 3: Intento de agregar widget inexistente.

        Given usuario autenticado
        When intenta agregar widget que no existe
        Then sistema lanza ValidationError
        """
        # Arrange
        usuario = User.objects.create_user(
            username='invalid.user',
            password='pass',
            email='invalid@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService
        from django.core.exceptions import ValidationError

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            DashboardService.personalizar_dashboard(
                usuario_id=usuario.id,
                widgets=['widget_inexistente']
            )

        assert 'widget' in str(exc_info.value).lower() or 'existe' in str(exc_info.value).lower()


@pytest.mark.django_db
class TestUC022_ExportarDashboard:
    """
    UC-022: Exportar Dashboard.

    Actor: Usuario autenticado
    Precondición: Usuario tiene permiso "sistema.vistas.dashboards.exportar"

    Flujo principal:
    1. Sistema recibe solicitud de exportación con formato
    2. Sistema genera snapshot de datos actuales
    3. Sistema convierte a formato solicitado (CSV/PDF)
    4. Sistema retorna archivo para descarga
    """

    def test_exportar_dashboard_csv(self):
        """
        UC-022 Escenario 1: Exportar dashboard a CSV.

        Given usuario con dashboard configurado
        When solicita exportar a CSV
        Then retorna datos en formato CSV
          And incluye todos los widgets visibles
        """
        # Arrange
        usuario = User.objects.create_user(
            username='export.user',
            password='pass',
            email='export@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService

        # Act
        csv_data = DashboardService.exportar_dashboard(
            usuario_id=usuario.id,
            formato='csv'
        )

        # Assert
        assert csv_data is not None
        assert isinstance(csv_data, str)
        # Verificar que contiene headers CSV
        assert ',' in csv_data or ';' in csv_data

    def test_exportar_dashboard_pdf(self):
        """
        UC-022 Escenario 2: Exportar dashboard a PDF.

        Given usuario con dashboard configurado
        When solicita exportar a PDF
        Then retorna datos en formato PDF (bytes)
        """
        # Arrange
        usuario = User.objects.create_user(
            username='pdf.user',
            password='pass',
            email='pdf@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService

        # Act
        pdf_data = DashboardService.exportar_dashboard(
            usuario_id=usuario.id,
            formato='pdf'
        )

        # Assert
        assert pdf_data is not None
        assert isinstance(pdf_data, bytes)
        # PDF debe empezar con magic bytes
        assert pdf_data.startswith(b'%PDF')


@pytest.mark.django_db
class TestUC023_CompartirDashboard:
    """
    UC-023: Compartir Dashboard.

    Actor: Usuario autenticado
    Precondición: Usuario tiene permiso "sistema.vistas.dashboards.compartir"

    Flujo principal:
    1. Sistema recibe configuración a compartir y usuario destino
    2. Sistema valida que usuario destino existe
    3. Sistema copia configuración al usuario destino
    4. Sistema notifica a usuario destino
    5. Sistema retorna confirmación
    """

    def test_compartir_configuracion_exitoso(self):
        """
        UC-023 Escenario 1: Compartir configuración de dashboard.

        Given usuario con configuración personalizada
        When comparte su configuración con otro usuario
        Then configuración es copiada
          And usuario destino puede verla
        """
        # Arrange
        usuario_origen = User.objects.create_user(
            username='share.from',
            password='pass',
            email='from@test.com'
        )
        usuario_destino = User.objects.create_user(
            username='share.to',
            password='pass',
            email='to@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService

        # Configurar dashboard origen
        DashboardService.personalizar_dashboard(
            usuario_id=usuario_origen.id,
            widgets=['total_calls', 'avg_duration']
        )

        # Act - Compartir
        resultado = DashboardService.compartir_dashboard(
            usuario_origen_id=usuario_origen.id,
            usuario_destino_id=usuario_destino.id
        )

        # Assert
        assert resultado is not None
        # Verificar que destino tiene la misma configuración
        dashboard_destino = DashboardService.ver_dashboard(usuario_id=usuario_destino.id)
        widget_types = [w['type'] for w in dashboard_destino['widgets']]
        assert 'total_calls' in widget_types
        assert 'avg_duration' in widget_types

    def test_compartir_a_usuario_inexistente(self):
        """
        UC-023 Escenario 2: Intento de compartir a usuario que no existe.

        Given usuario con configuración
        When intenta compartir a usuario inexistente
        Then sistema lanza ObjectDoesNotExist
        """
        # Arrange
        usuario_origen = User.objects.create_user(
            username='share.from',
            password='pass',
            email='from@test.com'
        )

        from callcentersite.apps.dashboard.services import DashboardService
        from django.core.exceptions import ObjectDoesNotExist

        # Act & Assert
        with pytest.raises(ObjectDoesNotExist):
            DashboardService.compartir_dashboard(
                usuario_origen_id=usuario_origen.id,
                usuario_destino_id=99999  # No existe
            )
