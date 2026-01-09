"""
Tests TDD para Casos de Uso del módulo de Llamadas.

Sistema de gestión de llamadas del call center.
Casos de uso implementados siguiendo TDD.
"""

import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from callcentersite.apps.llamadas.models import (
    Llamada,
    EstadoLlamada,
    TipoLlamada,
)
from callcentersite.apps.permissions.models import (
    Capacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
)

User = get_user_model()


@pytest.mark.django_db
class TestUC010_RegistrarLlamadaEntrante:
    """
    UC-010: Registrar Llamada Entrante.

    Actor: Agente de Call Center
    Precondición: Agente autenticado con permiso "sistema.operaciones.llamadas.registrar"

    Flujo principal:
    1. Sistema recibe datos de llamada entrante
    2. Sistema valida que agente tenga permiso
    3. Sistema genera código único de llamada
    4. Sistema crea registro de llamada con estado "en_curso"
    5. Sistema retorna código de llamada generado
    """

    def test_registrar_llamada_entrante_exitosa(self):
        """
        UC-010 Escenario 1: Registro exitoso de llamada entrante.

        Given un agente autenticado con permisos
          And datos válidos de llamada (teléfono, tipo)
        When se registra la llamada
        Then se crea registro con estado "en_curso"
          And se genera código único
          And se registra timestamp de inicio
        """
        # Arrange - Crear agente
        agente = User.objects.create_user(
            username='agente.callcenter',
            password='SecureP@ss123',
            email='agente@company.com',
        )

        # Crear permisos necesarios
        capacidad_registrar = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.registrar',
            accion='registrar',
            recurso='llamadas',
            dominio='operaciones',
            activa=True,
        )

        grupo = GrupoPermisos.objects.create(
            codigo='agentes_callcenter',
            nombre_display='Agentes Call Center',
            activo=True,
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad_registrar)
        UsuarioGrupo.objects.create(usuario=agente, grupo=grupo, activo=True)

        # Crear estados y tipos
        estado_en_curso = EstadoLlamada.objects.create(
            codigo='en_curso',
            nombre='En Curso',
            es_final=False,
            activo=True,
        )

        tipo_entrante = TipoLlamada.objects.create(
            codigo='entrante',
            nombre='Llamada Entrante',
            activo=True,
        )

        # Act - Registrar llamada usando servicio
        from callcentersite.apps.llamadas.services import LlamadaService

        llamada = LlamadaService.registrar_llamada_entrante(
            agente_id=agente.id,
            numero_telefono='+52-555-1234-567',
            tipo_id=tipo_entrante.id,
            cliente_nombre='Juan Pérez',
            cliente_email='juan@example.com',
        )

        # Assert
        assert llamada is not None
        assert llamada.codigo.startswith('CALL-')
        assert llamada.agente == agente
        assert llamada.numero_telefono == '+52-555-1234-567'
        assert llamada.estado == estado_en_curso
        assert llamada.tipo == tipo_entrante
        assert llamada.fecha_inicio is not None
        assert llamada.fecha_fin is None

    def test_registrar_llamada_sin_permiso(self):
        """
        UC-010 Escenario 2: Intento de registro sin permisos.

        Given un agente sin permiso de registrar llamadas
        When intenta registrar una llamada
        Then el sistema rechaza la operación
          And lanza excepción PermissionDenied
        """
        # Arrange
        agente_sin_permiso = User.objects.create_user(
            username='trainee.agent',
            password='SecureP@ss123',
            email='trainee@company.com',
        )

        tipo_entrante = TipoLlamada.objects.create(
            codigo='entrante',
            nombre='Llamada Entrante',
            activo=True,
        )

        # Act & Assert
        from callcentersite.apps.llamadas.services import LlamadaService
        from django.core.exceptions import PermissionDenied

        with pytest.raises(PermissionDenied) as exc_info:
            LlamadaService.registrar_llamada_entrante(
                agente_id=agente_sin_permiso.id,
                numero_telefono='+52-555-9999-999',
                tipo_id=tipo_entrante.id,
            )

        assert 'sin permiso' in str(exc_info.value).lower()

    def test_registrar_llamada_con_metadata(self):
        """
        UC-010 Escenario 3: Registro con metadata adicional.

        Given un agente con permisos
          And metadata adicional (origen IVR, cola, etc)
        When se registra la llamada
        Then metadata se almacena en campo JSON
        """
        # Arrange
        agente = User.objects.create_user(
            username='senior.agent',
            password='SecureP@ss123',
            email='senior@company.com',
        )

        capacidad = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.registrar',
            accion='registrar',
            recurso='llamadas',
            dominio='operaciones',
            activa=True,
        )

        grupo = GrupoPermisos.objects.create(
            codigo='agentes_senior',
            nombre_display='Agentes Senior',
            activo=True,
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad)
        UsuarioGrupo.objects.create(usuario=agente, grupo=grupo, activo=True)

        estado = EstadoLlamada.objects.create(
            codigo='en_curso',
            nombre='En Curso',
            activo=True,
        )

        tipo = TipoLlamada.objects.create(
            codigo='entrante',
            nombre='Entrante',
            activo=True,
        )

        # Act
        from callcentersite.apps.llamadas.services import LlamadaService

        metadata = {
            'origen_ivr': 'menu_principal',
            'cola': 'soporte_tecnico',
            'prioridad': 'alta',
            'intentos_previos': 2,
        }

        llamada = LlamadaService.registrar_llamada_entrante(
            agente_id=agente.id,
            numero_telefono='+52-555-7777-777',
            tipo_id=tipo.id,
            metadata=metadata,
        )

        # Assert
        assert llamada.metadata['origen_ivr'] == 'menu_principal'
        assert llamada.metadata['cola'] == 'soporte_tecnico'
        assert llamada.metadata['prioridad'] == 'alta'
        assert llamada.metadata['intentos_previos'] == 2


