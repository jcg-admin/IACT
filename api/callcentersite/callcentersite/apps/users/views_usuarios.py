"""
Vistas API REST para gestion de usuarios.

Endpoints:
    - GET    /api/usuarios/             (list)
    - POST   /api/usuarios/             (create)
    - GET    /api/usuarios/:id/         (retrieve)
    - PUT    /api/usuarios/:id/         (update)
    - PATCH  /api/usuarios/:id/         (partial_update)
    - DELETE /api/usuarios/:id/         (destroy)
    - POST   /api/usuarios/:id/suspender/    (action)
    - POST   /api/usuarios/:id/reactivar/    (action)
    - POST   /api/usuarios/:id/asignar_grupos/  (action)
    - POST   /api/register/             (public registration)

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tareas 43-59)
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers_usuarios import (
    AsignarGruposSerializer,
    SuspenderUsuarioSerializer,
    UserListSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .services_usuarios import UsuarioService

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de usuarios.

    Todas las operaciones verifican permisos granulares antes de ejecutarse.
    """

    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """Usa UserListSerializer para listados."""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def list(self, request):
        """
        Lista usuarios con filtros y paginacion.

        Query params:
            - activo: bool
            - email_contains: str
            - nombre_contains: str
            - grupo_codigo: str
            - page: int
            - page_size: int

        Permiso: sistema.administracion.usuarios.ver
        """
        try:
            # Obtener parametros de filtro
            filtros = {}
            if 'activo' in request.query_params:
                filtros['activo'] = request.query_params['activo'].lower() == 'true'
            if 'email_contains' in request.query_params:
                filtros['email_contains'] = request.query_params['email_contains']
            if 'nombre_contains' in request.query_params:
                filtros['nombre_contains'] = request.query_params['nombre_contains']
            if 'grupo_codigo' in request.query_params:
                filtros['grupo_codigo'] = request.query_params['grupo_codigo']

            # Obtener paginacion
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 50))

            # Llamar al servicio
            resultado = UsuarioService.listar_usuarios(
                usuario_solicitante_id=request.user.id,
                filtros=filtros,
                page=page,
                page_size=page_size,
            )

            return Response(resultado)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )

    def create(self, request):
        """
        Crea un nuevo usuario.

        Body:
            - email: str (requerido)
            - first_name: str (requerido)
            - last_name: str (requerido)
            - password: str (requerido)
            - is_staff: bool (opcional)

        Permiso: sistema.administracion.usuarios.crear
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = UsuarioService.crear_usuario(
                usuario_solicitante_id=request.user.id,
                datos=serializer.validated_data,
            )

            output_serializer = self.get_serializer(usuario)
            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, pk=None):
        """
        Obtiene detalle de un usuario.

        Permiso: sistema.administracion.usuarios.ver
        """
        try:
            # Verificar que tiene permiso (reutilizando listar)
            UsuarioService.listar_usuarios(
                usuario_solicitante_id=request.user.id,
                filtros={},
                page=1,
                page_size=1,
            )

            # Obtener usuario
            usuario = self.get_object()
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, pk=None):
        """
        Actualiza un usuario completo.

        Body:
            - email: str (opcional)
            - first_name: str (opcional)
            - last_name: str (opcional)
            - is_staff: bool (opcional)

        Permiso: sistema.administracion.usuarios.editar
        """
        serializer = self.get_serializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = UsuarioService.editar_usuario(
                usuario_solicitante_id=request.user.id,
                usuario_id=int(pk),
                datos=serializer.validated_data,
            )

            output_serializer = self.get_serializer(usuario)
            return Response(output_serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, pk=None):
        """
        Actualiza campos parciales de un usuario.

        Permiso: sistema.administracion.usuarios.editar
        """
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = UsuarioService.editar_usuario(
                usuario_solicitante_id=request.user.id,
                usuario_id=int(pk),
                datos=serializer.validated_data,
            )

            output_serializer = self.get_serializer(usuario)
            return Response(output_serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk=None):
        """
        Elimina un usuario (soft delete).

        Permiso: sistema.administracion.usuarios.eliminar
        """
        try:
            UsuarioService.eliminar_usuario(
                usuario_solicitante_id=request.user.id,
                usuario_id=int(pk),
            )

            return Response(
                {'message': 'Usuario eliminado exitosamente'},
                status=status.HTTP_204_NO_CONTENT,
            )

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=['post'])
    def suspender(self, request, pk=None):
        """
        Suspende un usuario.

        Body:
            - motivo: str (opcional)

        Permiso: sistema.administracion.usuarios.suspender
        """
        serializer = SuspenderUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = UsuarioService.suspender_usuario(
                usuario_solicitante_id=request.user.id,
                usuario_id=int(pk),
                motivo=serializer.validated_data.get('motivo', ''),
            )

            output_serializer = UserSerializer(usuario)
            return Response(output_serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=['post'])
    def reactivar(self, request, pk=None):
        """
        Reactiva un usuario suspendido.

        Permiso: sistema.administracion.usuarios.reactivar
        """
        try:
            usuario = UsuarioService.reactivar_usuario(
                usuario_solicitante_id=request.user.id,
                usuario_id=int(pk),
            )

            output_serializer = UserSerializer(usuario)
            return Response(output_serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=['post'])
    def asignar_grupos(self, request, pk=None):
        """
        Asigna grupos de permisos a un usuario.

        Body:
            - grupos_codigos: list[str] (requerido)

        Permiso: sistema.administracion.usuarios.asignar_grupos
        """
        serializer = AsignarGruposSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = UsuarioService.asignar_grupos_usuario(
                usuario_solicitante_id=request.user.id,
                usuario_id=int(pk),
                grupos_codigos=serializer.validated_data['grupos_codigos'],
            )

            output_serializer = UserSerializer(usuario)
            return Response(output_serializer.data)

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserRegistrationView(generics.CreateAPIView):
    """
    Vista para registro publico de usuarios.
    
    POST /api/register/
    
    Body:
        - username: str (requerido, unico)
        - email: str (requerido, unico)
        - password: str (requerido, minimo 8 caracteres)
        - password_confirm: str (requerido, debe coincidir)
    
    Returns:
        - 201 Created: Usuario registrado exitosamente
        - 400 Bad Request: Datos invalidos
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Registra un nuevo usuario."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                'message': 'Usuario registrado exitosamente',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            },
            status=status.HTTP_201_CREATED,
        )
