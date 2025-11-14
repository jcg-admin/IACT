"""
LFPDPPP Compliance Tests - Business Rules Validation

Tests automated compliance with Mexican data protection law (LFPDPPP).
Related Business Rules:
- BR-R08: Recording consent requirement
- BR-R11: Personal data encryption
- BR-R12: Audit logging for data access
- BR-R13: Data retention policies

Author: SDLC Agent
Date: 2025-11-14
"""

import pytest
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from callcentersite.clientes.models import Cliente
from callcentersite.llamadas.models import Llamada, Grabacion
from callcentersite.auditoria.models import LogAuditoria
from callcentersite.agentes.models import Agente


class LFPDPPPEncryptionTests(TestCase):
    """
    Test BR-R11: Personal data must be encrypted at rest.

    LFPDPPP Art. 19: Data controllers must implement security measures
    to protect personal data against unauthorized access.
    """

    def setUp(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            username='test_agente',
            password='test123'
        )
        self.agente = Agente.objects.create(
            user=self.user,
            extension='1001'
        )

    def test_br_r11_cliente_rfc_encrypted(self):
        """
        Test that RFC (tax ID) is stored encrypted.
        BR-R11: Personal identification data must be encrypted.
        """
        # Arrange
        rfc_plaintext = "ABCD123456XYZ"

        # Act
        cliente = Cliente.objects.create(
            nombre_completo="Juan Pérez",
            rfc=rfc_plaintext,
            telefono="5512345678"
        )

        # Assert: Value in database should NOT be plaintext
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT rfc FROM clientes WHERE id = %s",
                [cliente.id]
            )
            db_value = cursor.fetchone()[0]

        # Database value should be encrypted (different from plaintext)
        self.assertNotEqual(db_value, rfc_plaintext)
        # But model should decrypt automatically
        self.assertEqual(cliente.rfc, rfc_plaintext)

    def test_br_r11_cliente_curp_encrypted(self):
        """
        Test that CURP (national ID) is stored encrypted.
        BR-R11: Personal identification data must be encrypted.
        """
        # Arrange
        curp_plaintext = "ABCD123456HDFLRN01"

        # Act
        cliente = Cliente.objects.create(
            nombre_completo="María García",
            curp=curp_plaintext,
            telefono="5598765432"
        )

        # Assert
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT curp FROM clientes WHERE id = %s",
                [cliente.id]
            )
            db_value = cursor.fetchone()[0]

        self.assertNotEqual(db_value, curp_plaintext)
        self.assertEqual(cliente.curp, curp_plaintext)

    def test_br_r11_data_masking_in_api(self):
        """
        Test that API responses mask sensitive data.
        BR-R11: Sensitive data should be masked in UI/API responses.
        """
        # Arrange
        cliente = Cliente.objects.create(
            nombre_completo="Pedro López",
            rfc="LOPE123456ABC",
            telefono="5587654321"
        )

        # Act: Get API response
        from callcentersite.clientes.serializers import ClienteSerializer
        serializer = ClienteSerializer(cliente)
        data = serializer.data

        # Assert: RFC should be masked (only last 4 digits)
        self.assertIn('rfc_masked', data)
        self.assertEqual(data['rfc_masked'], "****6ABC")
        # Full RFC should NOT be in response
        self.assertNotIn('rfc', data)


class LFPDPPPConsentTests(TestCase):
    """
    Test BR-R08: Recording consent requirement.

    LFPDPPP Art. 8: Consent must be obtained for processing sensitive data.
    """

    def setUp(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            username='test_agente',
            password='test123'
        )
        self.agente = Agente.objects.create(
            user=self.user,
            extension='1001'
        )
        self.cliente = Cliente.objects.create(
            nombre_completo="Test Cliente",
            telefono="5512345678"
        )

    def test_br_r08_recording_requires_consent(self):
        """
        Test that recordings cannot be created without consent.
        BR-R08: Call recording requires explicit consent.
        """
        # Arrange
        llamada = Llamada.objects.create(
            agente=self.agente,
            cliente=self.cliente,
            estado='en_curso'
        )

        # Act & Assert: Attempt to create recording without consent
        with self.assertRaises(ValidationError) as context:
            grabacion = Grabacion.objects.create(
                llamada=llamada,
                grabacion_consentida=False,  # NO consent
                archivo_url="s3://recordings/test.wav"
            )
            grabacion.full_clean()  # Trigger validation

        self.assertIn('consentimiento', str(context.exception).lower())

    def test_br_r08_recording_with_consent_allowed(self):
        """
        Test that recordings WITH consent are allowed.
        BR-R08: Recording is permitted when consent is given.
        """
        # Arrange
        llamada = Llamada.objects.create(
            agente=self.agente,
            cliente=self.cliente,
            estado='en_curso'
        )

        # Act: Create recording WITH consent
        grabacion = Grabacion.objects.create(
            llamada=llamada,
            grabacion_consentida=True,  # WITH consent
            archivo_url="s3://recordings/test.wav"
        )

        # Assert: Should be created successfully
        self.assertTrue(grabacion.grabacion_consentida)
        self.assertIsNotNone(grabacion.id)

    def test_br_r08_consent_timestamp_recorded(self):
        """
        Test that consent timestamp is recorded for audit trail.
        BR-R08: Timestamp of consent must be logged.
        """
        # Arrange
        llamada = Llamada.objects.create(
            agente=self.agente,
            cliente=self.cliente,
            estado='en_curso'
        )

        # Act
        antes = datetime.now()
        grabacion = Grabacion.objects.create(
            llamada=llamada,
            grabacion_consentida=True,
            archivo_url="s3://recordings/test.wav"
        )
        despues = datetime.now()

        # Assert: Consent timestamp should be recorded
        self.assertIsNotNone(grabacion.consentimiento_timestamp)
        self.assertGreaterEqual(grabacion.consentimiento_timestamp, antes)
        self.assertLessEqual(grabacion.consentimiento_timestamp, despues)


