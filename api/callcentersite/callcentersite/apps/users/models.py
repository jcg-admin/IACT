"""Modelos en memoria para usuarios, roles y permisos."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar, Iterable, List

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


class UserManager(InMemoryManager):
    """Operaciones de creación de usuarios."""

    def create_user(self, username: str, password: str, email: str, **extra: Any):
        extra.setdefault("is_active", True)
        user = super().create(username=username, password=password, email=email, **extra)
        user.set_authenticated(True)
        return user


class PermissionManager(InMemoryManager):
    pass


class RoleManager(InMemoryManager):
    pass


class RoleAssignmentManager(InMemoryManager):
    def roles_for_user(self, user: "User") -> List["Role"]:
        return [assignment.role for assignment in self._records if assignment.user is user]


class UserPermissionManager(InMemoryManager):
    def has_permission(self, user: "User", codename: str) -> bool:
        return any(
            assignment.user is user and assignment.permission.codename == codename
            for assignment in self._records
        )

    def permissions_for_user(self, user: "User") -> List["Permission"]:
        return [assignment.permission for assignment in self._records if assignment.user is user]


class SegmentManager(InMemoryManager):
    def active_segments(self) -> Iterable["Segment"]:
        return [segment for segment in self._records if segment.is_active]

    def with_permission(self, codename: str) -> Iterable["Segment"]:
        return [segment for segment in self.active_segments() if segment.permissions.has_codename(codename)]


def reset_registry() -> None:
    """Limpia todos los registros en memoria (se ejecuta por prueba)."""

    for manager in _REGISTRY:
        manager.clear()


@dataclass
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
class User:
    """Usuario principal del sistema con campos adicionales."""

    username: str
    password: str
    email: str
    is_active: bool = True
    last_login_ip: str | None = None
    failed_login_attempts: int = 0
    is_deleted: bool = False
    deleted_at: datetime | None = None
    id: int = field(init=False, default=0)

    _is_authenticated: bool = field(init=False, default=True)
    created_at: datetime = field(init=False)
    updated_at: datetime = field(init=False)

    objects: ClassVar[UserManager]

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc)
        self.created_at = now
        self.updated_at = now

    @property
    def is_authenticated(self) -> bool:
        return self._is_authenticated and self.is_active and not self.is_deleted

    def set_authenticated(self, value: bool) -> None:
        self._is_authenticated = value

    def mark_deleted(self) -> None:
        self.is_active = False
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.updated_at = self.deleted_at


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
    granted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: int = field(init=False, default=0)

    objects: ClassVar[UserPermissionManager]


# Instanciar managers una vez que las clases existen
User.objects = UserManager(User)
Permission.objects = PermissionManager(Permission)
Role.objects = RoleManager(Role)
Segment.objects = SegmentManager(Segment)
RoleAssignment.objects = RoleAssignmentManager(RoleAssignment)
UserPermission.objects = UserPermissionManager(UserPermission)
