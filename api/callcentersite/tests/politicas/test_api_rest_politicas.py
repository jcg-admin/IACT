"""Tests de integración para API REST de políticas."""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from callcentersite.apps.politicas.models import Politica

User = get_user_model()


@pytest.mark.django_db
class TestPoliticaAPIREST:
    """Tests de integración para API REST /api/v1/politicas/"""

    def setup_method(self):
        """Setup para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='admin', password='pass', email='admin@test.com', is_staff=True)
        self.client.force_authenticate(user=self.user)

    def test_api_listar_politicas(self):
        """GET /api/v1/politicas/ - Listar políticas."""
        Politica.objects.create(titulo='P1', contenido='Contenido', creado_por=self.user)
        
        response = self.client.get('/api/v1/politicas/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_api_crear_politica(self):
        """POST /api/v1/politicas/ - Crear política."""
        datos = {
            'titulo': 'Nueva Política',
            'contenido': 'Contenido de la política',
            'estado': 'borrador'
        }
        
        response = self.client.post('/api/v1/politicas/', datos, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['titulo'] == 'Nueva Política'

    def test_api_obtener_politica(self):
        """GET /api/v1/politicas/{id}/ - Obtener política."""
        politica = Politica.objects.create(titulo='P1', contenido='Contenido', creado_por=self.user)
        
        response = self.client.get(f'/api/v1/politicas/{politica.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['titulo'] == 'P1'

    def test_api_publicar_politica(self):
        """POST /api/v1/politicas/{id}/publicar/ - Publicar política."""
        politica = Politica.objects.create(titulo='P1', contenido='Contenido', creado_por=self.user)
        
        response = self.client.post(f'/api/v1/politicas/{politica.id}/publicar/')
        
        assert response.status_code == status.HTTP_200_OK
        politica.refresh_from_db()
        assert politica.estado == 'publicada'

    def test_api_archivar_politica(self):
        """POST /api/v1/politicas/{id}/archivar/ - Archivar política."""
        politica = Politica.objects.create(titulo='P1', contenido='Contenido', creado_por=self.user, estado='publicada')
        
        response = self.client.post(f'/api/v1/politicas/{politica.id}/archivar/')
        
        assert response.status_code == status.HTTP_200_OK
        politica.refresh_from_db()
        assert politica.estado == 'archivada'

    def test_api_nueva_version(self):
        """POST /api/v1/politicas/{id}/nueva_version/ - Crear nueva versión."""
        politica = Politica.objects.create(titulo='P1', contenido='Contenido original', creado_por=self.user, version=1)
        
        response = self.client.post(
            f'/api/v1/politicas/{politica.id}/nueva_version/',
            {'contenido': 'Contenido actualizado'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['version'] == 2

    def test_api_autenticacion_requerida(self):
        """API requiere autenticación."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/v1/politicas/')
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
