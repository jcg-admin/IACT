#!/usr/bin/env python3
"""
Tests para EnvironmentConfig

Estos tests SI se ejecutan y validan que el sistema funciona correctamente.
"""

import os
import pytest
from unittest.mock import patch
from scripts.ai.shared.environment_config import EnvironmentConfig, get_environment_config
import scripts.ai.shared.environment_config as env_module


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton between tests."""
    env_module._env_config = None
    yield
    env_module._env_config = None


class TestEnvironmentDetection:
    """Tests de deteccion de ambiente."""

    def test_detect_development_default(self):
        """Por defecto debe detectar development."""
        with patch.dict(os.environ, {}, clear=True):
            config = EnvironmentConfig()
            assert config.environment == "development"
            assert config.is_dev is True
            assert config.is_staging is False
            assert config.is_prod is False

    def test_detect_staging_from_environment_var(self):
        """Debe detectar staging desde variable ENVIRONMENT."""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            config = EnvironmentConfig()
            assert config.environment == "staging"
            assert config.is_dev is False
            assert config.is_staging is True
            assert config.is_prod is False

    def test_detect_production_from_environment_var(self):
        """Debe detectar production desde variable ENVIRONMENT."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            config = EnvironmentConfig()
            assert config.environment == "production"
            assert config.is_dev is False
            assert config.is_staging is False
            assert config.is_prod is True

    def test_detect_from_app_env(self):
        """Debe detectar desde APP_ENV si ENVIRONMENT no existe."""
        with patch.dict(os.environ, {"APP_ENV": "staging"}, clear=True):
            config = EnvironmentConfig()
            assert config.environment == "staging"

    def test_case_insensitive_detection(self):
        """Deteccion debe ser case-insensitive."""
        with patch.dict(os.environ, {"ENVIRONMENT": "PRODUCTION"}, clear=True):
            config = EnvironmentConfig()
            assert config.environment == "production"


class TestDatabaseConfig:
    """Tests de configuracion de base de datos."""

    def test_development_database_config(self):
        """Development debe usar VM."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()
            db_config = config.get_database_config()

            assert db_config["use_vm"] is True
            assert db_config["host"] == "localhost"
            assert db_config["port"] == 5432
            assert db_config["database"] == "iact_dev"
            assert db_config["user"] == "dev_user"
            assert "ssh_tunnel" in db_config

    def test_staging_database_config(self):
        """Staging debe usar servidor de staging."""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            config = EnvironmentConfig()
            db_config = config.get_database_config()

            assert db_config["use_vm"] is False
            assert "staging" in db_config["host"]
            assert db_config["ssl_mode"] == "require"

    def test_production_database_config(self):
        """Production debe usar conexion directa con SSL."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            config = EnvironmentConfig()
            db_config = config.get_database_config()

            assert db_config["use_vm"] is False
            assert db_config["ssl_mode"] == "require"
            assert "ssl_ca" in db_config

    def test_development_ssh_tunnel_disabled_by_default(self):
        """SSH tunnel debe estar deshabilitado por defecto."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()
            db_config = config.get_database_config()

            assert db_config["ssh_tunnel"]["enabled"] is False

    def test_development_ssh_tunnel_can_be_enabled(self):
        """SSH tunnel puede habilitarse via env var."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "DB_SSH_TUNNEL": "true"
        }, clear=True):
            config = EnvironmentConfig()
            db_config = config.get_database_config()

            assert db_config["ssh_tunnel"]["enabled"] is True

    def test_custom_database_credentials(self):
        """Credenciales custom deben usarse si se proveen."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "DB_VM_HOST": "192.168.1.100",
            "DB_VM_PORT": "5433",
            "DB_VM_NAME": "my_custom_db",
            "DB_VM_USER": "my_user",
            "DB_VM_PASSWORD": "my_password"
        }, clear=True):
            config = EnvironmentConfig()
            db_config = config.get_database_config()

            assert db_config["host"] == "192.168.1.100"
            assert db_config["port"] == 5433
            assert db_config["database"] == "my_custom_db"
            assert db_config["user"] == "my_user"
            assert db_config["password"] == "my_password"


class TestLLMConfig:
    """Tests de configuracion de LLM."""

    def test_development_prefers_local_llm(self):
        """Development debe preferir Ollama local."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()
            llm_config = config.get_llm_config()

            assert llm_config["prefer_local"] is True
            assert llm_config["llm_provider"] == "ollama"
            assert llm_config["model"] == "llama3.1:8b"
            assert llm_config["fallback_to_heuristics"] is True

    def test_staging_uses_cheaper_model(self):
        """Staging debe usar modelo barato (Haiku)."""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            config = EnvironmentConfig()
            llm_config = config.get_llm_config()

            assert llm_config["prefer_local"] is False
            assert llm_config["llm_provider"] == "anthropic"
            assert "haiku" in llm_config["model"].lower()
            assert llm_config["monthly_budget"] == 50

    def test_production_uses_best_model(self):
        """Production debe usar mejor modelo (Sonnet)."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            config = EnvironmentConfig()
            llm_config = config.get_llm_config()

            assert llm_config["prefer_local"] is False
            assert llm_config["llm_provider"] == "anthropic"
            assert "sonnet" in llm_config["model"].lower()
            assert llm_config["monthly_budget"] == 100

    def test_custom_llm_budget(self):
        """Budget custom debe aplicarse."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "LLM_MONTHLY_BUDGET": "250"
        }, clear=True):
            config = EnvironmentConfig()
            llm_config = config.get_llm_config()

            assert llm_config["monthly_budget"] == 250


