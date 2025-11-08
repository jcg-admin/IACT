"""
Servicio de gestion de usuarios (CRUD).

Este servicio implementa las operaciones CRUD para usuarios,
con verificacion de permisos granulares en cada operacion.

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tareas 17-23)
"""

from __future__ import annotations

from typing import Dict, List, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q, QuerySet

from .models_permisos_granular import AuditoriaPermiso
from .services_permisos_granular import UserManagementService

User = get_user_model()


class UsuarioService:
    """Servicio para operaciones CRUD de usuarios."""

    @staticmethod
    def listar_usuarios(
        usuario_solicitante_id: int,
        filtros: Optional[Dict] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, object]:
        """
        Lista usuarios con filtros y paginacion.

        Args:
            usuario_solicitante_id: ID del usuario que solicita el listado
            filtros: Diccionario con filtros opcionales:
                - activo: bool (True/False)
                - email_contains: str
                - nombre_contains: str
                - grupo_codigo: str
            page: Numero de pagina (1-indexed)
            page_size: Cantidad de resultados por pagina

        Returns:
            Diccionario con:
                - resultados: Lista de usuarios
                - total: Cantidad total de usuarios
                - pagina: Pagina actual
                - paginas_totales: Total de paginas

        Raises:
            PermissionDenied: Si el usuario no tiene permiso

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 17)
        """
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.ver',
        )

        if not tiene_permiso:
            # Auditar intento denegado
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_solicitante_id,
                capacidad_codigo='sistema.administracion.usuarios.ver',
                recurso_tipo='usuario',
                accion='listar',
                resultado='denegado',
                razon='Usuario no tiene permiso sistema.administracion.usuarios.ver',
            )
            raise PermissionDenied(
                'No tiene permiso para listar usuarios'
            )

        # Auditar acceso permitido
        AuditoriaPermiso.objects.create(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.ver',
            recurso_tipo='usuario',
            accion='listar',
            resultado='permitido',
        )

        # Construir query base (excluir eliminados)
        queryset = User.objects.filter(is_deleted=False)

        # Aplicar filtros
        if filtros:
            if 'activo' in filtros:
                queryset = queryset.filter(is_active=filtros['activo'])

            if 'email_contains' in filtros:
                queryset = queryset.filter(
                    email__icontains=filtros['email_contains']
                )

            if 'nombre_contains' in filtros:
                queryset = queryset.filter(
                    Q(first_name__icontains=filtros['nombre_contains'])
                    | Q(last_name__icontains=filtros['nombre_contains'])
                )

            if 'grupo_codigo' in filtros:
                queryset = queryset.filter(
                    usuarios_grupos__grupo__codigo=filtros['grupo_codigo'],
                    usuarios_grupos__activo=True,
                ).distinct()

        # Contar total
        total = queryset.count()

        # Calcular paginacion
        offset = (page - 1) * page_size
        limit = page_size

        # Obtener usuarios de la pagina
        usuarios = list(
            queryset.order_by('-created_at')[offset : offset + limit].values(
                'id',
                'email',
                'first_name',
                'last_name',
                'is_active',
                'is_staff',
                'created_at',
                'last_login',
            )
        )

        # Calcular paginas totales
        paginas_totales = (total + page_size - 1) // page_size

        return {
            'resultados': usuarios,
            'total': total,
            'pagina': page,
            'paginas_totales': paginas_totales,
        }

    @staticmethod
    def crear_usuario(
        usuario_solicitante_id: int,
        datos: Dict,
    ) -> User:
        """
        Crea un nuevo usuario.

        Args:
            usuario_solicitante_id: ID del usuario que crea
            datos: Diccionario con datos del usuario:
                - email: str (requerido)
                - first_name: str (requerido)
                - last_name: str (requerido)
                - password: str (requerido)
                - is_staff: bool (opcional)

        Returns:
            Usuario creado

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si los datos son invalidos

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 18)
        """
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.crear',
        )

        if not tiene_permiso:
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_solicitante_id,
                capacidad_codigo='sistema.administracion.usuarios.crear',
                recurso_tipo='usuario',
                accion='crear',
                resultado='denegado',
                razon='Usuario no tiene permiso sistema.administracion.usuarios.crear',
            )
            raise PermissionDenied(
                'No tiene permiso para crear usuarios'
            )

        # Validar datos requeridos
        campos_requeridos = ['email', 'first_name', 'last_name', 'password']
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                raise ValidationError(f'Campo requerido: {campo}')

        # Validar email unico
        if User.objects.filter(email=datos['email']).exists():
            raise ValidationError(f'Email ya existe: {datos["email"]}')

        # Crear usuario
        usuario = User.objects.create_user(
            email=datos['email'],
            first_name=datos['first_name'],
            last_name=datos['last_name'],
            password=datos['password'],
            is_staff=datos.get('is_staff', False),
        )

        # Auditar accion
        AuditoriaPermiso.objects.create(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.crear',
            recurso_tipo='usuario',
            recurso_id=usuario.id,
            accion='crear',
            resultado='permitido',
            detalles=f'Usuario creado: {usuario.email}',
        )

        return usuario

    @staticmethod
    def editar_usuario(
        usuario_solicitante_id: int,
        usuario_id: int,
        datos: Dict,
    ) -> User:
        """
        Edita un usuario existente.

        Args:
            usuario_solicitante_id: ID del usuario que edita
            usuario_id: ID del usuario a editar
            datos: Diccionario con datos a actualizar:
                - email: str (opcional)
                - first_name: str (opcional)
                - last_name: str (opcional)
                - is_staff: bool (opcional)

        Returns:
            Usuario actualizado

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si los datos son invalidos

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 19)
        """
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.editar',
        )

        if not tiene_permiso:
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_solicitante_id,
                capacidad_codigo='sistema.administracion.usuarios.editar',
                recurso_tipo='usuario',
                recurso_id=usuario_id,
                accion='editar',
                resultado='denegado',
                razon='Usuario no tiene permiso sistema.administracion.usuarios.editar',
            )
            raise PermissionDenied(
                'No tiene permiso para editar usuarios'
            )

        # Validar usuario existe
        try:
            usuario = User.objects.get(id=usuario_id, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError(f'Usuario no encontrado: {usuario_id}')

        # Validar email unico si cambia
        if 'email' in datos and datos['email'] != usuario.email:
            if User.objects.filter(email=datos['email']).exists():
                raise ValidationError(f'Email ya existe: {datos["email"]}')
            usuario.email = datos['email']

        # Actualizar campos
        if 'first_name' in datos:
            usuario.first_name = datos['first_name']
        if 'last_name' in datos:
            usuario.last_name = datos['last_name']
        if 'is_staff' in datos:
            usuario.is_staff = datos['is_staff']

        usuario.save()

        # Auditar accion
        AuditoriaPermiso.objects.create(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.editar',
            recurso_tipo='usuario',
            recurso_id=usuario.id,
            accion='editar',
            resultado='permitido',
            detalles=f'Usuario editado: {usuario.email}',
        )

        return usuario

    @staticmethod
    def eliminar_usuario(
        usuario_solicitante_id: int,
        usuario_id: int,
    ) -> User:
        """
        Elimina un usuario (soft delete).

        Args:
            usuario_solicitante_id: ID del usuario que elimina
            usuario_id: ID del usuario a eliminar

        Returns:
            Usuario eliminado

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si el usuario no existe

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 20)
        """
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.eliminar',
        )

        if not tiene_permiso:
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_solicitante_id,
                capacidad_codigo='sistema.administracion.usuarios.eliminar',
                recurso_tipo='usuario',
                recurso_id=usuario_id,
                accion='eliminar',
                resultado='denegado',
                razon='Usuario no tiene permiso sistema.administracion.usuarios.eliminar',
            )
            raise PermissionDenied(
                'No tiene permiso para eliminar usuarios'
            )

        # Validar usuario existe
        try:
            usuario = User.objects.get(id=usuario_id, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError(f'Usuario no encontrado: {usuario_id}')

        # Marcar como eliminado (soft delete)
        usuario.is_deleted = True
        usuario.is_active = False
        from django.utils import timezone
        usuario.deleted_at = timezone.now()
        usuario.save()

        # Auditar accion
        AuditoriaPermiso.objects.create(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.eliminar',
            recurso_tipo='usuario',
            recurso_id=usuario.id,
            accion='eliminar',
            resultado='permitido',
            detalles=f'Usuario eliminado: {usuario.email}',
        )

        return usuario

    @staticmethod
    def suspender_usuario(
        usuario_solicitante_id: int,
        usuario_id: int,
        motivo: str = '',
    ) -> User:
        """
        Suspende un usuario.

        Args:
            usuario_solicitante_id: ID del usuario que suspende
            usuario_id: ID del usuario a suspender
            motivo: Motivo de la suspension

        Returns:
            Usuario suspendido

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si el usuario no existe o se intenta suspender a si mismo

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 21)
        """
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.suspender',
        )

        if not tiene_permiso:
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_solicitante_id,
                capacidad_codigo='sistema.administracion.usuarios.suspender',
                recurso_tipo='usuario',
                recurso_id=usuario_id,
                accion='suspender',
                resultado='denegado',
                razon='Usuario no tiene permiso sistema.administracion.usuarios.suspender',
            )
            raise PermissionDenied(
                'No tiene permiso para suspender usuarios'
            )

        # Validar no es el mismo usuario
        if usuario_solicitante_id == usuario_id:
            raise ValidationError('No puede suspenderse a si mismo')

        # Validar usuario existe
        try:
            usuario = User.objects.get(id=usuario_id, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError(f'Usuario no encontrado: {usuario_id}')

        # Marcar como suspendido
        usuario.is_active = False
        usuario.save()

        # TODO: Cerrar sesiones activas del usuario
        # from django.contrib.sessions.models import Session
        # Session.objects.filter(user_id=usuario_id).delete()

        # Auditar accion
        AuditoriaPermiso.objects.create(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.suspender',
            recurso_tipo='usuario',
            recurso_id=usuario.id,
            accion='suspender',
            resultado='permitido',
            detalles=f'Usuario suspendido: {usuario.email}. Motivo: {motivo}',
        )

        return usuario

    @staticmethod
    def reactivar_usuario(
        usuario_solicitante_id: int,
        usuario_id: int,
    ) -> User:
        """
        Reactiva un usuario suspendido.

        Args:
            usuario_solicitante_id: ID del usuario que reactiva
            usuario_id: ID del usuario a reactivar

        Returns:
            Usuario reactivado

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si el usuario no existe

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 22)
        """
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.reactivar',
        )

        if not tiene_permiso:
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_solicitante_id,
                capacidad_codigo='sistema.administracion.usuarios.reactivar',
                recurso_tipo='usuario',
                recurso_id=usuario_id,
                accion='reactivar',
                resultado='denegado',
                razon='Usuario no tiene permiso sistema.administracion.usuarios.reactivar',
            )
            raise PermissionDenied(
                'No tiene permiso para reactivar usuarios'
            )

        # Validar usuario existe
        try:
            usuario = User.objects.get(id=usuario_id, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError(f'Usuario no encontrado: {usuario_id}')

        # Marcar como activo
        usuario.is_active = True
        usuario.save()

        # Auditar accion
        AuditoriaPermiso.objects.create(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.reactivar',
            recurso_tipo='usuario',
            recurso_id=usuario.id,
            accion='reactivar',
            resultado='permitido',
            detalles=f'Usuario reactivado: {usuario.email}',
        )

        return usuario

    @staticmethod
    def asignar_grupos_usuario(
        usuario_solicitante_id: int,
        usuario_id: int,
        grupos_codigos: List[str],
    ) -> User:
        """
        Asigna grupos de permisos a un usuario.

        Args:
            usuario_solicitante_id: ID del usuario que asigna
            usuario_id: ID del usuario que recibe los grupos
            grupos_codigos: Lista de codigos de grupos a asignar

        Returns:
            Usuario con grupos asignados

        Raises:
            PermissionDenied: Si el usuario no tiene permiso
            ValidationError: Si el usuario no existe

        Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 23)
        """
        # Verificar permiso
        tiene_permiso = UserManagementService.usuario_tiene_permiso(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.asignar_grupos',
        )

        if not tiene_permiso:
            AuditoriaPermiso.objects.create(
                usuario_id=usuario_solicitante_id,
                capacidad_codigo='sistema.administracion.usuarios.asignar_grupos',
                recurso_tipo='usuario',
                recurso_id=usuario_id,
                accion='asignar_grupos',
                resultado='denegado',
                razon='Usuario no tiene permiso sistema.administracion.usuarios.asignar_grupos',
            )
            raise PermissionDenied(
                'No tiene permiso para asignar grupos a usuarios'
            )

        # Validar usuario existe
        try:
            usuario = User.objects.get(id=usuario_id, is_deleted=False)
        except User.DoesNotExist:
            raise ValidationError(f'Usuario no encontrado: {usuario_id}')

        # Desactivar grupos actuales
        from .models_permisos_granular import UsuarioGrupo
        UsuarioGrupo.objects.filter(
            usuario_id=usuario_id,
            activo=True,
        ).update(activo=False)

        # Asignar nuevos grupos
        for grupo_codigo in grupos_codigos:
            UserManagementService.asignar_grupo_a_usuario(
                usuario_id=usuario_id,
                grupo_codigo=grupo_codigo,
                asignado_por_id=usuario_solicitante_id,
            )

        # Auditar accion
        AuditoriaPermiso.objects.create(
            usuario_id=usuario_solicitante_id,
            capacidad_codigo='sistema.administracion.usuarios.asignar_grupos',
            recurso_tipo='usuario',
            recurso_id=usuario.id,
            accion='asignar_grupos',
            resultado='permitido',
            detalles=f'Grupos asignados a {usuario.email}: {", ".join(grupos_codigos)}',
        )

        return usuario