@pytest.mark.django_db
class TestUC011_FinalizarLlamada:
    """
    UC-011: Finalizar Llamada.

    Actor: Agente de Call Center
    Precondición: Llamada en estado "en_curso"

    Flujo principal:
    1. Sistema recibe solicitud de finalizar llamada
    2. Sistema valida que llamada exista y esté en curso
    3. Sistema valida permisos del agente
    4. Sistema actualiza estado a "finalizada"
    5. Sistema registra fecha_fin
    6. Sistema calcula duración
    """

    def test_finalizar_llamada_exitosa(self):
        """
        UC-011 Escenario 1: Finalización exitosa.

        Given una llamada en curso
          And agente con permisos
        When se finaliza la llamada
        Then estado cambia a "finalizada"
          And se registra fecha_fin
          And se calcula duración
        """
        # Arrange
        agente = User.objects.create_user(
            username='agent.finish',
            password='SecureP@ss123',
            email='finish@company.com',
        )

        # Permisos
        capacidad_finalizar = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.finalizar',
            accion='finalizar',
            recurso='llamadas',
            dominio='operaciones',
            activa=True,
        )

        grupo = GrupoPermisos.objects.create(
            codigo='agentes_activos',
            nombre_display='Agentes Activos',
            activo=True,
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad_finalizar)
        UsuarioGrupo.objects.create(usuario=agente, grupo=grupo, activo=True)

        # Estados
        estado_en_curso = EstadoLlamada.objects.create(
            codigo='en_curso',
            nombre='En Curso',
            es_final=False,
            activo=True,
        )

        estado_finalizada = EstadoLlamada.objects.create(
            codigo='finalizada',
            nombre='Finalizada',
            es_final=True,
            activo=True,
        )

        tipo = TipoLlamada.objects.create(
            codigo='entrante',
            nombre='Entrante',
            activo=True,
        )

        # Crear llamada en curso
        llamada = Llamada.objects.create(
            numero_telefono='+52-555-1111-111',
            tipo=tipo,
            estado=estado_en_curso,
            agente=agente,
            fecha_inicio=timezone.now() - timedelta(minutes=5),
        )

        # Act
        from callcentersite.apps.llamadas.services import LlamadaService

        llamada_finalizada = LlamadaService.finalizar_llamada(
            llamada_id=llamada.id,
            agente_id=agente.id,
            notas='Cliente satisfecho con la atención',
            resolucion='Problema resuelto',
        )

        # Assert
        assert llamada_finalizada.estado == estado_finalizada
        assert llamada_finalizada.fecha_fin is not None
        assert llamada_finalizada.fecha_fin > llamada_finalizada.fecha_inicio
        assert llamada_finalizada.notas == 'Cliente satisfecho con la atención'
        assert 'resolucion' in llamada_finalizada.metadata

    def test_finalizar_llamada_inexistente(self):
        """
        UC-011 Escenario 2: Intento de finalizar llamada inexistente.

        Given ID de llamada que no existe
          And agente con permisos válidos
        When se intenta finalizar
        Then sistema lanza excepción NotFound
        """
        # Arrange
        agente = User.objects.create_user(
            username='agent.test',
            password='SecureP@ss123',
            email='test@company.com',
        )

        # Dar permisos al agente
        capacidad = Capacidad.objects.create(
            nombre_completo='sistema.operaciones.llamadas.finalizar',
            accion='finalizar',
            recurso='llamadas',
            dominio='operaciones',
            activa=True,
        )

        grupo = GrupoPermisos.objects.create(
            codigo='test_finalizar',
            nombre_display='Test Finalizar',
            activo=True,
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad)
        UsuarioGrupo.objects.create(usuario=agente, grupo=grupo, activo=True)

        # Act & Assert
        from callcentersite.apps.llamadas.services import LlamadaService
        from django.core.exceptions import ObjectDoesNotExist

        with pytest.raises(ObjectDoesNotExist):
            LlamadaService.finalizar_llamada(
                llamada_id=99999,  # ID inexistente
                agente_id=agente.id,
            )


