#!/usr/bin/env python3
"""
Environment Configuration Manager

Maneja configuraciones diferentes según el ambiente (dev, staging, prod).
Permite a los agentes adaptarse automáticamente al contexto de ejecución.

Uso:
    from scripts.coding.ai.shared.environment_config import EnvironmentConfig

    config = EnvironmentConfig()
    db_config = config.get_database_config()
    api_config = config.get_api_config()
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class EnvironmentConfig:
    """
    Gestiona configuraciones por ambiente.

    Ambientes soportados:
    - development: Ambiente local, usa VM o mocks
    - staging: Ambiente de pruebas, usa recursos de staging
    - production: Ambiente productivo, usa credenciales reales
    """

    VALID_ENVIRONMENTS = ["development", "staging", "production"]

    def __init__(self):
        """Inicializa y detecta el ambiente actual."""
        self._load_env_file()
        self.environment = self._detect_environment()
        self.is_dev = self.environment == "development"
        self.is_staging = self.environment == "staging"
        self.is_prod = self.environment == "production"

    def _load_env_file(self):
        """Carga variables de entorno desde archivo .env"""
        try:
            project_root = Path(__file__).parent.parent.parent.parent
            env_file = project_root / ".env"

            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            # Solo setear si no existe (permite mocking en tests)
                            if key not in os.environ:
                                os.environ[key] = value
        except Exception:
            pass

    def _detect_environment(self) -> str:
        """
        Detecta el ambiente actual.

        Orden de detección:
        1. Variable ENVIRONMENT en .env
        2. Variable APP_ENV
        3. Variable DJANGO_ENV
        4. Default: development
        """
        env = os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or os.getenv("DJANGO_ENV")

        if env and env.lower() in self.VALID_ENVIRONMENTS:
            return env.lower()

        # Default a development
        return "development"

    def get_database_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de base de datos según ambiente.

        Returns:
            dict con: host, port, database, user, password, use_vm
        """
        if self.is_dev:
            # Desarrollo: Conectar a VM
            return {
                "host": os.getenv("DB_VM_HOST", "localhost"),
                "port": int(os.getenv("DB_VM_PORT", "5432")),
                "database": os.getenv("DB_VM_NAME", "iact_dev"),
                "user": os.getenv("DB_VM_USER", "dev_user"),
                "password": os.getenv("DB_VM_PASSWORD", "dev_password"),
                "use_vm": True,
                "ssh_tunnel": {
                    "enabled": os.getenv("DB_SSH_TUNNEL", "false").lower() == "true",
                    "host": os.getenv("DB_SSH_HOST", "192.168.1.100"),
                    "port": int(os.getenv("DB_SSH_PORT", "22")),
                    "user": os.getenv("DB_SSH_USER", "vagrant")
                }
            }

        elif self.is_staging:
            # Staging: Usar base de datos de staging
            return {
                "host": os.getenv("DB_STAGING_HOST", "staging-db.internal"),
                "port": int(os.getenv("DB_STAGING_PORT", "5432")),
                "database": os.getenv("DB_STAGING_NAME", "iact_staging"),
                "user": os.getenv("DB_STAGING_USER"),
                "password": os.getenv("DB_STAGING_PASSWORD"),
                "use_vm": False,
                "ssl_mode": "require"
            }

        else:  # production
            # Producción: Credenciales directas
            return {
                "host": os.getenv("DB_PROD_HOST"),
                "port": int(os.getenv("DB_PROD_PORT", "5432")),
                "database": os.getenv("DB_PROD_NAME"),
                "user": os.getenv("DB_PROD_USER"),
                "password": os.getenv("DB_PROD_PASSWORD"),
                "use_vm": False,
                "ssl_mode": "require",
                "ssl_ca": os.getenv("DB_PROD_SSL_CA")
            }

    def get_api_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de APIs externas según ambiente.

        Returns:
            dict con configuraciones de APIs
        """
        if self.is_dev:
            return {
                "base_url": os.getenv("API_DEV_URL", "http://localhost:8000"),
                "timeout": 30,
                "verify_ssl": False,
                "use_mock": os.getenv("USE_API_MOCK", "false").lower() == "true"
            }

        elif self.is_staging:
            return {
                "base_url": os.getenv("API_STAGING_URL"),
                "timeout": 30,
                "verify_ssl": True,
                "use_mock": False
            }

        else:  # production
            return {
                "base_url": os.getenv("API_PROD_URL"),
                "timeout": 60,
                "verify_ssl": True,
                "use_mock": False,
                "rate_limit": int(os.getenv("API_RATE_LIMIT", "100"))
            }

    def get_llm_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de LLM según ambiente.

        Returns:
            dict con configuración de LLM apropiada
        """
        if self.is_dev:
            # Desarrollo: Preferir Ollama local o heurísticas
            return {
                "prefer_local": True,
                "llm_provider": os.getenv("LLM_PROVIDER", "ollama"),
                "model": os.getenv("LLM_MODEL", "llama3.1:8b"),
                "use_llm": os.getenv("USE_LLM", "true").lower() == "true",
                "fallback_to_heuristics": True,
                "max_tokens": 2000
            }

        elif self.is_staging:
            # Staging: Usar LLM cloud pero con límites
            return {
                "prefer_local": False,
                "llm_provider": os.getenv("LLM_PROVIDER", "anthropic"),
                "model": os.getenv("LLM_MODEL", "claude-3-haiku-20240307"),  # Modelo más barato
                "use_llm": True,
                "fallback_to_heuristics": True,
                "max_tokens": 4000,
                "monthly_budget": 50  # Budget menor en staging
            }

        else:  # production
            # Producción: Usar mejor modelo disponible
            return {
                "prefer_local": False,
                "llm_provider": os.getenv("LLM_PROVIDER", "anthropic"),
                "model": os.getenv("LLM_MODEL", "claude-sonnet-4-5-20250929"),
                "use_llm": True,
                "fallback_to_heuristics": True,
                "max_tokens": 8000,
                "monthly_budget": int(os.getenv("LLM_MONTHLY_BUDGET", "100"))
            }

    def get_cache_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de cache según ambiente.

        Returns:
            dict con configuración de cache
        """
        if self.is_dev:
            return {
                "enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
                "backend": "memory",  # Cache en memoria para dev
                "ttl": 3600  # 1 hora
            }

        elif self.is_staging:
            return {
                "enabled": True,
                "backend": "redis",
                "host": os.getenv("REDIS_STAGING_HOST", "localhost"),
                "port": int(os.getenv("REDIS_STAGING_PORT", "6379")),
                "ttl": 7200  # 2 horas
            }

        else:  # production
            return {
                "enabled": True,
                "backend": "redis",
                "host": os.getenv("REDIS_PROD_HOST"),
                "port": int(os.getenv("REDIS_PROD_PORT", "6379")),
                "password": os.getenv("REDIS_PROD_PASSWORD"),
                "ttl": 86400  # 24 horas
            }

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de logging según ambiente.

        Returns:
            dict con nivel de logging y destinos
        """
        if self.is_dev:
            return {
                "level": "DEBUG",
                "console": True,
                "file": False,
                "format": "%(levelname)s - %(message)s"
            }

        elif self.is_staging:
            return {
                "level": "INFO",
                "console": True,
                "file": True,
                "file_path": "/var/log/iact/staging.log",
                "format": "[%(asctime)s] %(levelname)s - %(message)s"
            }

        else:  # production
            return {
                "level": "WARNING",
                "console": False,
                "file": True,
                "file_path": "/var/log/iact/production.log",
                "format": "[%(asctime)s] %(name)s %(levelname)s - %(message)s",
                "sentry_dsn": os.getenv("SENTRY_DSN")  # Monitoring de errores
            }

    def get_feature_flags(self) -> Dict[str, bool]:
        """
        Obtiene feature flags según ambiente.

        Returns:
            dict con features habilitadas/deshabilitadas
        """
        if self.is_dev:
            return {
                "enable_llm": True,
                "enable_cache": True,
                "enable_analytics": False,
                "enable_email": False,
                "debug_mode": True,
                "mock_external_apis": True
            }

        elif self.is_staging:
            return {
                "enable_llm": True,
                "enable_cache": True,
                "enable_analytics": True,
                "enable_email": True,  # Emails a direcciones de test
                "debug_mode": False,
                "mock_external_apis": False
            }

        else:  # production
            return {
                "enable_llm": True,
                "enable_cache": True,
                "enable_analytics": True,
                "enable_email": True,
                "debug_mode": False,
                "mock_external_apis": False
            }

    def is_feature_enabled(self, feature: str) -> bool:
        """
        Verifica si una feature está habilitada.

        Args:
            feature: Nombre de la feature

        Returns:
            True si está habilitada
        """
        return self.get_feature_flags().get(feature, False)

    def validate_config(self) -> bool:
        """
        Valida que la configuración del ambiente actual sea completa.

        Returns:
            True si la configuración es válida
        """
        if self.is_prod:
            # En producción, validar que existan credenciales críticas
            required = [
                "DB_PROD_HOST",
                "DB_PROD_USER",
                "DB_PROD_PASSWORD",
                "API_PROD_URL"
            ]

            missing = [var for var in required if not os.getenv(var)]

            if missing:
                raise ValueError(f"Producción requiere variables: {', '.join(missing)}")

        return True


# Singleton global
_env_config: Optional[EnvironmentConfig] = None


def get_environment_config() -> EnvironmentConfig:
    """
    Obtiene la instancia global de EnvironmentConfig.

    Returns:
        Instancia de EnvironmentConfig
    """
    global _env_config
    if _env_config is None:
        _env_config = EnvironmentConfig()
    return _env_config
