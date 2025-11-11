"""
Tests TDD para Casos de Uso del módulo de Configuración.

Sistema de gestión de configuraciones del sistema.
Casos de uso implementados siguiendo TDD.
"""

import json
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from callcentersite.apps.configuracion.models import ConfiguracionSistema, AuditoriaConfiguracion

User = get_user_model()


@pytest.mark.django_db
class TestUC024_VerConfiguracion:
    """
    UC-024: Ver Configuración del Sistema.

    Actor: Administrador/Usuario con permiso
    Precondición: Usuario tiene permiso "sistema.tecnico.configuracion.ver"

    Flujo principal:
    1. Sistema recibe solicitud de configuración
    2. Sistema retorna parámetros con sus valores actuales
    3. Sistema incluye descripción y tipo de dato
    """

    def test_ver_configuracion_especifica(self):
        """
        UC-024 Escenario 1: Ver configuración específica por clave.

        Given configuración existente
        When se consulta por clave
        Then retorna valor con metadatos
        """
        # Arrange
        config = ConfiguracionSistema.objects.create(
            clave='max_intentos_login',
            valor='3',
            tipo='integer',
            descripcion='Máximo de intentos de login fallidos',
            valor_default='3'
        )

        from callcentersite.apps.configuracion.services import ConfigService

        # Act
        resultado = ConfigService.ver_configuracion(clave='max_intentos_login')

        # Assert
        assert resultado is not None
        assert resultado.clave == 'max_intentos_login'
        assert resultado.valor == '3'
        assert resultado.tipo == 'integer'
        assert resultado.get_valor_typed() == 3

    def test_listar_todas_configuraciones(self):
        """
        UC-024 Escenario 2: Listar todas las configuraciones.

        Given múltiples configuraciones
        When se listan todas
        Then retorna lista completa ordenada
        """
        # Arrange
        ConfiguracionSistema.objects.create(
            clave='param1', valor='val1', tipo='string', valor_default='val1'
        )
        ConfiguracionSistema.objects.create(
            clave='param2', valor='val2', tipo='string', valor_default='val2'
        )

        from callcentersite.apps.configuracion.services import ConfigService

        # Act
        configs = ConfigService.listar_configuraciones()

        # Assert
        assert len(configs) >= 2
        assert all(isinstance(c, ConfiguracionSistema) for c in configs)


@pytest.mark.django_db
class TestUC025_ModificarConfiguracion:
    """
    UC-025: Modificar Configuración.

    Actor: Administrador
    Precondición: Usuario tiene permiso "sistema.tecnico.configuracion.modificar"

    Flujo principal:
    1. Sistema recibe clave y nuevo valor
    2. Sistema valida tipo de dato
    3. Sistema guarda valor anterior en auditoría
    4. Sistema actualiza configuración
    5. Sistema registra quién y cuándo modificó
    """

    def test_modificar_configuracion_exitoso(self):
        """
        UC-025 Escenario 1: Modificar configuración existente.

        Given configuración con valor actual
        When se actualiza a nuevo valor
        Then valor es actualizado
          And se crea registro de auditoría
        """
        # Arrange
        usuario = User.objects.create_user(
            username='admin', password='pass', email='admin@test.com'
        )
        config = ConfiguracionSistema.objects.create(
            clave='timeout_session',
            valor='30',
            tipo='integer',
            valor_default='30'
        )

        from callcentersite.apps.configuracion.services import ConfigService

        # Act
        ConfigService.modificar_configuracion(
            clave='timeout_session',
            nuevo_valor='60',
            usuario_id=usuario.id,
            motivo='Aumentar tiempo de sesión'
        )

        # Assert
        config.refresh_from_db()
        assert config.valor == '60'
        assert config.modificado_por == usuario

        # Verificar auditoría
        auditoria = AuditoriaConfiguracion.objects.filter(
            configuracion=config
        ).first()
        assert auditoria is not None
        assert auditoria.valor_anterior == '30'
        assert auditoria.valor_nuevo == '60'
        assert auditoria.modificado_por == usuario

    def test_modificar_con_validacion_tipo(self):
        """
        UC-025 Escenario 2: Validar tipo de dato al modificar.

        Given configuración tipo integer
        When se intenta poner valor no numérico
        Then sistema lanza ValidationError
        """
        # Arrange
        usuario = User.objects.create_user(
            username='admin', password='pass', email='admin@test.com'
        )
        ConfiguracionSistema.objects.create(
            clave='param_int',
            valor='10',
            tipo='integer',
            valor_default='10'
        )

        from callcentersite.apps.configuracion.services import ConfigService

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ConfigService.modificar_configuracion(
                clave='param_int',
                nuevo_valor='not_a_number',
                usuario_id=usuario.id
            )

        assert 'tipo' in str(exc_info.value).lower() or 'valor' in str(exc_info.value).lower()


