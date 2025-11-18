"""Modelos de Django para usuarios y sistema de permisos en memoria."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone as dt_timezone
from typing import Any, ClassVar, Iterable, List

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

# =============================================================================
# MODELO USER DE DJANGO (Opción C - Modelo totalmente custom)
# =============================================================================


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User."""

    def create_user(self, username: str, password: str, email: str, **extra_fields):
        """Crea y guarda un usuario regular."""
        if not username:
            raise ValueError('El username es obligatorio')
        if not email:
            raise ValueError('El email es obligatorio')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('status', 'ACTIVO')

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: str, email: str, **extra_fields):
        """Crea y guarda un superusuario."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 'ACTIVO')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True')

        return self.create_user(username, password, email, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario custom heredando de AbstractBaseUser.

    Campos principales:
    - username: Identificador único del usuario
    - email: Email del usuario
    - password: Hash bcrypt de la contraseña (manejado por AbstractBaseUser)
    - is_active: Si el usuario está activo
    - status: Estado del usuario (ACTIVO/INACTIVO)

    Seguridad y bloqueo:
    - is_locked: Si la cuenta está bloqueada
    - locked_until: Timestamp hasta cuando está bloqueada
    - lock_reason: Razón del bloqueo
    - failed_login_attempts: Contador de intentos fallidos
    - last_failed_login_at: Timestamp del último intento fallido
    - last_login_ip: IP del último login

    Borrado lógico:
    - is_deleted: Marca de borrado lógico
    - deleted_at: Timestamp del borrado

    Segmentación:
    - segment: Segmento del usuario (ej: 'GE', 'MARKETING')

    Metadata:
    - created_at: Timestamp de creación
    - updated_at: Timestamp de última actualización
    - last_login_at: Timestamp del último login exitoso
    """

    # Campos básicos
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Nombre de usuario único'
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        help_text='Email del usuario'
    )

    # Status y activación
    is_active = models.BooleanField(
        default=True,
        help_text='Si el usuario está activo'
    )
    status = models.CharField(
        max_length=20,
        default='ACTIVO',
        choices=[
            ('ACTIVO', 'Activo'),
            ('INACTIVO', 'Inactivo'),
        ],
        help_text='Estado del usuario'
    )

    # Seguridad y bloqueo
    is_locked = models.BooleanField(
        default=False,
        help_text='Si la cuenta está bloqueada'
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp hasta cuando está bloqueada'
    )
    lock_reason = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text='Razón del bloqueo'
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text='Contador de intentos fallidos de login'
    )
    last_failed_login_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp del último intento fallido'
    )
    last_login_ip = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text='IP del último login'
    )
    last_login_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp del último login exitoso'
    )

    # Borrado lógico
    is_deleted = models.BooleanField(
        default=False,
        help_text='Marca de borrado lógico'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp del borrado'
    )

    # Segmentación
    segment = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text='Segmento del usuario'
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp de última actualización'
    )

    # Para Django Admin
    is_staff = models.BooleanField(
        default=False,
        help_text='Si el usuario puede acceder al admin'
    )

    # Configuración del modelo
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return self.username

    def mark_deleted(self) -> None:
        """Realiza borrado lógico del usuario."""
        self.is_active = False
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.updated_at = self.deleted_at
        self.save(update_fields=['is_active', 'is_deleted', 'deleted_at', 'updated_at'])

    def set_authenticated(self, value: bool) -> None:
        """
        Método de compatibilidad para tests.
        En AbstractBaseUser, is_authenticated es una propiedad que siempre es True.
        """
        # Este método existe para compatibilidad con tests antiguos
        # pero en Django el estado de autenticación se maneja de otra forma
        pass

    @property
    def is_authenticated(self) -> bool:
        """
        Override del property is_authenticated de AbstractBaseUser.
        Retorna True solo si el usuario está activo y no eliminado.
        """
        return self.is_active and not self.is_deleted


class UserSession(models.Model):
    """
    Sesión de usuario para control de sesión única.

    Permite rastrear sesiones activas y cerrar sesiones previas
    cuando el usuario inicia sesión desde un nuevo dispositivo.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text='Usuario dueño de la sesión'
    )
    session_key = models.CharField(
        max_length=255,
        unique=True,
        help_text='Clave única de sesión'
    )
    last_activity_at = models.DateTimeField(
        default=timezone.now,
        help_text='Último timestamp de actividad en la sesión',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Si la sesión está activa'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP de origen de la sesión'
    )
    user_agent = models.TextField(
        blank=True,
        default='',
        help_text='User agent del navegador/dispositivo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp de creación de sesión'
    )
    logged_out_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp de cierre de sesión'
    )
    logout_reason = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text='Razón del cierre de sesión'
    )

    class Meta:
        db_table = 'users_user_session'
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        status = 'activa' if self.is_active else 'cerrada'
        return f'Sesión {self.session_key[:8]}... - {self.user.username} ({status})'

    def close(self, reason: str = 'MANUAL') -> None:
        """Cierra la sesión."""
        self.is_active = False
        self.logged_out_at = timezone.now()
        self.logout_reason = reason
        self.save(update_fields=['is_active', 'logged_out_at', 'logout_reason'])


class PasswordHistory(models.Model):
    """Histórico de contraseñas usadas por un usuario."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_history',
    )
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users_password_history'
        ordering = ['-created_at']


