"""Tests TDD para Casos de Uso del módulo de Políticas."""

import pytest
from django.contrib.auth import get_user_model

from callcentersite.apps.politicas.models import Politica
from callcentersite.apps.politicas.services import PoliticaService

User = get_user_model()


@pytest.mark.django_db
class TestCrearPolitica:
    """Test de creación de políticas."""

    def test_crear_politica_exitoso(self):
        """Crear política en estado borrador."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        politica = PoliticaService.crear_politica(
            titulo='Política de Vacaciones',
            contenido='Los empleados tienen derecho a 15 días de vacaciones al año.',
            creado_por_id=usuario.id
        )
        
        assert politica.titulo == 'Política de Vacaciones'
        assert politica.version == 1
        assert politica.estado == 'borrador'
        assert politica.creado_por == usuario


@pytest.mark.django_db
class TestListarPoliticas:
    """Test de listado de políticas."""

    def test_listar_todas_politicas(self):
        """Listar todas las políticas."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        PoliticaService.crear_politica('P1', 'Contenido 1', usuario.id)
        PoliticaService.crear_politica('P2', 'Contenido 2', usuario.id)
        
        politicas = PoliticaService.listar_politicas()
        assert len(politicas) >= 2

    def test_filtrar_politicas_por_estado(self):
        """Filtrar políticas por estado."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        p1 = PoliticaService.crear_politica('P1', 'Contenido 1', usuario.id)
        p1.estado = 'publicada'
        p1.save()
        
        PoliticaService.crear_politica('P2', 'Contenido 2', usuario.id)
        
        publicadas = PoliticaService.listar_politicas(estado='publicada')
        assert len(publicadas) >= 1
        assert all(p.estado == 'publicada' for p in publicadas)


@pytest.mark.django_db
class TestPublicarPolitica:
    """Test de publicación de políticas."""

    def test_publicar_politica_exitoso(self):
        """Publicar política borrador."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        publicador = User.objects.create_user(username='publicador', password='pass', email='pub@test.com')
        
        politica = PoliticaService.crear_politica('P1', 'Contenido', usuario.id)
        
        resultado = PoliticaService.publicar_politica(politica.id, publicador.id)
        
        assert resultado.estado == 'publicada'
        assert resultado.publicado_por == publicador


@pytest.mark.django_db
class TestArchivarPolitica:
    """Test de archivado de políticas."""

    def test_archivar_politica_exitoso(self):
        """Archivar política obsoleta."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        politica = PoliticaService.crear_politica('P1', 'Contenido', usuario.id)
        
        resultado = PoliticaService.archivar_politica(politica.id)
        
        assert resultado.estado == 'archivada'


@pytest.mark.django_db
class TestNuevaVersionPolitica:
    """Test de versionamiento de políticas."""

    def test_crear_nueva_version_exitoso(self):
        """Crear nueva versión de política existente."""
        usuario = User.objects.create_user(username='admin', password='pass', email='admin@test.com')
        
        politica_v1 = PoliticaService.crear_politica('Política de Vacaciones', 'Contenido original', usuario.id)
        
        politica_v2 = PoliticaService.nueva_version(
            politica_v1.id,
            'Contenido actualizado con nuevas reglas',
            usuario.id
        )
        
        assert politica_v2.titulo == politica_v1.titulo
        assert politica_v2.version == 2
        assert politica_v2.contenido == 'Contenido actualizado con nuevas reglas'
        assert politica_v2.estado == 'borrador'
