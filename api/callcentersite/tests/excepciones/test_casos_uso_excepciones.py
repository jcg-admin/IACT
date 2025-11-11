"""Tests TDD para Casos de Uso del módulo de Excepciones."""

import pytest
from django.contrib.auth import get_user_model

from callcentersite.apps.excepciones.models import Excepcion
from callcentersite.apps.excepciones.services import ExcepcionService

User = get_user_model()


@pytest.mark.django_db
class TestSolicitarExcepcion:
    """Test de solicitud de excepciones."""

    def test_solicitar_excepcion_exitoso(self):
        """Solicitar excepción."""
        usuario = User.objects.create_user(username='user', password='pass', email='user@test.com')
        
        excepcion = ExcepcionService.solicitar_excepcion(
            titulo='Excepción horario especial',
            justificacion='Cliente VIP requiere atención fuera de horario',
            tipo='horario',
            solicitado_por_id=usuario.id
        )
        
        assert excepcion.titulo == 'Excepción horario especial'
        assert excepcion.estado == 'solicitada'
        assert excepcion.solicitado_por == usuario


@pytest.mark.django_db
class TestListarExcepciones:
    """Test de listado de excepciones."""

    def test_listar_todas_excepciones(self):
        """Listar todas las excepciones."""
        usuario = User.objects.create_user(username='user', password='pass', email='user@test.com')
        
        ExcepcionService.solicitar_excepcion('E1', 'Just1', 'tipo1', usuario.id)
        ExcepcionService.solicitar_excepcion('E2', 'Just2', 'tipo2', usuario.id)
        
        excepciones = ExcepcionService.listar_excepciones()
        assert len(excepciones) >= 2

    def test_filtrar_excepciones_por_estado(self):
        """Filtrar excepciones por estado."""
        usuario = User.objects.create_user(username='user', password='pass', email='user@test.com')
        
        e1 = ExcepcionService.solicitar_excepcion('E1', 'Just1', 'tipo1', usuario.id)
        e1.estado = 'aprobada'
        e1.save()
        
        ExcepcionService.solicitar_excepcion('E2', 'Just2', 'tipo2', usuario.id)
        
        aprobadas = ExcepcionService.listar_excepciones(estado='aprobada')
        assert len(aprobadas) >= 1
        assert all(e.estado == 'aprobada' for e in aprobadas)


@pytest.mark.django_db
class TestAprobarExcepcion:
    """Test de aprobación de excepciones."""

    def test_aprobar_excepcion_exitoso(self):
        """Aprobar excepción solicitada."""
        usuario = User.objects.create_user(username='user', password='pass', email='user@test.com')
        aprobador = User.objects.create_user(username='aprobador', password='pass', email='aprobador@test.com')
        
        excepcion = ExcepcionService.solicitar_excepcion('E1', 'Justificación', 'horario', usuario.id)
        
        resultado = ExcepcionService.aprobar_excepcion(excepcion.id, aprobador.id)
        
        assert resultado.estado == 'aprobada'
        assert resultado.aprobado_por == aprobador


@pytest.mark.django_db
class TestRechazarExcepcion:
    """Test de rechazo de excepciones."""

    def test_rechazar_excepcion_exitoso(self):
        """Rechazar excepción solicitada."""
        usuario = User.objects.create_user(username='user', password='pass', email='user@test.com')
        rechazador = User.objects.create_user(username='rechazador', password='pass', email='rechazador@test.com')
        
        excepcion = ExcepcionService.solicitar_excepcion('E1', 'Justificación', 'horario', usuario.id)
        
        resultado = ExcepcionService.rechazar_excepcion(excepcion.id, rechazador.id)
        
        assert resultado.estado == 'rechazada'
        assert resultado.aprobado_por == rechazador


@pytest.mark.django_db
class TestExportarExcepciones:
    """Test de exportación de excepciones."""

    def test_exportar_excepciones_json(self):
        """Exportar excepciones a JSON."""
        usuario = User.objects.create_user(username='user', password='pass', email='user@test.com')
        
        ExcepcionService.solicitar_excepcion('E1', 'Justificación', 'horario', usuario.id)
        
        json_data = ExcepcionService.exportar_excepciones()
        
        assert json_data is not None
        assert 'E1' in json_data
        assert 'horario' in json_data