# =============================================================================
# MODELOS EN MEMORIA (Para sistema de permisos granular - mantener como está)
# =============================================================================

_REGISTRY: list["InMemoryManager[Any]"] = []


class InMemoryManager:
    """Administrador base que persiste objetos en listas in-memory."""

    def __init__(self, model_cls):
        self.model_cls = model_cls
        self._records: List[Any] = []
        self._next_id = 1
        _REGISTRY.append(self)

    def create(self, **kwargs):
        instance = self.model_cls(**kwargs)
        instance.id = self._next_id
        self._next_id += 1
        self._records.append(instance)
        return instance

    def all(self) -> List[Any]:
        return list(self._records)

    def clear(self) -> None:
        self._records.clear()
        self._next_id = 1


class PermissionManager(InMemoryManager):
    pass


class RoleManager(InMemoryManager):
    pass


class RoleAssignmentManager(InMemoryManager):
    def roles_for_user(self, user: "User") -> List["Role"]:
        return [
            assignment.role for assignment in self._records if assignment.user is user
        ]


class UserPermissionManager(InMemoryManager):
    def has_permission(self, user: "User", codename: str) -> bool:
        return any(
            assignment.user is user and assignment.permission.codename == codename
            for assignment in self._records
        )

    def permissions_for_user(self, user: "User") -> List["Permission"]:
        return [
            assignment.permission
            for assignment in self._records
            if assignment.user is user
        ]


class SegmentManager(InMemoryManager):
    def active_segments(self) -> Iterable["Segment"]:
        return [segment for segment in self._records if segment.is_active]

    def with_permission(self, codename: str) -> Iterable["Segment"]:
        return [
            segment
            for segment in self.active_segments()
            if segment.permissions.has_codename(codename)
        ]


def reset_registry() -> None:
    """Limpia todos los registros en memoria (se ejecuta por prueba)."""

    for manager in _REGISTRY:
        manager.clear()


@dataclass(eq=False)
class Permission:
    """Permiso granular definido por recurso y acción."""

    codename: str
    name: str
    resource: str
    action: str
    description: str
    id: int = field(init=False, default=0)

    objects: ClassVar[PermissionManager]

    def __hash__(self) -> int:  # pragma: no cover - utilitario
        return hash(self.codename)

    def __eq__(self, other: object) -> bool:  # pragma: no cover - utilitario
        if not isinstance(other, Permission):
            return False
        return self.codename == other.codename


class PermissionCollection:
    """Colección liviana para relaciones muchos-a-muchos."""

    def __init__(self) -> None:
        self._items: List[Permission] = []

    def add(self, permission: Permission) -> None:
        if permission not in self._items:
            self._items.append(permission)

    def values_list(self, field_name: str, *, flat: bool = False) -> List[Any]:
        if not flat:
            raise ValueError("Solo se soporta flat=True en esta colección simplificada")
        return [getattr(permission, field_name) for permission in self._items]

    def has_codename(self, codename: str) -> bool:
        return any(permission.codename == codename for permission in self._items)

    def __iter__(self):  # pragma: no cover - soporte iteración
        return iter(self._items)

    def __len__(self) -> int:  # pragma: no cover - soporte len
        return len(self._items)


@dataclass
class Role:
    """Rol que agrupa permisos para asignación indirecta."""

    name: str
    description: str
    is_system_role: bool = False
    id: int = field(init=False, default=0)
    permissions: PermissionCollection = field(init=False)

    objects: ClassVar[RoleManager]

    def __post_init__(self) -> None:
        self.permissions = PermissionCollection()


@dataclass
class Segment:
    """Segmentación de usuarios con criterios dinámicos."""

    name: str
    description: str
    criteria: dict[str, Any]
    is_active: bool = True
    id: int = field(init=False, default=0)
    permissions: PermissionCollection = field(init=False)

    objects: ClassVar[SegmentManager]

    def __post_init__(self) -> None:
        self.permissions = PermissionCollection()

    def matches(self, user: "User") -> bool:
        for field, expected in self.criteria.items():
            if getattr(user, field, None) != expected:
                return False
        return True


@dataclass
class RoleAssignment:
    """Relación entre usuarios y roles."""

    user: User
    role: Role
    granted_by: User
    id: int = field(init=False, default=0)

    objects: ClassVar[RoleAssignmentManager]


@dataclass
class UserPermission:
    """Permisos directos asignados a un usuario."""

    user: User
    permission: Permission
    granted_by: User
    granted_at: datetime = field(default_factory=lambda: datetime.now(dt_timezone.utc))
    id: int = field(init=False, default=0)

    objects: ClassVar[UserPermissionManager]


# Instanciar managers una vez que las clases existen
Permission.objects = PermissionManager(Permission)
Role.objects = RoleManager(Role)
Segment.objects = SegmentManager(Segment)
RoleAssignment.objects = RoleAssignmentManager(RoleAssignment)
UserPermission.objects = UserPermissionManager(UserPermission)