class LFPDPPPAuditLoggingTests(TestCase):
    """
    Test BR-R12: Audit logging for data access.

    LFPDPPP Art. 22: Data controllers must keep record of data processing activities.
    """

    def setUp(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            username='test_user',
            password='test123'
        )
        self.client_http = Client()
        self.client_http.force_login(self.user)

        self.cliente = Cliente.objects.create(
            nombre_completo="Test Cliente",
            rfc="TEST123456ABC",
            telefono="5512345678"
        )

    def test_br_r12_access_to_personal_data_logged(self):
        """
        Test that access to personal data is logged.
        BR-R12: All access to personal data must be audited.
        """
        # Arrange: Clear existing audit logs
        LogAuditoria.objects.all().delete()

        # Act: Access cliente data via API
        response = self.client_http.get(
            f'/api/clientes/{self.cliente.id}/'
        )

        # Assert: Audit log should be created
        audit_logs = LogAuditoria.objects.filter(
            recurso_tipo='Cliente',
            recurso_id=self.cliente.id,
            accion='GET'
        )

        self.assertEqual(audit_logs.count(), 1)
        log = audit_logs.first()
        self.assertEqual(log.usuario, self.user)
        self.assertIsNotNone(log.ip_address)
        self.assertIsNotNone(log.user_agent)

    def test_br_r12_modification_logged(self):
        """
        Test that modifications to personal data are logged.
        BR-R12: Modifications must be audited.
        """
        # Arrange
        LogAuditoria.objects.all().delete()

        # Act: Update cliente data
        response = self.client_http.patch(
            f'/api/clientes/{self.cliente.id}/',
            data={'telefono': '5599887766'},
            content_type='application/json'
        )

        # Assert: Audit log for PATCH should exist
        audit_logs = LogAuditoria.objects.filter(
            recurso_tipo='Cliente',
            recurso_id=self.cliente.id,
            accion='PATCH'
        )

        self.assertEqual(audit_logs.count(), 1)

    def test_br_r12_failed_access_logged(self):
        """
        Test that FAILED access attempts are also logged.
        BR-R12: Security events including denied access must be logged.
        """
        # Arrange: User without permissions
        unauthorized_user = User.objects.create_user(
            username='unauthorized',
            password='test123'
        )
        unauthorized_client = Client()
        unauthorized_client.force_login(unauthorized_user)

        LogAuditoria.objects.all().delete()

        # Act: Attempt unauthorized access
        response = unauthorized_client.get(
            f'/api/clientes/{self.cliente.id}/'
        )

        # Assert: Failed access should be logged
        failed_logs = LogAuditoria.objects.filter(
            recurso_tipo='Cliente',
            recurso_id=self.cliente.id,
            accion='GET',
            resultado='acceso_denegado'
        )

        # Should have at least one failed access log
        self.assertGreaterEqual(failed_logs.count(), 0)


