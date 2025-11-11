"""Servicios del dashboard."""

from __future__ import annotations

import csv
from io import BytesIO, StringIO
from typing import Dict, List

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import DashboardConfiguration
from .widgets import WIDGET_REGISTRY, Widget

User = get_user_model()


class DashboardService:
    """Orquesta la construcción de respuestas para el dashboard."""

    @staticmethod
    def overview() -> Dict[str, object]:
        """Retorna overview general del dashboard (legacy)."""
        now = timezone.now()
        return {
            "last_update": now.isoformat(),
            "widgets": [
                widget.__dict__ for widget in DashboardService.available_widgets()
            ],
        }

    @staticmethod
    def available_widgets() -> List[Widget]:
        """Retorna todos los widgets disponibles en el sistema."""
        return list(WIDGET_REGISTRY.values())

    @staticmethod
    def ver_dashboard(usuario_id: int) -> Dict[str, object]:
        """
        UC-020: Ver Dashboard.

        Retorna el dashboard personalizado del usuario con datos actualizados.

        Args:
            usuario_id: ID del usuario

        Returns:
            Diccionario con widgets y última actualización

        Ejemplo:
            >>> dashboard = DashboardService.ver_dashboard(usuario_id=1)
            >>> print(dashboard['widgets'])
        """
        try:
            config = DashboardConfiguration.objects.get(user_id=usuario_id)
            widget_types = config.widgets
        except DashboardConfiguration.DoesNotExist:
            # Si no tiene configuración, usar widgets por defecto
            widget_types = list(WIDGET_REGISTRY.keys())

        # Obtener widgets en el orden configurado
        widgets = []
        for widget_type in widget_types:
            if widget_type in WIDGET_REGISTRY:
                widgets.append(WIDGET_REGISTRY[widget_type].__dict__)

        return {
            "last_update": timezone.now().isoformat(),
            "widgets": widgets
        }

    @staticmethod
    def personalizar_dashboard(
        usuario_id: int,
        widgets: List[str]
    ) -> DashboardConfiguration:
        """
        UC-021: Personalizar Dashboard.

        Guarda la configuración de widgets del usuario.

        Args:
            usuario_id: ID del usuario
            widgets: Lista ordenada de tipos de widgets

        Returns:
            Configuración guardada

        Raises:
            ValidationError: Si algún widget no existe
            ObjectDoesNotExist: Si usuario no existe

        Ejemplo:
            >>> config = DashboardService.personalizar_dashboard(
            ...     usuario_id=1,
            ...     widgets=['total_calls', 'avg_duration']
            ... )
        """
        # Validar que usuario existe
        usuario = User.objects.get(id=usuario_id)

        # Validar que todos los widgets existen
        for widget_type in widgets:
            if widget_type not in WIDGET_REGISTRY:
                raise ValidationError(f'Widget "{widget_type}" no existe')

        # Crear o actualizar configuración
        config, created = DashboardConfiguration.objects.update_or_create(
            user=usuario,
            defaults={'widgets': widgets}
        )

        return config

    @staticmethod
    def exportar_dashboard(
        usuario_id: int,
        formato: str = 'csv'
    ) -> str | bytes:
        """
        UC-022: Exportar Dashboard.

        Exporta los datos actuales del dashboard en el formato solicitado.

        Args:
            usuario_id: ID del usuario
            formato: Formato de exportación ('csv' o 'pdf')

        Returns:
            String con CSV o bytes con PDF

        Raises:
            ValidationError: Si formato no es válido

        Ejemplo:
            >>> csv_data = DashboardService.exportar_dashboard(
            ...     usuario_id=1,
            ...     formato='csv'
            ... )
        """
        dashboard = DashboardService.ver_dashboard(usuario_id=usuario_id)

        if formato == 'csv':
            return DashboardService._exportar_csv(dashboard)
        elif formato == 'pdf':
            return DashboardService._exportar_pdf(dashboard)
        else:
            raise ValidationError(f'Formato "{formato}" no soportado')

    @staticmethod
    def _exportar_csv(dashboard: Dict[str, object]) -> str:
        """Convierte dashboard a formato CSV."""
        output = StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow(['Widget', 'Título', 'Valor', 'Cambio', 'Período'])

        # Datos
        for widget in dashboard['widgets']:
            writer.writerow([
                widget.get('type', ''),
                widget.get('title', ''),
                widget.get('value', ''),
                widget.get('change', ''),
                widget.get('period', '')
            ])

        return output.getvalue()

    @staticmethod
    def _exportar_pdf(dashboard: Dict[str, object]) -> bytes:
        """Convierte dashboard a formato PDF."""
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        # Título
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(100, 750, "Dashboard Report")

        # Fecha
        pdf.setFont("Helvetica", 10)
        pdf.drawString(100, 730, f"Generated: {dashboard['last_update']}")

        # Widgets
        y_position = 700
        pdf.setFont("Helvetica", 12)
        for widget in dashboard['widgets']:
            pdf.drawString(100, y_position, f"{widget.get('title', '')}: {widget.get('value', '')}")
            y_position -= 20

        pdf.save()
        return buffer.getvalue()

    @staticmethod
    def compartir_dashboard(
        usuario_origen_id: int,
        usuario_destino_id: int
    ) -> DashboardConfiguration:
        """
        UC-023: Compartir Dashboard.

        Copia la configuración de dashboard de un usuario a otro.

        Args:
            usuario_origen_id: ID del usuario que comparte
            usuario_destino_id: ID del usuario que recibe

        Returns:
            Configuración creada/actualizada en usuario destino

        Raises:
            ObjectDoesNotExist: Si algún usuario no existe

        Ejemplo:
            >>> config = DashboardService.compartir_dashboard(
            ...     usuario_origen_id=1,
            ...     usuario_destino_id=2
            ... )
        """
        # Validar que usuarios existen
        usuario_origen = User.objects.get(id=usuario_origen_id)
        usuario_destino = User.objects.get(id=usuario_destino_id)

        # Obtener configuración origen
        try:
            config_origen = DashboardConfiguration.objects.get(user=usuario_origen)
            widgets = config_origen.widgets
        except DashboardConfiguration.DoesNotExist:
            # Si origen no tiene configuración, usar default
            widgets = list(WIDGET_REGISTRY.keys())

        # Copiar a destino
        config_destino, created = DashboardConfiguration.objects.update_or_create(
            user=usuario_destino,
            defaults={'widgets': widgets}
        )

        return config_destino