class TestCacheConfig:
    """Tests de configuracion de cache."""

    def test_development_uses_memory_cache(self):
        """Development debe usar cache en memoria."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()
            cache_config = config.get_cache_config()

            assert cache_config["backend"] == "memory"
            assert cache_config["enabled"] is True

    def test_staging_uses_redis(self):
        """Staging debe usar Redis."""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            config = EnvironmentConfig()
            cache_config = config.get_cache_config()

            assert cache_config["backend"] == "redis"
            assert "host" in cache_config
            assert "port" in cache_config

    def test_production_uses_redis_with_password(self):
        """Production debe usar Redis con password."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            config = EnvironmentConfig()
            cache_config = config.get_cache_config()

            assert cache_config["backend"] == "redis"
            assert "password" in cache_config

    def test_cache_can_be_disabled(self):
        """Cache puede deshabilitarse."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "CACHE_ENABLED": "false"
        }, clear=True):
            config = EnvironmentConfig()
            cache_config = config.get_cache_config()

            assert cache_config["enabled"] is False


class TestFeatureFlags:
    """Tests de feature flags."""

    def test_development_has_debug_enabled(self):
        """Development debe tener debug habilitado."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()
            flags = config.get_feature_flags()

            assert flags["debug_mode"] is True
            assert flags["mock_external_apis"] is True
            assert flags["enable_email"] is False

    def test_production_has_debug_disabled(self):
        """Production debe tener debug deshabilitado."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            config = EnvironmentConfig()
            flags = config.get_feature_flags()

            assert flags["debug_mode"] is False
            assert flags["mock_external_apis"] is False
            assert flags["enable_email"] is True

    def test_is_feature_enabled_helper(self):
        """Helper is_feature_enabled debe funcionar."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()

            assert config.is_feature_enabled("debug_mode") is True
            assert config.is_feature_enabled("enable_email") is False


class TestConfigValidation:
    """Tests de validacion de configuracion."""

    def test_development_validation_passes(self):
        """Validacion en development debe pasar."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()
            assert config.validate_config() is True

    def test_staging_validation_passes(self):
        """Validacion en staging debe pasar."""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            config = EnvironmentConfig()
            assert config.validate_config() is True

    def test_production_requires_credentials(self):
        """Production debe requerir credenciales criticas."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            config = EnvironmentConfig()

            with pytest.raises(ValueError) as exc_info:
                config.validate_config()

            assert "DB_PROD_HOST" in str(exc_info.value)

    def test_production_validation_passes_with_credentials(self):
        """Production debe pasar con todas las credenciales."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "DB_PROD_HOST": "prod-db.example.com",
            "DB_PROD_USER": "prod_user",
            "DB_PROD_PASSWORD": "secure_password",
            "API_PROD_URL": "https://api.example.com"
        }, clear=True):
            config = EnvironmentConfig()
            assert config.validate_config() is True


class TestSingletonPattern:
    """Tests del patron singleton."""

    def test_get_environment_config_returns_same_instance(self):
        """get_environment_config debe retornar misma instancia."""
        config1 = get_environment_config()
        config2 = get_environment_config()

        assert config1 is config2

    def test_singleton_preserves_state(self):
        """Singleton debe preservar estado."""
        config1 = get_environment_config()
        env1 = config1.environment

        config2 = get_environment_config()
        env2 = config2.environment

        assert env1 == env2


class TestAPIConfig:
    """Tests de configuracion de API."""

    def test_development_api_local(self):
        """Development debe usar API local."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()
            api_config = config.get_api_config()

            assert "localhost" in api_config["base_url"]
            assert api_config["verify_ssl"] is False

    def test_production_api_secure(self):
        """Production debe verificar SSL."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            config = EnvironmentConfig()
            api_config = config.get_api_config()

            assert api_config["verify_ssl"] is True
            assert "rate_limit" in api_config


class TestLoggingConfig:
    """Tests de configuracion de logging."""

    def test_development_verbose_logging(self):
        """Development debe tener logging verbose."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()
            log_config = config.get_logging_config()

            assert log_config["level"] == "DEBUG"
            assert log_config["console"] is True
            assert log_config["file"] is False

    def test_production_minimal_logging(self):
        """Production debe tener logging minimal."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            config = EnvironmentConfig()
            log_config = config.get_logging_config()

            assert log_config["level"] == "WARNING"
            assert log_config["console"] is False
            assert log_config["file"] is True


# Tests de integracion
class TestIntegration:
    """Tests de integracion end-to-end."""

    def test_full_development_workflow(self):
        """Test completo de workflow de desarrollo."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            config = EnvironmentConfig()

            # Verificar deteccion
            assert config.is_dev

            # Verificar configs
            db = config.get_database_config()
            assert db["use_vm"] is True

            llm = config.get_llm_config()
            assert llm["prefer_local"] is True

            cache = config.get_cache_config()
            assert cache["backend"] == "memory"

            # Validar
            assert config.validate_config() is True

    def test_full_production_workflow(self):
        """Test completo de workflow de produccion."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "DB_PROD_HOST": "prod-db.com",
            "DB_PROD_USER": "user",
            "DB_PROD_PASSWORD": "pass",
            "API_PROD_URL": "https://api.com"
        }, clear=True):
            config = EnvironmentConfig()

            # Verificar deteccion
            assert config.is_prod

            # Verificar configs
            db = config.get_database_config()
            assert db["use_vm"] is False
            assert db["ssl_mode"] == "require"

            llm = config.get_llm_config()
            assert "sonnet" in llm["model"].lower()

            cache = config.get_cache_config()
            assert cache["backend"] == "redis"

            flags = config.get_feature_flags()
            assert flags["debug_mode"] is False

            # Validar
            assert config.validate_config() is True
