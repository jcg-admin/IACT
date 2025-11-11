"""Tests de integración para API REST de excepciones."""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from callcentersite.apps.excepciones.models import Excepcion

User = get_user_model()


@pytest.mark.django_db
class TestExcepcionAPIREST:
    """Tests de integración para API REST /api/v1/excepciones/"""

    def setup_method(self):
        """Setup para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='user', password='pass', email='user@test.com', is_staff=True)
        self.client.force_authenticate(user=self.user)

    def test_api_listar_excepciones(self):
        """GET /api/v1/excepciones/ - Listar excepciones."""
        Excepcion.objects.create(titulo='E1', justificacion='Just', tipo='horario', solicitado_por=self.user)
        
        response = self.client.get('/api/v1/excepciones/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_api_crear_excepcion(self):
        """POST /api/v1/excepciones/ - Crear excepción."""
        datos = {
            'titulo': 'Nueva Excepción',
            'justificacion': 'Cliente VIP requiere atención especial',
            'tipo': 'horario',
            'estado': 'solicitada'
        }
        
        response = self.client.post('/api/v1/excepciones/', datos, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['titulo'] == 'Nueva Excepción'

    def test_api_obtener_excepcion(self):
        """GET /api/v1/excepciones/{id}/ - Obtener excepción."""
        excepcion = Excepcion.objects.create(titulo='E1', justificacion='Just', tipo='horario', solicitado_por=self.user)
        
        response = self.client.get(f'/api/v1/excepciones/{excepcion.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['titulo'] == 'E1'

    def test_api_aprobar_excepcion(self):
        """POST /api/v1/excepciones/{id}/aprobar/ - Aprobar excepción."""
        excepcion = Excepcion.objects.create(
            titulo='E1', justificacion='Just', tipo='horario',
            solicitado_por=self.user, estado='solicitada'
        )
        
        response = self.client.post(f'/api/v1/excepciones/{excepcion.id}/aprobar/')
        
        assert response.status_code == status.HTTP_200_OK
        excepcion.refresh_from_db()
        assert excepcion.estado == 'aprobada'

    def test_api_rechazar_excepcion(self):
        """POST /api/v1/excepciones/{id}/rechazar/ - Rechazar excepción."""
        excepcion = Excepcion.objects.create(
            titulo='E1', justificacion='Just', tipo='horario',
            solicitado_por=self.user, estado='solicitada'
        )
        
        response = self.client.post(f'/api/v1/excepciones/{excepcion.id}/rechazar/')
        
        assert response.status_code == status.HTTP_200_OK
        excepcion.refresh_from_db()
        assert excepcion.estado == 'rechazada'

    def test_api_exportar_excepciones(self):
        """POST /api/v1/excepciones/exportar/ - Exportar excepciones."""
        Excepcion.objects.create(titulo='E1', justificacion='Just', tipo='horario', solicitado_por=self.user)
        
        response = self.client.post('/api/v1/excepciones/exportar/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'application/json' in response['Content-Type']

    def test_api_autenticacion_requerida(self):
        """API requiere autenticación."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/v1/excepciones/')
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
