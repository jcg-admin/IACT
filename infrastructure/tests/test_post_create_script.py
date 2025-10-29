"""Pruebas de smoke para el script post-create del devcontainer."""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "infrastructure/devcontainer/scripts/post-create.sh"


def test_post_create_instala_copilot_cli_con_validaciones():
    """El script debe validar versiones modernas y publicar la instalación de Copilot CLI."""
    contenido = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "node --version" in contenido, "Se espera la verificación de la versión de Node.js"
    assert "npm --version" in contenido, "Se espera la verificación de la versión de npm"
    assert "Node >=22" in contenido and "npm >=10" in contenido, "Se requiere la validación de versiones mínimas"
    assert "npm install -g @github/copilot" in contenido, "Debe instalar el paquete oficial de Copilot CLI"
    assert "command -v copilot" in contenido, "El script debe verificar que el comando copilot quede disponible"


def test_post_create_ejecuta_pytest_como_smoke_test():
    """El script debe ejecutar pytest con los flags de smoke test para dar visibilidad temprana."""
    contenido = SCRIPT_PATH.read_text(encoding="utf-8")

    assert (
        "python -m pytest --maxfail=1 --disable-warnings -q" in contenido
    ), "Se espera la ejecución automática de pytest en modo no bloqueante"
