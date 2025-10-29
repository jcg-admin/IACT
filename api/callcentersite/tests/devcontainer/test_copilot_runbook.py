"""Pruebas sobre la documentación operativa de Copilot CLI."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_PATH = REPO_ROOT / "docs/07-devops/runbooks/github-copilot-codespaces.md"


def test_runbook_incluye_recetario_completo():
    """El runbook debe mantener las secciones documentadas del recetario CLI."""
    contenido = RUNBOOK_PATH.read_text(encoding="utf-8")
    secciones = [
        "### 6.1 Instalación automatizada",
        "### 6.2 Autenticación y validaciones",
        "### 6.3 Arranque rápido del repositorio",
        "### 6.4 Rastreo de issues y priorización",
        "### 6.5 Flujo de implementación asistida",
        "### 6.6 Automatización de entrega",
        "### 6.7 Utilidades de soporte",
        "### 6.8 Extensión con MCP adicionales",
    ]

    for seccion in secciones:
        assert seccion in contenido, f"No se encontró la sección requerida: {seccion}"


def test_runbook_documenta_comandos_clave():
    """El runbook debe listar los comandos esenciales para operar Copilot CLI."""
    contenido = RUNBOOK_PATH.read_text(encoding="utf-8")
    comandos = [
        "npm install -g @github/copilot",
        "/login",
        "Explain the layout of this project.",
        "Make sure my environment is ready to build this project.",
        "Find good first issues in this repository and rank them by difficulty.",
        "Start implementing issue #1234. Show me the diff before applying.",
        "Stage changes, write a commit referencing #1234, and open a draft PR.",
        "What process is using port 8080? Kill it and verify the port is free.",
        "/mcp add",
    ]

    for comando in comandos:
        assert comando in contenido, f"No se encontró el comando documentado: {comando}"
