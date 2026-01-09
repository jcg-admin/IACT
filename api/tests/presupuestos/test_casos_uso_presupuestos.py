"""
Tests TDD para Casos de Uso del módulo de Presupuestos.

Sistema de gestión de presupuestos.
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from callcentersite.apps.presupuestos.models import Presupuesto
from callcentersite.apps.presupuestos.services import PresupuestoService

User = get_user_model()


@pytest.mark.django_db
class TestCrearPresupuesto:
    """Test de creación de presupuestos."""

    def test_crear_presupuesto_exitoso(self):
        """Crear presupuesto en estado borrador."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        presupuesto = PresupuestoService.crear_presupuesto(
            titulo='Presupuesto Q1 2025',
            descripcion='Presupuesto del primer trimestre',
            monto=100000.00,
            periodo_inicio=date(2025, 1, 1),
            periodo_fin=date(2025, 3, 31),
            creado_por_id=usuario.id
        )
        
        assert presupuesto.titulo == 'Presupuesto Q1 2025'
        assert presupuesto.monto == 100000.00
        assert presupuesto.estado == 'borrador'
        assert presupuesto.creado_por == usuario


@pytest.mark.django_db
class TestListarPresupuestos:
    """Test de listado de presupuestos."""

    def test_listar_todos_presupuestos(self):
        """Listar todos los presupuestos."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        PresupuestoService.crear_presupuesto('P1', 'Desc1', 1000, date.today(), date.today() + timedelta(days=30), usuario.id)
        PresupuestoService.crear_presupuesto('P2', 'Desc2', 2000, date.today(), date.today() + timedelta(days=30), usuario.id)
        
        presupuestos = PresupuestoService.listar_presupuestos()
        assert len(presupuestos) >= 2

    def test_filtrar_presupuestos_por_estado(self):
        """Filtrar presupuestos por estado."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        p1 = PresupuestoService.crear_presupuesto('P1', 'Desc1', 1000, date.today(), date.today() + timedelta(days=30), usuario.id)
        p1.estado = 'pendiente'
        p1.save()
        
        PresupuestoService.crear_presupuesto('P2', 'Desc2', 2000, date.today(), date.today() + timedelta(days=30), usuario.id)
        
        pendientes = PresupuestoService.listar_presupuestos(estado='pendiente')
        assert len(pendientes) >= 1
        assert all(p.estado == 'pendiente' for p in pendientes)


@pytest.mark.django_db
class TestAprobarPresupuesto:
    """Test de aprobación de presupuestos."""

    def test_aprobar_presupuesto_exitoso(self):
        """Aprobar presupuesto pendiente."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        aprobador = User.objects.create_user(username='aprobador', password='pass', email='aprobador@test.com')
        
        presupuesto = PresupuestoService.crear_presupuesto('P1', 'Desc', 1000, date.today(), date.today() + timedelta(days=30), usuario.id)
        presupuesto.estado = 'pendiente'
        presupuesto.save()
        
        resultado = PresupuestoService.aprobar_presupuesto(presupuesto.id, aprobador.id)
        
        assert resultado.estado == 'aprobado'
        assert resultado.aprobado_por == aprobador

    def test_aprobar_presupuesto_no_pendiente_falla(self):
        """No se puede aprobar presupuesto que no está pendiente."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        presupuesto = PresupuestoService.crear_presupuesto('P1', 'Desc', 1000, date.today(), date.today() + timedelta(days=30), usuario.id)
        # estado = 'borrador', no 'pendiente'
        
        with pytest.raises(ValidationError):
            PresupuestoService.aprobar_presupuesto(presupuesto.id, usuario.id)


@pytest.mark.django_db
class TestRechazarPresupuesto:
    """Test de rechazo de presupuestos."""

    def test_rechazar_presupuesto_exitoso(self):
        """Rechazar presupuesto pendiente."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        rechazador = User.objects.create_user(username='rechazador', password='pass', email='rechazador@test.com')
        
        presupuesto = PresupuestoService.crear_presupuesto('P1', 'Desc', 1000, date.today(), date.today() + timedelta(days=30), usuario.id)
        presupuesto.estado = 'pendiente'
        presupuesto.save()
        
        resultado = PresupuestoService.rechazar_presupuesto(presupuesto.id, rechazador.id)
        
        assert resultado.estado == 'rechazado'
        assert resultado.aprobado_por == rechazador


@pytest.mark.django_db
class TestExportarPresupuestos:
    """Test de exportación de presupuestos."""

    def test_exportar_presupuestos_json(self):
        """Exportar presupuestos a JSON."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        PresupuestoService.crear_presupuesto('P1', 'Desc', 1000, date.today(), date.today() + timedelta(days=30), usuario.id)
        
        json_data = PresupuestoService.exportar_presupuestos()
        
        assert json_data is not None
        assert 'P1' in json_data
        assert '1000' in json_data
