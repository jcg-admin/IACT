"""
Descubrimiento automático de estructura de proyecto.

Este módulo detecta dinámicamente la estructura del proyecto
sin asumir nombres específicos de dominios o convenciones.
Es portable a cualquier proyecto.
"""

import os
from pathlib import Path
from typing import Dict, List, Set


class ProjectStructureDiscovery:
    """Descubre estructura de proyecto automáticamente."""

    def __init__(self, project_root: str = None):
        """
        Inicializa el descubridor de estructura.

        Args:
            project_root: Ruta raíz del proyecto. Si None, usa el directorio actual.
        """
        if project_root is None:
            # Buscar raíz del proyecto (donde está .git o docs/)
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / ".git").exists() or (current / "docs").exists():
                    project_root = str(current)
                    break
                current = current.parent
            else:
                project_root = str(Path.cwd())

        self.project_root = Path(project_root)
        self.docs_root = self.project_root / "docs"

    def discover_domains(self) -> List[str]:
        """
        Descubre dominios del proyecto escaneando docs/.

        Returns:
            Lista de nombres de dominios encontrados.

        Example:
            >>> discovery = ProjectStructureDiscovery()
            >>> discovery.discover_domains()
            ['backend', 'frontend', 'infraestructura', 'ai']
        """
        if not self.docs_root.exists():
            return []

        # Detectar subdirectorios que parecen dominios
        # (excluir directorios especiales como gobernanza, desarrollo, devops)
        SPECIAL_DIRS = {
            "gobernanza",
            "desarrollo",
            "devops",
            "dora",
            "guias",
            ".git",
            "__pycache__",
        }

        domains = []
        for item in self.docs_root.iterdir():
            if not item.is_dir():
                continue

            # Excluir directorios especiales
            if item.name in SPECIAL_DIRS:
                continue

            # Excluir directorios ocultos
            if item.name.startswith("."):
                continue

            # Verificar que contenga archivos de documentación
            has_docs = any(
                f.suffix in {".md", ".rst", ".txt"}
                for f in item.rglob("*")
                if f.is_file()
            )

            if has_docs:
                domains.append(item.name)

        return sorted(domains)

    def discover_subdirectories(self, domain: str) -> List[str]:
        """
        Descubre subdirectorios estándar de un dominio.

        Args:
            domain: Nombre del dominio

        Returns:
            Lista de subdirectorios encontrados

        Example:
            >>> discovery.discover_subdirectories('backend')
            ['arquitectura', 'requisitos', 'tareas', 'guias']
        """
        domain_path = self.docs_root / domain
        if not domain_path.exists():
            return []

        subdirs = []
        for item in domain_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                subdirs.append(item.name)

        return sorted(subdirs)

    def discover_transversal_areas(self) -> List[str]:
        """
        Descubre áreas transversales (ej: gobernanza).

        Returns:
            Lista de áreas transversales
        """
        POTENTIAL_TRANSVERSAL = {"gobernanza", "desarrollo", "devops", "dora"}

        transversal = []
        if not self.docs_root.exists():
            return transversal

        for item in self.docs_root.iterdir():
            if item.is_dir() and item.name in POTENTIAL_TRANSVERSAL:
                transversal.append(item.name)

        return sorted(transversal)

    def build_structure_map(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Construye mapa completo de estructura del proyecto.

        Returns:
            Diccionario con estructura completa:
            {
                'domains': {
                    'backend': ['arquitectura', 'requisitos', ...],
                    'frontend': [...],
                },
                'transversal': ['gobernanza', ...],
            }
        """
        domains = self.discover_domains()
        domain_map = {}

        for domain in domains:
            subdirs = self.discover_subdirectories(domain)
            domain_map[domain] = subdirs

        transversal = self.discover_transversal_areas()

        return {"domains": domain_map, "transversal": transversal}

    def get_domain_files(
        self, domain: str, extensions: Set[str] = None
    ) -> List[Path]:
        """
        Obtiene todos los archivos de un dominio.

        Args:
            domain: Nombre del dominio
            extensions: Conjunto de extensiones a incluir (ej: {'.md', '.py'})

        Returns:
            Lista de rutas de archivos
        """
        if extensions is None:
            extensions = {".md", ".rst", ".txt"}

        domain_path = self.docs_root / domain
        if not domain_path.exists():
            return []

        files = []
        for ext in extensions:
            files.extend(domain_path.rglob(f"*{ext}"))

        return sorted(files)


def main():
    """Ejemplo de uso del descubridor."""
    discovery = ProjectStructureDiscovery()

    print("Estructura del proyecto:")
    print("=" * 60)

    structure = discovery.build_structure_map()

    print(f"\nDominios encontrados: {len(structure['domains'])}")
    for domain, subdirs in structure["domains"].items():
        print(f"\n  {domain}/")
        for subdir in subdirs[:5]:  # Primeros 5
            print(f"    ├── {subdir}/")
        if len(subdirs) > 5:
            print(f"    └── ... ({len(subdirs) - 5} más)")

    print(f"\nÁreas transversales: {structure['transversal']}")


if __name__ == "__main__":
    main()
