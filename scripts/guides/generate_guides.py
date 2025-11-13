#!/usr/bin/env python3
"""
Documentation Guide Generator para el proyecto IACT.

Genera guías operativas automáticamente basándose en:
- Workflows CI/CD
- Scripts de automatización
- Agentes SDLC
- Fases del proceso SDLC
- Templates y procedimientos

Uso:
    python scripts/generate_guides.py --priority P0
    python scripts/generate_guides.py --category onboarding
    python scripts/generate_guides.py --all
    python scripts/generate_guides.py --dry-run
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re


class GuideMetadata:
    """Metadata para una guía."""

    def __init__(
        self,
        id: str,
        titulo: str,
        categoria: str,
        audiencia: str,
        prioridad: str,
        tiempo_lectura: int,
        descripcion: str,
        pasos: List[Dict],
        prerequisitos: List[str],
        validaciones: List[str],
        troubleshooting: List[Dict],
        proximos_pasos: List[str],
        referencias: Dict[str, str],
        mantenedores: List[str]
    ):
        self.id = id
        self.titulo = titulo
        self.categoria = categoria
        self.audiencia = audiencia
        self.prioridad = prioridad
        self.tiempo_lectura = tiempo_lectura
        self.descripcion = descripcion
        self.pasos = pasos
        self.prerequisitos = prerequisitos
        self.validaciones = validaciones
        self.troubleshooting = troubleshooting
        self.proximos_pasos = proximos_pasos
        self.referencias = referencias
        self.mantenedores = mantenedores


class DocumentationGuideGenerator:
    """Generador automático de guías de documentación."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        """
        Inicializa el generador.

        Args:
            project_root: Raíz del proyecto
            dry_run: Si True, no escribe archivos
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.template_path = project_root / "docs" / "plantillas" / "guia-template.md"
        self.output_dir = project_root / "docs" / "guias"

        # Estadísticas
        self.guides_generated = 0
        self.guides_skipped = 0

    def load_template(self) -> str:
        """Carga la plantilla de guía."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template no encontrado: {self.template_path}")

        return self.template_path.read_text(encoding='utf-8')

    def generate_guide(self, metadata: GuideMetadata) -> str:
        """
        Genera una guía a partir de metadata.

        Args:
            metadata: Metadata de la guía

        Returns:
            Contenido de la guía en markdown
        """
        template = self.load_template()

        # Generar secciones
        prerequisitos_md = "\n".join(f"- [ ] {p}" for p in metadata.prerequisitos)

        pasos_md = ""
        for i, paso in enumerate(metadata.pasos, 1):
            pasos_md += f"""### {i}. {paso['titulo']}

{paso['descripcion']}

**Comando**:
```bash
{paso.get('comando', '# No requiere comando')}
```

**Output esperado**:
```
{paso.get('output', 'Comando ejecutado exitosamente')}
```

"""

        validaciones_md = "\n".join(f"- [ ] {v}" for v in metadata.validaciones)

        troubleshooting_md = ""
        for i, error in enumerate(metadata.troubleshooting, 1):
            troubleshooting_md += f"""### Error {i}: {error['titulo']}

**Sintomas**:
```
{error['sintomas']}
```

**Causa**: {error['causa']}

**Solucion**:
```bash
{error['solucion']}
```

