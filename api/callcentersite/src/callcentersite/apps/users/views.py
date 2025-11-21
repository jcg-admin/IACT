"""ViewSets para la API REST de usuarios."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied

from .models import User
from .services import UserService
from .serializers import (
    UserSerializer,
    CrearUsuarioSerializer,
    ActualizarUsuarioSerializer,
    BloquearUsuarioSerializer,
    CambiarContrasenaSerializer,
    FiltrosUsuariosSerializer,
)


class UserViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de usuarios/agentes.

    Endpoints:
    - POST   /users/                - Crear usuario (UC-014)
    - GET    /users/                - Listar usuarios (UC-018)
    - GET    /users/{id}/           - Obtener usuario
    - PATCH  /users/{id}/           - Actualizar usuario (UC-015)
    - DELETE /users/{id}/           - Eliminar usuario (UC-017)
    - POST   /users/{id}/bloquear/  - Bloquear usuario (UC-016)
    - POST   /users/{id}/desbloquear/ - Desbloquear usuario (UC-016)
    - POST   /users/{id}/cambiar_contrasena/ - Cambiar contraseña (UC-019)
    """

    permission_classes = [IsAuthenticated]

    def create(self, request):
        """
        UC-014: Crear usuario.

        POST /api/v1/users/
        {
            "username": "nuevo.agente",
            "email": "nuevo@company.com",
            "password": "SecureP@ss123",
            "segment": "GE"
        }
        """
        serializer = CrearUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = UserService.crear_usuario(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                segment=serializer.validated_data.get('segment', ''),
            )

            return Response(
                UserSerializer(usuario).data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request):
        """
        UC-018: Listar usuarios con filtros.

        GET /api/v1/users/?segment=VIP&is_locked=false
        """
        # Parsear query params
        segment = request.query_params.get('segment')
        is_locked_str = request.query_params.get('is_locked')
        incluir_eliminados = request.query_params.get('incluir_eliminados', 'false').lower() == 'true'

        # Convertir is_locked string a boolean
        is_locked = None
        if is_locked_str:
            is_locked = is_locked_str.lower() in ['true', '1', 'yes']

        usuarios = UserService.listar_usuarios(
            segment=segment,
            is_locked=is_locked,
            incluir_eliminados=incluir_eliminados
        )

        serializer = UserSerializer(usuarios, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Obtener usuario específico.

        GET /api/v1/users/{id}/
        """
        try:
            usuario = User.objects.get(pk=pk)
            serializer = UserSerializer(usuario)
            return Response(serializer.data)

        except ObjectDoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    def partial_update(self, request, pk=None):
        """
        UC-015: Actualizar usuario.

        PATCH /api/v1/users/{id}/
        {
            "email": "nuevo@email.com",
            "segment": "VIP"
        }
        """
        serializer = ActualizarUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = UserService.actualizar_usuario(
                usuario_id=int(pk),
                email=serializer.validated_data.get('email'),
                segment=serializer.validated_data.get('segment'),
            )

            return Response(UserSerializer(usuario).data)

        except ObjectDoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        """
        UC-017: Eliminar usuario (soft delete).

        DELETE /api/v1/users/{id}/
        """
        try:
            UserService.eliminar_usuario(usuario_id=int(pk))

            return Response(
                {'message': 'Usuario eliminado exitosamente'},
                status=status.HTTP_204_NO_CONTENT
            )

        except ObjectDoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def bloquear(self, request, pk=None):
        """
        UC-016: Bloquear usuario.

        POST /api/v1/users/{id}/bloquear/
        {
            "razon": "Violación de políticas"
        }
        """
        serializer = BloquearUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            UserService.bloquear_usuario(
                usuario_id=int(pk),
                razon=serializer.validated_data.get('razon', '')
            )

            return Response(
                {'message': 'Usuario bloqueado exitosamente'},
                status=status.HTTP_200_OK
            )

        except ObjectDoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desbloquear(self, request, pk=None):
        """
        UC-016: Desbloquear usuario.

        POST /api/v1/users/{id}/desbloquear/
        """
        try:
            UserService.desbloquear_usuario(usuario_id=int(pk))

            return Response(
                {'message': 'Usuario desbloqueado exitosamente'},
                status=status.HTTP_200_OK
            )

        except ObjectDoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def cambiar_contrasena(self, request, pk=None):
        """
        UC-019: Cambiar contraseña.

        POST /api/v1/users/{id}/cambiar_contrasena/
        {
            "contrasena_actual": "OldP@ss123",
            "contrasena_nueva": "NewP@ss456"
        }
        """
        serializer = CambiarContrasenaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            UserService.cambiar_contrasena(
                usuario_id=int(pk),
                contrasena_actual=serializer.validated_data['contrasena_actual'],
                contrasena_nueva=serializer.validated_data['contrasena_nueva']
            )

            return Response(
                {'message': 'Contraseña cambiada exitosamente'},
                status=status.HTTP_200_OK
            )

        except ObjectDoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