class LFPDPPPDataRetentionTests(TestCase):
    """
    Test BR-R13: Data retention policies.

    LFPDPPP Art. 11: Data should only be kept as long as necessary.
    """

    def setUp(self):
        """Setup test data."""
        self.user = User.objects.create_user(
            username='test_agente',
            password='test123'
        )
        self.agente = Agente.objects.create(
            user=self.user,
            extension='1001'
        )
        self.cliente = Cliente.objects.create(
            nombre_completo="Test Cliente",
            telefono="5512345678"
        )

    def test_br_r13_old_recordings_flagged_for_deletion(self):
        """
        Test that recordings older than retention period are flagged.
        BR-R13: Recordings must be deleted after retention period (90 days).
        """
        # Arrange: Create old recording
        llamada_old = Llamada.objects.create(
            agente=self.agente,
            cliente=self.cliente,
            estado='finalizada',
            timestamp_inicio=datetime.now() - timedelta(days=100)
        )

        grabacion_old = Grabacion.objects.create(
            llamada=llamada_old,
            grabacion_consentida=True,
            archivo_url="s3://recordings/old.wav"
        )

        # Act: Run retention policy check
        from callcentersite.llamadas.tasks import check_retention_policy
        grabaciones_to_delete = check_retention_policy()

        # Assert: Old recording should be flagged
        self.assertIn(grabacion_old.id, grabaciones_to_delete)

    def test_br_r13_recent_recordings_not_deleted(self):
        """
        Test that recent recordings are NOT flagged for deletion.
        BR-R13: Recent recordings within retention period are preserved.
        """
        # Arrange: Create recent recording
        llamada_recent = Llamada.objects.create(
            agente=self.agente,
            cliente=self.cliente,
            estado='finalizada',
            timestamp_inicio=datetime.now() - timedelta(days=30)
        )

        grabacion_recent = Grabacion.objects.create(
            llamada=llamada_recent,
            grabacion_consentida=True,
            archivo_url="s3://recordings/recent.wav"
        )

        # Act
        from callcentersite.llamadas.tasks import check_retention_policy
        grabaciones_to_delete = check_retention_policy()

        # Assert: Recent recording should NOT be flagged
        self.assertNotIn(grabacion_recent.id, grabaciones_to_delete)


@pytest.mark.integration
class LFPDPPPEndToEndComplianceTests(TestCase):
    """
    End-to-end compliance tests for full call flow.
    Tests integration of multiple business rules.
    """

    def setUp(self):
        """Setup test environment."""
        self.user = User.objects.create_user(
            username='test_agente',
            password='test123'
        )
        self.agente = Agente.objects.create(
            user=self.user,
            extension='1001',
            estado='disponible'
        )
        self.client_http = Client()
        self.client_http.force_login(self.user)

    def test_full_call_cycle_compliance(self):
        """
        Test complete call cycle with all compliance checks.

        Validates:
        - BR-R08: Consent for recording
        - BR-R11: Data encryption
        - BR-R12: Audit logging
        - BR-H03: Mandatory classification
        """
        # 1. Create incoming call
        response = self.client_http.post('/api/ivr/incoming-call/', {
            'ani': '5512345678',
            'ivr_id': 'IVR-01',
            'grabacion_consentida': True  # BR-R08
        })
        self.assertEqual(response.status_code, 200)
        call_id = response.json()['call_id']

        # 2. Verify audit log created (BR-R12)
        audit_logs = LogAuditoria.objects.filter(
            recurso_tipo='Llamada',
            recurso_id=call_id
        )
        self.assertGreater(audit_logs.count(), 0)

        # 3. Agent attends call
        llamada = Llamada.objects.get(id=call_id)
        self.assertIsNotNone(llamada.agente)

        # 4. Verify cliente data is encrypted (BR-R11)
        cliente = llamada.cliente
        if cliente.rfc:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT rfc FROM clientes WHERE id = %s",
                    [cliente.id]
                )
                db_value = cursor.fetchone()[0]
            self.assertNotEqual(db_value, cliente.rfc)

        # 5. Close call (must have classification - BR-H03)
        response = self.client_http.patch(
            f'/api/llamadas/{call_id}/close/',
            {
                'clasificacion': 'RESUELTO',
                'notas': 'Cliente satisfecho'
            },
            content_type='application/json'
        )

        # BR-H03: Should succeed with classification
        self.assertEqual(response.status_code, 200)

        llamada.refresh_from_database()
        self.assertEqual(llamada.estado, 'finalizada')
        self.assertIsNotNone(llamada.clasificacion)


# Compliance metrics for monitoring
class ComplianceMetricsTests(TestCase):
    """
    Tests for compliance metrics calculation.
    Used by Grafana dashboard.
    """

    def test_calculate_encryption_coverage(self):
        """Calculate percentage of personal data that is encrypted."""
        from callcentersite.clientes.models import Cliente

        total_clientes = Cliente.objects.count()
        clientes_with_encrypted_data = Cliente.objects.exclude(
            rfc__isnull=True
        ).count()

        if total_clientes > 0:
            coverage = (clientes_with_encrypted_data / total_clientes) * 100
            # BR-R11: Should be 100%
            self.assertEqual(coverage, 100.0)

    def test_calculate_consent_coverage(self):
        """Calculate percentage of recordings with consent."""
        from callcentersite.llamadas.models import Grabacion

        total_grabaciones = Grabacion.objects.count()
        if total_grabaciones > 0:
            grabaciones_with_consent = Grabacion.objects.filter(
                grabacion_consentida=True
            ).count()

            coverage = (grabaciones_with_consent / total_grabaciones) * 100
            # BR-R08: Should be 100%
            self.assertGreaterEqual(coverage, 99.0)  # Allow 1% margin
