"""Servicios de negocio para la app de usuarios."""

from __future__ import annotations

from typing import Iterable, List, Optional, Set

from django.contrib.auth.hashers import check_password
from django.core.exceptions import PermissionDenied, ValidationError, ObjectDoesNotExist
from django.db import IntegrityError

from . import models

User = models.User


class PermissionService:
    """Evalúa permisos según precedencia definida."""

    @staticmethod
    def has_permission(user: User, permission_codename: str) -> bool:
        """Evalúa si el usuario tiene el permiso solicitado."""

        if not user.is_authenticated:
            return False

        if PermissionService._has_direct_permission(user, permission_codename):
            return True

        if PermissionService._has_role_permission(user, permission_codename):
            return True

        return PermissionService._has_segment_permission(user, permission_codename)

    @staticmethod
    def _has_direct_permission(user: User, permission_codename: str) -> bool:
        return models.UserPermission.objects.has_permission(user, permission_codename)

    @staticmethod
    def _has_role_permission(user: User, permission_codename: str) -> bool:
        for role in models.RoleAssignment.objects.roles_for_user(user):
            if role.permissions.has_codename(permission_codename):
                return True
        return False

    @staticmethod
    def _has_segment_permission(user: User, permission_codename: str) -> bool:
        for segment in models.Segment.objects.with_permission(permission_codename):
            if segment.matches(user):
                return True
        return False

    @staticmethod
    def permissions_for_user(user: User) -> Iterable[str]:
        """Retorna todos los permisos efectivos del usuario."""

        direct: Set[str] = {
            permission.codename
            for permission in models.UserPermission.objects.permissions_for_user(user)
        }

        role_based: Set[str] = set()
        for role in models.RoleAssignment.objects.roles_for_user(user):
            role_based.update(role.permissions.values_list("codename", flat=True))

        segment_permissions: Set[str] = set()
        for segment in models.Segment.objects.active_segments():
            if segment.matches(user):
                segment_permissions.update(
                    segment.permissions.values_list("codename", flat=True)
                )

        return direct.union(role_based).union(segment_permissions)


