"""
Cargador de configuración para PlacementAgent.

Carga configuración desde archivo JSON (opcional).
Si no existe, usa auto-discovery completo.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class PlacementConfig:
    """Configuración del PlacementAgent."""

    def __init__(self, config_path: str = None):
        """
        Inicializa configuración.

        Args:
            config_path: Ruta al archivo de configuración.
                        Si None, busca en ubicación por defecto.
        """
        self.config_data = {}
        self._load_config(config_path)

    def _find_default_config(self) -> Optional[Path]:
        """
        Busca archivo de configuración en ubicaciones estándar.

        Returns:
            Path al archivo de configuración, o None si no existe.
        """
        # Buscar desde directorio actual hacia arriba
        current = Path(__file__).resolve()

        # Ubicaciones posibles
        search_paths = [
            current.parent / "placement_config.json",
            current.parent.parent / "config" / "placement_config.json",
            current.parent.parent.parent / "config" / "placement_config.json",
        ]

        # Buscar en proyecto raíz
        project_root = current
        while project_root.parent != project_root:
            if (project_root / ".git").exists():
                search_paths.append(
                    project_root
                    / "scripts/coding/ai/config/placement_config.json"
                )
                break
            project_root = project_root.parent

        # Retornar primera que existe
        for path in search_paths:
            if path.exists():
                return path

        return None

    def _load_config(self, config_path: str = None):
        """
        Carga configuración desde archivo JSON.

        Args:
            config_path: Ruta al archivo de configuración
        """
        if config_path is None:
            config_file = self._find_default_config()
        else:
            config_file = Path(config_path)

        if config_file is None or not config_file.exists():
            # No hay config - usar auto-discovery completo
            self.config_data = self._get_default_config()
            return

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self.config_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Error al cargar - usar defaults
            self.config_data = self._get_default_config()

    def _get_default_config(self) -> Dict:
        """
        Retorna configuración por defecto (auto-discovery completo).

        Returns:
            Diccionario con configuración por defecto
        """
        return {
            "version": "1.0.0",
            "project": {"docs_root": "docs"},
            "domains": {
                "auto_discover": True,
                "custom_keywords": {},
            },
            "artifact_types": {
                "auto_discover_from_templates": True,
                "custom_patterns": {},
            },
            "ownership_rules": {
                "always_transversal": ["adr", "plantilla_generica"],
                "always_agent": [
                    "documentacion_agente",
                    "configuracion_agente",
                ],
                "min_domain_keywords_for_detection": 2,
            },
            "locations": {
                "transversal_base": "docs/gobernanza",
                "domain_base": "docs/{domain}",
                "agent_base": "scripts/coding/ai/agents",
                "temp_base": "/tmp",
            },
        }

    def get_custom_keywords(self) -> Dict[str, List[str]]:
        """
        Obtiene keywords personalizadas por dominio.

        Returns:
            Diccionario {dominio: [keywords]}
            Vacío si auto_discover está habilitado.
        """
        if self.config_data.get("domains", {}).get("auto_discover", True):
            return {}

        return self.config_data.get("domains", {}).get("custom_keywords", {})

    def should_auto_discover_domains(self) -> bool:
        """
        Indica si debe usar auto-discovery para dominios.

        Returns:
            True si debe auto-descubrir, False si usa config.
        """
        return self.config_data.get("domains", {}).get("auto_discover", True)

    def get_always_transversal_types(self) -> List[str]:
        """
        Obtiene tipos que siempre son transversales.

        Returns:
            Lista de tipos (ej: ['adr', 'plantilla_generica'])
        """
        return self.config_data.get("ownership_rules", {}).get(
            "always_transversal", ["adr", "plantilla_generica"]
        )

    def get_always_agent_types(self) -> List[str]:
        """
        Obtiene tipos que siempre van a agentes.

        Returns:
            Lista de tipos (ej: ['documentacion_agente'])
        """
        return self.config_data.get("ownership_rules", {}).get(
            "always_agent",
            ["documentacion_agente", "configuracion_agente"],
        )

    def get_min_keywords_for_detection(self) -> int:
        """
        Obtiene umbral mínimo de keywords para detectar dominio.

        Returns:
            Número mínimo de keywords (default: 2)
        """
        return self.config_data.get("ownership_rules", {}).get(
            "min_domain_keywords_for_detection", 2
        )

    def get_location_pattern(self, location_type: str) -> str:
        """
        Obtiene patrón de ubicación.

        Args:
            location_type: Tipo de ubicación
                          ('transversal_base', 'domain_base', etc.)

        Returns:
            Patrón de ubicación
        """
        locations = self.config_data.get("locations", {})
        defaults = {
            "transversal_base": "docs/gobernanza",
            "domain_base": "docs/{domain}",
            "agent_base": "scripts/coding/ai/agents",
            "temp_base": "/tmp",
        }

        return locations.get(location_type, defaults.get(location_type, ""))


def main():
    """Ejemplo de uso del config loader."""
    config = PlacementConfig()

    print("Configuración cargada:")
    print("=" * 60)
    print(f"Auto-discover domains: {config.should_auto_discover_domains()}")
    print(f"Custom keywords: {config.get_custom_keywords()}")
    print(f"Always transversal: {config.get_always_transversal_types()}")
    print(f"Always agent: {config.get_always_agent_types()}")
    print(
        f"Min keywords for detection: {config.get_min_keywords_for_detection()}"
    )


if __name__ == "__main__":
    main()
