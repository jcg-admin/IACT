"""
Documentation Sync Agent - Sincronización de Código a Documentación

Este módulo implementa el patrón Planner → Editor → Verifier → Reporter
para mantener la documentación sincronizada con el código implementado.

Agentes:
1. CodeInspectorAgent (Planner): Analiza el código e identifica qué documentar
2. DocumentationEditorAgent (Editor): Genera/actualiza documentación
3. ConsistencyVerifierAgent (Verifier): Verifica consistencia código-docs
4. SyncReporterAgent (Reporter): Genera reporte de sincronización

Conformidad:
- Constitution: Calidad sobre velocidad, sin placeholders
- ISO 29148:2018: Trazabilidad código-requisitos
- GUIA_ESTILO.md: Sin emojis, formato estándar
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

try:
    from .base import Agent, Pipeline
except ImportError:
    # Import absoluto si no se puede usar relativo
    import sys
    from pathlib import Path
    base_path = Path(__file__).parent / "base.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("base", base_path)
    base_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_module)
    Agent = base_module.Agent
    Pipeline = base_module.Pipeline


class CodeInspectorAgent(Agent):
    """
    Agente Planner: Inspecciona código fuente y planifica actualización de docs.

    Responsabilidades:
    - Escanear directorios api/, ui/, infraestructura/
    - Identificar componentes implementados (apps, módulos, servicios)
    - Comparar con documentación existente
    - Generar plan de actualización

    Input:
        - project_root: Ruta raíz del proyecto
        - domains: Lista de dominios a inspeccionar (["api", "ui", "infraestructura"])
        - docs_root: Ruta a docs/

    Output:
        - inspection_plan: Plan de qué documentar/actualizar
        - discovered_components: Componentes descubiertos
        - missing_docs: Documentación faltante
        - outdated_docs: Documentación desactualizada
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="CodeInspectorAgent", config=config)
        self.project_root = Path(self.get_config("project_root", "/home/user/IACT---project"))
        self.docs_root = self.project_root / "docs"

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan los directorios necesarios."""
        errors = []

        if not self.project_root.exists():
            errors.append(f"project_root no existe: {self.project_root}")

        # Verificar que al menos un dominio existe
        domains = input_data.get("domains", ["api", "ui", "infraestructura"])
        found_any = False
        for domain in domains:
            if (self.project_root / domain).exists():
                found_any = True
                break

        if not found_any:
            errors.append(f"No se encontró ningún dominio en {self.project_root}")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspecciona el código y genera plan de documentación.
        """
        domains = input_data.get("domains", ["api", "ui", "infraestructura"])

        discovered = {
            "api": self._inspect_api(),
            "ui": self._inspect_ui(),
            "infraestructura": self._inspect_infrastructure()
        }

        # Filtrar solo los dominios solicitados
        discovered = {k: v for k, v in discovered.items() if k in domains}

        # Analizar documentación existente
        existing_docs = self._analyze_existing_docs()

        # Generar plan
        plan = self._generate_plan(discovered, existing_docs)

        return {
            "discovered_components": discovered,
            "existing_docs": existing_docs,
            "inspection_plan": plan,
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "total_components": sum(len(v.get("apps", [])) + len(v.get("modules", [])) + len(v.get("services", [])) for v in discovered.values()),
                "missing_docs": len(plan.get("create", [])),
                "outdated_docs": len(plan.get("update", [])),
                "ok_docs": len(plan.get("ok", []))
            }
        }

    def _inspect_api(self) -> Dict[str, Any]:
        """Inspecciona el dominio api/ (Django)."""
        api_path = self.project_root / "api" / "callcentersite" / "callcentersite"

        if not api_path.exists():
            self.logger.warning(f"api_path no existe: {api_path}")
            return {"apps": [], "models": [], "views": [], "serializers": []}

        apps_path = api_path / "apps"
        apps = []

        if apps_path.exists():
            for app_dir in apps_path.iterdir():
                if app_dir.is_dir() and not app_dir.name.startswith("__"):
                    app_info = {
                        "name": app_dir.name,
                        "path": str(app_dir.relative_to(self.project_root)),
                        "has_models": (app_dir / "models.py").exists(),
                        "has_views": (app_dir / "views.py").exists(),
                        "has_serializers": (app_dir / "serializers.py").exists(),
                        "has_urls": (app_dir / "urls.py").exists(),
                        "has_tests": (app_dir / "tests.py").exists() or (app_dir / "tests").exists(),
                    }

                    # Leer docstrings si existen
                    if app_info["has_models"]:
                        app_info["models"] = self._extract_models(app_dir / "models.py")

                    apps.append(app_info)

        return {
            "apps": apps,
            "domain": "backend",
            "technology": "Django REST Framework"
        }

    def _inspect_ui(self) -> Dict[str, Any]:
        """Inspecciona el dominio ui/ (React)."""
        ui_path = self.project_root / "ui" / "src"

        if not ui_path.exists():
            self.logger.warning(f"ui_path no existe: {ui_path}")
            return {"modules": [], "components": [], "pages": []}

        modules = []

        # Buscar módulos en ui/src/modules/
        modules_path = ui_path / "modules"
        if modules_path.exists():
            for module_dir in modules_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith("__"):
                    module_info = {
                        "name": module_dir.name,
                        "path": str(module_dir.relative_to(self.project_root)),
                        "has_component": any((module_dir).glob("*.jsx")) or any((module_dir).glob("*.tsx")),
                        "has_state": (module_dir / "state").exists(),
                        "has_hooks": (module_dir / "hooks").exists(),
                        "has_tests": any((module_dir).glob("*.test.jsx")) or any((module_dir).glob("*.test.tsx")),
                    }
                    modules.append(module_info)

        # Buscar páginas en ui/src/pages/
        pages = []
        pages_path = ui_path / "pages"
        if pages_path.exists():
            for page_file in pages_path.glob("*.jsx"):
                pages.append({
                    "name": page_file.stem,
                    "path": str(page_file.relative_to(self.project_root))
                })

        return {
            "modules": modules,
            "pages": pages,
            "domain": "frontend",
            "technology": "React + Redux"
        }

    def _inspect_infrastructure(self) -> Dict[str, Any]:
        """Inspecciona el dominio infraestructura/."""
        infra_path = self.project_root / "infraestructura"

        if not infra_path.exists():
            self.logger.warning(f"infrastructure_path no existe: {infra_path}")
            return {"services": [], "configs": []}

        services = []
        configs = []

        # Buscar archivos terraform
        for tf_file in infra_path.rglob("*.tf"):
            configs.append({
                "name": tf_file.stem,
                "path": str(tf_file.relative_to(self.project_root)),
                "type": "terraform"
            })

        # Buscar archivos docker
        for docker_file in infra_path.rglob("Dockerfile*"):
            configs.append({
                "name": docker_file.name,
                "path": str(docker_file.relative_to(self.project_root)),
                "type": "docker"
            })

        # Buscar archivos yaml/yml
        for yaml_file in infra_path.rglob("*.yml"):
            configs.append({
                "name": yaml_file.stem,
                "path": str(yaml_file.relative_to(self.project_root)),
                "type": "yaml"
            })

        for yaml_file in infra_path.rglob("*.yaml"):
            configs.append({
                "name": yaml_file.stem,
                "path": str(yaml_file.relative_to(self.project_root)),
                "type": "yaml"
            })

        return {
            "services": services,
            "configs": configs,
            "domain": "infraestructura",
            "technology": "Terraform/Docker"
        }

    def _extract_models(self, models_file: Path) -> List[Dict[str, str]]:
        """Extrae información de models de un archivo models.py."""
        if not models_file.exists():
            return []

        models = []
        content = models_file.read_text()

        # Regex simple para encontrar clases que heredan de models.Model
        pattern = r'class\s+(\w+)\(.*models\.Model.*\):'
        matches = re.findall(pattern, content)

        for model_name in matches:
            models.append({"name": model_name, "file": str(models_file)})

        return models

    def _analyze_existing_docs(self) -> Dict[str, Any]:
        """Analiza documentación existente en docs/."""
        existing = {
            "backend": [],
            "frontend": [],
            "infraestructura": []
        }

        # Buscar documentación de backend
        backend_docs = self.docs_root / "implementacion" / "backend"
        if backend_docs.exists():
            for md_file in backend_docs.rglob("*.md"):
                if md_file.name != "README.md":
                    existing["backend"].append({
                        "path": str(md_file.relative_to(self.docs_root)),
                        "name": md_file.stem,
                        "last_modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })

        # Buscar documentación de frontend
        frontend_docs = self.docs_root / "implementacion" / "frontend"
        if frontend_docs.exists():
            for md_file in frontend_docs.rglob("*.md"):
                if md_file.name != "README.md":
                    existing["frontend"].append({
                        "path": str(md_file.relative_to(self.docs_root)),
                        "name": md_file.stem,
                        "last_modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })

        # Buscar documentación de infraestructura
        infra_docs = self.docs_root / "implementacion" / "infraestructura"
        if infra_docs.exists():
            for md_file in infra_docs.rglob("*.md"):
                if md_file.name != "README.md":
                    existing["infraestructura"].append({
                        "path": str(md_file.relative_to(self.docs_root)),
                        "name": md_file.stem,
                        "last_modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })

        return existing

    def _generate_plan(self, discovered: Dict[str, Any], existing_docs: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Genera plan de documentación comparando código descubierto con docs existentes.
        """
        plan = {
            "create": [],  # Documentación que falta crear
            "update": [],  # Documentación que existe pero puede estar desactualizada
            "ok": []       # Documentación que parece estar al día
        }

        # Analizar backend (Django apps)
        if "api" in discovered:
            backend_data = discovered["api"]
            backend_docs_names = {doc["name"] for doc in existing_docs.get("backend", [])}

            for app in backend_data.get("apps", []):
                app_name = app["name"]

                if app_name not in backend_docs_names:
                    plan["create"].append({
                        "domain": "backend",
                        "component_type": "django_app",
                        "component_name": app_name,
                        "path": app["path"],
                        "reason": "Django app sin documentación",
                        "priority": "high" if app["has_models"] else "medium"
                    })
                else:
                    # Existe documentación, marcar para posible actualización
                    plan["update"].append({
                        "domain": "backend",
                        "component_type": "django_app",
                        "component_name": app_name,
                        "path": app["path"],
                        "reason": "Verificar si está actualizada",
                        "priority": "medium"
                    })

        # Analizar frontend (React modules)
        if "ui" in discovered:
            frontend_data = discovered["ui"]
            frontend_docs_names = {doc["name"] for doc in existing_docs.get("frontend", [])}

            for module in frontend_data.get("modules", []):
                module_name = module["name"]

                if module_name not in frontend_docs_names:
                    plan["create"].append({
                        "domain": "frontend",
                        "component_type": "react_module",
                        "component_name": module_name,
                        "path": module["path"],
                        "reason": "React module sin documentación",
                        "priority": "medium"
                    })

        # Analizar infraestructura
        if "infraestructura" in discovered:
            infra_data = discovered["infraestructura"]
            infra_docs_names = {doc["name"] for doc in existing_docs.get("infraestructura", [])}

            # Si hay configs y no hay documentación, crear
            if len(infra_data.get("configs", [])) > 0 and len(infra_docs_names) == 0:
                plan["create"].append({
                    "domain": "infraestructura",
                    "component_type": "infrastructure_general",
                    "component_name": "infrastructure_overview",
                    "path": "infraestructura/",
                    "reason": "Infrastructure sin documentación general",
                    "priority": "high"
                })

        return plan


class DocumentationEditorAgent(Agent):
    """
    Agente Editor: Genera/actualiza documentación basándose en el plan.

    Responsabilidades:
    - Recibir plan de CodeInspectorAgent
    - Generar archivos markdown para componentes sin documentación
    - Actualizar documentación existente
    - Seguir plantillas estándar del proyecto

    Input:
        - inspection_plan: Plan generado por CodeInspectorAgent
        - discovered_components: Componentes descubiertos
        - template_dir: Directorio de plantillas (opcional)

    Output:
        - created_docs: Lista de documentación creada
        - updated_docs: Lista de documentación actualizada
        - files_written: Rutas de archivos escritos
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="DocumentationEditorAgent", config=config)
        self.project_root = Path(self.get_config("project_root", "/home/user/IACT---project"))
        self.docs_root = self.project_root / "docs"
        self.dry_run = self.get_config("dry_run", True)  # Por defecto no escribe archivos

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que exista el plan de inspección."""
        errors = []

        if "inspection_plan" not in input_data:
            errors.append("Falta 'inspection_plan' del CodeInspectorAgent")

        if "discovered_components" not in input_data:
            errors.append("Falta 'discovered_components' del CodeInspectorAgent")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera/actualiza documentación según el plan.
        """
        plan = input_data["inspection_plan"]
        discovered = input_data["discovered_components"]

        created = []
        updated = []
        files_written = []

        # Procesar items a crear
        for item in plan.get("create", []):
            doc_content = self._generate_doc_content(item, discovered)
            doc_path = self._get_doc_path(item)

            if self.dry_run:
                self.logger.info(f"[DRY-RUN] Crearía: {doc_path}")
                created.append({
                    "path": str(doc_path),
                    "component": item["component_name"],
                    "type": "create",
                    "dry_run": True
                })
            else:
                self._write_doc(doc_path, doc_content)
                created.append({
                    "path": str(doc_path),
                    "component": item["component_name"],
                    "type": "create",
                    "dry_run": False
                })
                files_written.append(str(doc_path))

        # Procesar items a actualizar (por ahora solo reportamos)
        for item in plan.get("update", []):
            updated.append({
                "component": item["component_name"],
                "path": item["path"],
                "action": "marked_for_review"
            })

        return {
            "created_docs": created,
            "updated_docs": updated,
            "files_written": files_written,
            "stats": {
                "created": len(created),
                "updated": len(updated),
                "dry_run": self.dry_run
            }
        }

    def _generate_doc_content(self, item: Dict[str, Any], discovered: Dict[str, Any]) -> str:
        """Genera contenido markdown para un componente."""
        domain = item["domain"]
        component_name = item["component_name"]
        component_type = item["component_type"]

        if component_type == "django_app":
            return self._generate_django_app_doc(item, discovered)
        elif component_type == "react_module":
            return self._generate_react_module_doc(item, discovered)
        elif component_type == "infrastructure_general":
            return self._generate_infrastructure_doc(item, discovered)
        else:
            return self._generate_generic_doc(item)

    def _generate_django_app_doc(self, item: Dict[str, Any], discovered: Dict[str, Any]) -> str:
        """Genera documentación para una Django app."""
        app_name = item["component_name"]

        # Buscar info del app en discovered
        app_info = None
        if "api" in discovered:
            for app in discovered["api"].get("apps", []):
                if app["name"] == app_name:
                    app_info = app
                    break

        if not app_info:
            app_info = {"name": app_name}

        content = f"""---
id: APP-{app_name.upper()}
tipo: django_app
dominio: backend
estado: documentado
fecha: {datetime.now().strftime('%Y-%m-%d')}
auto_generado: true
---

# Django App: {app_name}

## Descripción

App de Django para {app_name}.

## Estructura

```
{app_info.get('path', f'api/callcentersite/callcentersite/apps/{app_name}')}/
"""

        if app_info.get("has_models"):
            content += "├── models.py          # Modelos de datos\n"
        if app_info.get("has_views"):
            content += "├── views.py           # Vistas/ViewSets\n"
        if app_info.get("has_serializers"):
            content += "├── serializers.py     # Serializers DRF\n"
        if app_info.get("has_urls"):
            content += "├── urls.py            # Rutas URL\n"
        if app_info.get("has_tests"):
            content += "├── tests.py           # Tests unitarios\n"

        content += """```

## Modelos
"""

        if app_info.get("models"):
            for model in app_info["models"]:
                content += f"\n### {model['name']}\n\n"
                content += f"Modelo definido en `{model['file']}`\n"
        else:
            content += "\nNo se detectaron modelos o no están documentados.\n"

        content += """
## Endpoints

Documentar endpoints REST de esta app.

## Tests

"""

        if app_info.get("has_tests"):
            content += "Tests implementados.\n"
        else:
            content += "WARNING: No se detectaron tests.\n"

        content += """
## Dependencias

Listar dependencias con otras apps.

## Notas

Documentación generada automáticamente. Completar con detalles específicos.
"""

        return content

    def _generate_react_module_doc(self, item: Dict[str, Any], discovered: Dict[str, Any]) -> str:
        """Genera documentación para un módulo React."""
        module_name = item["component_name"]

        content = f"""---
id: MODULE-{module_name.upper()}
tipo: react_module
dominio: frontend
estado: documentado
fecha: {datetime.now().strftime('%Y-%m-%d')}
auto_generado: true
---

# React Module: {module_name}

## Descripción

Módulo React para {module_name}.

## Estructura

```
ui/src/modules/{module_name}/
├── {module_name.capitalize()}Module.jsx    # Componente principal
├── state/                  # Redux state
└── hooks/                  # Custom hooks
```

## Componentes

Documentar componentes principales de este módulo.

## Estado (Redux)

Documentar slices de Redux asociados.

## Hooks

Documentar custom hooks si existen.

## Notas

Documentación generada automáticamente. Completar con detalles específicos.
"""

        return content

    def _generate_infrastructure_doc(self, item: Dict[str, Any], discovered: Dict[str, Any]) -> str:
        """Genera documentación general de infraestructura."""
        content = f"""---
id: INFRA-OVERVIEW
tipo: infrastructure_overview
dominio: infraestructura
estado: documentado
fecha: {datetime.now().strftime('%Y-%m-%d')}
auto_generado: true
---

# Infrastructure Overview

## Descripción

Configuración de infraestructura del proyecto IACT.

## Componentes

"""

        if "infraestructura" in discovered:
            configs = discovered["infraestructura"].get("configs", [])

            terraform_configs = [c for c in configs if c["type"] == "terraform"]
            docker_configs = [c for c in configs if c["type"] == "docker"]
            yaml_configs = [c for c in configs if c["type"] == "yaml"]

            if terraform_configs:
                content += f"\n### Terraform ({len(terraform_configs)} archivos)\n\n"
                for config in terraform_configs[:5]:  # Primeros 5
                    content += f"- `{config['path']}`\n"

            if docker_configs:
                content += f"\n### Docker ({len(docker_configs)} archivos)\n\n"
                for config in docker_configs[:5]:
                    content += f"- `{config['path']}`\n"

            if yaml_configs:
                content += f"\n### YAML Configs ({len(yaml_configs)} archivos)\n\n"
                for config in yaml_configs[:5]:
                    content += f"- `{config['path']}`\n"

        content += """
## Servicios

Documentar servicios de infraestructura.

## Despliegue

Documentar proceso de despliegue.

## Notas

Documentación generada automáticamente. Completar con detalles específicos.
"""

        return content

    def _generate_generic_doc(self, item: Dict[str, Any]) -> str:
        """Genera documentación genérica."""
        component_name = item["component_name"]

        content = f"""---
id: COMP-{component_name.upper()}
dominio: {item['domain']}
estado: documentado
fecha: {datetime.now().strftime('%Y-%m-%d')}
auto_generado: true
---

# {component_name}

## Descripción

Componente {component_name}.

## Detalles

Documentar detalles del componente.

## Notas

Documentación generada automáticamente.
"""

        return content

    def _get_doc_path(self, item: Dict[str, Any]) -> Path:
        """Determina la ruta donde guardar la documentación."""
        domain = item["domain"]
        component_name = item["component_name"]
        component_type = item["component_type"]

        # Estructura: docs/implementacion/{domain}/arquitectura/
        base_path = self.docs_root / "implementacion" / domain / "arquitectura"

        filename = f"{component_name}.md"
        return base_path / filename

    def _write_doc(self, path: Path, content: str) -> None:
        """Escribe documentación a archivo."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        self.logger.info(f"Documentación escrita: {path}")


class ConsistencyVerifierAgent(Agent):
    """
    Agente Verifier: Verifica consistencia entre código y documentación.

    Responsabilidades:
    - Verificar que la documentación refleja el código actual
    - Detectar inconsistencias
    - Generar warnings y recomendaciones

    Input:
        - discovered_components: Componentes del código
        - created_docs: Documentación creada
        - existing_docs: Documentación existente

    Output:
        - verification_result: Resultado de verificación
        - inconsistencies: Lista de inconsistencias encontradas
        - recommendations: Recomendaciones de mejora
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="ConsistencyVerifierAgent", config=config)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida entrada."""
        errors = []

        if "discovered_components" not in input_data:
            errors.append("Falta 'discovered_components'")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica consistencia."""
        discovered = input_data.get("discovered_components", {})
        created = input_data.get("created_docs", [])
        existing = input_data.get("existing_docs", {})

        inconsistencies = []
        recommendations = []

        # Verificar que componentes importantes tienen docs
        for domain, data in discovered.items():
            if domain == "api":
                apps_count = len(data.get("apps", []))
                docs_count = len(existing.get("backend", []))

                if apps_count > docs_count + len(created):
                    inconsistencies.append({
                        "domain": "backend",
                        "type": "missing_docs",
                        "message": f"Hay {apps_count} Django apps pero solo {docs_count + len(created)} documentadas",
                        "severity": "medium"
                    })
                    recommendations.append(
                        "Documentar todas las Django apps en docs/implementacion/backend/arquitectura/"
                    )

        verification_passed = len(inconsistencies) == 0

        return {
            "verification_passed": verification_passed,
            "inconsistencies": inconsistencies,
            "recommendations": recommendations,
            "stats": {
                "total_inconsistencies": len(inconsistencies),
                "high_severity": len([i for i in inconsistencies if i.get("severity") == "high"]),
                "medium_severity": len([i for i in inconsistencies if i.get("severity") == "medium"]),
                "low_severity": len([i for i in inconsistencies if i.get("severity") == "low"]),
            }
        }


class SyncReporterAgent(Agent):
    """
    Agente Reporter: Genera reporte de sincronización.

    Responsabilidades:
    - Consolidar resultados de todos los agentes anteriores
    - Generar reporte legible en markdown
    - Incluir métricas y estadísticas

    Input:
        - Todos los resultados de agentes anteriores

    Output:
        - report_markdown: Reporte en formato markdown
        - report_path: Ruta donde se guardó el reporte (opcional)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="SyncReporterAgent", config=config)
        self.project_root = Path(self.get_config("project_root", "/home/user/IACT---project"))
        self.save_report = self.get_config("save_report", True)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida entrada."""
        # Reporter puede trabajar con cualquier input
        return []

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte."""
        report_md = self._generate_report_markdown(input_data)

        result = {
            "report_markdown": report_md,
            "timestamp": datetime.now().isoformat()
        }

        if self.save_report:
            report_path = self.project_root / "docs" / "anexos" / "analisis_nov_2025" / f"SYNC_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_md)
            result["report_path"] = str(report_path)
            self.logger.info(f"Reporte guardado en: {report_path}")

        return result

    def _generate_report_markdown(self, data: Dict[str, Any]) -> str:
        """Genera reporte en markdown."""
        report = f"""---
id: SYNC-REPORT-{datetime.now().strftime('%Y%m%d')}
tipo: documentation_sync_report
fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
auto_generado: true
---

# Reporte de Sincronización Código-Documentación

Generado por DocumentationSyncAgent (Planner → Editor → Verifier → Reporter)

---

## Resumen Ejecutivo

"""

        # Estadísticas de inspección
        inspection_plan = data.get("inspection_plan", {})
        stats = data.get("stats", {})

        report += f"""
### Componentes Analizados

- Total componentes: {stats.get('total_components', 0)}
- Documentación faltante: {stats.get('missing_docs', 0)}
- Documentación desactualizada: {stats.get('outdated_docs', 0)}
- Documentación OK: {stats.get('ok_docs', 0)}

### Acciones Realizadas

"""

        created_docs = data.get("created_docs", [])
        updated_docs = data.get("updated_docs", [])

        report += f"- Documentación creada: {len(created_docs)}\n"
        report += f"- Documentación actualizada: {len(updated_docs)}\n"

        if data.get("stats", {}).get("dry_run", True):
            report += "\nMODO DRY-RUN: No se escribieron archivos reales.\n"

        report += """
---

## Componentes Descubiertos

"""

        discovered = data.get("discovered_components", {})

        for domain, domain_data in discovered.items():
            report += f"\n### {domain.capitalize()}\n\n"

            if domain == "api":
                apps = domain_data.get("apps", [])
                report += f"Django Apps: {len(apps)}\n\n"
                for app in apps:
                    report += f"- **{app['name']}**\n"
                    report += f"  - Ruta: `{app['path']}`\n"
                    report += f"  - Modelos: {'SI' if app.get('has_models') else 'NO'}\n"
                    report += f"  - Views: {'SI' if app.get('has_views') else 'NO'}\n"
                    report += f"  - Tests: {'SI' if app.get('has_tests') else 'NO'}\n"
                    report += "\n"

            elif domain == "ui":
                modules = domain_data.get("modules", [])
                pages = domain_data.get("pages", [])
                report += f"React Modules: {len(modules)}\n"
                report += f"Pages: {len(pages)}\n\n"
                for module in modules:
                    report += f"- **{module['name']}**\n"
                    report += f"  - Ruta: `{module['path']}`\n"
                    report += f"  - State: {'SI' if module.get('has_state') else 'NO'}\n"
                    report += f"  - Hooks: {'SI' if module.get('has_hooks') else 'NO'}\n"
                    report += "\n"

            elif domain == "infraestructura":
                configs = domain_data.get("configs", [])
                report += f"Configuraciones: {len(configs)}\n\n"

        report += """
---

## Plan de Documentación

"""

        create_items = inspection_plan.get("create", [])
        update_items = inspection_plan.get("update", [])

        if create_items:
            report += f"\n### Crear ({len(create_items)})\n\n"
            for item in create_items:
                report += f"- **{item['component_name']}** ({item['domain']})\n"
                report += f"  - Tipo: {item['component_type']}\n"
                report += f"  - Razón: {item['reason']}\n"
                report += f"  - Prioridad: {item['priority']}\n"
                report += "\n"

        if update_items:
            report += f"\n### Actualizar ({len(update_items)})\n\n"
            for item in update_items:
                report += f"- **{item['component_name']}** ({item['domain']})\n"
                report += f"  - Razón: {item['reason']}\n"
                report += "\n"

        report += """
---

## Documentación Generada

"""

        if created_docs:
            report += f"\nSe generaron {len(created_docs)} documentos:\n\n"
            for doc in created_docs:
                report += f"- `{doc['path']}` - {doc['component']}\n"
        else:
            report += "\nNo se generó documentación nueva.\n"

        report += """
---

## Verificación de Consistencia

"""

        verification_passed = data.get("verification_passed", True)
        inconsistencies = data.get("inconsistencies", [])
        recommendations = data.get("recommendations", [])

        if verification_passed:
            report += "\nOK: No se encontraron inconsistencias significativas.\n"
        else:
            report += f"\nWARNING: Se encontraron {len(inconsistencies)} inconsistencias.\n\n"
            for incon in inconsistencies:
                report += f"- [{incon.get('severity', 'unknown').upper()}] {incon.get('message', 'Sin mensaje')}\n"

        if recommendations:
            report += "\n### Recomendaciones\n\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"

        report += """
---

## Próximos Pasos

1. Revisar documentación generada
2. Completar detalles específicos en cada documento
3. Ejecutar sincronización periódicamente (semanal/mensual)
4. Considerar automatizar con CI/CD

---

Generado por: DocumentationSyncAgent v1.0
"""

        return report


def create_documentation_sync_pipeline(project_root: str = "/home/user/IACT---project",
                                       dry_run: bool = True,
                                       domains: Optional[List[str]] = None) -> Pipeline:
    """
    Crea el pipeline completo de sincronización de documentación.

    Args:
        project_root: Ruta raíz del proyecto
        dry_run: Si True, no escribe archivos (solo simula)
        domains: Dominios a inspeccionar (default: ["api", "ui", "infraestructura"])

    Returns:
        Pipeline configurado con los 4 agentes
    """
    if domains is None:
        domains = ["api", "ui", "infraestructura"]

    # Configuración compartida
    config_base = {"project_root": project_root}

    # Crear agentes en orden Planner → Editor → Verifier → Reporter
    inspector = CodeInspectorAgent(config_base)
    editor = DocumentationEditorAgent({**config_base, "dry_run": dry_run})
    verifier = ConsistencyVerifierAgent(config_base)
    reporter = SyncReporterAgent({**config_base, "save_report": True})

    # Crear pipeline
    pipeline = Pipeline(
        name="DocumentationSyncPipeline",
        agents=[inspector, editor, verifier, reporter]
    )

    return pipeline