@pytest.mark.django_db
class TestUC012_ConsultarHistorialLlamadas:
    """
    UC-012: Consultar Historial de Llamadas.

    Actor: Agente/Supervisor
    Precondición: Usuario autenticado con permisos de consulta

    Flujo principal:
    1. Sistema recibe filtros de búsqueda
    2. Sistema valida permisos
    3. Sistema aplica filtros
    4. Sistema retorna lista paginada de llamadas
    """

    def test_consultar_llamadas_por_agente(self):
        """
        UC-012 Escenario 1: Consultar llamadas de un agente específico.

        Given llamadas registradas para diferentes agentes
        When se consulta por agente específico
        Then retorna solo llamadas de ese agente
        """
        # Arrange
        agente1 = User.objects.create_user(
            username='agent1', password='pass', email='a1@test.com'
        )
        agente2 = User.objects.create_user(
            username='agent2', password='pass', email='a2@test.com'
        )

        estado = EstadoLlamada.objects.create(codigo='finalizada', nombre='Finalizada')
        tipo = TipoLlamada.objects.create(codigo='entrante', nombre='Entrante')

        # Crear 3 llamadas para agente1 y 2 para agente2
        for i in range(3):
            Llamada.objects.create(
                numero_telefono=f'+52-555-111-{i}',
                tipo=tipo,
                estado=estado,
                agente=agente1,
            )

        for i in range(2):
            Llamada.objects.create(
                numero_telefono=f'+52-555-222-{i}',
                tipo=tipo,
                estado=estado,
                agente=agente2,
            )

        # Act
        from callcentersite.apps.llamadas.services import LlamadaService

        llamadas_agente1 = LlamadaService.consultar_historial(
            agente_id=agente1.id
        )

        # Assert
        assert len(llamadas_agente1) == 3
        assert all(ll.agente == agente1 for ll in llamadas_agente1)

    def test_consultar_llamadas_por_rango_fechas(self):
        """
        UC-012 Escenario 2: Consultar llamadas por rango de fechas.

        Given llamadas en diferentes fechas
        When se consulta por rango específico
        Then retorna solo llamadas dentro del rango
        """
        # Arrange
        agente = User.objects.create_user(
            username='agent.range', password='pass', email='range@test.com'
        )

        estado = EstadoLlamada.objects.create(codigo='finalizada', nombre='Finalizada')
        tipo = TipoLlamada.objects.create(codigo='entrante', nombre='Entrante')

        # Crear llamadas en diferentes fechas
        hoy = timezone.now()
        ayer = hoy - timedelta(days=1)
        hace_2_dias = hoy - timedelta(days=2)

        Llamada.objects.create(
            numero_telefono='+52-555-HOY',
            tipo=tipo,
            estado=estado,
            agente=agente,
            fecha_inicio=hoy,
        )

        Llamada.objects.create(
            numero_telefono='+52-555-AYER',
            tipo=tipo,
            estado=estado,
            agente=agente,
            fecha_inicio=ayer,
        )

        Llamada.objects.create(
            numero_telefono='+52-555-ANTES',
            tipo=tipo,
            estado=estado,
            agente=agente,
            fecha_inicio=hace_2_dias,
        )

        # Act - Consultar solo último día
        from callcentersite.apps.llamadas.services import LlamadaService

        fecha_desde = ayer.replace(hour=0, minute=0, second=0)
        llamadas_recientes = LlamadaService.consultar_historial(
            agente_id=agente.id,
            fecha_desde=fecha_desde,
        )

        # Assert
        assert len(llamadas_recientes) == 2  # hoy y ayer, no hace 2 días
