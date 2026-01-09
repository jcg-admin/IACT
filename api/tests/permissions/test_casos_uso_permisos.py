"""
Tests TDD para Casos de Uso del Sistema de Permisos Granular.

Sistema de Permisos Granular - PRIORIDAD 1
Casos de uso basados en las 8 tablas principales:
1. Funcion
2. Capacidad
3. FuncionCapacidad
4. GrupoPermisos
5. GrupoCapacidad
6. UsuarioGrupo
7. PermisoExcepcional
8. AuditoriaPermiso

Referencias:
- REQ-PERM-001: Sistema de Permisos Granular
- ADR-012: NO usar roles jerarquicos
"""

import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from callcentersite.apps.permissions.models import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermisos,
    GrupoCapacidad,
    UsuarioGrupo,
    PermisoExcepcional,
    AuditoriaPermiso,
)

User = get_user_model()


@pytest.mark.django_db
class TestUC001_VerificarPermisoUsuario:
    """
    UC-001: Verificar si un usuario tiene un permiso específico.

    Flujo principal:
    1. Sistema recibe usuario_id y nombre_capacidad
    2. Sistema busca capacidad por nombre_completo
    3. Sistema verifica grupos activos del usuario
    4. Sistema verifica permisos excepcionales
    5. Sistema retorna True si tiene permiso, False si no
    """

    def test_usuario_con_grupo_tiene_capacidad(self):
        """
        UC-001 Escenario 1: Usuario tiene capacidad a través de grupo.

        Given un usuario registrado
          And un grupo "visualizacion_basica" con capacidad "sistema.vistas.dashboards.ver"
          And el usuario pertenece al grupo
        When se verifica has_permission(user, "sistema.vistas.dashboards.ver")
        Then retorna True
        """
        # Arrange - Crear usuario
        user = User.objects.create_user(
            username="juan.perez",
            password="SecureP@ss123",
            email="juan.perez@company.com",
        )

        # Crear capacidad
        capacidad_ver_dashboards = Capacidad.objects.create(
            nombre_completo="sistema.vistas.dashboards.ver",
            accion="ver",
            recurso="dashboards",
            dominio="vistas",
            nivel_sensibilidad="bajo",
            descripcion="Permite ver dashboards",
            activa=True,
        )

        # Crear grupo
        grupo_visualizacion = GrupoPermisos.objects.create(
            codigo="visualizacion_basica",
            nombre_display="Visualización Básica",
            descripcion="Acceso de solo lectura a dashboards",
            tipo_acceso="operativo",
            activo=True,
        )

        # Asociar capacidad al grupo
        GrupoCapacidad.objects.create(
            grupo=grupo_visualizacion,
            capacidad=capacidad_ver_dashboards,
        )

        # Asignar grupo al usuario
        UsuarioGrupo.objects.create(
            usuario=user,
            grupo=grupo_visualizacion,
            asignado_por=user,
            activo=True,
        )

        # Act - Verificar permiso
        tiene_permiso = self._usuario_tiene_capacidad(user, "sistema.vistas.dashboards.ver")

        # Assert
        assert tiene_permiso is True

    def test_usuario_sin_grupo_no_tiene_capacidad(self):
        """
        UC-001 Escenario 2: Usuario sin grupos no tiene capacidad.

        Given un usuario sin grupos asignados
        When se verifica has_permission(user, "sistema.vistas.dashboards.ver")
        Then retorna False
        """
        # Arrange
        user = User.objects.create_user(
            username="maria.garcia",
            password="SecureP@ss123",
            email="maria.garcia@company.com",
        )

        # Crear capacidad pero no asignarla
        Capacidad.objects.create(
            nombre_completo="sistema.vistas.dashboards.ver",
            accion="ver",
            recurso="dashboards",
            dominio="vistas",
            activa=True,
        )

        # Act
        tiene_permiso = self._usuario_tiene_capacidad(user, "sistema.vistas.dashboards.ver")

        # Assert
        assert tiene_permiso is False

    def test_usuario_con_grupo_inactivo_no_tiene_capacidad(self):
        """
        UC-001 Escenario 3: Grupo inactivo no otorga permisos.

        Given un usuario con grupo asignado
          And el grupo está marcado como activo=False
        When se verifica has_permission
        Then retorna False
        """
        # Arrange
        user = User.objects.create_user(
            username="pedro.lopez",
            password="SecureP@ss123",
            email="pedro.lopez@company.com",
        )

        capacidad = Capacidad.objects.create(
            nombre_completo="sistema.admin.usuarios.editar",
            accion="editar",
            recurso="usuarios",
            dominio="admin",
            activa=True,
        )

        grupo = GrupoPermisos.objects.create(
            codigo="admin_usuarios",
            nombre_display="Administración de Usuarios",
            activo=False,  # INACTIVO
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad)
        UsuarioGrupo.objects.create(usuario=user, grupo=grupo, activo=True)

        # Act
        tiene_permiso = self._usuario_tiene_capacidad(user, "sistema.admin.usuarios.editar")

        # Assert
        assert tiene_permiso is False

    def test_usuario_con_permiso_excepcional_concedido(self):
        """
        UC-001 Escenario 4: Permiso excepcional concedido otorga acceso.

        Given un usuario sin grupos
          And un permiso excepcional tipo="conceder" activo
        When se verifica has_permission
        Then retorna True
        """
        # Arrange
        user = User.objects.create_user(
            username="ana.torres",
            password="SecureP@ss123",
            email="ana.torres@company.com",
        )

        capacidad = Capacidad.objects.create(
            nombre_completo="sistema.reportes.financieros.exportar",
            accion="exportar",
            recurso="reportes_financieros",
            dominio="reportes",
            activa=True,
        )

        # Conceder permiso excepcional
        PermisoExcepcional.objects.create(
            usuario=user,
            capacidad=capacidad,
            tipo="conceder",
            motivo="Proyecto especial de Q4",
            fecha_fin=timezone.now() + timedelta(days=30),
            activo=True,
        )

        # Act
        tiene_permiso = self._usuario_tiene_capacidad(user, "sistema.reportes.financieros.exportar")

        # Assert
        assert tiene_permiso is True

    def test_usuario_con_permiso_excepcional_revocado(self):
        """
        UC-001 Escenario 5: Permiso excepcional revocado niega acceso.

        Given un usuario con grupo que tiene capacidad
          And un permiso excepcional tipo="revocar" activo
        When se verifica has_permission
        Then retorna False (la revocación tiene prioridad)
        """
        # Arrange
        user = User.objects.create_user(
            username="carlos.ruiz",
            password="SecureP@ss123",
            email="carlos.ruiz@company.com",
        )

        capacidad = Capacidad.objects.create(
            nombre_completo="sistema.operaciones.aprobar_cambios",
            accion="aprobar",
            recurso="cambios",
            dominio="operaciones",
            activa=True,
        )

        grupo = GrupoPermisos.objects.create(
            codigo="operaciones_senior",
            nombre_display="Operaciones Senior",
            activo=True,
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=capacidad)
        UsuarioGrupo.objects.create(usuario=user, grupo=grupo, activo=True)

        # Revocar temporalmente el permiso
        PermisoExcepcional.objects.create(
            usuario=user,
            capacidad=capacidad,
            tipo="revocar",
            motivo="Investigación de incidente #1234",
            fecha_fin=timezone.now() + timedelta(days=7),
            activo=True,
        )

        # Act
        tiene_permiso = self._usuario_tiene_capacidad(user, "sistema.operaciones.aprobar_cambios")

        # Assert
        assert tiene_permiso is False

    def test_permiso_excepcional_expirado_no_aplica(self):
        """
        UC-001 Escenario 6: Permiso excepcional expirado no se considera.

        Given un usuario con permiso excepcional
          And fecha_fin < fecha_actual
        When se verifica has_permission
        Then el permiso excepcional se ignora
        """
        # Arrange
        user = User.objects.create_user(
            username="lucia.martinez",
            password="SecureP@ss123",
            email="lucia.martinez@company.com",
        )

        capacidad = Capacidad.objects.create(
            nombre_completo="sistema.temp.feature.usar",
            accion="usar",
            recurso="temp_feature",
            dominio="temp",
            activa=True,
        )

        # Permiso excepcional EXPIRADO
        PermisoExcepcional.objects.create(
            usuario=user,
            capacidad=capacidad,
            tipo="conceder",
            motivo="Testing temporal",
            fecha_fin=timezone.now() - timedelta(days=1),  # EXPIRADO
            activo=True,
        )

        # Act
        tiene_permiso = self._usuario_tiene_capacidad(user, "sistema.temp.feature.usar")

        # Assert
        assert tiene_permiso is False

    # Helper method
    def _usuario_tiene_capacidad(self, user, nombre_capacidad):
        """
        Simula la lógica de verificación de permisos.

        Esta es la implementación que debería estar en el servicio real.
        """
        # 1. Verificar que el usuario esté autenticado
        if not user.is_authenticated:
            return False

        # 2. Buscar la capacidad
        try:
            capacidad = Capacidad.objects.get(
                nombre_completo=nombre_capacidad,
                activa=True
            )
        except Capacidad.DoesNotExist:
            return False

        # 3. Verificar permisos excepcionales REVOCADOS (tienen prioridad)
        permisos_revocados = PermisoExcepcional.objects.filter(
            usuario=user,
            capacidad=capacidad,
            tipo="revocar",
            activo=True,
        )

        for permiso in permisos_revocados:
            # Si no tiene fecha_fin o aún no expiró
            if permiso.fecha_fin is None or permiso.fecha_fin > timezone.now():
                return False

        # 4. Verificar permisos excepcionales CONCEDIDOS
        permisos_concedidos = PermisoExcepcional.objects.filter(
            usuario=user,
            capacidad=capacidad,
            tipo="conceder",
            activo=True,
        )

        for permiso in permisos_concedidos:
            # Si no tiene fecha_fin o aún no expiró
            if permiso.fecha_fin is None or permiso.fecha_fin > timezone.now():
                return True

        # 5. Verificar permisos por GRUPOS
        grupos_usuario = UsuarioGrupo.objects.filter(
            usuario=user,
            activo=True,
        ).select_related('grupo')

        for ug in grupos_usuario:
            # Verificar que el grupo esté activo
            if not ug.grupo.activo:
                continue

            # Verificar expiración
            if ug.fecha_expiracion and ug.fecha_expiracion < timezone.now():
                continue

            # Verificar si el grupo tiene la capacidad
            if GrupoCapacidad.objects.filter(
                grupo=ug.grupo,
                capacidad=capacidad
            ).exists():
                return True

        return False


