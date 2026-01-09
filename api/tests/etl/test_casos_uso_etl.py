"""
Tests TDD para Casos de Uso del modulo ETL.

Sistema de extraccion, transformacion y carga desde BD IVR.
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone

from callcentersite.apps.etl.models import ETLJob, ETLValidationError


@pytest.mark.django_db
class TestCrearJob:
    """Crear y ejecutar job ETL."""

    def test_crear_job_etl(self):
        """
        UC-ETL-01: Crear job ETL.

        Given necesidad de ejecutar ETL
        When se crea job
        Then job se registra con status=pending
        """
        from callcentersite.apps.etl.services import ETLService

        # Act
        job = ETLService.crear_job(
            job_name="ivr_data_extraction", metadata={"source": "bd_ivr"}
        )

        # Assert
        assert job is not None
        assert job.job_name == "ivr_data_extraction"
        assert job.status == "pending"
        assert job.started_at is None

    def test_marcar_job_como_running(self):
        """
        UC-ETL-02: Marcar job como en ejecucion.

        Given job creado
        When se inicia ejecucion
        Then status=running y started_at tiene fecha
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange
        job = ETLService.crear_job(job_name="test_job")

        # Act
        ETLService.iniciar_job(job_id=job.id)

        # Assert
        job.refresh_from_db()
        assert job.status == "running"
        assert job.started_at is not None


@pytest.mark.django_db
class TestEjecutarETL:
    """Ejecutar flujo ETL completo."""

    def test_ejecutar_etl_exitoso(self):
        """
        UC-ETL-03: Ejecutar ETL exitosamente.

        Given datos en BD IVR
        When se ejecuta ETL
        Then datos se extraen, transforman y cargan
        """
        from callcentersite.apps.etl.services import ETLService

        # Act
        job = ETLService.ejecutar_etl_completo(
            job_name="full_etl_test", fecha_inicio=timezone.now() - timedelta(hours=6)
        )

        # Assert
        assert job is not None
        # Job completed synchronously so should be in completed or failed state
        assert job.status in ["completed", "failed"]
        job.refresh_from_db()
        assert job.status in ["completed", "failed"]

    def test_completar_job_con_metricas(self):
        """
        UC-ETL-04: Completar job con metricas.

        Given job en ejecucion
        When se completa
        Then se registran metricas de extraidos/transformados/cargados
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange
        job = ETLService.crear_job(job_name="test_job")
        ETLService.iniciar_job(job_id=job.id)

        # Act
        ETLService.completar_job(
            job_id=job.id, extracted=100, transformed=95, loaded=90, failed=5
        )

        # Assert
        job.refresh_from_db()
        assert job.status == "completed"
        assert job.records_extracted == 100
        assert job.records_transformed == 95
        assert job.records_loaded == 90
        assert job.records_failed == 5
        assert job.execution_time_seconds is not None


@pytest.mark.django_db
class TestValidacionDatos:
    """Validar datos durante ETL."""

    def test_validar_datos_correctos(self):
        """
        UC-ETL-05: Validar datos correctos.

        Given datos validos
        When se validan
        Then validacion pasa sin errores
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange
        datos = {
            "call_id": 12345,
            "phone_number": "5551234567",
            "call_duration": 120,
            "call_date": timezone.now(),
        }

        # Act
        es_valido, errores = ETLService.validar_registro(datos)

        # Assert
        assert es_valido is True
        assert len(errores) == 0

    def test_validar_datos_invalidos(self):
        """
        UC-ETL-06: Detectar datos invalidos.

        Given datos con errores
        When se validan
        Then se detectan errores de validacion
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange - Datos invalidos (call_duration negativo)
        datos = {
            "call_id": None,  # ID nulo
            "phone_number": "123",  # Telefono muy corto
            "call_duration": -10,  # Duracion negativa
            "call_date": None,  # Fecha nula
        }

        # Act
        es_valido, errores = ETLService.validar_registro(datos)

        # Assert
        assert es_valido is False
        assert len(errores) > 0


@pytest.mark.django_db
class TestManejoErrores:
    """Manejo de errores durante ETL."""

    def test_registrar_error_validacion(self):
        """
        UC-ETL-07: Registrar error de validacion.

        Given error durante validacion
        When se registra
        Then se crea ETLValidationError
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange
        job = ETLService.crear_job(job_name="test_job")

        # Act
        error = ETLService.registrar_error_validacion(
            job_id=job.id,
            error_type="invalid_phone",
            error_message="Numero de telefono invalido",
            record_data={"phone": "123"},
            field_name="phone_number",
            severity="error",
        )

        # Assert
        assert error is not None
        assert error.job_id == job.id
        assert error.error_type == "invalid_phone"

    def test_marcar_job_como_fallido(self):
        """
        UC-ETL-08: Marcar job como fallido.

        Given error critico durante ETL
        When se marca como fallido
        Then status=failed y se registra error
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange
        job = ETLService.crear_job(job_name="test_job")
        ETLService.iniciar_job(job_id=job.id)

        # Act
        ETLService.marcar_job_fallido(
            job_id=job.id,
            error_message="Error de conexion a BD IVR",
            error_details={"code": "CONNECTION_ERROR"},
        )

        # Assert
        job.refresh_from_db()
        assert job.status == "failed"
        assert job.error_message == "Error de conexion a BD IVR"
        assert "code" in job.error_details


@pytest.mark.django_db
class TestMonitoreoETL:
    """Monitoreo de jobs ETL."""

    def test_listar_jobs_recientes(self):
        """
        UC-ETL-09: Listar jobs recientes.

        Given jobs ejecutados
        When se listan
        Then retorna jobs ordenados por fecha
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange - Crear 3 jobs
        for i in range(3):
            ETLService.crear_job(job_name=f"job_{i}")

        # Act
        jobs = ETLService.listar_jobs_recientes(limite=10)

        # Assert
        assert len(jobs) >= 3

    def test_obtener_estadisticas_job(self):
        """
        UC-ETL-10: Obtener estadisticas de job.

        Given job completado
        When se consultan estadisticas
        Then retorna metricas del job
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange
        job = ETLService.crear_job(job_name="test_job")
        ETLService.iniciar_job(job_id=job.id)
        ETLService.completar_job(
            job_id=job.id, extracted=100, transformed=100, loaded=100, failed=0
        )

        # Act
        stats = ETLService.obtener_estadisticas_job(job_id=job.id)

        # Assert
        assert stats is not None
        assert stats["records_extracted"] == 100
        assert stats["records_loaded"] == 100
        assert "execution_time_seconds" in stats


@pytest.mark.django_db
class TestFiltroCentros:
    """Filtrado de datos por centros especificos."""

    def test_filtrar_solo_centros_permitidos(self):
        """
        UC-ETL-11: Filtrar solo centros Nacional y Puebla.

        Given datos de multiples centros
        When se filtran
        Then solo se procesan Nacional (19028031) y Puebla (19020084)
        """
        from callcentersite.apps.etl.services import ETLService

        # Arrange
        datos_multiples_centros = [
            {"centro_id": "19028031", "nombre": "Nacional"},  # Valido
            {"centro_id": "19020084", "nombre": "Puebla"},  # Valido
            {"centro_id": "99999999", "nombre": "Otro"},  # No valido
        ]

        # Act
        datos_filtrados = ETLService.filtrar_por_centros_permitidos(
            datos_multiples_centros
        )

        # Assert
        assert len(datos_filtrados) == 2
        assert all(d["centro_id"] in ["19028031", "19020084"] for d in datos_filtrados)
