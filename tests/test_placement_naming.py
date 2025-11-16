"""
Tests para RF-004: Generar Nombre Estandarizado

TDD RED Phase: Estos tests DEBEN fallar inicialmente.
"""

import pytest
from scripts.coding.ai.agents.placement.naming import (
    construir_nombre,
    normalizar_descripcion,
    normalizar_nombre
)


class TestConstruirNombre:
    """Tests para generacion de nombres por tipo"""

    def test_construir_nombre_task(self):
        """RF-004: Generar nombre de TASK con formato estandar"""
        tipo = "task"
        nombre_original = "tarea.md"
        contexto = {
            "id": "001",
            "descripcion": "Implementar Feature"
        }

        resultado = construir_nombre(tipo, nombre_original, contexto)

        assert resultado == "TASK-001-implementar_feature.md"

    def test_construir_nombre_adr(self):
        """RF-004: Generar nombre de ADR con formato estandar"""
        tipo = "adr"
        nombre_original = "decision.md"
        contexto = {
            "id": "010",
            "descripcion": "Arquitectura por Dominios"
        }

        resultado = construir_nombre(tipo, nombre_original, contexto)

        assert resultado == "ADR-010-arquitectura_por_dominios.md"

    def test_construir_nombre_analisis_con_fecha(self):
        """RF-004: Generar nombre de analisis con tema y fecha"""
        tipo = "analisis"
        nombre_original = "analisis.md"
        contexto = {
            "tema": "DOCS_ESTRUCTURA"
        }

        resultado = construir_nombre(tipo, nombre_original, contexto)

        # Debe contener ANALISIS_DOCS_ESTRUCTURA_YYYYMMDD.md
        assert resultado.startswith("ANALISIS_DOCS_ESTRUCTURA_")
        assert resultado.endswith(".md")
        assert len(resultado) == len("ANALISIS_DOCS_ESTRUCTURA_20251116.md")

    def test_construir_nombre_guia(self):
        """RF-004: Generar nombre de guia con tema"""
        tipo = "guia"
        nombre_original = "guia.md"
        contexto = {
            "tema": "TESTING"
        }

        resultado = construir_nombre(tipo, nombre_original, contexto)

        assert resultado == "GUIA_TESTING.md"

    def test_construir_nombre_indice(self):
        """RF-004: Nombre de indice siempre es INDEX.md"""
        tipo = "indice"
        nombre_original = "cualquier_nombre.md"
        contexto = {}

        resultado = construir_nombre(tipo, nombre_original, contexto)

        assert resultado == "INDEX.md"


class TestNormalizarDescripcion:
    """Tests para normalizacion de descripciones"""

    def test_normalizar_elimina_emojis(self):
        """RF-004: Eliminar emojis de descripcion"""
        descripcion = "Fix Bug 🐛 en Login"

        resultado = normalizar_descripcion(descripcion)

        assert resultado == "fix_bug_en_login"
        assert "🐛" not in resultado

    def test_normalizar_elimina_caracteres_especiales(self):
        """RF-004: Eliminar caracteres especiales"""
        descripcion = "Análisis de Docs 📊!!!"

        resultado = normalizar_descripcion(descripcion)

        # Debe quedar sin emoji ni signos de exclamacion
        assert "📊" not in resultado
        assert "!" not in resultado

    def test_normalizar_convierte_a_lowercase(self):
        """RF-004: Convertir a lowercase"""
        descripcion = "Implementar FEATURE Nueva"

        resultado = normalizar_descripcion(descripcion)

        assert resultado == "implementar_feature_nueva"
        assert resultado.islower()

    def test_normalizar_reemplaza_espacios_por_underscores(self):
        """RF-004: Espacios se convierten en underscores"""
        descripcion = "Crear nueva funcionalidad"

        resultado = normalizar_descripcion(descripcion)

        assert " " not in resultado
        assert resultado == "crear_nueva_funcionalidad"

    def test_normalizar_elimina_underscores_multiples(self):
        """RF-004: Underscores multiples se consolidan a uno"""
        descripcion = "Feature___con____espacios"

        resultado = normalizar_descripcion(descripcion)

        assert "___" not in resultado
        assert "____" not in resultado
        assert resultado == "feature_con_espacios"

    def test_normalizar_elimina_underscores_extremos(self):
        """RF-004: Eliminar underscores al inicio/fin"""
        descripcion = "___feature_testing___"

        resultado = normalizar_descripcion(descripcion)

        assert not resultado.startswith("_")
        assert not resultado.endswith("_")
        assert resultado == "feature_testing"


class TestNormalizarNombre:
    """Tests para normalizacion de nombres de archivo"""

    def test_normalizar_mantiene_extension(self):
        """RF-004: Mantener extension de archivo"""
        nombre = "Archivo Test.md"

        resultado = normalizar_nombre(nombre)

        assert resultado.endswith(".md")
        assert resultado == "archivo_test.md"

    def test_normalizar_archivo_sin_extension(self):
        """RF-004: Manejar archivos sin extension"""
        nombre = "archivo_sin_extension"

        resultado = normalizar_nombre(nombre)

        assert "." not in resultado
        assert resultado == "archivo_sin_extension"
