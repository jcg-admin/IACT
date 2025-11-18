from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import yaml


def load_devcontainer() -> Dict:
    config_path = Path(".devcontainer/devcontainer.json")
    # devcontainer.json uses JSONC with comments, strip them for parsing
    content_lines = []
    for line in config_path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            continue

        # Remove inline JSONC comments while preserving content
        if "//" in line:
            line = line.split("//", 1)[0].rstrip()
            if not line:
                continue

        content_lines.append(line)

    return json.loads("\n".join(content_lines))


def load_compose() -> Dict:
    compose_path = Path(".devcontainer/docker_compose.yml")
    return yaml.safe_load(compose_path.read_text())


def load_env_example(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def test_devcontainer_uses_single_python_interpreter():
    dockerfile = Path(".devcontainer/Dockerfile").read_text()
    devcontainer = load_devcontainer()

    assert "python:3.12" in dockerfile, "Dockerfile base image should match Python 3.12"
    assert "./infrastructure/cpython/installer" not in devcontainer.get("features", {}), (
        "Custom CPython installer should be removed to avoid duplicate runtimes"
    )
    assert devcontainer.get("customizations", {}).get("vscode", {}).get("settings", {}).get(
        "python.defaultInterpreterPath"
    ) == "/usr/local/bin/python3"


def test_compose_uses_env_files_with_examples():
    compose = load_compose()
    env_example_path = Path(".devcontainer/.env.example")

    assert env_example_path.exists(), "DevContainer must provide .env.example"

    env_values = load_env_example(env_example_path)

    for service_name in ("app", "db_postgres", "db_mariadb"):
        service = compose["services"][service_name]
        assert "env_file" in service, f"Service {service_name} should include env_file"
        env_files = service["env_file"]
        assert ".env" in env_files or env_example_path.name in env_files

    expected_keys = {
        "DJANGO_SETTINGS_MODULE",
        "DEBUG",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "MARIADB_HOST",
        "MARIADB_PORT",
        "MARIADB_DATABASE",
        "MARIADB_USER",
        "MARIADB_ROOT_PASSWORD",
        "DJANGO_SUPERUSER_USERNAME",
        "DJANGO_SUPERUSER_EMAIL",
        "DJANGO_SUPERUSER_PASSWORD",
        "TZ",
    }

    missing_keys = sorted(expected_keys - set(env_values))
    assert not missing_keys, f"Missing keys in .env.example: {', '.join(missing_keys)}"
