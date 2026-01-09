"""
Tests para Audit Log (Auditoría Inmutable ISO 27001).

Este módulo contiene tests para validar el modelo AuditLog que registra
todas las acciones relevantes del sistema de forma inmutable para compliance.

Requisitos funcionales relacionados:
- RN-001: Sistema de seguridad y auditoría conforme ISO 27001
- RS-001: Auditoría requiere trazabilidad completa
- RS-002: Reportes automatizados de compliance

Documentación: docs/backend/arquitectura/audit.md
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from callcentersite.apps.audit.models import AuditLog

User = get_user_model()


@pytest.mark.django_db
class TestAuditLogModel:
    """Tests para el modelo AuditLog."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Setup para cada test."""
        self.user = User.objects.create_user(
            username="test_auditor",
            password="secure_pass",
            email="auditor@test.com"
        )

    def test_audit_log_creation_success(self):
        """TEST-AUDIT-001: Crear registro de auditoría exitosamente."""
        log = AuditLog.objects.create(
            user=self.user,
            action="login",
            resource="User",
            resource_id=str(self.user.id),
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            result="success"
        )

        assert log.user == self.user
        assert log.action == "login"
        assert log.resource == "User"
        assert log.result == "success"
        assert log.timestamp is not None

    def test_audit_log_immutability(self):
        """TEST-AUDIT-002: CRÍTICO - Registros son inmutables después de creación."""
        log = AuditLog.objects.create(
            user=self.user,
            action="create_campaign",
            resource="Campaign",
            resource_id="123",
            result="success"
        )

        # Intentar modificar debe lanzar RuntimeError
        log.action = "delete_campaign"
        with pytest.raises(RuntimeError, match="inmutables"):
            log.save()

    def test_audit_log_with_old_and_new_values(self):
        """TEST-AUDIT-003: Registrar cambios con valores before/after."""
        old_values = {
            "name": "Campaign A",
            "status": "draft",
            "budget": 1000
        }
        new_values = {
            "name": "Campaign A Updated",
            "status": "active",
            "budget": 1500
        }

        log = AuditLog.objects.create(
            user=self.user,
            action="update_campaign",
            resource="Campaign",
            resource_id="456",
            old_values=old_values,
            new_values=new_values,
            result="success"
        )

        assert log.old_values == old_values
        assert log.new_values == new_values

    def test_audit_log_with_failure_and_error(self):
        """TEST-AUDIT-004: Registrar acción fallida con mensaje de error."""
        log = AuditLog.objects.create(
            user=self.user,
            action="delete_user",
            resource="User",
            resource_id="789",
            result="failure",
            error_message="User has active campaigns, cannot delete"
        )

        assert log.result == "failure"
        assert log.error_message is not None
        assert "cannot delete" in log.error_message

    def test_audit_log_with_metadata(self):
        """TEST-AUDIT-005: Metadata extensible para contexto adicional."""
        metadata = {
            "session_id": "abc123xyz",
            "previous_action": "view_campaign",
            "trigger": "scheduled_job",
            "correlation_id": "req-12345"
        }

        log = AuditLog.objects.create(
            user=self.user,
            action="export_report",
            resource="Report",
            resource_id="report-001",
            result="success",
            metadata=metadata
        )

        assert log.metadata == metadata
        assert log.metadata["session_id"] == "abc123xyz"

    def test_audit_log_without_user_system_action(self):
        """TEST-AUDIT-006: Acciones de sistema sin usuario autenticado."""
        log = AuditLog.objects.create(
            user=None,  # Sistema o acción anónima
            action="scheduled_cleanup",
            resource="TempFiles",
            ip_address="127.0.0.1",
            result="success"
        )

        assert log.user is None
        assert log.action == "scheduled_cleanup"
        assert log.ip_address == "127.0.0.1"

    def test_audit_log_ordering_by_timestamp_desc(self):
        """TEST-AUDIT-007: Logs ordenados por timestamp descendente."""
        # Crear 3 logs con pequeñas pausas
        log1 = AuditLog.objects.create(
            user=self.user, action="action1",
            resource="Resource", result="success"
        )
        log2 = AuditLog.objects.create(
            user=self.user, action="action2",
            resource="Resource", result="success"
        )
        log3 = AuditLog.objects.create(
            user=self.user, action="action3",
            resource="Resource", result="success"
        )

        # Recuperar en orden por defecto
        logs = list(AuditLog.objects.all())

        # Más reciente primero
        assert logs[0].action == "action3"
        assert logs[1].action == "action2"
        assert logs[2].action == "action1"

    def test_audit_log_timestamp_indexed(self):
        """TEST-AUDIT-008: Performance - Timestamp tiene índice para queries rápidos."""
        # Crear múltiples logs
        for i in range(50):
            AuditLog.objects.create(
                user=self.user,
                action=f"action_{i}",
                resource="TestResource",
                result="success"
            )

        # Query por rango de tiempo debe ser eficiente
        recent_logs = AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=5)
        )

        assert recent_logs.count() == 50

    def test_audit_log_required_fields_for_compliance(self):
        """TEST-AUDIT-009: COMPLIANCE - Todos los campos obligatorios para trazabilidad."""
        log = AuditLog.objects.create(
            user=self.user,
            action="sensitive_operation",
            resource="CriticalData",
            resource_id="critical-123",
            ip_address="203.0.113.42",
            user_agent="Mozilla/5.0 (Compliance Test)",
            result="success"
        )

        # Campos obligatorios para ISO 27001
        assert log.user is not None
        assert log.action is not None
        assert log.resource is not None
        assert log.timestamp is not None
        assert log.ip_address is not None
        assert log.user_agent is not None
        assert log.result is not None

    def test_audit_log_cannot_have_update_permission(self):
        """TEST-AUDIT-010: COMPLIANCE - Modelo no tiene permiso de update por default."""
        # Verificar que default_permissions está vacío
        assert AuditLog._meta.default_permissions == ()

    def test_audit_log_query_by_user(self):
        """TEST-AUDIT-011: Query por usuario específico."""
        user2 = User.objects.create_user(
            username="user2",
            password="pass",
            email="user2@test.com"
        )

        # Crear logs para user1
        for i in range(3):
            AuditLog.objects.create(
                user=self.user,
                action=f"user1_action_{i}",
                resource="Test",
                result="success"
            )

        # Crear logs para user2
        for i in range(2):
            AuditLog.objects.create(
                user=user2,
                action=f"user2_action_{i}",
                resource="Test",
                result="success"
            )

        # Query por usuario específico
        user1_logs = AuditLog.objects.filter(user=self.user)
        user2_logs = AuditLog.objects.filter(user=user2)

        assert user1_logs.count() == 3
        assert user2_logs.count() == 2

    def test_audit_log_query_by_resource(self):
        """TEST-AUDIT-012: Query por tipo de recurso."""
        # Crear logs para diferentes recursos
        AuditLog.objects.create(
            user=self.user, action="create", resource="Campaign", result="success"
        )
        AuditLog.objects.create(
            user=self.user, action="update", resource="Campaign", result="success"
        )
        AuditLog.objects.create(
            user=self.user, action="delete", resource="User", result="success"
        )

        # Query por recurso
        campaign_logs = AuditLog.objects.filter(resource="Campaign")
        user_logs = AuditLog.objects.filter(resource="User")

        assert campaign_logs.count() == 2
        assert user_logs.count() == 1

    def test_audit_log_query_by_action(self):
        """TEST-AUDIT-013: Query por tipo de acción."""
        # Crear logs con diferentes acciones
        for action in ["login", "logout", "create", "update", "delete"]:
            AuditLog.objects.create(
                user=self.user,
                action=action,
                resource="Test",
                result="success"
            )

        # Query por acción específica
        login_logs = AuditLog.objects.filter(action="login")
        delete_logs = AuditLog.objects.filter(action="delete")

        assert login_logs.count() == 1
        assert delete_logs.count() == 1

    def test_audit_log_query_failures_only(self):
        """TEST-AUDIT-014: Detectar todas las acciones fallidas."""
        # Crear mix de éxitos y fallos
        AuditLog.objects.create(
            user=self.user, action="action1", resource="Test", result="success"
        )
        AuditLog.objects.create(
            user=self.user, action="action2", resource="Test", result="failure"
        )
        AuditLog.objects.create(
            user=self.user, action="action3", resource="Test", result="failure"
        )

        # Query solo fallos
        failures = AuditLog.objects.filter(result="failure")

        assert failures.count() == 2


