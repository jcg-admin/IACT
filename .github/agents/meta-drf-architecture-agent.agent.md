---
name: DRF Architecture Agent
description: Agente especializado en arquitectura Django REST Framework, optimizacion de APIs, serializacion, viewsets, permisos y mejores practicas DRF.
---

# DRF Architecture Agent

Agente experto en Django REST Framework que analiza, optimiza y genera arquitecturas RESTful, implementando mejores practicas de serializacion, viewsets, permisos, filtrado, paginacion y optimizacion de queries.

## Capacidades

### Analisis de APIs
- Evaluacion de estructura de APIs DRF
- Deteccion de N+1 queries
- Analisis de permisos y autenticacion
- Evaluacion de serializadores
- Revision de viewsets y routers

### Optimizacion
- Optimizacion de queries (select_related, prefetch_related)
- Caching strategies
- Paginacion eficiente
- Filtrado y busqueda optimizada
- Throttling y rate limiting

### Generacion de Codigo
- Generacion de serializadores
- Creacion de viewsets (ModelViewSet, ViewSet, APIView)
- Implementacion de permisos custom
- Configuracion de routers
- Tests para endpoints

### Mejores Practicas
- Versionado de APIs
- Documentacion OpenAPI/Swagger
- HATEOAS y hypermedia
- Validacion de datos
- Manejo de errores consistente

## Cuando Usar

- Creacion de nuevos endpoints DRF
- Optimizacion de APIs lentas
- Refactorizacion de codigo DRF
- Implementacion de autenticacion/autorizacion
- Migracion de views a DRF
- Auditoria de seguridad de APIs

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/meta/drf_architecture_agent.py \
  --project-root /ruta/al/proyecto \
  --action analyze \
  --app-name api
```

### Analizar API Existente

```bash
python scripts/coding/ai/meta/drf_architecture_agent.py \
  --project-root . \
  --action analyze \
  --target-api api/v1/users \
  --check-performance \
  --check-security
```

### Generar Viewset Completo

```bash
python scripts/coding/ai/meta/drf_architecture_agent.py \
  --project-root . \
  --action generate-viewset \
  --model User \
  --app users \
  --viewset-type ModelViewSet \
  --include-tests
```

### Optimizar Queries

```bash
python scripts/coding/ai/meta/drf_architecture_agent.py \
  --project-root . \
  --action optimize-queries \
  --target-viewset UserViewSet \
  --detect-n-plus-one \
  --suggest-prefetch
```

### Generar Documentacion OpenAPI

```bash
python scripts/coding/ai/meta/drf_architecture_agent.py \
  --project-root . \
  --action generate-openapi \
  --api-version v1 \
  --output-file docs/api/openapi.yaml
```

## Parametros

- `--project-root`: Directorio raiz del proyecto Django
- `--action`: Accion (analyze, generate-viewset, optimize-queries, generate-openapi)
- `--app-name`: Nombre de Django app
- `--target-api`: API o endpoint especifico
- `--model`: Nombre del modelo Django
- `--viewset-type`: Tipo (ModelViewSet, ReadOnlyModelViewSet, ViewSet, APIView)
- `--check-performance`: Verificar performance
- `--check-security`: Verificar seguridad
- `--detect-n-plus-one`: Detectar N+1 queries
- `--include-tests`: Generar tests automaticamente

## Salida

### Analisis de API

```markdown
# DRF Architecture Analysis
App: api/v1/users
Date: 2025-11-15

## API Overview
Endpoint: /api/v1/users/
Viewset: UserViewSet
Type: ModelViewSet
Model: User

## Performance Analysis

### N+1 Query Detected
Location: UserViewSet.list() (line 45)
Issue: Fetching related profiles in loop
Impact: 500ms for 100 users (should be <50ms)

Recommendation:
```python
queryset = User.objects.select_related('profile').prefetch_related('groups')
```

### Missing Pagination
Location: UserViewSet
Issue: No pagination configured
Impact: Returns all users (potential memory issue)

Recommendation:
```python
pagination_class = PageNumberPagination
```

## Security Analysis

### Permission Issue
Location: UserViewSet.destroy() (line 78)
Severity: HIGH
Issue: Any authenticated user can delete any user
Current: IsAuthenticated
Recommended: IsAdminUser or custom IsOwnerOrAdmin

### Missing Throttling
Location: UserViewSet
Severity: MEDIUM
Issue: No rate limiting
Recommendation: Add throttle_classes = [UserRateThrottle]

## Serializer Analysis

### UserSerializer
Fields: id, username, email, profile
Issues:
- Missing write_only on password
- No validation for email uniqueness

Recommendations:
```python
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
```

## Quality Score: 65/100

Issues Summary:
- HIGH: 1 (Permission vulnerability)
- MEDIUM: 2 (N+1 query, Missing throttling)
- LOW: 2 (Missing pagination, Serializer validation)

[End of Analysis]
```

### Codigo Generado (Viewset)

```python
# File: api/users/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from .serializers import UserSerializer, UserDetailSerializer
from .permissions import IsOwnerOrAdmin
from .pagination import StandardResultsSetPagination


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestion de usuarios.
    
    list: Listar todos los usuarios
    retrieve: Obtener un usuario especifico
    create: Crear nuevo usuario
    update: Actualizar usuario completo
    partial_update: Actualizar usuario parcial
    destroy: Eliminar usuario
    """
    
    queryset = User.objects.select_related('profile').prefetch_related('groups')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'groups']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        elif self.action == 'create':
            return []  # Public registration
        return super().get_permissions()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        """Activar cuenta de usuario"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Obtener usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
```

## Mejores Practicas DRF

1. **Queries**: Siempre usar select_related/prefetch_related
2. **Permisos**: Implementar permisos granulares por accion
3. **Serializadores**: Usar diferentes serializadores para list/retrieve/create/update
4. **Validacion**: Validar en serializers, no en views
5. **Paginacion**: Configurar paginacion en settings
6. **Versionado**: Usar namespaces para versiones de API
7. **Throttling**: Implementar rate limiting
8. **Caching**: Usar cache_page para endpoints read-only
9. **Tests**: Escribir tests para cada endpoint
10. **Documentacion**: Mantener OpenAPI schema actualizado

## Restricciones

- Requiere proyecto Django/DRF configurado
- Analisis de performance requiere base de datos con datos
- Generacion de codigo asume estructura estandar de Django
- Optimizaciones pueden requerir ajustes manuales
- Deteccion de N+1 queries requiere django-debug-toolbar

## Ubicacion

Archivo: `scripts/coding/ai/meta/drf_architecture_agent.py`