@pytest.mark.django_db
class TestUC026_ExportarConfiguracion:
    """
    UC-026: Exportar Configuración.

    Actor: Administrador
    Precondición: Usuario tiene permiso "sistema.tecnico.configuracion.exportar"

    Flujo principal:
    1. Sistema recibe solicitud de exportación
    2. Sistema genera JSON con todas las configuraciones
    3. Sistema incluye metadatos (descripción, tipo)
    4. Sistema retorna archivo para descarga
    """

    def test_exportar_configuracion_json(self):
        """
        UC-026 Escenario 1: Exportar todas las configuraciones a JSON.

        Given configuraciones existentes
        When se exportan
        Then retorna JSON válido con todas las configs
        """
        # Arrange
        ConfiguracionSistema.objects.create(
            clave='param1',
            valor='value1',
            tipo='string',
            descripcion='Parámetro 1',
            valor_default='default1'
        )
        ConfiguracionSistema.objects.create(
            clave='param2',
            valor='100',
            tipo='integer',
            descripcion='Parámetro 2',
            valor_default='50'
        )

        from callcentersite.apps.configuracion.services import ConfigService

        # Act
        json_data = ConfigService.exportar_configuracion()

        # Assert
        assert json_data is not None
        configs = json.loads(json_data)
        assert len(configs) >= 2
        assert all('clave' in c for c in configs)
        assert all('valor' in c for c in configs)
        assert all('tipo' in c for c in configs)


@pytest.mark.django_db
class TestUC027_ImportarConfiguracion:
    """
    UC-027: Importar Configuración.

    Actor: Administrador
    Precondición: Usuario tiene permiso "sistema.tecnico.configuracion.importar"

    Flujo principal:
    1. Sistema recibe archivo JSON con configuraciones
    2. Sistema valida estructura y tipos de datos
    3. Sistema actualiza configuraciones existentes
    4. Sistema crea configuraciones nuevas
    5. Sistema registra auditoría de todos los cambios
    """

    def test_importar_configuracion_json(self):
        """
        UC-027 Escenario 1: Importar configuraciones desde JSON.

        Given JSON válido con configuraciones
        When se importa
        Then configuraciones son creadas/actualizadas
        """
        # Arrange
        usuario = User.objects.create_user(
            username='admin', password='pass', email='admin@test.com'
        )

        json_data = json.dumps([
            {
                'clave': 'new_param',
                'valor': 'new_value',
                'tipo': 'string',
                'descripcion': 'Nuevo parámetro',
                'valor_default': 'default'
            }
        ])

        from callcentersite.apps.configuracion.services import ConfigService

        # Act
        resultado = ConfigService.importar_configuracion(
            json_data=json_data,
            usuario_id=usuario.id
        )

        # Assert
        assert resultado['creadas'] >= 1
        config = ConfiguracionSistema.objects.get(clave='new_param')
        assert config.valor == 'new_value'

    def test_importar_actualiza_existentes(self):
        """
        UC-027 Escenario 2: Importar actualiza configuraciones existentes.

        Given configuración existente
        When se importa JSON con mismo key pero nuevo valor
        Then configuración es actualizada (no duplicada)
        """
        # Arrange
        usuario = User.objects.create_user(
            username='admin', password='pass', email='admin@test.com'
        )
        ConfiguracionSistema.objects.create(
            clave='existing_param',
            valor='old_value',
            tipo='string',
            valor_default='default'
        )

        json_data = json.dumps([
            {
                'clave': 'existing_param',
                'valor': 'new_value',
                'tipo': 'string',
                'descripcion': 'Updated',
                'valor_default': 'default'
            }
        ])

        from callcentersite.apps.configuracion.services import ConfigService

        # Act
        resultado = ConfigService.importar_configuracion(
            json_data=json_data,
            usuario_id=usuario.id
        )

        # Assert
        assert resultado['actualizadas'] >= 1
        config = ConfiguracionSistema.objects.get(clave='existing_param')
        assert config.valor == 'new_value'
        # No debe haber duplicados
        assert ConfiguracionSistema.objects.filter(clave='existing_param').count() == 1


