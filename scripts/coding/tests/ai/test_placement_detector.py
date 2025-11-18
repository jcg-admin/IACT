"""
Tests para RF-001: Detectar Tipo de Artefacto

TDD RED Phase: Estos tests DEBEN fallar inicialmente porque
el codigo aun no esta implementado.
"""

import pytest
from scripts.coding.ai.agents.placement.detector import (
    detectar_tipo,
    detectar_dominios_en_contenido
)


class TestDetectarTipoPorNombre:
    """Tests para deteccion de tipo desde nombre de archivo"""

    def test_detectar_task_por_nombre(self):
        """RF-001: Detectar tipo 'task' desde nombre TASK-XXX"""
        nombre = "TASK-001-implementar_feature.md"
        contenido = "# Task\n\nDescripcion de la tarea"

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "task"

    def test_detectar_adr_por_nombre(self):
        """RF-001: Detectar tipo 'adr' desde nombre ADR-XXX"""
        nombre = "ADR-010-arquitectura_dominios.md"
        contenido = "# ADR\n\nDecision arquitectonica"

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "adr"

    def test_detectar_analisis_por_nombre(self):
        """RF-001: Detectar tipo 'analisis' desde nombre ANALISIS_XXX"""
        nombre = "ANALISIS_DOCS_ESTRUCTURA_20251116.md"
        contenido = "# Analisis\n\n## Hallazgos"

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "analisis"

    def test_detectar_guia_por_nombre(self):
        """RF-001: Detectar tipo 'guia' desde nombre GUIA_XXX"""
        nombre = "GUIA_TESTING.md"
        contenido = "# Guia de Testing"

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "guia"

    def test_detectar_indice_por_nombre(self):
        """RF-001: Detectar tipo 'indice' desde nombre INDEX.md"""
        nombre = "INDEX.md"
        contenido = "# Indice\n\n- Archivo 1\n- Archivo 2"

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "indice"


class TestDetectarTipoPorContenido:
    """Tests para deteccion de tipo desde contenido"""

    def test_detectar_adr_por_contenido(self):
        """RF-001: Detectar tipo 'adr' desde patron de contenido"""
        nombre = "documento.md"
        contenido = """
        # Decision Arquitectonica

        ## Decision
        Usaremos arquitectura por dominios

        ## Status
        Accepted
        """

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "adr"

    def test_detectar_documentacion_agente_por_contenido(self):
        """RF-001: Detectar tipo 'documentacion_agente' desde patron"""
        nombre = "README.md"
        contenido = """
        # Agente de Placement

        ## Sub-Agentes
        - Detector
        - Classifier

        ## Arquitectura
        Pipeline de clasificacion
        """

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "documentacion_agente"

    def test_detectar_plan_testing_por_contenido(self):
        """RF-001: Detectar tipo 'plan_testing' desde patron"""
        nombre = "plan.md"
        contenido = """
        # Plan de Testing

        ## Casos de Prueba
        - Test 1
        - Test 2

        ## Cobertura
        90%
        """

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "plan_testing"


class TestDetectarTipoFallback:
    """Tests para caso de tipo no detectado"""

    def test_tipo_no_detectado_devuelve_documento_general(self):
        """RF-001: Si no se detecta tipo, devolver 'documento_general'"""
        nombre = "archivo_generico.md"
        contenido = "Contenido sin patrones reconocibles"

        resultado = detectar_tipo(nombre, contenido)

        assert resultado == "documento_general"


class TestDetectarDominiosEnContenido:
    """Tests para deteccion de dominios mencionados en contenido"""

    def test_detectar_dominio_backend(self):
        """RF-002: Detectar mencion de dominio backend"""
        contenido = """
        Este documento describe la API Django REST.
        Usaremos PostgreSQL para la base de datos.
        """

        dominios = detectar_dominios_en_contenido(contenido)

        assert "backend" in dominios

    def test_detectar_dominio_frontend(self):
        """RF-002: Detectar mencion de dominio frontend"""
        contenido = """
        Implementaremos con React y Redux.
        El componente usara TypeScript.
        """

        dominios = detectar_dominios_en_contenido(contenido)

        assert "frontend" in dominios

    def test_detectar_multiples_dominios(self):
        """RF-002: Detectar multiples dominios mencionados"""
        contenido = """
        La API Django (backend) se comunicara con
        la aplicacion React (frontend) via REST.
        """

        dominios = detectar_dominios_en_contenido(contenido)

        assert "backend" in dominios
        assert "frontend" in dominios

    def test_sin_dominios_devuelve_lista_vacia(self):
        """RF-002: Si no se mencionan dominios, devolver lista vacia"""
        contenido = "Este es un documento generico sin menciones tecnicas"

        dominios = detectar_dominios_en_contenido(contenido)

        assert dominios == []