class UserService:
    """
    Servicio de gestión de usuarios/agentes del call center.

    Implementa casos de uso para administración de usuarios.
    """

    @staticmethod
    def crear_usuario(
        username: str,
        email: str,
        password: str,
        segment: str = '',
    ) -> User:
        """
        UC-014: Crear usuario/agente.

        Args:
            username: Nombre de usuario (único)
            email: Email del usuario (único)
            password: Contraseña en texto plano (será hasheada)
            segment: Segmento del usuario (opcional)

        Returns:
            Usuario creado

        Raises:
            ValidationError: Si username o email ya existen

        Ejemplo:
            >>> usuario = UserService.crear_usuario(
            ...     username='nuevo.agente',
            ...     email='nuevo@company.com',
            ...     password='SecureP@ss123',
            ...     segment='GE'
            ... )
        """
        # Validar username único
        if User.objects.filter(username=username).exists():
            raise ValidationError(f'Username "{username}" ya existe')

        # Validar email único
        if User.objects.filter(email=email).exists():
            raise ValidationError(f'Email "{email}" ya existe')

        # Crear usuario con contraseña hasheada
        try:
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                segment=segment,
                status='ACTIVO',
                is_locked=False,
                failed_login_attempts=0
            )
        except IntegrityError as e:
            raise ValidationError(f'Error al crear usuario: {str(e)}')

        return usuario

    @staticmethod
    def actualizar_usuario(
        usuario_id: int,
        email: Optional[str] = None,
        segment: Optional[str] = None,
    ) -> User:
        """
        UC-015: Actualizar perfil de usuario.

        Args:
            usuario_id: ID del usuario a actualizar
            email: Nuevo email (opcional)
            segment: Nuevo segmento (opcional)

        Returns:
            Usuario actualizado

        Raises:
            ObjectDoesNotExist: Si usuario no existe

        Ejemplo:
            >>> usuario = UserService.actualizar_usuario(
            ...     usuario_id=1,
            ...     email='nuevo@email.com',
            ...     segment='VIP'
            ... )
        """
        usuario = User.objects.get(id=usuario_id)

        if email is not None:
            usuario.email = email

        if segment is not None:
            usuario.segment = segment

        usuario.save()
        return usuario

    @staticmethod
    def bloquear_usuario(
        usuario_id: int,
        razon: str = '',
    ) -> None:
        """
        UC-016: Bloquear usuario manualmente.

        Args:
            usuario_id: ID del usuario a bloquear
            razon: Razón del bloqueo (opcional)

        Raises:
            ObjectDoesNotExist: Si usuario no existe

        Ejemplo:
            >>> UserService.bloquear_usuario(
            ...     usuario_id=1,
            ...     razon='Violación de políticas'
            ... )
        """
        usuario = User.objects.get(id=usuario_id)

        usuario.is_locked = True
        usuario.locked_until = None  # Bloqueo indefinido
        usuario.lock_reason = 'ADMIN_LOCK'

        usuario.save(update_fields=['is_locked', 'locked_until', 'lock_reason'])

    @staticmethod
    def desbloquear_usuario(usuario_id: int) -> None:
        """
        UC-016: Desbloquear usuario.

        Args:
            usuario_id: ID del usuario a desbloquear

        Raises:
            ObjectDoesNotExist: Si usuario no existe

        Ejemplo:
            >>> UserService.desbloquear_usuario(usuario_id=1)
        """
        usuario = User.objects.get(id=usuario_id)

        usuario.is_locked = False
        usuario.locked_until = None
        usuario.failed_login_attempts = 0
        usuario.lock_reason = ''

        usuario.save(update_fields=[
            'is_locked',
            'locked_until',
            'failed_login_attempts',
            'lock_reason'
        ])

    @staticmethod
    def eliminar_usuario(usuario_id: int) -> None:
        """
        UC-017: Eliminar usuario (soft delete).

        Args:
            usuario_id: ID del usuario a eliminar

        Raises:
            ObjectDoesNotExist: Si usuario no existe

        Ejemplo:
            >>> UserService.eliminar_usuario(usuario_id=1)
        """
        usuario = User.objects.get(id=usuario_id)
        usuario.mark_deleted()

    @staticmethod
    def listar_usuarios(
        segment: Optional[str] = None,
        is_locked: Optional[bool] = None,
        incluir_eliminados: bool = False,
    ) -> List[User]:
        """
        UC-018: Consultar/Listar usuarios.

        Args:
            segment: Filtrar por segmento (opcional)
            is_locked: Filtrar por estado de bloqueo (opcional)
            incluir_eliminados: Incluir usuarios eliminados (default: False)

        Returns:
            Lista de usuarios

        Ejemplo:
            >>> usuarios = UserService.listar_usuarios(segment='VIP')
            >>> usuarios_bloqueados = UserService.listar_usuarios(is_locked=True)
        """
        queryset = User.objects.all()

        # Excluir eliminados por defecto
        if not incluir_eliminados:
            queryset = queryset.filter(is_deleted=False)

        # Aplicar filtros opcionales
        if segment is not None:
            queryset = queryset.filter(segment=segment)

        if is_locked is not None:
            queryset = queryset.filter(is_locked=is_locked)

        return list(queryset.order_by('-created_at'))

    @staticmethod
    def cambiar_contrasena(
        usuario_id: int,
        contrasena_actual: str,
        contrasena_nueva: str,
    ) -> None:
        """
        UC-019: Cambiar contraseña de usuario.

        Args:
            usuario_id: ID del usuario
            contrasena_actual: Contraseña actual (para validar)
            contrasena_nueva: Nueva contraseña

        Raises:
            ObjectDoesNotExist: Si usuario no existe
            PermissionDenied: Si contraseña actual es incorrecta

        Ejemplo:
            >>> UserService.cambiar_contrasena(
            ...     usuario_id=1,
            ...     contrasena_actual='OldP@ss123',
            ...     contrasena_nueva='NewP@ss456'
            ... )
        """
        usuario = User.objects.get(id=usuario_id)

        # Validar contraseña actual
        if not check_password(contrasena_actual, usuario.password):
            raise PermissionDenied('Contraseña actual incorrecta')

        # Establecer nueva contraseña (será hasheada automáticamente)
        usuario.set_password(contrasena_nueva)
        usuario.save()
