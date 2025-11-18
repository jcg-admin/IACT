"""Servicios del dashboard."""

from __future__ import annotations

from typing import Dict, List, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from callcentersite.apps.users.models_permisos_granular import AuditoriaPermiso
from callcentersite.apps.users.service_helpers import (
    auditar_accion_exitosa,
    validar_usuario_existe,
    verificar_permiso_y_auditar,
)
from callcentersite.apps.users.services_permisos_granular import UserManagementService

from .models import DashboardConfiguracion
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
    def exportar(
        usuario_id: int,
        formato: str = 'pdf',
    ) -> Dict[str, object]:
        """
        Exporta dashboard a PDF o Excel.

        Args:
            usuario_id: ID del usuario que exporta
            formato: Formato de exportacion ('pdf' o 'excel')

        Returns:
            Diccionario con datos de exportacion:
                - formato: str
                - archivo: str (path o URL del archivo)
                - timestamp: str

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si el formato es invalido

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 26)
        """
        # Verificar permiso y auditar
        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.exportar',
            recurso_tipo='dashboard',
            accion='exportar',
            mensaje_error='No tiene permiso para exportar dashboards',
        )

        # Validar formato
        if formato not in ['pdf', 'excel']:
            raise ValidationError(f'Formato invalido: {formato}. Use pdf o excel')

        # TODO: Implementar logica real de exportacion
        # Por ahora retornamos un placeholder
        archivo = f'/tmp/dashboard_{usuario_id}_{timezone.now().timestamp()}.{formato}'

        # Auditar acción exitosa
        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.exportar',
            recurso_tipo='dashboard',
            accion='exportar',
            detalles=f'Dashboard exportado a {formato}',
        )

        return {
            'formato': formato,
            'archivo': archivo,
            'timestamp': timezone.now().isoformat(),
        }

    @staticmethod
    def personalizar(
        usuario_id: int,
        configuracion: Dict,
    ) -> DashboardConfiguracion:
        """
        Guarda configuracion personalizada de dashboard.

        Args:
            usuario_id: ID del usuario
            configuracion: Diccionario con configuracion de widgets y layout

        Returns:
            Objeto DashboardConfiguracion guardado

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si la configuracion no es valida JSON

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 28)
        """
        # Verificar permiso y auditar
        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.personalizar',
            recurso_tipo='dashboard',
            accion='personalizar',
            mensaje_error='No tiene permiso para personalizar dashboards',
        )

        # Validar que configuracion sea dict
        if not isinstance(configuracion, dict):
            raise ValidationError('Configuracion debe ser un objeto JSON')

        # Guardar o actualizar configuracion
        config, created = DashboardConfiguracion.objects.update_or_create(
            usuario_id=usuario_id,
            defaults={'configuracion': configuracion},
        )

        # Auditar acción exitosa
        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.personalizar',
            recurso_tipo='dashboard',
            accion='personalizar',
            recurso_id=config.id,
            detalles=f'Dashboard personalizado. Widgets: {len(configuracion.get("widgets", []))}',
        )

        return config

    @staticmethod
    def compartir(
        usuario_id: int,
        compartir_con_usuario_id: Optional[int] = None,
        compartir_con_grupo_codigo: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Comparte dashboard con otro usuario o grupo.

        Args:
            usuario_id: ID del usuario que comparte
            compartir_con_usuario_id: ID del usuario receptor (opcional)
            compartir_con_grupo_codigo: Codigo del grupo receptor (opcional)

        Returns:
            Diccionario con resultado:
                - compartido_con: str (email o nombre de grupo)
                - tipo: str ('usuario' o 'grupo')
                - timestamp: str

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si no se especifica receptor o no existe

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 30)
        """
        # Verificar permiso y auditar
        verificar_permiso_y_auditar(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.compartir',
            recurso_tipo='dashboard',
            accion='compartir',
            mensaje_error='No tiene permiso para compartir dashboards',
        )

        # Validar que se especifico al menos un receptor
        if not compartir_con_usuario_id and not compartir_con_grupo_codigo:
            raise ValidationError(
                'Debe especificar compartir_con_usuario_id o compartir_con_grupo_codigo'
            )

        compartido_con = None
        tipo = None

        # Compartir con usuario
        if compartir_con_usuario_id:
            try:
                usuario_receptor = User.objects.get(
                    id=compartir_con_usuario_id,
                    is_deleted=False,
                )
                compartido_con = usuario_receptor.email
                tipo = 'usuario'
            except User.DoesNotExist:
                raise ValidationError(
                    f'Usuario receptor no encontrado: {compartir_con_usuario_id}'
                )

        # Compartir con grupo
        if compartir_con_grupo_codigo:
            from callcentersite.apps.users.models_permisos_granular import GrupoPermiso
            try:
                grupo = GrupoPermiso.objects.get(codigo=compartir_con_grupo_codigo)
                compartido_con = grupo.nombre
                tipo = 'grupo'
            except GrupoPermiso.DoesNotExist:
                raise ValidationError(
                    f'Grupo no encontrado: {compartir_con_grupo_codigo}'
                )

        # TODO: Implementar logica real de compartir
        # (crear registro en tabla compartidos, enviar notificacion, etc.)

        # Auditar acción exitosa
        auditar_accion_exitosa(
            usuario_id=usuario_id,
            capacidad_codigo='sistema.vistas.dashboards.compartir',
            recurso_tipo='dashboard',
            accion='compartir',
            detalles=f'Dashboard compartido con {tipo}: {compartido_con}',
        )

        return {
            'compartido_con': compartido_con,
            'tipo': tipo,
            'timestamp': timezone.now().isoformat(),
        }
