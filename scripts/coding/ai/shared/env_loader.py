"""
Cargador de variables de entorno desde archivo .env

Automaticamente carga las API keys y configuraciones desde .env
al inicializar cualquier agente SDLC.
"""

import os
from pathlib import Path


def load_env_file(env_file: str = ".env") -> dict:
    """
    Carga variables de entorno desde archivo .env

    Args:
        env_file: Ruta al archivo .env (default: ".env" en raíz del proyecto)

    Returns:
        Dict con variables cargadas
    """
    # Buscar .env en la raíz del proyecto
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / env_file

    loaded_vars = {}

    if not env_path.exists():
        return loaded_vars

    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()

                # Ignorar comentarios y líneas vacías
                if not line or line.startswith('#'):
                    continue

                # Parsear KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remover comillas si existen
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Setear variable de entorno
                    os.environ[key] = value
                    loaded_vars[key] = value

    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

    return loaded_vars


def get_llm_config_from_env() -> dict:
    """
    Obtiene configuración de LLM desde variables de entorno.

    Returns:
        Config dict para agentes SDLC o None si no hay LLM disponible
    """
    # Cargar .env si existe
    load_env_file()

    # Detectar proveedor disponible
    prefer_provider = os.getenv("PREFER_LLM_PROVIDER", "auto")

    if prefer_provider == "auto":
        # Auto-detectar según API keys disponibles
        if os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
            model = "claude-sonnet-4-5-20250929"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
            model = "gpt-4o"
        elif os.getenv("HF_LOCAL_MODEL_PATH") or os.getenv("HF_MODEL_ID"):
            provider = "huggingface"
            model = os.getenv("HF_LOCAL_MODEL_PATH") or os.getenv("HF_MODEL_ID")
        elif os.getenv("OLLAMA_BASE_URL"):
            provider = "ollama"
            model = "qwen2.5-coder:32b"
        else:
            # No hay LLM disponible, usar heurísticas
            return None

    elif prefer_provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("Warning: ANTHROPIC_API_KEY not found, falling back to heuristics")
            return None
        provider = "anthropic"
        model = "claude-sonnet-4-5-20250929"

    elif prefer_provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY not found, falling back to heuristics")
            return None
        provider = "openai"
        model = "gpt-4o"

    elif prefer_provider == "ollama":
        provider = "ollama"
        model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:32b")

    elif prefer_provider == "huggingface":
        model = os.getenv("HF_LOCAL_MODEL_PATH") or os.getenv("HF_MODEL_ID")
        if not model:
            print("Warning: HF_LOCAL_MODEL_PATH/HF_MODEL_ID not found, heuristics fallback")
            return None
        provider = "huggingface"

    else:
        print(f"Warning: Unknown provider '{prefer_provider}', using heuristics")
        return None

    # Construir config
    config = {
        "llm_provider": provider,
        "model": model,
        "use_llm": True
    }

    # Agregar URL de Ollama si es necesario
    if provider == "ollama":
        config["ollama_base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    if provider == "huggingface":
        if os.getenv("HF_MODEL_ID"):
            config["hf_model_id"] = os.getenv("HF_MODEL_ID")
        generate_kwargs = os.getenv("HF_GENERATE_KWARGS")
        if generate_kwargs:
            try:
                import json
                config["hf_generate_kwargs"] = json.loads(generate_kwargs)
            except Exception:
                print("Warning: No se pudo parsear HF_GENERATE_KWARGS, se ignora")

    return config


def verify_api_keys():
    """Verifica que las API keys estén configuradas correctamente."""
    load_env_file()

    print("\n" + "="*70)
    print("VERIFICACION DE CONFIGURACION LLM")
    print("="*70 + "\n")

    # Verificar Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        masked = f"{anthropic_key[:15]}...{anthropic_key[-4:]}"
        print(f"[OK] ANTHROPIC_API_KEY: {masked}")
    else:
        print("[  ] ANTHROPIC_API_KEY: No configurada")

    # Verificar OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        masked = f"{openai_key[:15]}...{openai_key[-4:]}"
        print(f"[OK] OPENAI_API_KEY: {masked}")
    else:
        print("[  ] OPENAI_API_KEY: No configurada")

    # Verificar Ollama
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    if ollama_url:
        print(f"[OK] OLLAMA_BASE_URL: {ollama_url}")
    else:
        print("[  ] OLLAMA_BASE_URL: No configurada")

    # Configuración de optimización
    print("\n" + "-"*70)
    print("CONFIGURACION DE OPTIMIZACION")
    print("-"*70 + "\n")

    budget = os.getenv("LLM_MONTHLY_BUDGET", "100")
    print(f"Presupuesto mensual: ${budget}")

    optimization = os.getenv("ENABLE_COST_OPTIMIZATION", "false")
    print(f"Optimizacion de costos: {optimization}")

    provider = os.getenv("PREFER_LLM_PROVIDER", "auto")
    print(f"Proveedor preferido: {provider}")

    environment = os.getenv("ENVIRONMENT", "development")
    print(f"Entorno: {environment}")

    # Mostrar config resultante
    print("\n" + "-"*70)
    print("CONFIG AUTO-DETECTADA")
    print("-"*70 + "\n")

    config = get_llm_config_from_env()
    if config:
        print(f"Provider: {config['llm_provider']}")
        print(f"Model: {config['model']}")
        print(f"Use LLM: {config['use_llm']}")
        if 'ollama_base_url' in config:
            print(f"Ollama URL: {config['ollama_base_url']}")
    else:
        print("Config: Heuristicas (sin LLM)")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Ejecutar verificación
    verify_api_keys()
