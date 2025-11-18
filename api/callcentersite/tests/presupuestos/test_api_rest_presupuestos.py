"""Tests de integración para API REST de presupuestos."""

import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from callcentersite.apps.presupuestos.models import Presupuesto

User = get_user_model()


@pytest.mark.django_db
class TestPresupuestoAPIREST:
    """Tests de integración para API REST /api/v1/presupuestos/"""

    def setup_method(self):
        """Setup para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='admin', password='pass', email='admin@test.com', is_staff=True)
        self.client.force_authenticate(user=self.user)

    def test_api_listar_presupuestos(self):
        """GET /api/v1/presupuestos/ - Listar presupuestos."""
        Presupuesto.objects.create(
            titulo='P1', descripcion='Desc', monto=1000,
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=30),
            creado_por=self.user
        )
        
        response = self.client.get('/api/v1/presupuestos/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_api_crear_presupuesto(self):
        """POST /api/v1/presupuestos/ - Crear presupuesto."""
        datos = {
            'titulo': 'Nuevo Presupuesto',
            'descripcion': 'Descripción',
            'monto': '50000.00',
            'periodo_inicio': str(date.today()),
            'periodo_fin': str(date.today() + timedelta(days=90)),
            'estado': 'borrador'
        }
        
        response = self.client.post('/api/v1/presupuestos/', datos, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['titulo'] == 'Nuevo Presupuesto'

    def test_api_obtener_presupuesto(self):
        """GET /api/v1/presupuestos/{id}/ - Obtener presupuesto."""
        presupuesto = Presupuesto.objects.create(
            titulo='P1', descripcion='Desc', monto=1000,
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=30),
            creado_por=self.user
        )
        
        response = self.client.get(f'/api/v1/presupuestos/{presupuesto.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['titulo'] == 'P1'

    def test_api_aprobar_presupuesto(self):
        """POST /api/v1/presupuestos/{id}/aprobar/ - Aprobar presupuesto."""
        presupuesto = Presupuesto.objects.create(
            titulo='P1', descripcion='Desc', monto=1000,
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=30),
            creado_por=self.user, estado='pendiente'
        )
        
        response = self.client.post(f'/api/v1/presupuestos/{presupuesto.id}/aprobar/')
        
        assert response.status_code == status.HTTP_200_OK
        presupuesto.refresh_from_db()
        assert presupuesto.estado == 'aprobado'

    def test_api_rechazar_presupuesto(self):
        """POST /api/v1/presupuestos/{id}/rechazar/ - Rechazar presupuesto."""
        presupuesto = Presupuesto.objects.create(
            titulo='P1', descripcion='Desc', monto=1000,
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=30),
            creado_por=self.user, estado='pendiente'
        )
        
        response = self.client.post(f'/api/v1/presupuestos/{presupuesto.id}/rechazar/')
        
        assert response.status_code == status.HTTP_200_OK
        presupuesto.refresh_from_db()
        assert presupuesto.estado == 'rechazado'

    def test_api_exportar_presupuestos(self):
        """POST /api/v1/presupuestos/exportar/ - Exportar presupuestos."""
        Presupuesto.objects.create(
            titulo='P1', descripcion='Desc', monto=1000,
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=30),
            creado_por=self.user
        )
        
        response = self.client.post('/api/v1/presupuestos/exportar/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'application/json' in response['Content-Type']

    def test_api_autenticacion_requerida(self):
        """API requiere autenticación."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/v1/presupuestos/')
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