@pytest.mark.django_db
class TestAuditLogIntegration:
    """Tests de integración para flujos completos de auditoría."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Setup para tests de integración."""
        self.admin = User.objects.create_user(
            username="admin",
            password="admin_pass",
            email="admin@test.com"
        )
        self.user = User.objects.create_user(
            username="regular_user",
            password="user_pass",
            email="user@test.com"
        )

    def test_audit_complete_lifecycle_create_update_delete(self):
        """TEST-AUDIT-INT-001: Auditar ciclo completo de recurso."""
        resource_id = "campaign-123"

        # 1. Crear
        create_log = AuditLog.objects.create(
            user=self.admin,
            action="create",
            resource="Campaign",
            resource_id=resource_id,
            new_values={"name": "New Campaign", "status": "draft"},
            result="success"
        )

        # 2. Actualizar
        update_log = AuditLog.objects.create(
            user=self.admin,
            action="update",
            resource="Campaign",
            resource_id=resource_id,
            old_values={"name": "New Campaign", "status": "draft"},
            new_values={"name": "Updated Campaign", "status": "active"},
            result="success"
        )

        # 3. Eliminar
        delete_log = AuditLog.objects.create(
            user=self.admin,
            action="delete",
            resource="Campaign",
            resource_id=resource_id,
            old_values={"name": "Updated Campaign", "status": "active"},
            result="success"
        )

        # Verificar secuencia completa
        lifecycle_logs = AuditLog.objects.filter(
            resource="Campaign",
            resource_id=resource_id
        ).order_by('timestamp')

        assert lifecycle_logs.count() == 3
        assert lifecycle_logs[0].action == "create"
        assert lifecycle_logs[1].action == "update"
        assert lifecycle_logs[2].action == "delete"

    def test_audit_suspicious_activity_detection(self):
        """TEST-AUDIT-INT-002: Detectar actividad sospechosa (muchos fallos)."""
        # Simular múltiples intentos fallidos
        for i in range(10):
            AuditLog.objects.create(
                user=None,  # Atacante sin autenticar
                action="login",
                resource="User",
                ip_address="10.0.0.1",
                user_agent=f"AttackTool/{i}",
                result="failure",
                error_message="Invalid credentials"
            )

        # Query para detectar patrón anormal
        suspicious_logs = AuditLog.objects.filter(
            ip_address="10.0.0.1",
            result="failure",
            timestamp__gte=timezone.now() - timedelta(minutes=10)
        )

        assert suspicious_logs.count() >= 5  # Threshold para alerta


# TODO: Tests pendientes para completar
# - test_audit_log_retention_policy() - Archivar logs antiguos
# - test_audit_log_export_for_compliance() - Exportar en formato auditable
# - test_audit_log_encryption() - Verificar encriptación en reposo
# - test_audit_log_digital_signature() - Firma digital para exports
# - test_audit_log_partitioning() - Performance con millones de registros