@pytest.mark.django_db
class TestUC002_ObtenerPermisosUsuario:
    """
    UC-002: Obtener lista completa de permisos de un usuario.

    Retorna todas las capacidades efectivas considerando:
    - Grupos activos
    - Permisos excepcionales concedidos
    - Menos permisos excepcionales revocados
    """

    def test_obtener_permisos_de_usuario_con_multiples_grupos(self):
        """
        UC-002 Escenario 1: Usuario con múltiples grupos.

        Given un usuario con 2 grupos activos
          And grupo1 tiene capacidades [A, B]
          And grupo2 tiene capacidades [C, D]
        When se obtienen permisos del usuario
        Then retorna [A, B, C, D] sin duplicados
        """
        # Arrange
        user = User.objects.create_user(
            username="diego.fernandez",
            password="SecureP@ss123",
            email="diego.fernandez@company.com",
        )

        # Crear capacidades
        cap_a = Capacidad.objects.create(
            nombre_completo="sistema.ventas.clientes.ver",
            accion="ver", recurso="clientes", dominio="ventas", activa=True
        )
        cap_b = Capacidad.objects.create(
            nombre_completo="sistema.ventas.pedidos.ver",
            accion="ver", recurso="pedidos", dominio="ventas", activa=True
        )
        cap_c = Capacidad.objects.create(
            nombre_completo="sistema.reportes.ventas.generar",
            accion="generar", recurso="reportes_ventas", dominio="reportes", activa=True
        )
        cap_d = Capacidad.objects.create(
            nombre_completo="sistema.reportes.ventas.exportar",
            accion="exportar", recurso="reportes_ventas", dominio="reportes", activa=True
        )

        # Crear grupos
        grupo1 = GrupoPermisos.objects.create(
            codigo="ventas_basico",
            nombre_display="Ventas Básico",
            activo=True
        )
        grupo2 = GrupoPermisos.objects.create(
            codigo="reportes_ventas",
            nombre_display="Reportes de Ventas",
            activo=True
        )

        # Asociar capacidades
        GrupoCapacidad.objects.create(grupo=grupo1, capacidad=cap_a)
        GrupoCapacidad.objects.create(grupo=grupo1, capacidad=cap_b)
        GrupoCapacidad.objects.create(grupo=grupo2, capacidad=cap_c)
        GrupoCapacidad.objects.create(grupo=grupo2, capacidad=cap_d)

        # Asignar grupos al usuario
        UsuarioGrupo.objects.create(usuario=user, grupo=grupo1, activo=True)
        UsuarioGrupo.objects.create(usuario=user, grupo=grupo2, activo=True)

        # Act
        capacidades = self._obtener_capacidades_usuario(user)

        # Assert
        assert len(capacidades) == 4
        nombres = {c.nombre_completo for c in capacidades}
        assert nombres == {
            "sistema.ventas.clientes.ver",
            "sistema.ventas.pedidos.ver",
            "sistema.reportes.ventas.generar",
            "sistema.reportes.ventas.exportar",
        }

    def test_obtener_permisos_con_excepcionales_concedidos(self):
        """
        UC-002 Escenario 2: Incluir permisos excepcionales concedidos.

        Given un usuario con 1 grupo con capacidades [A, B]
          And permiso excepcional concedido para capacidad C
        When se obtienen permisos
        Then retorna [A, B, C]
        """
        # Arrange
        user = User.objects.create_user(
            username="elena.castro",
            password="SecureP@ss123",
            email="elena.castro@company.com",
        )

        cap_a = Capacidad.objects.create(
            nombre_completo="sistema.ops.monitoreo.ver",
            accion="ver", recurso="monitoreo", dominio="ops", activa=True
        )
        cap_b = Capacidad.objects.create(
            nombre_completo="sistema.ops.alertas.ver",
            accion="ver", recurso="alertas", dominio="ops", activa=True
        )
        cap_c = Capacidad.objects.create(
            nombre_completo="sistema.ops.servidor.reiniciar",
            accion="reiniciar", recurso="servidor", dominio="ops",
            nivel_sensibilidad="critico", activa=True
        )

        grupo = GrupoPermisos.objects.create(
            codigo="ops_monitoreo",
            nombre_display="Monitoreo Ops",
            activo=True
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=cap_a)
        GrupoCapacidad.objects.create(grupo=grupo, capacidad=cap_b)
        UsuarioGrupo.objects.create(usuario=user, grupo=grupo, activo=True)

        # Conceder permiso excepcional para reiniciar servidor
        PermisoExcepcional.objects.create(
            usuario=user,
            capacidad=cap_c,
            tipo="conceder",
            motivo="Incidente crítico #567",
            fecha_fin=timezone.now() + timedelta(hours=4),
            activo=True,
        )

        # Act
        capacidades = self._obtener_capacidades_usuario(user)

        # Assert
        assert len(capacidades) == 3
        nombres = {c.nombre_completo for c in capacidades}
        assert "sistema.ops.servidor.reiniciar" in nombres

    def test_obtener_permisos_excluye_revocados(self):
        """
        UC-002 Escenario 3: Excluir permisos revocados.

        Given un usuario con grupo con capacidades [A, B, C]
          And permiso excepcional revocado para capacidad B
        When se obtienen permisos
        Then retorna [A, C] (sin B)
        """
        # Arrange
        user = User.objects.create_user(
            username="fernando.vega",
            password="SecureP@ss123",
            email="fernando.vega@company.com",
        )

        cap_a = Capacidad.objects.create(
            nombre_completo="sistema.finanzas.facturas.ver",
            accion="ver", recurso="facturas", dominio="finanzas", activa=True
        )
        cap_b = Capacidad.objects.create(
            nombre_completo="sistema.finanzas.facturas.aprobar",
            accion="aprobar", recurso="facturas", dominio="finanzas", activa=True
        )
        cap_c = Capacidad.objects.create(
            nombre_completo="sistema.finanzas.facturas.exportar",
            accion="exportar", recurso="facturas", dominio="finanzas", activa=True
        )

        grupo = GrupoPermisos.objects.create(
            codigo="finanzas_facturas",
            nombre_display="Gestión de Facturas",
            activo=True
        )

        GrupoCapacidad.objects.create(grupo=grupo, capacidad=cap_a)
        GrupoCapacidad.objects.create(grupo=grupo, capacidad=cap_b)
        GrupoCapacidad.objects.create(grupo=grupo, capacidad=cap_c)
        UsuarioGrupo.objects.create(usuario=user, grupo=grupo, activo=True)

        # Revocar temporalmente capacidad de aprobar
        PermisoExcepcional.objects.create(
            usuario=user,
            capacidad=cap_b,
            tipo="revocar",
            motivo="Auditoria en curso",
            activo=True,
        )

        # Act
        capacidades = self._obtener_capacidades_usuario(user)

        # Assert
        nombres = {c.nombre_completo for c in capacidades}
        assert "sistema.finanzas.facturas.ver" in nombres
        assert "sistema.finanzas.facturas.exportar" in nombres
        assert "sistema.finanzas.facturas.aprobar" not in nombres

    # Helper method
    def _obtener_capacidades_usuario(self, user):
        """Obtiene todas las capacidades efectivas del usuario."""
        capacidades_set = set()

        # 1. Obtener capacidades de grupos activos
        grupos = UsuarioGrupo.objects.filter(
            usuario=user,
            activo=True,
            grupo__activo=True,
        ).select_related('grupo')

        for ug in grupos:
            # Verificar expiración
            if ug.fecha_expiracion and ug.fecha_expiracion < timezone.now():
                continue

            # Obtener capacidades del grupo
            grupo_caps = GrupoCapacidad.objects.filter(
                grupo=ug.grupo
            ).select_related('capacidad')

            for gc in grupo_caps:
                if gc.capacidad.activa:
                    capacidades_set.add(gc.capacidad)

        # 2. Agregar permisos excepcionales concedidos
        permisos_concedidos = PermisoExcepcional.objects.filter(
            usuario=user,
            tipo="conceder",
            activo=True,
        ).select_related('capacidad')

        for permiso in permisos_concedidos:
            # Verificar vigencia
            if permiso.fecha_fin is None or permiso.fecha_fin > timezone.now():
                if permiso.capacidad.activa:
                    capacidades_set.add(permiso.capacidad)

        # 3. Remover permisos excepcionales revocados
        permisos_revocados = PermisoExcepcional.objects.filter(
            usuario=user,
            tipo="revocar",
            activo=True,
        ).select_related('capacidad')

        for permiso in permisos_revocados:
            # Verificar vigencia
            if permiso.fecha_fin is None or permiso.fecha_fin > timezone.now():
                capacidades_set.discard(permiso.capacidad)

        return list(capacidades_set)