"""

        proximos_pasos_md = "\n".join(f"{i}. {p}" for i, p in enumerate(metadata.proximos_pasos, 1))

        referencias_md = "\n".join(f"- {k}: `{v}`" for k, v in metadata.referencias.items())

        mantenedores_md = ", ".join(f"@{m}" for m in metadata.mantenedores)

        # Reemplazar placeholders
        content = template.replace("{CATEGORIA}", metadata.categoria)
        content = content.replace("{NUMERO}", metadata.id.split("-")[-1])
        content = content.replace("{AUDIENCIA}", metadata.audiencia)
        content = content.replace("{PRIORIDAD}", metadata.prioridad)
        content = content.replace("{MINUTOS}", str(metadata.tiempo_lectura))
        content = content.replace("{FECHA}", datetime.now().strftime("%Y-%m-%d"))
        content = content.replace("{TITULO}", metadata.titulo)
        content = content.replace("{DESCRIPCION_BREVE}", metadata.descripcion)
        content = content.replace("{AUDIENCIA_DETALLADA}", metadata.audiencia)
        content = content.replace("{TIEMPO_EJECUCION}", str(metadata.tiempo_lectura * 2))
        content = content.replace("{MANTENEDORES}", mantenedores_md)

        # Reemplazar secciones completas
        content = re.sub(r'- \[ \] Pre-requisito.*?\n\n', prerequisitos_md + "\n\n", content, flags=re.DOTALL)
        content = re.sub(r'### 1\. \{PASO_1.*?### 3\. \{PASO_3.*?\n\n', pasos_md, content, flags=re.DOTALL)
        content = re.sub(r'- \[ \] Validacion.*?\n\n', validaciones_md + "\n\n", content, flags=re.DOTALL)
        content = re.sub(r'### Error 1:.*?### Error 2:.*?\n\n', troubleshooting_md, content, flags=re.DOTALL)
        content = re.sub(r'1\. \{SIGUIENTE_GUIA.*?3\. \{SIGUIENTE.*?\n\n', proximos_pasos_md + "\n\n", content, flags=re.DOTALL)
        content = re.sub(r'- Documentacion tecnica:.*?- Mas informacion:.*?\n\n', referencias_md + "\n\n", content, flags=re.DOTALL)

        # Limpiar placeholders restantes
        placeholders = ['{OWNER}', '{PATH_DOCS_TECNICA}', '{PATH_SCRIPT}', '{PATH_INFO_ADICIONAL}']
        for placeholder in placeholders:
            content = content.replace(placeholder, "TBD")

        return content

    def save_guide(self, metadata: GuideMetadata, content: str) -> Path:
        """
        Guarda una guía en disco.

        Args:
            metadata: Metadata de la guía
            content: Contenido de la guía

        Returns:
            Path donde se guardó la guía
        """
        # Determinar directorio de categoría
        category_dir = self.output_dir / metadata.categoria
        category_dir.mkdir(parents=True, exist_ok=True)

        # Generar nombre de archivo
        filename = f"{metadata.id.lower().replace('guia-', '').replace('-', '_')}.md"
        output_path = category_dir / filename

        if self.dry_run:
            print(f"[DRY-RUN] Guardaría guía en: {output_path}")
            self.guides_generated += 1
            return output_path

        # Escribir archivo
        output_path.write_text(content, encoding='utf-8')
        print(f"Generada: {output_path}")
        self.guides_generated += 1

        return output_path

    def get_p0_guides_metadata(self) -> List[GuideMetadata]:
        """
        Define las 20 guías P0 prioritarias para onboarding.

        Returns:
            Lista de metadata de guías P0
        """
        guides = []

        # ONBOARDING (7 guías)
        guides.append(GuideMetadata(
            id="GUIA-ONBOARDING-001",
            titulo="Configurar Entorno de Desarrollo Local",
            categoria="onboarding",
            audiencia="desarrollador-nuevo",
            prioridad="P0",
            tiempo_lectura=15,
            descripcion="Aprende a configurar tu entorno de desarrollo local para trabajar en el proyecto IACT.",
            pasos=[
                {
                    "titulo": "Verificar requisitos del sistema",
                    "descripcion": "Antes de comenzar, verifica que tu sistema cumple con los requisitos mínimos.",
                    "comando": "python --version && node --version && git --version",
                    "output": "Python 3.11+, Node.js 18+, Git 2.x"
                },
                {
                    "titulo": "Clonar el repositorio",
                    "descripcion": "Clona el repositorio del proyecto en tu máquina local.",
                    "comando": "git clone https://github.com/2-Coatl/IACT---project.git\ncd IACT---project",
                    "output": "Repositorio clonado exitosamente"
                },
                {
                    "titulo": "Configurar variables de entorno",
                    "descripcion": "Copia el archivo .env.example y configura las variables necesarias.",
                    "comando": "cp .env.example .env\n# Edita .env con tus valores",
                    "output": "Archivo .env creado"
                },
                {
                    "titulo": "Instalar dependencias backend",
                    "descripcion": "Instala las dependencias de Python para el backend Django.",
                    "comando": "cd api\npip install -r requirements.txt",
                    "output": "Dependencias instaladas correctamente"
                },
                {
                    "titulo": "Instalar dependencias frontend",
                    "descripcion": "Instala las dependencias de Node.js para el frontend React.",
                    "comando": "cd frontend\nnpm install",
                    "output": "Dependencias instaladas correctamente"
                }
            ],
            prerequisitos=[
                "Python 3.11 o superior instalado",
                "Node.js 18 o superior instalado",
                "Git instalado y configurado",
                "Cuenta de GitHub con acceso al repositorio",
                "Editor de código (VS Code recomendado)"
            ],
            validaciones=[
                "python --version muestra 3.11+",
                "node --version muestra 18+",
                "git status funciona sin errores",
                "Archivo .env existe y tiene valores configurados",
                "pip list muestra django instalado"
            ],
            troubleshooting=[
                {
                    "titulo": "Error de permisos al clonar repositorio",
                    "sintomas": "Permission denied (publickey)",
                    "causa": "SSH key no configurada en GitHub",
                    "solucion": "Configura tu SSH key: ssh-keygen -t ed25519 -C 'tu@email.com'\ncat ~/.ssh/id_ed25519.pub  # Agregar a GitHub"
                },
                {
                    "titulo": "Versión de Python incorrecta",
                    "sintomas": "Python 2.x o 3.x < 3.11",
                    "causa": "Sistema usa versión antigua de Python",
                    "solucion": "Instala Python 3.11+ desde python.org o usa pyenv:\npyenv install 3.11.0\npyenv local 3.11.0"
                }
            ],
            proximos_pasos=[
                "Ejecutar tests localmente (Ver guía GUIA-TESTING-001)",
                "Crear tu primer feature branch (Ver guía GUIA-WORKFLOWS-001)",
                "Ejecutar el proyecto localmente (Ver guía GUIA-ONBOARDING-002)"
            ],
            referencias={
                "Procedimiento completo": "docs/gobernanza/procesos/procedimientos/procedimiento_instalacion_entorno.md",
                "Requisitos del sistema": "README.md",
                "Troubleshooting avanzado": "docs/guias/troubleshooting/01-problemas-comunes-setup.md"
            },
            mantenedores=["tech-lead", "devops-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-ONBOARDING-002",
            titulo="Ejecutar Proyecto Localmente",
            categoria="onboarding",
            audiencia="desarrollador-nuevo",
            prioridad="P0",
            tiempo_lectura=10,
            descripcion="Aprende a ejecutar el proyecto completo (backend + frontend) en tu entorno local.",
            pasos=[
                {
                    "titulo": "Iniciar base de datos",
                    "descripcion": "Inicia MySQL o PostgreSQL localmente (según tu configuración).",
                    "comando": "# Opción 1: Docker\ndocker-compose up -d mysql\n\n# Opción 2: Servicio local\nsudo systemctl start mysql",
                    "output": "Base de datos iniciada"
                },
                {
                    "titulo": "Aplicar migraciones",
                    "descripcion": "Aplica las migraciones de Django para crear el esquema de BD.",
                    "comando": "cd api\npython manage.py migrate",
                    "output": "Migraciones aplicadas correctamente"
                },
                {
                    "titulo": "Iniciar servidor backend",
                    "descripcion": "Inicia el servidor de desarrollo Django.",
                    "comando": "python manage.py runserver 8000",
                    "output": "Starting development server at http://127.0.0.1:8000/"
                },
                {
                    "titulo": "Iniciar servidor frontend",
                    "descripcion": "En otra terminal, inicia el servidor de desarrollo React.",
                    "comando": "cd frontend\nnpm run dev",
                    "output": "Server running at http://localhost:3000"
                },
                {
                    "titulo": "Verificar funcionamiento",
                    "descripcion": "Abre tu navegador y verifica que todo funcione.",
                    "comando": "# Abre en navegador:\n# http://localhost:3000 (Frontend)\n# http://localhost:8000/admin (Backend Admin)",
                    "output": "Aplicación corriendo correctamente"
                }
            ],
            prerequisitos=[
                "Entorno de desarrollo configurado (Ver GUIA-ONBOARDING-001)",
                "Base de datos MySQL o PostgreSQL instalada",
                "Puertos 3000 y 8000 disponibles"
            ],
            validaciones=[
                "Backend responde en http://localhost:8000/admin",
                "Frontend carga en http://localhost:3000",
                "No hay errores en consola de navegador",
                "Logs de servidor no muestran errores críticos"
            ],
            troubleshooting=[
                {
                    "titulo": "Error de conexión a base de datos",
                    "sintomas": "django.db.utils.OperationalError: Can't connect",
                    "causa": "Base de datos no está corriendo o credenciales incorrectas",
                    "solucion": "Verifica que la BD esté corriendo:\ndocker-compose ps\n# Verifica credenciales en .env"
                },
                {
                    "titulo": "Puerto 8000 ya en uso",
                    "sintomas": "Error: That port is already in use",
                    "causa": "Otro proceso usa el puerto 8000",
                    "solucion": "Mata el proceso o usa otro puerto:\nlsof -ti:8000 | xargs kill -9\n# O usa otro puerto:\npython manage.py runserver 8001"
                }
            ],
            proximos_pasos=[
                "Ejecutar tests (Ver GUIA-TESTING-001)",
                "Crear feature branch (Ver GUIA-WORKFLOWS-001)",
                "Hacer primer commit (Ver GUIA-WORKFLOWS-002)"
            ],
            referencias={
                "Documentación Django": "https://docs.djangoproject.com/",
                "Documentación React": "https://react.dev/",
                "Procedimiento desarrollo local": "docs/gobernanza/procesos/procedimientos/procedimiento_desarrollo_local.md"
            },
            mantenedores=["tech-lead", "backend-lead", "frontend-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-ONBOARDING-003",
            titulo="Estructura del Proyecto IACT",
            categoria="onboarding",
            audiencia="desarrollador-nuevo",
            prioridad="P0",
            tiempo_lectura=8,
            descripcion="Entiende la estructura de directorios y organización del código del proyecto IACT.",
            pasos=[
                {
                    "titulo": "Explorar directorio raíz",
                    "descripcion": "Familiarízate con los directorios principales del proyecto.",
                    "comando": "ls -la",
                    "output": "api/, frontend/, docs/, scripts/, infraestructura/, .github/"
                },
                {
                    "titulo": "Revisar backend (api/)",
                    "descripcion": "El backend Django está en el directorio api/.",
                    "comando": "tree api/ -L 2 -d",
                    "output": "api/\n├── apps/\n├── core/\n├── config/\n└── tests/"
                },
                {
                    "titulo": "Revisar frontend (frontend/)",
                    "descripcion": "El frontend React está en el directorio frontend/.",
                    "comando": "tree frontend/src -L 2 -d",
                    "output": "frontend/src/\n├── components/\n├── pages/\n├── hooks/\n└── utils/"
                },
                {
                    "titulo": "Revisar documentación (docs/)",
                    "descripcion": "Toda la documentación está organizada en docs/.",
                    "comando": "ls docs/",
                    "output": "arquitectura/, gobernanza/, requisitos/, adr/, guias/"
                }
            ],
            prerequisitos=[
                "Repositorio clonado localmente",
                "Familiaridad básica con terminal"
            ],
            validaciones=[
                "Entiendes qué contiene cada directorio principal",
                "Sabes dónde encontrar el código backend",
                "Sabes dónde encontrar el código frontend",
                "Sabes dónde encontrar la documentación"
            ],
            troubleshooting=[
                {
                    "titulo": "No encuentro un archivo específico",
                    "sintomas": "Buscando un archivo y no lo encuentro",
                    "causa": "No sabes en qué directorio buscar",
                    "solucion": "Usa find para buscar:\nfind . -name 'nombre_archivo.py'\n# O usa grep para buscar contenido:\ngrep -r 'texto_a_buscar' ."
                }
            ],
            proximos_pasos=[
                "Revisar arquitectura del sistema (docs/arquitectura/)",
                "Leer ADRs importantes (docs/adr/)",
                "Entender flujo de desarrollo (Ver GUIA-WORKFLOWS-001)"
            ],
            referencias={
                "Arquitectura del sistema": "docs/arquitectura/",
                "ADRs": "docs/adr/",
                "README principal": "README.md"
            },
            mantenedores=["arquitecto-senior", "tech-lead"]
        ))

        # WORKFLOWS (4 guías)
        guides.append(GuideMetadata(
            id="GUIA-WORKFLOWS-001",
            titulo="Crear Feature Branch",
            categoria="workflows",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=5,
            descripcion="Aprende a crear un feature branch siguiendo las convenciones del proyecto.",
            pasos=[
                {
                    "titulo": "Actualizar rama principal",
                    "descripcion": "Asegúrate de tener la última versión de develop.",
                    "comando": "git checkout develop\ngit pull origin develop",
                    "output": "Already up to date."
                },
                {
                    "titulo": "Crear feature branch",
                    "descripcion": "Crea tu branch con el formato correcto: feature/TASK-XXX-descripcion.",
                    "comando": "git checkout -b feature/TASK-123-agregar-autenticacion",
                    "output": "Switched to a new branch 'feature/TASK-123-agregar-autenticacion'"
                },
                {
                    "titulo": "Verificar branch activo",
                    "descripcion": "Verifica que estás en el branch correcto.",
                    "comando": "git branch",
                    "output": "* feature/TASK-123-agregar-autenticacion\n  develop\n  main"
                }
            ],
            prerequisitos=[
                "Git configurado correctamente",
                "Repositorio clonado",
                "Acceso al repositorio remoto"
            ],
            validaciones=[
                "git branch muestra tu nuevo branch con asterisco",
                "Branch sigue convención feature/TASK-XXX-descripcion",
                "Estás partiendo desde develop actualizado"
            ],
            troubleshooting=[
                {
                    "titulo": "Error al hacer pull",
                    "sintomas": "error: Your local changes would be overwritten",
                    "causa": "Tienes cambios sin commitear en develop",
                    "solucion": "Guarda tus cambios primero:\ngit stash\ngit pull origin develop\ngit stash pop"
                }
            ],
            proximos_pasos=[
                "Hacer commits convencionales (Ver GUIA-WORKFLOWS-002)",
                "Crear Pull Request (Ver GUIA-WORKFLOWS-003)"
            ],
            referencias={
                "Git workflow": "docs/gobernanza/procesos/SDLC_PROCESS.md",
                "Convenciones de nombres": "docs/gobernanza/CONTRIBUTING.md"
            },
            mantenedores=["tech-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-WORKFLOWS-002",
            titulo="Hacer Commits Convencionales",
            categoria="workflows",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=7,
            descripcion="Aprende a escribir commits siguiendo Conventional Commits para mantener un historial limpio.",
            pasos=[
                {
                    "titulo": "Entender formato de commit",
                    "descripcion": "Los commits deben seguir el formato: tipo(scope): mensaje.",
                    "comando": "# Formato:\n# tipo(scope): mensaje\n# \n# Tipos: feat, fix, docs, style, refactor, test, chore\n# Ejemplo:\n# feat(auth): agregar login con OAuth2",
                    "output": "Formato aprendido"
                },
                {
                    "titulo": "Hacer commit de feature",
                    "descripcion": "Usa 'feat' para nuevas funcionalidades.",
                    "comando": "git add .\ngit commit -m \"feat(auth): agregar sistema de autenticacion OAuth2\"",
                    "output": "Commit creado correctamente"
                },
                {
                    "titulo": "Hacer commit de bugfix",
                    "descripcion": "Usa 'fix' para correcciones de bugs.",
                    "comando": "git commit -m \"fix(api): corregir error 500 en endpoint /users\"",
                    "output": "Commit creado correctamente"
                },
                {
                    "titulo": "Verificar historial",
                    "descripcion": "Verifica que tu commit sigue las convenciones.",
                    "comando": "git log --oneline -5",
                    "output": "Lista de commits con formato correcto"
                }
            ],
            prerequisitos=[
                "Feature branch creado (Ver GUIA-WORKFLOWS-001)",
                "Cambios listos para commitear"
            ],
            validaciones=[
                "Commits siguen formato tipo(scope): mensaje",
                "Tipo de commit es correcto (feat, fix, docs, etc)",
                "Mensaje es claro y descriptivo",
                "git log muestra commits bien formateados"
            ],
            troubleshooting=[
                {
                    "titulo": "Pre-commit hook rechaza commit",
                    "sintomas": "Commit rejected: invalid format",
                    "causa": "Mensaje de commit no sigue convenciones",
                    "solucion": "Reescribe el commit:\ngit commit --amend -m \"feat(scope): mensaje correcto\""
                }
            ],
            proximos_pasos=[
                "Crear Pull Request (Ver GUIA-WORKFLOWS-003)",
                "Entender CI/CD (Ver GUIA-WORKFLOWS-004)"
            ],
            referencias={
                "Conventional Commits": "https://www.conventionalcommits.org/",
                "Guía de contribución": "CONTRIBUTING.md"
            },
            mantenedores=["tech-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-WORKFLOWS-003",
            titulo="Crear Pull Request",
            categoria="workflows",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=10,
            descripcion="Aprende a crear un Pull Request que pase todos los checks de CI/CD y sea fácil de revisar.",
            pasos=[
                {
                    "titulo": "Push de tu branch",
                    "descripcion": "Sube tus cambios al repositorio remoto.",
                    "comando": "git push origin feature/TASK-123-descripcion",
                    "output": "Branch pushed to remote"
                },
                {
                    "titulo": "Crear PR desde GitHub",
                    "descripcion": "Ve a GitHub y crea el Pull Request.",
                    "comando": "# Abre: https://github.com/2-Coatl/IACT---project/pulls\n# Click en 'New Pull Request'\n# Selecciona tu branch",
                    "output": "PR creado"
                },
                {
                    "titulo": "Completar template de PR",
                    "descripcion": "Llena el template con toda la información requerida.",
                    "comando": "# Completa:\n# - Descripción del cambio\n# - Issues relacionados (#123)\n# - Checklist de testing\n# - Screenshots si aplica",
                    "output": "Template completado"
                },
                {
                    "titulo": "Esperar checks de CI",
                    "descripcion": "Espera a que pasen todos los checks automáticos.",
                    "comando": "# GitHub Actions ejecutará:\n# - Linting\n# - Tests\n# - Build\n# - Security scans",
                    "output": "All checks passed"
                }
            ],
            prerequisitos=[
                "Feature branch con commits (Ver GUIA-WORKFLOWS-002)",
                "Tests pasando localmente (Ver GUIA-TESTING-001)",
                "Cambios pusheados a remote"
            ],
            validaciones=[
                "PR tiene título descriptivo",
                "Template está completamente llenado",
                "Todos los checks de CI pasan",
                "PR está asignado a reviewers",
                "Labels correctos aplicados (feature, bug, etc)"
            ],
            troubleshooting=[
                {
                    "titulo": "CI falla en linting",
                    "sintomas": "Lint check failed",
                    "causa": "Código no cumple estándares de estilo",
                    "solucion": "Ejecuta linter localmente y corrige:\ncd api && flake8 .\ncd frontend && npm run lint"
                },
                {
                    "titulo": "Tests fallan en CI",
                    "sintomas": "Test check failed",
                    "causa": "Tests no pasan en entorno CI",
                    "solucion": "Ejecuta tests localmente:\n./scripts/ci/backend_test.sh\n./scripts/ci/frontend_test.sh"
                }
            ],
            proximos_pasos=[
                "Interpretar resultados de CI/CD (Ver GUIA-WORKFLOWS-004)",
                "Incorporar feedback de code review",
                "Merge y deployment (Ver GUIA-DEPLOYMENT-001)"
            ],
            referencias={
                "Template de PR": ".github/pull_request_template.md",
                "Workflow de CI": ".github/workflows/backend-ci.yml",
                "Proceso de code review": "docs/gobernanza/procesos/SDLC_PROCESS.md"
            },
            mantenedores=["tech-lead", "qa-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-WORKFLOWS-004",
            titulo="Interpretar Resultados de CI/CD",
            categoria="workflows",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=8,
            descripcion="Aprende a interpretar los resultados de los workflows de CI/CD y solucionar problemas comunes.",
            pasos=[
                {
                    "titulo": "Acceder a GitHub Actions",
                    "descripcion": "Navega a la pestaña Actions de GitHub para ver los workflows.",
                    "comando": "# Abre: https://github.com/2-Coatl/IACT---project/actions",
                    "output": "Lista de workflow runs"
                },
                {
                    "titulo": "Identificar workflow fallido",
                    "descripcion": "Identifica qué workflow falló y en qué job.",
                    "comando": "# Click en el run fallido\n# Identifica el job con X roja\n# Click en el job para ver logs",
                    "output": "Logs del job fallido"
                },
                {
                    "titulo": "Analizar logs de error",
                    "descripcion": "Lee los logs para entender la causa del fallo.",
                    "comando": "# Busca líneas con ERROR o FAILED\n# Lee el stack trace completo\n# Identifica el archivo y línea del error",
                    "output": "Causa del error identificada"
                },
                {
                    "titulo": "Reproducir error localmente",
                    "descripcion": "Intenta reproducir el error en tu máquina local.",
                    "comando": "./scripts/ci/backend_test.sh\n# O el script correspondiente al workflow que falló",
                    "output": "Error reproducido localmente"
                }
            ],
            prerequisitos=[
                "PR creado (Ver GUIA-WORKFLOWS-003)",
                "Acceso a GitHub Actions"
            ],
            validaciones=[
                "Sabes navegar a GitHub Actions",
                "Puedes identificar qué job falló",
                "Entiendes cómo leer logs de CI",
                "Puedes reproducir errores localmente"
            ],
            troubleshooting=[
                {
                    "titulo": "No puedo ver logs de Actions",
                    "sintomas": "Actions tab vacío o sin permisos",
                    "causa": "Falta de permisos en repositorio",
                    "solucion": "Solicita permisos al admin del repo"
                },
                {
                    "titulo": "Error solo ocurre en CI, no localmente",
                    "sintomas": "Tests pasan local pero fallan en CI",
                    "causa": "Diferencias de entorno (Python version, DB, etc)",
                    "solucion": "Verifica versiones:\n# En CI se usa Python 3.11, MySQL 8.0\n# Asegúrate de usar las mismas versiones localmente"
                }
            ],
            proximos_pasos=[
                "Corregir errores y push nuevo commit",
                "Validar que CI pase antes de pedir review",
                "Entender test pyramid (Ver GUIA-TESTING-003)"
            ],
            referencias={
                "GitHub Actions docs": "https://docs.github.com/actions",
                "Workflows del proyecto": ".github/workflows/",
                "Scripts de CI": "scripts/ci/"
            },
            mantenedores=["devops-lead", "tech-lead"]
        ))

        # TESTING (3 guías)
        guides.append(GuideMetadata(
            id="GUIA-TESTING-001",
            titulo="Ejecutar Tests Backend Localmente",
            categoria="testing",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=8,
            descripcion="Aprende a ejecutar la suite completa de tests del backend Django en tu entorno local.",
            pasos=[
                {
                    "titulo": "Preparar entorno de tests",
                    "descripcion": "Asegúrate de tener las dependencias de testing instaladas.",
                    "comando": "cd api\npip install -r requirements.txt",
                    "output": "Dependencias instaladas"
                },
                {
                    "titulo": "Ejecutar todos los tests",
                    "descripcion": "Ejecuta la suite completa de tests con pytest.",
                    "comando": "pytest",
                    "output": "===== XX passed in X.XXs ====="
                },
                {
                    "titulo": "Ejecutar tests con coverage",
                    "descripcion": "Ejecuta tests y genera reporte de cobertura.",
                    "comando": "pytest --cov=. --cov-report=html --cov-report=term",
                    "output": "Coverage: 85%"
                },
                {
                    "titulo": "Ejecutar tests de un módulo específico",
                    "descripcion": "Ejecuta solo los tests de un módulo particular.",
                    "comando": "pytest tests/test_authentication.py -v",
                    "output": "Tests del módulo ejecutados"
                }
            ],
            prerequisitos=[
                "Backend configurado (Ver GUIA-ONBOARDING-001)",
                "Base de datos de test configurada",
                "pytest instalado"
            ],
            validaciones=[
                "pytest ejecuta sin errores",
                "Coverage es >= 80%",
                "Todos los tests pasan",
                "Reporte HTML generado en htmlcov/"
            ],
            troubleshooting=[
                {
                    "titulo": "ImportError al ejecutar tests",
                    "sintomas": "ModuleNotFoundError: No module named 'X'",
                    "causa": "Dependencia faltante o PYTHONPATH incorrecto",
                    "solucion": "Reinstala dependencias:\npip install -r requirements.txt\n# O configura PYTHONPATH:\nexport PYTHONPATH=$PYTHONPATH:$(pwd)"
                },
                {
                    "titulo": "Tests fallan por base de datos",
                    "sintomas": "django.db.utils.OperationalError",
                    "causa": "Base de datos de test no configurada",
                    "solucion": "Configura TEST_DATABASE en settings:\n# Django crea automáticamente test_<database>\n# Asegúrate de tener permisos para crear BD"
                }
            ],
            proximos_pasos=[
                "Ejecutar tests frontend (Ver GUIA-TESTING-002)",
                "Validar test pyramid (Ver GUIA-TESTING-003)",
                "Escribir nuevos tests"
            ],
            referencias={
                "Pytest docs": "https://docs.pytest.org/",
                "Script CI backend": "scripts/ci/backend_test.sh",
                "Coverage config": "pytest.ini"
            },
            mantenedores=["qa-lead", "backend-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-TESTING-002",
            titulo="Ejecutar Tests Frontend Localmente",
            categoria="testing",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=8,
            descripcion="Aprende a ejecutar tests unitarios, de integración y E2E del frontend React.",
            pasos=[
                {
                    "titulo": "Ejecutar tests unitarios",
                    "descripcion": "Ejecuta tests unitarios con Jest.",
                    "comando": "cd frontend\nnpm run test:unit",
                    "output": "Tests passed"
                },
                {
                    "titulo": "Ejecutar tests con coverage",
                    "descripcion": "Genera reporte de cobertura de código.",
                    "comando": "npm run test:coverage",
                    "output": "Coverage: 85%"
                },
                {
                    "titulo": "Ejecutar tests E2E",
                    "descripcion": "Ejecuta tests end-to-end con Cypress/Playwright.",
                    "comando": "npm run test:e2e",
                    "output": "E2E tests passed"
                },
                {
                    "titulo": "Ejecutar tests en modo watch",
                    "descripcion": "Ejecuta tests en modo watch para desarrollo.",
                    "comando": "npm run test:watch",
                    "output": "Watching for file changes..."
                }
            ],
            prerequisitos=[
                "Frontend configurado (Ver GUIA-ONBOARDING-001)",
                "Node modules instalados",
                "Backend corriendo para tests E2E"
            ],
            validaciones=[
                "Tests unitarios pasan",
                "Coverage >= 80%",
                "Tests E2E pasan",
                "No hay warnings en consola"
            ],
            troubleshooting=[
                {
                    "titulo": "Tests E2E fallan por timeout",
                    "sintomas": "Timeout waiting for element",
                    "causa": "Backend no está corriendo o es lento",
                    "solucion": "Inicia backend primero:\ncd api && python manage.py runserver\n# O aumenta timeout en cypress.config.js"
                }
            ],
            proximos_pasos=[
                "Validar test pyramid (Ver GUIA-TESTING-003)",
                "Escribir nuevos tests",
                "Ejecutar todos los tests antes de PR"
            ],
            referencias={
                "Jest docs": "https://jestjs.io/",
                "Script CI frontend": "scripts/ci/frontend_test.sh",
                "Test pyramid": "docs/gobernanza/ci_cd/workflows/test-pyramid.md"
            },
            mantenedores=["qa-lead", "frontend-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-TESTING-003",
            titulo="Validar Test Pyramid",
            categoria="testing",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=6,
            descripcion="Aprende a validar que tu código cumple con la pirámide de tests (60% unit, 30% integration, 10% E2E).",
            pasos=[
                {
                    "titulo": "Ejecutar validación de pyramid",
                    "descripcion": "Ejecuta el script que valida la distribución de tests.",
                    "comando": "./scripts/ci/test_pyramid_check.sh",
                    "output": "Test pyramid validation: PASSED\nUnit: 62%, Integration: 28%, E2E: 10%"
                },
                {
                    "titulo": "Revisar reporte detallado",
                    "descripcion": "Revisa el reporte JSON generado con detalles.",
                    "comando": "cat test-pyramid-report.json | jq .",
                    "output": "JSON con distribución de tests"
                },
                {
                    "titulo": "Identificar desbalances",
                    "descripcion": "Si falla, identifica qué categoría está desbalanceada.",
                    "comando": "# El script te dirá:\n# - Demasiados tests E2E (>10%)\n# - Pocos tests unitarios (<60%)\n# - etc",
                    "output": "Causa del desbalance identificada"
                }
            ],
            prerequisitos=[
                "Tests backend ejecutados (Ver GUIA-TESTING-001)",
                "Tests frontend ejecutados (Ver GUIA-TESTING-002)",
                "pytest-json-report instalado"
            ],
            validaciones=[
                "Pyramid check pasa",
                "Unit tests: 60% ± 10%",
                "Integration tests: 30% ± 10%",
                "E2E tests: 10% ± 5%"
            ],
            troubleshooting=[
                {
                    "titulo": "Demasiados tests E2E",
                    "sintomas": "E2E tests: 25% (expected ~10%)",
                    "causa": "Algunos tests E2E deberían ser integration",
                    "solucion": "Revisa tests E2E y mueve los que no necesiten navegador completo a integration tests"
                }
            ],
            proximos_pasos=[
                "Ajustar distribución de tests si falla",
                "Crear PR (Ver GUIA-WORKFLOWS-003)"
            ],
            referencias={
                "Test Pyramid": "https://martinfowler.com/bliki/TestPyramid.html",
                "Workflow test-pyramid.yml": ".github/workflows/test-pyramid.yml",
                "Script validación": "scripts/ci/test_pyramid_check.sh"
            },
            mantenedores=["qa-lead"]
        ))

        # DEPLOYMENT (2 guías)
        guides.append(GuideMetadata(
            id="GUIA-DEPLOYMENT-001",
            titulo="Workflow de Deployment",
            categoria="deployment",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=10,
            descripcion="Entiende cómo funciona el proceso de deployment automático a staging y producción.",
            pasos=[
                {
                    "titulo": "Deployment a staging (automático)",
                    "descripcion": "Cada push a develop despliega automáticamente a staging.",
                    "comando": "# Push a develop:\ngit push origin develop\n\n# Workflow deploy.yml se ejecuta automáticamente",
                    "output": "Deployment to staging initiated"
                },
                {
                    "titulo": "Verificar smoke tests en staging",
                    "descripcion": "El workflow ejecuta smoke tests automáticamente.",
                    "comando": "# Ver en GitHub Actions:\n# Job: smoke-tests-staging\n# Verifica que pasan todos los checks",
                    "output": "Smoke tests passed"
                },
                {
                    "titulo": "Deployment a production (manual)",
                    "descripcion": "Para production, se requiere aprobación manual.",
                    "comando": "# Merge a main:\ngit checkout main\ngit merge develop\ngit push origin main\n\n# En GitHub Actions, aprueba el deployment manual",
                    "output": "Deployment to production approved"
                },
                {
                    "titulo": "Verificar deployment exitoso",
                    "descripcion": "Verifica que el deployment completó correctamente.",
                    "comando": "# Checks automáticos:\n# 1. Blue-green swap completado\n# 2. Health checks pasan\n# 3. Smoke tests pasan\n# 4. Rollback disponible",
                    "output": "Deployment successful"
                }
            ],
            prerequisitos=[
                "PR mergeado a develop o main",
                "Todos los tests CI pasando",
                "Permisos de deployment (para production)"
            ],
            validaciones=[
                "Workflow deploy.yml se ejecutó",
                "Blue-green deployment completó",
                "Smoke tests pasaron",
                "Aplicación accesible en staging/production",
                "Rollback disponible"
            ],
            troubleshooting=[
                {
                    "titulo": "Smoke tests fallan en staging",
                    "sintomas": "Smoke test failed: /health endpoint not responding",
                    "causa": "Aplicación no inició correctamente",
                    "solucion": "Revisa logs:\n# GitHub Actions -> Job logs\n# Verifica migraciones, variables de entorno, etc"
                },
                {
                    "titulo": "Rollback necesario",
                    "sintomas": "Deployment causó incidente en producción",
                    "causa": "Bug crítico no detectado en staging",
                    "solucion": "Ejecuta rollback inmediato:\n# GitHub Actions -> deploy.yml -> Re-run with rollback flag\n# O manualmente:\n./scripts/deploy/rollback.sh"
                }
            ],
            proximos_pasos=[
                "Monitorear aplicación en producción",
                "Revisar DORA metrics (Ver GUIA-DEPLOYMENT-002)",
                "Crear post-deployment report"
            ],
            referencias={
                "Workflow deployment": ".github/workflows/deploy.yml",
                "Scripts deployment": "scripts/deploy/",
                "Blue-green deployment": "docs/gobernanza/ci_cd/workflows/deploy.md"
            },
            mantenedores=["devops-lead", "tech-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-DEPLOYMENT-002",
            titulo="Validar Restricciones Criticas",
            categoria="deployment",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=5,
            descripcion="Aprende a validar que tu código no viola restricciones críticas del proyecto (RNF-002).",
            pasos=[
                {
                    "titulo": "Ejecutar validación de restricciones",
                    "descripcion": "Ejecuta el script que valida restricciones críticas.",
                    "comando": "./scripts/validate_critical_restrictions.sh",
                    "output": "All critical restrictions validated: PASSED"
                },
                {
                    "titulo": "Revisar restricciones validadas",
                    "descripcion": "El script valida que NO uses tecnologías prohibidas.",
                    "comando": "# Valida que NO uses:\n# - Redis\n# - RabbitMQ\n# - Celery\n# - MongoDB\n# - Elasticsearch",
                    "output": "No prohibited technologies found"
                },
                {
                    "titulo": "Revisar resultado detallado",
                    "descripcion": "Si falla, revisa qué restricción violaste.",
                    "comando": "# El script te dirá:\n# ERROR: Found Redis import in file.py:123\n# ERROR: Found RabbitMQ config in settings.py:456",
                    "output": "Violación identificada"
                }
            ],
            prerequisitos=[
                "Código completo y listo para commit",
                "Script validate_critical_restrictions.sh disponible"
            ],
            validaciones=[
                "Script pasa sin errores",
                "No hay imports de tecnologías prohibidas",
                "No hay configuraciones de tecnologías prohibidas",
                "CI workflow también pasa esta validación"
            ],
            troubleshooting=[
                {
                    "titulo": "Encontró Redis import",
                    "sintomas": "ERROR: Found 'redis' import",
                    "causa": "Código intenta usar Redis (prohibido por RNF-002)",
                    "solucion": "Usa alternativa permitida:\n# En lugar de Redis para cache, usa:\n# - Django cache framework con database backend\n# - Memcached (permitido)\n# Ver ADR-XXX para alternatives"
                }
            ],
            proximos_pasos=[
                "Si pasa: crear PR (Ver GUIA-WORKFLOWS-003)",
                "Si falla: refactorizar para usar tecnologías permitidas"
            ],
            referencias={
                "Script validación": "scripts/validate_critical_restrictions.sh",
                "RNF-002": "docs/requisitos/rnf-002-restricciones-criticas.md",
                "Alternativas permitidas": "docs/adr/"
            },
            mantenedores=["arquitecto-senior", "tech-lead"]
        ))

        # TROUBLESHOOTING (1 guía)
        guides.append(GuideMetadata(
            id="GUIA-TROUBLESHOOTING-001",
            titulo="Problemas Comunes de Setup",
            categoria="troubleshooting",
            audiencia="desarrollador-nuevo",
            prioridad="P0",
            tiempo_lectura=15,
            descripcion="Soluciones a los problemas más comunes al configurar el entorno de desarrollo.",
            pasos=[
                {
                    "titulo": "Diagnosticar el problema",
                    "descripcion": "Identifica en qué categoría cae tu problema.",
                    "comando": "# Categorías comunes:\n# 1. Problemas de instalación (Python, Node)\n# 2. Problemas de base de datos\n# 3. Problemas de permisos\n# 4. Problemas de dependencias\n# 5. Problemas de red/proxy",
                    "output": "Categoría identificada"
                },
                {
                    "titulo": "Aplicar solución correspondiente",
                    "descripcion": "Busca tu problema en la sección de troubleshooting.",
                    "comando": "# Ver secciones abajo para soluciones específicas",
                    "output": "Solución encontrada"
                },
                {
                    "titulo": "Verificar que se resolvió",
                    "descripcion": "Ejecuta comando de verificación.",
                    "comando": "# Según el problema:\npython --version\nnode --version\ngit --version\npip list\nnpm list",
                    "output": "Problema resuelto"
                }
            ],
            prerequisitos=[
                "Acceso al sistema",
                "Permisos de instalación de software"
            ],
            validaciones=[
                "Problema identificado correctamente",
                "Solución aplicada",
                "Verificación exitosa"
            ],
            troubleshooting=[
                {
                    "titulo": "Python version incorrecta",
                    "sintomas": "python --version muestra 2.x o 3.x < 3.11",
                    "causa": "Sistema operativo usa versión antigua",
                    "solucion": "# Opción 1: Instalar desde python.org\n# Opción 2: Usar pyenv\ncurl https://pyenv.run | bash\npyenv install 3.11.0\npyenv global 3.11.0"
                },
                {
                    "titulo": "Node version incorrecta",
                    "sintomas": "node --version muestra < 18",
                    "causa": "Versión antigua de Node.js",
                    "solucion": "# Usar nvm:\ncurl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash\nnvm install 18\nnvm use 18"
                },
                {
                    "titulo": "Error de conexión a MySQL",
                    "sintomas": "Can't connect to MySQL server",
                    "causa": "MySQL no está corriendo o credenciales incorrectas",
                    "solucion": "# Verificar que MySQL corre:\nsudo systemctl status mysql\n# Si no corre, iniciarlo:\nsudo systemctl start mysql\n# Verificar credenciales en .env"
                },
                {
                    "titulo": "Permission denied al instalar dependencias",
                    "sintomas": "EACCES: permission denied",
                    "causa": "Falta de permisos para escribir en directorio",
                    "solucion": "# NO uses sudo con npm\n# Configura npm prefix:\nmkdir ~/.npm-global\nnpm config set prefix '~/.npm-global'\n# Agrega a PATH en ~/.bashrc:\nexport PATH=~/.npm-global/bin:$PATH"
                },
                {
                    "titulo": "Port already in use",
                    "sintomas": "Error: listen EADDRINUSE: address already in use :::3000",
                    "causa": "Otro proceso usa el puerto",
                    "solucion": "# Encuentra y mata el proceso:\nlsof -ti:3000 | xargs kill -9\n# O usa otro puerto:\nPORT=3001 npm run dev"
                },
                {
                    "titulo": "Module not found",
                    "sintomas": "ModuleNotFoundError: No module named 'X'",
                    "causa": "Dependencia no instalada o PYTHONPATH incorrecto",
                    "solucion": "# Reinstalar dependencias:\npip install -r requirements.txt\n# O agregar a PYTHONPATH:\nexport PYTHONPATH=$PYTHONPATH:$(pwd)/api"
                }
            ],
            proximos_pasos=[
                "Completar setup de entorno (Ver GUIA-ONBOARDING-001)",
                "Ejecutar proyecto (Ver GUIA-ONBOARDING-002)",
                "Si problema persiste: crear issue en GitHub con label 'help-wanted'"
            ],
            referencias={
                "Documentación completa setup": "docs/gobernanza/procesos/procedimientos/procedimiento_instalacion_entorno.md",
                "Requisitos del sistema": "README.md#requirements",
                "Canal de ayuda": "#dev-help en Slack"
            },
            mantenedores=["tech-lead", "devops-lead"]
        ))

        # ONBOARDING adicionales (4 guías más para completar 20)
        guides.append(GuideMetadata(
            id="GUIA-ONBOARDING-004",
            titulo="Configurar Variables de Entorno",
            categoria="onboarding",
            audiencia="desarrollador-nuevo",
            prioridad="P0",
            tiempo_lectura=7,
            descripcion="Aprende a configurar correctamente las variables de entorno necesarias para el proyecto.",
            pasos=[
                {
                    "titulo": "Copiar archivo de ejemplo",
                    "descripcion": "Crea tu archivo .env desde el template.",
                    "comando": "cp .env.example .env",
                    "output": ".env creado"
                },
                {
                    "titulo": "Configurar variables de base de datos",
                    "descripcion": "Configura las credenciales de tu base de datos local.",
                    "comando": "# Edita .env:\nDB_NAME=iact_dev\nDB_USER=tu_usuario\nDB_PASSWORD=tu_password\nDB_HOST=localhost\nDB_PORT=3306",
                    "output": "Variables de BD configuradas"
                },
                {
                    "titulo": "Configurar SECRET_KEY de Django",
                    "descripcion": "Genera una secret key única para tu entorno.",
                    "comando": "python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'",
                    "output": "Secret key generada"
                },
                {
                    "titulo": "Verificar configuración",
                    "descripcion": "Verifica que todas las variables están configuradas.",
                    "comando": "cd api\npython manage.py check",
                    "output": "System check identified no issues"
                }
            ],
            prerequisitos=[
                "Repositorio clonado",
                "Base de datos instalada"
            ],
            validaciones=[
                ".env existe y tiene valores",
                "SECRET_KEY es única (no la del ejemplo)",
                "Credenciales de BD son correctas",
                "python manage.py check pasa"
            ],
            troubleshooting=[
                {
                    "titulo": "SECRET_KEY inválida",
                    "sintomas": "ImproperlyConfigured: The SECRET_KEY setting must not be empty",
                    "causa": "SECRET_KEY no está configurada en .env",
                    "solucion": "Genera y agrega SECRET_KEY:\npython -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'\n# Copia el output a .env"
                }
            ],
            proximos_pasos=[
                "Ejecutar proyecto (Ver GUIA-ONBOARDING-002)",
                "Configurar herramientas de desarrollo"
            ],
            referencias={
                ".env.example": ".env.example",
                "Django settings": "api/config/settings.py"
            },
            mantenedores=["tech-lead", "backend-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-ONBOARDING-005",
            titulo="Usar Agentes SDLC - Planning",
            categoria="onboarding",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=10,
            descripcion="Aprende a usar el SDLCPlannerAgent para convertir feature requests en GitHub issues estructurados.",
            pasos=[
                {
                    "titulo": "Preparar feature request",
                    "descripcion": "Prepara una descripción clara de la feature que quieres implementar.",
                    "comando": "# Ejemplo:\n# 'Implementar sistema de notificaciones push para usuarios'",
                    "output": "Feature request definido"
                },
                {
                    "titulo": "Ejecutar SDLCPlannerAgent",
                    "descripcion": "Ejecuta el agente para generar el issue estructurado.",
                    "comando": "python scripts/ai/agents/sdlc_planner.py \\\n  --input \"Feature: Sistema de notificaciones push\" \\\n  --output docs/sdlc_outputs/planning/",
                    "output": "Issue generado en docs/sdlc_outputs/planning/issue-XXX.md"
                },
                {
                    "titulo": "Revisar issue generado",
                    "descripcion": "Revisa que el issue tenga toda la información necesaria.",
                    "comando": "cat docs/sdlc_outputs/planning/issue-XXX.md",
                    "output": "Issue con:\n- User story\n- Acceptance criteria\n- Story points\n- Labels"
                },
                {
                    "titulo": "Crear issue en GitHub",
                    "descripcion": "Usa el contenido generado para crear el issue en GitHub.",
                    "comando": "gh issue create --title \"Feature: Notificaciones push\" \\\n  --body-file docs/sdlc_outputs/planning/issue-XXX.md \\\n  --label feature,planning",
                    "output": "Issue #XXX creado en GitHub"
                }
            ],
            prerequisitos=[
                "Python 3.11+ instalado",
                "GitHub CLI (gh) instalado",
                "GITHUB_TOKEN configurado"
            ],
            validaciones=[
                "Agente ejecuta sin errores",
                "Issue generado contiene user story",
                "Issue contiene acceptance criteria",
                "Issue creado en GitHub"
            ],
            troubleshooting=[
                {
                    "titulo": "GITHUB_TOKEN no configurado",
                    "sintomas": "Error: GITHUB_TOKEN required",
                    "causa": "Variable de entorno faltante",
                    "solucion": "Crea personal access token en GitHub:\n# Settings -> Developer settings -> Personal access tokens\n# Crea token con scope 'repo'\nexport GITHUB_TOKEN='tu_token'"
                }
            ],
            proximos_pasos=[
                "Usar SDLCFeasibilityAgent para análisis de viabilidad",
                "Usar SDLCDesignAgent para diseño técnico",
                "Iniciar fase de Implementation"
            ],
            referencias={
                "SDLCPlannerAgent": "scripts/ai/agents/sdlc_planner.py",
                "SDLC Process": "docs/gobernanza/procesos/SDLC_PROCESS.md",
                "Agentes SDLC": "docs/gobernanza/procesos/AGENTES_SDLC.md"
            },
            mantenedores=["tech-lead", "arquitecto-senior"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-ONBOARDING-006",
            titulo="Validar Documentacion",
            categoria="onboarding",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=6,
            descripcion="Aprende a validar que tu documentación cumple con la estructura y estándares del proyecto.",
            pasos=[
                {
                    "titulo": "Ejecutar validación de estructura",
                    "descripcion": "Ejecuta el script que valida la estructura de docs/.",
                    "comando": "./scripts/validar_estructura_docs.sh",
                    "output": "Documentation structure validation: PASSED"
                },
                {
                    "titulo": "Revisar warnings",
                    "descripcion": "Si hay warnings, revísalos y corrígelos.",
                    "comando": "# El script puede mostrar:\n# WARNING: Missing frontmatter in file.md\n# WARNING: Broken link to non-existent.md",
                    "output": "Warnings corregidos"
                },
                {
                    "titulo": "Validar links",
                    "descripcion": "Verifica que no haya links rotos en tu documentación.",
                    "comando": "# El workflow docs-validation.yml hace esto automáticamente\n# Puedes ejecutarlo localmente con:\nmarkdown-link-check docs/**/*.md",
                    "output": "Todos los links válidos"
                }
            ],
            prerequisitos=[
                "Documentación escrita en docs/",
                "Script validar_estructura_docs.sh disponible"
            ],
            validaciones=[
                "Script pasa sin errores",
                "Frontmatter YAML presente en todos los .md",
                "No hay links rotos",
                "Estructura de directorios correcta"
            ],
            troubleshooting=[
                {
                    "titulo": "Missing frontmatter",
                    "sintomas": "WARNING: Missing frontmatter in file.md",
                    "causa": "Archivo .md sin metadata YAML",
                    "solucion": "Agrega frontmatter al inicio:\n---\nid: DOC-XXX\ntipo: guia\ncategoria: onboarding\n---"
                }
            ],
            proximos_pasos=[
                "Crear PR con documentación",
                "Esperar validación automática en CI"
            ],
            referencias={
                "Script validación": "scripts/validar_estructura_docs.sh",
                "Workflow docs-validation": ".github/workflows/docs-validation.yml",
                "Estándares documentación": "docs/gobernanza/CONTRIBUTING.md"
            },
            mantenedores=["doc-lead", "tech-lead"]
        ))

        guides.append(GuideMetadata(
            id="GUIA-ONBOARDING-007",
            titulo="Generar Indices de Requisitos",
            categoria="onboarding",
            audiencia="desarrollador",
            prioridad="P0",
            tiempo_lectura=5,
            descripcion="Aprende a generar automáticamente índices de requisitos del proyecto.",
            pasos=[
                {
                    "titulo": "Ejecutar generador de índices",
                    "descripcion": "Ejecuta el script Python que genera índices automáticamente.",
                    "comando": "python scripts/requisitos/generar_indices.py",
                    "output": "Índices generados en docs/requisitos/"
                },
                {
                    "titulo": "Verificar índices generados",
                    "descripcion": "Revisa que los índices se generaron correctamente.",
                    "comando": "ls docs/requisitos/*/INDICE.md",
                    "output": "Lista de archivos INDICE.md"
                },
                {
                    "titulo": "Commit de índices",
                    "descripcion": "Los índices son auto-generados, commitéalos.",
                    "comando": "git add docs/requisitos/*/INDICE.md\ngit commit -m \"docs(requisitos): actualizar indices automaticos\"",
                    "output": "Índices commiteados"
                }
            ],
            prerequisitos=[
                "Requisitos escritos en docs/requisitos/",
                "Python 3.11+ instalado"
            ],
            validaciones=[
                "Script ejecuta sin errores",
                "Archivos INDICE.md generados",
                "Índices contienen todos los requisitos",
                "Links en índices funcionan"
            ],
            troubleshooting=[
                {
                    "titulo": "Script falla por frontmatter inválido",
                    "sintomas": "Error parsing YAML frontmatter",
                    "causa": "Algún requisito tiene frontmatter mal formateado",
                    "solucion": "Valida frontmatter:\npython scripts/requisitos/validar_frontmatter.py\n# Corrige el archivo que marca como inválido"
                }
            ],
            proximos_pasos=[
                "Validar trazabilidad de requisitos",
                "Crear PR con índices actualizados"
            ],
            referencias={
                "Script generador": "scripts/requisitos/generar_indices.py",
                "Workflow requirements_index": ".github/workflows/requirements_index.yml",
                "Plantilla requisito": "docs/plantillas/template_requisito_funcional.md"
            },
            mantenedores=["arquitecto-senior", "product-owner"]
        ))

        return guides

    def generate_p0_guides(self) -> List[Path]:
        """
        Genera las 20 guías P0.

        Returns:
            Lista de paths de guías generadas
        """
        print("\n" + "=" * 80)
        print("GENERANDO GUIAS P0 DE ONBOARDING")
        print("=" * 80 + "\n")

        guides_metadata = self.get_p0_guides_metadata()
        generated_paths = []

        for metadata in guides_metadata:
            try:
                content = self.generate_guide(metadata)
                path = self.save_guide(metadata, content)
                generated_paths.append(path)
            except Exception as e:
                print(f"ERROR generando {metadata.id}: {e}")
                self.guides_skipped += 1

        return generated_paths

    def generate_summary_report(self) -> Dict:
        """
        Genera reporte resumen de generación.

        Returns:
            Diccionario con estadísticas
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "guides_generated": self.guides_generated,
            "guides_skipped": self.guides_skipped,
            "total_planned": 147,
            "p0_completed": self.guides_generated,
            "p0_target": 20,
            "completion_percentage": round((self.guides_generated / 20) * 100, 2) if self.guides_generated else 0
        }


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Generador de guías de documentación para IACT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:

  # Generar todas las guías P0
  python scripts/generate_guides.py --priority P0

  # Dry-run (no escribe archivos)
  python scripts/generate_guides.py --priority P0 --dry-run

  # Generar guías de una categoría específica
  python scripts/generate_guides.py --category onboarding

  # Ver reporte de coverage
  python scripts/generate_guides.py --report
        """
    )

    parser.add_argument(
        '--priority',
        choices=['P0', 'P1', 'P2', 'P3', 'all'],
        default='P0',
        help='Prioridad de guías a generar (default: P0)'
    )

    parser.add_argument(
        '--category',
        choices=['onboarding', 'workflows', 'testing', 'deployment', 'troubleshooting', 'all'],
        help='Categoría específica de guías a generar'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simular generación sin escribir archivos'
    )

    parser.add_argument(
        '--report',
        action='store_true',
        help='Generar solo reporte de coverage'
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    generator = DocumentationGuideGenerator(project_root, dry_run=args.dry_run)

    try:
        if args.report:
            report = generator.generate_summary_report()
            print(json.dumps(report, indent=2))
            return 0

        # Generar guías P0
        if args.priority == 'P0' or args.priority == 'all':
            generated_paths = generator.generate_p0_guides()

            # Imprimir resumen
            print("\n" + "=" * 80)
            print("RESUMEN DE GENERACION")
            print("=" * 80)
            report = generator.generate_summary_report()
            print(f"\nGuías generadas: {report['guides_generated']}/{report['p0_target']}")
            print(f"Completitud: {report['completion_percentage']}%")
            print(f"Guías omitidas: {report['guides_skipped']}")

            if generated_paths:
                print(f"\nGuías creadas en:")
                for path in generated_paths[:5]:  # Mostrar primeras 5
                    print(f"  - {path}")
                if len(generated_paths) > 5:
                    print(f"  ... y {len(generated_paths) - 5} más")

            print("\n" + "=" * 80)

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
