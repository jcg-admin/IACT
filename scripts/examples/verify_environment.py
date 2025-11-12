#!/usr/bin/env python3
"""
Script de Verificacion de Configuracion de Ambiente

Verifica que la configuracion del ambiente actual sea valida y muestra
informacion detallada de todas las configuraciones.

Uso:
    python3 examples/verify_environment.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ai.shared.environment_config import get_environment_config


def print_section(title: str):
    """Imprime una seccion con formato."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def print_config_item(key: str, value: any, indent: int = 0):
    """Imprime un item de configuracion."""
    spaces = " " * indent
    if isinstance(value, bool):
        status = "[OK]" if value else "[DISABLED]"
        print(f"{spaces}{key:<30} {status}")
    elif isinstance(value, dict):
        print(f"{spaces}{key}:")
        for k, v in value.items():
            print_config_item(k, v, indent + 2)
    else:
        print(f"{spaces}{key:<30} {value}")


def main():
    """Verifica y muestra configuracion del ambiente."""
    try:
        config = get_environment_config()

        # Header
        print_section("CONFIGURACION DE AMBIENTE")

        # Ambiente actual
        print(f"Ambiente detectado: {config.environment.upper()}")
        print(f"  - Es desarrollo:  {config.is_dev}")
        print(f"  - Es staging:     {config.is_staging}")
        print(f"  - Es produccion:  {config.is_prod}")

        # Database
        print_section("DATABASE CONFIGURATION")
        db_config = config.get_database_config()
        print_config_item("Host", db_config.get("host"))
        print_config_item("Port", db_config.get("port"))
        print_config_item("Database", db_config.get("database"))
        print_config_item("User", db_config.get("user"))
        print_config_item("Password", "***" if db_config.get("password") else "NOT SET")
        print_config_item("Usa VM", db_config.get("use_vm", False))

        if db_config.get("ssh_tunnel"):
            print("\nSSH Tunnel:")
            tunnel = db_config["ssh_tunnel"]
            print_config_item("Enabled", tunnel.get("enabled"), 2)
            if tunnel.get("enabled"):
                print_config_item("SSH Host", tunnel.get("host"), 2)
                print_config_item("SSH Port", tunnel.get("port"), 2)
                print_config_item("SSH User", tunnel.get("user"), 2)

        # API
        print_section("API CONFIGURATION")
        api_config = config.get_api_config()
        print_config_item("Base URL", api_config.get("base_url"))
        print_config_item("Timeout", f"{api_config.get('timeout')}s")
        print_config_item("Verify SSL", api_config.get("verify_ssl"))
        print_config_item("Use Mock", api_config.get("use_mock", False))

        # LLM
        print_section("LLM CONFIGURATION")
        llm_config = config.get_llm_config()
        print_config_item("Provider", llm_config.get("llm_provider"))
        print_config_item("Model", llm_config.get("model"))
        print_config_item("Use LLM", llm_config.get("use_llm"))
        print_config_item("Prefer Local", llm_config.get("prefer_local", False))
        print_config_item("Fallback", llm_config.get("fallback_to_heuristics"))
        print_config_item("Max Tokens", llm_config.get("max_tokens"))

        if "monthly_budget" in llm_config:
            print_config_item("Monthly Budget", f"${llm_config['monthly_budget']}")

        # Cache
        print_section("CACHE CONFIGURATION")
        cache_config = config.get_cache_config()
        print_config_item("Enabled", cache_config.get("enabled"))
        print_config_item("Backend", cache_config.get("backend"))

        if cache_config.get("backend") == "redis":
            print_config_item("Redis Host", cache_config.get("host"))
            print_config_item("Redis Port", cache_config.get("port"))
            has_password = bool(cache_config.get("password"))
            print_config_item("Redis Password", "***" if has_password else "NOT SET")

        print_config_item("TTL", f"{cache_config.get('ttl')}s")

        # Logging
        print_section("LOGGING CONFIGURATION")
        log_config = config.get_logging_config()
        print_config_item("Level", log_config.get("level"))
        print_config_item("Console", log_config.get("console"))
        print_config_item("File", log_config.get("file"))

        if log_config.get("file"):
            print_config_item("File Path", log_config.get("file_path"))

        if log_config.get("sentry_dsn"):
            print_config_item("Sentry", "Configured")

        # Feature Flags
        print_section("FEATURE FLAGS")
        features = config.get_feature_flags()
        for feature, enabled in features.items():
            print_config_item(feature, enabled)

        # Validacion
        print_section("VALIDATION")
        try:
            config.validate_config()
            print("[OK] Configuracion valida")

            # Warnings especificos
            if config.is_prod:
                print("\nADVERTENCIAS DE PRODUCCION:")
                if not db_config.get("password"):
                    print("  [WARNING] Password de base de datos no configurada")
                if log_config.get("level") == "DEBUG":
                    print("  [WARNING] Debug level en produccion no recomendado")
                if not log_config.get("sentry_dsn"):
                    print("  [WARNING] Sentry no configurado (no hay error monitoring)")

        except ValueError as e:
            print(f"[ERROR] Configuracion invalida: {e}")
            return 1

        # Recomendaciones
        print_section("RECOMENDACIONES")

        if config.is_dev:
            print("Modo Desarrollo:")
            print("  - Levantar servicios: docker-compose -f docker-compose.dev.yml up")
            print("  - Instalar Ollama: brew install ollama (Mac) o curl -fsSL https://ollama.com/install.sh | sh (Linux)")
            print("  - Ejecutar agentes: python3 test_case1_viabilidad.py")

        elif config.is_staging:
            print("Modo Staging:")
            print("  - Verificar acceso a staging-db.internal")
            print("  - Configurar ANTHROPIC_API_KEY en .env")
            print("  - Ejecutar tests: python3 -m pytest")

        elif config.is_prod:
            print("Modo Produccion:")
            print("  - [CRITICO] Verificar todas las credenciales")
            print("  - [CRITICO] Backup de base de datos antes de deploy")
            print("  - [CRITICO] Configurar monitoring (Sentry)")
            print("  - Ejecutar smoke tests post-deploy")

        print(f"\n{'='*70}\n")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Error al verificar configuracion: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