@pytest.mark.django_db
class TestUC028_AuditarConfiguracion:
    """
    UC-028: Auditar Configuración.

    Actor: Administrador/Auditor
    Precondición: Usuario tiene permiso "sistema.tecnico.configuracion.auditar"

    Flujo principal:
    1. Sistema recibe solicitud de historial
    2. Sistema retorna cambios ordenados cronológicamente
    3. Sistema incluye quién, qué, cuándo y por qué
    """

    def test_ver_historial_configuracion(self):
        """
        UC-028 Escenario 1: Ver historial de cambios de una configuración.

        Given configuración con múltiples cambios
        When se consulta historial
        Then retorna lista ordenada de cambios
        """
        # Arrange
        usuario = User.objects.create_user(
            username='admin', password='pass', email='admin@test.com'
        )
        config = ConfiguracionSistema.objects.create(
            clave='test_param',
            valor='value1',
            tipo='string',
            valor_default='default'
        )

        # Crear auditorías manualmente
        AuditoriaConfiguracion.objects.create(
            configuracion=config,
            valor_anterior='value1',
            valor_nuevo='value2',
            modificado_por=usuario,
            motivo='Primer cambio'
        )
        AuditoriaConfiguracion.objects.create(
            configuracion=config,
            valor_anterior='value2',
            valor_nuevo='value3',
            modificado_por=usuario,
            motivo='Segundo cambio'
        )

        from callcentersite.apps.configuracion.services import ConfigService

        # Act
        historial = ConfigService.ver_historial_configuracion(clave='test_param')

        # Assert
        assert len(historial) == 2
        assert historial[0].valor_nuevo == 'value3'  # Más reciente primero
        assert historial[1].valor_nuevo == 'value2'

    def test_ver_historial_completo_sistema(self):
        """
        UC-028 Escenario 2: Ver historial completo del sistema.

        Given múltiples configuraciones con cambios
        When se consulta historial global
        Then retorna todos los cambios ordenados
        """
        # Arrange
        usuario = User.objects.create_user(
            username='admin', password='pass', email='admin@test.com'
        )
        config1 = ConfiguracionSistema.objects.create(
            clave='param1', valor='val1', tipo='string', valor_default='val1'
        )
        config2 = ConfiguracionSistema.objects.create(
            clave='param2', valor='val2', tipo='string', valor_default='val2'
        )

        AuditoriaConfiguracion.objects.create(
            configuracion=config1,
            valor_anterior='old1',
            valor_nuevo='val1',
            modificado_por=usuario
        )
        AuditoriaConfiguracion.objects.create(
            configuracion=config2,
            valor_anterior='old2',
            valor_nuevo='val2',
            modificado_por=usuario
        )

        from callcentersite.apps.configuracion.services import ConfigService

        # Act
        historial = ConfigService.ver_historial_completo()

        # Assert
        assert len(historial) >= 2