@pytest.mark.django_db
class TestUC005_RegistrarAuditoria:
    """
    UC-005: Registrar acceso en auditoría.

    Registra TODOS los intentos de acceso (concedidos y denegados)
    para capacidades que requieren auditoría.
    """

    def test_registrar_acceso_concedido_en_auditoria(self):
        """
        UC-005 Escenario 1: Registrar acceso concedido.

        Given un usuario que accede a un recurso
          And el usuario tiene el permiso requerido
        When se registra en auditoría
        Then se crea registro con accion_realizada="acceso_concedido"
        """
        # Arrange
        user = User.objects.create_user(
            username="gabriela.rojas",
            password="SecureP@ss123",
            email="gabriela.rojas@company.com",
        )

        capacidad = Capacidad.objects.create(
            nombre_completo="sistema.admin.usuarios.eliminar",
            accion="eliminar",
            recurso="usuarios",
            dominio="admin",
            nivel_sensibilidad="critico",
            requiere_auditoria=True,
            activa=True,
        )

        # Act - Registrar acceso exitoso
        auditoria = AuditoriaPermiso.objects.create(
            usuario=user,
            capacidad="sistema.admin.usuarios.eliminar",
            accion_realizada="acceso_concedido",
            recurso_accedido="/api/v1/usuarios/123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0...",
            metadata={"usuario_eliminado_id": 123, "razon": "Usuario duplicado"},
        )

        # Assert
        assert auditoria.id is not None
        assert auditoria.usuario == user
        assert auditoria.accion_realizada == "acceso_concedido"
        assert auditoria.metadata["usuario_eliminado_id"] == 123

    def test_registrar_acceso_denegado_en_auditoria(self):
        """
        UC-005 Escenario 2: Registrar acceso denegado.

        Given un usuario que intenta acceder sin permiso
        When se registra en auditoría
        Then se crea registro con accion_realizada="acceso_denegado"
        """
        # Arrange
        user = User.objects.create_user(
            username="hector.silva",
            password="SecureP@ss123",
            email="hector.silva@company.com",
        )

        # Act - Registrar intento fallido
        auditoria = AuditoriaPermiso.objects.create(
            usuario=user,
            capacidad="sistema.finanzas.nomina.ver",
            accion_realizada="acceso_denegado",
            recurso_accedido="/api/v1/nomina/2025-11",
            ip_address="192.168.1.150",
            user_agent="Chrome/120.0",
            metadata={"razon_denegado": "Usuario sin grupo de finanzas"},
        )

        # Assert
        assert auditoria.id is not None
        assert auditoria.accion_realizada == "acceso_denegado"
        assert auditoria.metadata["razon_denegado"] is not None

    def test_buscar_intentos_fallidos_ultimas_24_horas(self):
        """
        UC-005 Escenario 3: Consultar intentos fallidos recientes.

        Given registros de auditoría de últimas 24 horas
        When se consultan accesos denegados
        Then retorna solo los accesos denegados del período
        """
        # Arrange
        user = User.objects.create_user(
            username="isabel.mendoza",
            password="SecureP@ss123",
            email="isabel.mendoza@company.com",
        )

        # Crear varios intentos
        for i in range(3):
            AuditoriaPermiso.objects.create(
                usuario=user,
                capacidad=f"sistema.test.recurso{i}.ver",
                accion_realizada="acceso_denegado",
                recurso_accedido=f"/api/recurso{i}",
                ip_address="192.168.1.200",
            )

        # Crear un acceso exitoso
        AuditoriaPermiso.objects.create(
            usuario=user,
            capacidad="sistema.test.otro.ver",
            accion_realizada="acceso_concedido",
            recurso_accedido="/api/otro",
            ip_address="192.168.1.200",
        )

        # Act - Consultar solo denegados
        ultimas_24h = timezone.now() - timedelta(hours=24)
        intentos_fallidos = AuditoriaPermiso.objects.filter(
            usuario=user,
            accion_realizada="acceso_denegado",
            timestamp__gte=ultimas_24h,
        ).order_by('-timestamp')

        # Assert
        assert intentos_fallidos.count() == 3
        for intento in intentos_fallidos:
            assert intento.accion_realizada == "acceso_denegado"
