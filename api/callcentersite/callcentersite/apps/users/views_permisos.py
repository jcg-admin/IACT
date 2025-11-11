"""
Vistas API REST para el sistema de permisos granular.

Endpoints:
  FUNCIONES:
    - GET    /api/permisos/funciones/             (list)
    - POST   /api/permisos/funciones/             (create)
    - GET    /api/permisos/funciones/:id/         (retrieve)
    - PUT    /api/permisos/funciones/:id/         (update)
    - DELETE /api/permisos/funciones/:id/         (destroy)

  CAPACIDADES:
    - GET    /api/permisos/capacidades/           (list)
    - POST   /api/permisos/capacidades/           (create)
    - GET    /api/permisos/capacidades/:id/       (retrieve)
    - PUT    /api/permisos/capacidades/:id/       (update)
    - DELETE /api/permisos/capacidades/:id/       (destroy)

  GRUPOS:
    - GET    /api/permisos/grupos/                (list)
    - POST   /api/permisos/grupos/                (create)
    - GET    /api/permisos/grupos/:id/            (retrieve)
    - PUT    /api/permisos/grupos/:id/            (update)
    - DELETE /api/permisos/grupos/:id/            (destroy)

  PERMISOS EXCEPCIONALES:
    - GET    /api/permisos/excepcionales/         (list)
    - POST   /api/permisos/excepcionales/         (create - grant)
    - DELETE /api/permisos/excepcionales/:id/     (destroy - revoke)

  AUDITORIA:
    - GET    /api/permisos/auditoria/             (list, read-only)

  VERIFICACIÓN:
    - GET    /api/permisos/verificar/:usuario_id/capacidades/
    - GET    /api/permisos/verificar/:usuario_id/tiene-permiso/?capacidad=X
    - GET    /api/permisos/verificar/:usuario_id/menu/
    - GET    /api/permisos/verificar/:usuario_id/grupos/

Referencia: docs/backend/arquitectura/permisos-granular.md
"""

from django.db import connection
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models_permisos_granular import (
    Funcion,
    Capacidad,
    GrupoPermiso,
    PermisoExcepcional,
    AuditoriaPermiso,
    UsuarioGrupo,
)
from .serializers_permisos import (
    FuncionListSerializer,
    FuncionDetailSerializer,
    FuncionCreateUpdateSerializer,
    CapacidadListSerializer,
    CapacidadDetailSerializer,
    CapacidadCreateUpdateSerializer,
    GrupoPermisoListSerializer,
    GrupoPermisoDetailSerializer,
    GrupoPermisoCreateUpdateSerializer,
    PermisoExcepcionalListSerializer,
    PermisoExcepcionalDetailSerializer,
    PermisoExcepcionalCreateSerializer,
    AuditoriaPermisoSerializer,
    UsuarioCapacidadesSerializer,
    VerificarPermisoSerializer,
    MenuUsuarioSerializer,
)
from .services_permisos_granular import UserManagementService

User = get_user_model()


# =============================================================================
# FUNCION VIEWSET
# =============================================================================

class FuncionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de funciones.

    Permisos requeridos:
    - Ver: sistema.administracion.funciones.ver
    - Crear: sistema.administracion.funciones.crear
    - Editar: sistema.administracion.funciones.editar
    - Eliminar: sistema.administracion.funciones.eliminar
    """

    queryset = Funcion.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Selecciona serializer según la acción."""
        if self.action == 'list':
            return FuncionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FuncionCreateUpdateSerializer
        return FuncionDetailSerializer

    def list(self, request):
        """Lista todas las funciones con filtros opcionales."""
        queryset = self.get_queryset()

        # Filtros
        if 'activa' in request.query_params:
            activa = request.query_params['activa'].lower() == 'true'
            queryset = queryset.filter(activa=activa)

        if 'dominio' in request.query_params:
            queryset = queryset.filter(dominio=request.query_params['dominio'])

        if 'categoria' in request.query_params:
            queryset = queryset.filter(categoria=request.query_params['categoria'])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Crea una nueva función."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        funcion = serializer.save()

        output_serializer = FuncionDetailSerializer(funcion)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Obtiene detalle de una función."""
        funcion = self.get_object()
        serializer = self.get_serializer(funcion)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Actualiza una función completa."""
        funcion = self.get_object()
        serializer = self.get_serializer(funcion, data=request.data)
        serializer.is_valid(raise_exception=True)
        funcion = serializer.save()

        output_serializer = FuncionDetailSerializer(funcion)
        return Response(output_serializer.data)

    def partial_update(self, request, pk=None):
        """Actualiza campos parciales de una función."""
        funcion = self.get_object()
        serializer = self.get_serializer(funcion, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        funcion = serializer.save()

        output_serializer = FuncionDetailSerializer(funcion)
        return Response(output_serializer.data)

    def destroy(self, request, pk=None):
        """Desactiva una función (soft delete)."""
        funcion = self.get_object()
        funcion.activa = False
        funcion.save()

        return Response(
            {'message': 'Función desactivada exitosamente'},
            status=status.HTTP_204_NO_CONTENT
        )


# =============================================================================
# CAPACIDAD VIEWSET
# =============================================================================

class CapacidadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de capacidades.

    Permisos requeridos:
    - Ver: sistema.administracion.capacidades.ver
    - Crear: sistema.administracion.capacidades.crear
    - Editar: sistema.administracion.capacidades.editar
    - Eliminar: sistema.administracion.capacidades.eliminar
    """

    queryset = Capacidad.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Selecciona serializer según la acción."""
        if self.action == 'list':
            return CapacidadListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CapacidadCreateUpdateSerializer
        return CapacidadDetailSerializer

    def list(self, request):
        """Lista todas las capacidades con filtros opcionales."""
        queryset = self.get_queryset()

        # Filtros
        if 'activa' in request.query_params:
            activa = request.query_params['activa'].lower() == 'true'
            queryset = queryset.filter(activa=activa)

        if 'nivel_riesgo' in request.query_params:
            queryset = queryset.filter(nivel_riesgo=request.query_params['nivel_riesgo'])

        if 'codigo_contains' in request.query_params:
            queryset = queryset.filter(
                codigo__icontains=request.query_params['codigo_contains']
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Crea una nueva capacidad."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        capacidad = serializer.save()

        output_serializer = CapacidadDetailSerializer(capacidad)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Obtiene detalle de una capacidad."""
        capacidad = self.get_object()
        serializer = self.get_serializer(capacidad)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Actualiza una capacidad completa."""
        capacidad = self.get_object()
        serializer = self.get_serializer(capacidad, data=request.data)
        serializer.is_valid(raise_exception=True)
        capacidad = serializer.save()

        output_serializer = CapacidadDetailSerializer(capacidad)
        return Response(output_serializer.data)

    def partial_update(self, request, pk=None):
        """Actualiza campos parciales de una capacidad."""
        capacidad = self.get_object()
        serializer = self.get_serializer(capacidad, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        capacidad = serializer.save()

        output_serializer = CapacidadDetailSerializer(capacidad)
        return Response(output_serializer.data)

    def destroy(self, request, pk=None):
        """Desactiva una capacidad (soft delete)."""
        capacidad = self.get_object()
        capacidad.activa = False
        capacidad.save()

        return Response(
            {'message': 'Capacidad desactivada exitosamente'},
            status=status.HTTP_204_NO_CONTENT
        )


# =============================================================================
# GRUPO PERMISO VIEWSET
# =============================================================================

class GrupoPermisoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de grupos de permisos.

    Permisos requeridos:
    - Ver: sistema.administracion.grupos.ver
    - Crear: sistema.administracion.grupos.crear
    - Editar: sistema.administracion.grupos.editar
    - Eliminar: sistema.administracion.grupos.eliminar
    """

    queryset = GrupoPermiso.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Selecciona serializer según la acción."""
        if self.action == 'list':
            return GrupoPermisoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return GrupoPermisoCreateUpdateSerializer
        return GrupoPermisoDetailSerializer

    def list(self, request):
        """Lista todos los grupos con filtros opcionales."""
        queryset = self.get_queryset()

        # Filtros
        if 'activo' in request.query_params:
            activo = request.query_params['activo'].lower() == 'true'
            queryset = queryset.filter(activo=activo)

        if 'categoria' in request.query_params:
            queryset = queryset.filter(categoria=request.query_params['categoria'])

        if 'nivel_riesgo' in request.query_params:
            queryset = queryset.filter(nivel_riesgo=request.query_params['nivel_riesgo'])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Crea un nuevo grupo de permisos."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grupo = serializer.save()

        output_serializer = GrupoPermisoDetailSerializer(grupo)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Obtiene detalle de un grupo."""
        grupo = self.get_object()
        serializer = self.get_serializer(grupo)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Actualiza un grupo completo."""
        grupo = self.get_object()
        serializer = self.get_serializer(grupo, data=request.data)
        serializer.is_valid(raise_exception=True)
        grupo = serializer.save()

        output_serializer = GrupoPermisoDetailSerializer(grupo)
        return Response(output_serializer.data)

    def partial_update(self, request, pk=None):
        """Actualiza campos parciales de un grupo."""
        grupo = self.get_object()
        serializer = self.get_serializer(grupo, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        grupo = serializer.save()

        output_serializer = GrupoPermisoDetailSerializer(grupo)
        return Response(output_serializer.data)

    def destroy(self, request, pk=None):
        """Desactiva un grupo (soft delete)."""
        grupo = self.get_object()
        grupo.activo = False
        grupo.save()

        return Response(
            {'message': 'Grupo desactivado exitosamente'},
            status=status.HTTP_204_NO_CONTENT
        )


# =============================================================================
# PERMISO EXCEPCIONAL VIEWSET
# =============================================================================

class PermisoExcepcionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para permisos excepcionales.

    Operaciones:
    - List: Ver todos los permisos excepcionales
    - Create: Otorgar permiso excepcional
    - Retrieve: Ver detalle
    - Destroy: Revocar permiso excepcional

    Permisos requeridos:
    - Ver: sistema.administracion.permisos_excepcionales.ver
    - Otorgar: sistema.administracion.permisos_excepcionales.otorgar
    - Revocar: sistema.administracion.permisos_excepcionales.revocar
    """

    queryset = PermisoExcepcional.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Selecciona serializer según la acción."""
        if self.action == 'list':
            return PermisoExcepcionalListSerializer
        elif self.action == 'create':
            return PermisoExcepcionalCreateSerializer
        return PermisoExcepcionalDetailSerializer

    def list(self, request):
        """Lista permisos excepcionales con filtros."""
        queryset = self.get_queryset()

        # Filtros
        if 'usuario_id' in request.query_params:
            queryset = queryset.filter(usuario_id=request.query_params['usuario_id'])

        if 'activo' in request.query_params:
            activo = request.query_params['activo'].lower() == 'true'
            queryset = queryset.filter(activo=activo)

        if 'tipo' in request.query_params:
            queryset = queryset.filter(tipo=request.query_params['tipo'])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Otorga un permiso excepcional.

        Usa el servicio UserManagementService para otorgar el permiso.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Usar servicio para otorgar permiso
        permiso = UserManagementService.otorgar_permiso_excepcional(
            usuario_solicitante_id=request.user.id,
            usuario_objetivo_id=serializer.validated_data['usuario_id'],
            capacidad_codigo=serializer.validated_data['capacidad_codigo'],
            tipo=serializer.validated_data['tipo'],
            fecha_inicio=serializer.validated_data.get('fecha_inicio'),
            fecha_expiracion=serializer.validated_data.get('fecha_expiracion'),
            motivo=serializer.validated_data['motivo'],
        )

        output_serializer = PermisoExcepcionalDetailSerializer(permiso)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Obtiene detalle de un permiso excepcional."""
        permiso = self.get_object()
        serializer = self.get_serializer(permiso)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Revoca un permiso excepcional."""
        permiso = self.get_object()
        permiso.activo = False
        permiso.save()

        return Response(
            {'message': 'Permiso excepcional revocado exitosamente'},
            status=status.HTTP_204_NO_CONTENT
        )


# =============================================================================
# AUDITORIA VIEWSET
# =============================================================================

class AuditoriaPermisoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para auditoría de permisos.

    Permisos requeridos:
    - Ver: sistema.administracion.auditoria.ver
    """

    queryset = AuditoriaPermiso.objects.all()
    serializer_class = AuditoriaPermisoSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Lista logs de auditoría con filtros."""
        queryset = self.get_queryset()

        # Filtros
        if 'usuario_id' in request.query_params:
            queryset = queryset.filter(usuario_id=request.query_params['usuario_id'])

        if 'accion' in request.query_params:
            queryset = queryset.filter(accion=request.query_params['accion'])

        if 'capacidad_codigo' in request.query_params:
            queryset = queryset.filter(
                capacidad_codigo=request.query_params['capacidad_codigo']
            )

        if 'desde' in request.query_params:
            queryset = queryset.filter(timestamp__gte=request.query_params['desde'])

        if 'hasta' in request.query_params:
            queryset = queryset.filter(timestamp__lte=request.query_params['hasta'])

        # Limitar resultados
        limit = int(request.query_params.get('limit', 100))
        queryset = queryset[:limit]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# =============================================================================
# VERIFICACION VIEWSET (Custom endpoints)
# =============================================================================

class VerificacionPermisoViewSet(viewsets.ViewSet):
    """
    ViewSet para verificación de permisos.

    Endpoints custom:
    - GET /verificar/:usuario_id/capacidades/
    - GET /verificar/:usuario_id/tiene-permiso/?capacidad=X
    - GET /verificar/:usuario_id/menu/
    - GET /verificar/:usuario_id/grupos/
    """

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='capacidades')
    def capacidades(self, request, pk=None):
        """
        Obtiene todas las capacidades de un usuario.

        Usa la función SQL optimizada: obtener_capacidades_usuario()
        """
        usuario_id = int(pk)

        # Verificar que el usuario existe
        if not User.objects.filter(id=usuario_id).exists():
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Usar función SQL para obtener capacidades
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT obtener_capacidades_usuario(%s)",
                [usuario_id]
            )
            capacidades = cursor.fetchone()[0] or []

        data = {
            'usuario_id': usuario_id,
            'capacidades': capacidades,
            'total': len(capacidades),
        }

        serializer = UsuarioCapacidadesSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='tiene-permiso')
    def tiene_permiso(self, request, pk=None):
        """
        Verifica si un usuario tiene una capacidad específica.

        Query params:
        - capacidad: str (requerido)

        Usa la función SQL optimizada: usuario_tiene_permiso()
        """
        usuario_id = int(pk)
        capacidad_codigo = request.query_params.get('capacidad')

        if not capacidad_codigo:
            return Response(
                {'error': 'Query param "capacidad" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que el usuario existe
        if not User.objects.filter(id=usuario_id).exists():
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Usar función SQL para verificar permiso
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT usuario_tiene_permiso(%s, %s)",
                [usuario_id, capacidad_codigo]
            )
            tiene_permiso = cursor.fetchone()[0]

        data = {
            'usuario_id': usuario_id,
            'capacidad_codigo': capacidad_codigo,
            'tiene_permiso': tiene_permiso,
        }

        serializer = VerificarPermisoSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='menu')
    def menu(self, request, pk=None):
        """
        Genera menú dinámico basado en permisos del usuario.

        Usa la función SQL optimizada: obtener_menu_usuario()
        """
        usuario_id = int(pk)

        # Verificar que el usuario existe
        if not User.objects.filter(id=usuario_id).exists():
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Usar función SQL para generar menú
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT obtener_menu_usuario(%s)",
                [usuario_id]
            )
            menu = cursor.fetchone()[0] or {}

        data = {
            'usuario_id': usuario_id,
            'menu': menu,
        }

        serializer = MenuUsuarioSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='grupos')
    def grupos(self, request, pk=None):
        """
        Obtiene grupos activos de un usuario.

        Usa la función SQL optimizada: obtener_grupos_usuario()
        """
        usuario_id = int(pk)

        # Verificar que el usuario existe
        if not User.objects.filter(id=usuario_id).exists():
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Usar función SQL para obtener grupos
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT obtener_grupos_usuario(%s)",
                [usuario_id]
            )
            grupos = cursor.fetchone()[0] or []

        return Response({
            'usuario_id': usuario_id,
            'grupos': grupos,
            'total': len(grupos),
        })
