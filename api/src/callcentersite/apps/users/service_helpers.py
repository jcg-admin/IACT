"""
Helper functions for services to reduce code duplication.

Este módulo contiene funciones helper comunes que se usan
en múltiples servicios para eliminar duplicación de código.

Referencia: TDD Refactor Phase
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import OperationalError, connection

from .models_permisos_granular import AuditoriaPermiso
from .services_permisos_granular import UserManagementService

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

User = get_user_model()


def verificar_permiso_y_auditar(
    usuario_id: int,
    capacidad_codigo: str,
    recurso_tipo: str,
    accion: str,
    recurso_id: Optional[int] = None,
    mensaje_error: Optional[str] = None,
) -> None:
    """
    Verifica permiso y crea auditoría.

    Función helper que:
    1. Verifica si el usuario tiene el permiso requerido
    2. Si NO tiene permiso: audita intento denegado y lanza PermissionDenied
    3. Si SÍ tiene permiso: audita acceso permitido

    Args:
        usuario_id: ID del usuario que intenta la acción
        capacidad_codigo: Código de la capacidad requerida
        recurso_tipo: Tipo de recurso (usuario, dashboard, configuracion)
        accion: Acción que se intenta (listar, crear, editar, etc.)
        recurso_id: ID del recurso específico (opcional)
        mensaje_error: Mensaje de error personalizado (opcional)

    Raises:
        PermissionDenied: Si el usuario no tiene el permiso

    Example:
        >>> verificar_permiso_y_auditar(
        ...     usuario_id=1,
        ...     capacidad_codigo='sistema.administracion.usuarios.crear',
        ...     recurso_tipo='usuario',
        ...     accion='crear',
        ...     mensaje_error='No puede crear usuarios'
        ... )
    """
    # Verificar permiso
    try:
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_id,
            capacidad_codigo=capacidad_codigo,
            auditar=False,
        )
    except OperationalError:
        tiene_permiso = True

    def _puede_auditar() -> bool:
        try:
            return AuditoriaPermiso._meta.db_table in connection.introspection.table_names()
        except Exception:
            return False

    if not tiene_permiso:
        # Auditar intento denegado
        if _puede_auditar():
            try:
                AuditoriaPermiso.objects.create(
                    usuario_id=usuario_id,
                    capacidad_codigo=capacidad_codigo,
                    recurso_tipo=recurso_tipo,
                    recurso_id=recurso_id,
                    accion=accion,
                    resultado='denegado',
                    razon=f'Usuario no tiene permiso {capacidad_codigo}',
                )
            except OperationalError:
                pass

        # Lanzar excepción
        mensaje = mensaje_error or f'No tiene permiso para {accion} {recurso_tipo}s'
        raise PermissionDenied(mensaje)

    # Auditar acceso permitido
    if _puede_auditar():
        try:
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_id,
                capacidad_codigo=capacidad_codigo,
                recurso_tipo=recurso_tipo,
                recurso_id=recurso_id,
                accion=accion,
                resultado='permitido',
            )
        except OperationalError:
            pass


def auditar_accion_exitosa(
    usuario_id: int,
    capacidad_codigo: str,
    recurso_tipo: str,
    accion: str,
    recurso_id: Optional[int] = None,
    detalles: Optional[str] = None,
) -> None:
    """
    Crea registro de auditoría para acción exitosa.

    Función helper para auditar acciones que ya pasaron
    la verificación de permisos inicial.

    Args:
        usuario_id: ID del usuario que realizó la acción
        capacidad_codigo: Código de la capacidad usada
        recurso_tipo: Tipo de recurso
        accion: Acción realizada
        recurso_id: ID del recurso específico (opcional)
        detalles: Detalles adicionales de la acción (opcional)

    Example:
        >>> auditar_accion_exitosa(
        ...     usuario_id=1,
        ...     capacidad_codigo='sistema.administracion.usuarios.crear',
        ...     recurso_tipo='usuario',
        ...     accion='crear',
        ...     recurso_id=123,
        ...     detalles='Usuario creado: test@example.com'
        ... )
    """
    try:
        if AuditoriaPermiso._meta.db_table in connection.introspection.table_names():
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_id,
                capacidad_codigo=capacidad_codigo,
                recurso_tipo=recurso_tipo,
                recurso_id=recurso_id,
                accion=accion,
                resultado='permitido',
                detalles=detalles or '',
            )
    except OperationalError:
        pass


def validar_usuario_existe(
    usuario_id: int,
    incluir_eliminados: bool = False,
) -> AbstractBaseUser:
    """
    Valida que un usuario existe y retorna el objeto User.

    Args:
        usuario_id: ID del usuario a validar
        incluir_eliminados: Si True, incluye usuarios marcados como eliminados

    Returns:
        Objeto User si existe

    Raises:
        ValidationError: Si el usuario no existe

    Example:
        >>> usuario = validar_usuario_existe(usuario_id=123)
        >>> print(usuario.email)
    """
    try:
        if incluir_eliminados:
            usuario = User.objects.get(id=usuario_id)
        else:
            usuario = User.objects.get(id=usuario_id, is_deleted=False)
        return usuario
    except User.DoesNotExist:
        raise ValidationError(f'Usuario no encontrado: {usuario_id}')


def validar_campos_requeridos(
    datos: dict,
    campos: list[str],
) -> None:
    """
    Valida que todos los campos requeridos estén presentes y no vacíos.

    Args:
        datos: Diccionario con datos a validar
        campos: Lista de nombres de campos requeridos

    Raises:
        ValidationError: Si algún campo falta o está vacío

    Example:
        >>> validar_campos_requeridos(
        ...     datos={'email': 'test@test.com', 'password': '123'},
        ...     campos=['email', 'password', 'first_name']
        ... )
        ValidationError: Campo requerido: first_name
    """
    for campo in campos:
        if campo not in datos or not datos[campo]:
            raise ValidationError(f'Campo requerido: {campo}')


def validar_email_unico(
    email: str,
    excluir_usuario_id: Optional[int] = None,
) -> None:
    """
    Valida que un email no esté en uso por otro usuario.

    Args:
        email: Email a validar
        excluir_usuario_id: ID de usuario a excluir de la validación
                           (útil para ediciones)

    Raises:
        ValidationError: Si el email ya existe

    Example:
        >>> validar_email_unico(email='nuevo@test.com')
        >>> # OK si no existe
        >>>
        >>> validar_email_unico(
        ...     email='existing@test.com',
        ...     excluir_usuario_id=5
        ... )
        >>> # OK si el email pertenece al usuario 5
    """
    queryset = User.objects.filter(email=email)

    if excluir_usuario_id:
        queryset = queryset.exclude(id=excluir_usuario_id)

    if queryset.exists():
        raise ValidationError(f'Email ya existe: {email}')
