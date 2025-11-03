#!/usr/bin/env python3
"""
Generador de Índices ISO 29148
Escanea todos los requisitos en docs/implementacion/ y genera:
- BRS (Business Requirements Specification)
- StRS (Stakeholder Requirements Specification)
- SyRS (System Requirements Specification)
- SRS (Software Requirements Specification)
- RTM (Requirements Traceability Matrix)
"""

import os
import re
from pathlib import Path
from typing import Dict, List
import yaml

# Paths
DOCS_PATH = Path("docs")
IMPL_PATH = DOCS_PATH / "implementacion"
OUTPUT_PATH = DOCS_PATH / "requisitos"

def extract_frontmatter(filepath: Path) -> Dict:
    """Extrae el frontmatter YAML de un archivo markdown."""
    try:
        content = filepath.read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))
        return {}
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return {}

def collect_requirements() -> Dict[str, List[Dict]]:
    """Recopila todos los requisitos por tipo."""
    requirements = {
        'necesidades': [],
        'negocio': [],
        'stakeholders': [],
        'funcionales': [],
        'no_funcionales': []
    }

    for md_file in IMPL_PATH.rglob('*.md'):
        if md_file.name.startswith('_') or md_file.name == 'README.md':
            continue

        frontmatter = extract_frontmatter(md_file)
        if not frontmatter or 'tipo' not in frontmatter:
            continue

        req_type = frontmatter.get('tipo')
        if req_type in requirements:
            frontmatter['filepath'] = md_file
            frontmatter['relpath'] = md_file.relative_to(DOCS_PATH)
            requirements[req_type].append(frontmatter)

    return requirements

def generate_brs(requirements: Dict) -> str:
    """Genera Business Requirements Specification (ISO 29148 Clause 9.3)."""
    content = """---
id: BRS-AUTO-GENERATED
tipo: indice
titulo: Business Requirements Specification (BRS)
estandar: ISO/IEC/IEEE 29148:2018 - Clause 9.3
generado: AUTO-GENERADO - NO EDITAR MANUALMENTE
fecha_generacion: AUTO
---

# Business Requirements Specification (BRS)

**Conformidad**: ISO/IEC/IEEE 29148:2018 - Clause 9.3

Este documento es **generado automáticamente** por CI/CD.
Para modificar, edite los archivos fuente en `docs/implementacion/`.

---

## Índice de Requisitos de Negocio

"""

    reqs = requirements.get('negocio', [])
    if not reqs:
        content += "\n⚠️ **No se encontraron requisitos de negocio.**\n"
    else:
        content += f"\n**Total de requisitos de negocio**: {len(reqs)}\n\n"

        for req in sorted(reqs, key=lambda x: x.get('id', '')):
            req_id = req.get('id', 'N/A')
            titulo = req.get('titulo', 'Sin título')
            estado = req.get('estado', 'N/A')
            prioridad = req.get('prioridad', 'N/A')
            relpath = req.get('relpath', '')

            content += f"### {req_id}: {titulo}\n\n"
            content += f"- **Estado**: {estado}\n"
            content += f"- **Prioridad**: {prioridad}\n"
            content += f"- **Archivo**: [{relpath}](../{relpath})\n"

            if 'trazabilidad_upward' in req:
                content += f"- **Trazabilidad (origen)**: {', '.join(req['trazabilidad_upward'])}\n"

            if 'stakeholders' in req:
                content += f"- **Stakeholders**: {', '.join(req['stakeholders'])}\n"

            content += "\n---\n\n"

    return content

def generate_strs(requirements: Dict) -> str:
    """Genera Stakeholder Requirements Specification (ISO 29148 Clause 9.4)."""
    content = """---
id: STRS-AUTO-GENERATED
tipo: indice
titulo: Stakeholder Requirements Specification (StRS)
estandar: ISO/IEC/IEEE 29148:2018 - Clause 9.4
generado: AUTO-GENERADO - NO EDITAR MANUALMENTE
---

# Stakeholder Requirements Specification (StRS)

**Conformidad**: ISO/IEC/IEEE 29148:2018 - Clause 9.4

---

## Índice de Requisitos de Stakeholders

"""

    reqs = requirements.get('stakeholders', [])
    if not reqs:
        content += "\n⚠️ **No se encontraron requisitos de stakeholders.**\n"
    else:
        content += f"\n**Total de requisitos de stakeholders**: {len(reqs)}\n\n"

        for req in sorted(reqs, key=lambda x: x.get('id', '')):
            req_id = req.get('id', 'N/A')
            titulo = req.get('titulo', 'Sin título')
            dominio = req.get('dominio', 'N/A')
            relpath = req.get('relpath', '')

            content += f"### {req_id}: {titulo}\n\n"
            content += f"- **Dominio**: {dominio}\n"
            content += f"- **Archivo**: [{relpath}](../{relpath})\n\n"

    return content

def generate_srs(requirements: Dict) -> str:
    """Genera Software Requirements Specification (ISO 29148 Clause 9.6)."""
    content = """---
id: SRS-AUTO-GENERATED
tipo: indice
titulo: Software Requirements Specification (SRS)
estandar: ISO/IEC/IEEE 29148:2018 - Clause 9.6
generado: AUTO-GENERADO - NO EDITAR MANUALMENTE
---

# Software Requirements Specification (SRS)

**Conformidad**: ISO/IEC/IEEE 29148:2018 - Clause 9.6

---

## Requisitos Funcionales

"""

    funcionales = requirements.get('funcionales', [])
    no_funcionales = requirements.get('no_funcionales', [])

    if funcionales:
        content += f"\n**Total**: {len(funcionales)} requisitos funcionales\n\n"
        for req in sorted(funcionales, key=lambda x: x.get('id', '')):
            req_id = req.get('id', 'N/A')
            titulo = req.get('titulo', 'Sin título')
            dominio = req.get('dominio', 'N/A')
            estado = req.get('estado', 'N/A')
            relpath = req.get('relpath', '')

            content += f"### {req_id}: {titulo}\n\n"
            content += f"- **Dominio**: {dominio}\n"
            content += f"- **Estado**: {estado}\n"
            content += f"- **Archivo**: [{relpath}](../{relpath})\n\n"
    else:
        content += "\n⚠️ **No se encontraron requisitos funcionales.**\n\n"

    content += "\n---\n\n## Requisitos No Funcionales\n\n"

    if no_funcionales:
        content += f"\n**Total**: {len(no_funcionales)} requisitos no funcionales\n\n"
        for req in sorted(no_funcionales, key=lambda x: x.get('id', '')):
            req_id = req.get('id', 'N/A')
            titulo = req.get('titulo', 'Sin título')
            categoria = req.get('categoria', 'N/A')
            relpath = req.get('relpath', '')

            content += f"### {req_id}: {titulo}\n\n"
            content += f"- **Categoría**: {categoria}\n"
            content += f"- **Archivo**: [{relpath}](../{relpath})\n\n"
    else:
        content += "\n⚠️ **No se encontraron requisitos no funcionales.**\n\n"

    return content

def generate_rtm(requirements: Dict) -> str:
    """Genera Requirements Traceability Matrix."""
    content = """---
id: RTM-AUTO-GENERATED
tipo: matriz_trazabilidad
titulo: Requirements Traceability Matrix (RTM)
generado: AUTO-GENERADO - NO EDITAR MANUALMENTE
---

# Requirements Traceability Matrix (RTM)

Matriz de trazabilidad bidireccional de todos los requisitos del proyecto.

---

## Trazabilidad Completa

| ID Requisito | Tipo | Título | Origen (Upward) | Derivados (Downward) |
|--------------|------|--------|-----------------|----------------------|
"""

    all_reqs = []
    for req_type, reqs in requirements.items():
        all_reqs.extend(reqs)

    for req in sorted(all_reqs, key=lambda x: x.get('id', '')):
        req_id = req.get('id', 'N/A')
        req_type = req.get('tipo', 'N/A')
        titulo = req.get('titulo', 'Sin título')[:50]

        upward = req.get('trazabilidad_upward', [])
        downward = req.get('trazabilidad_downward', [])

        upward_str = ', '.join(upward) if upward else '-'
        downward_str = ', '.join(downward) if downward else '-'

        content += f"| {req_id} | {req_type} | {titulo}... | {upward_str} | {downward_str} |\n"

    content += "\n---\n\n**Total de requisitos**: " + str(len(all_reqs)) + "\n"

    return content

def main():
    """Función principal."""
    print("🔍 Recopilando requisitos...")
    requirements = collect_requirements()

    # Crear directorio de salida
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    print("📝 Generando BRS (Business Requirements Specification)...")
    brs_content = generate_brs(requirements)
    (OUTPUT_PATH / "brs_business_requirements.md").write_text(brs_content, encoding='utf-8')

    print("📝 Generando StRS (Stakeholder Requirements Specification)...")
    strs_content = generate_strs(requirements)
    (OUTPUT_PATH / "strs_stakeholder_requirements.md").write_text(strs_content, encoding='utf-8')

    print("📝 Generando SRS (Software Requirements Specification)...")
    srs_content = generate_srs(requirements)
    (OUTPUT_PATH / "srs_software_requirements.md").write_text(srs_content, encoding='utf-8')

    print("📝 Generando RTM (Requirements Traceability Matrix)...")
    rtm_content = generate_rtm(requirements)
    (OUTPUT_PATH / "matriz_trazabilidad_rtm.md").write_text(rtm_content, encoding='utf-8')

    # Generar README
    readme_content = """---
id: DOC-REQ-AUTO-INDEX
generado: AUTO
---

# Índices de Requisitos (ISO 29148)

**⚠️ ESTOS ARCHIVOS SON AUTO-GENERADOS - NO EDITAR MANUALMENTE**

Los índices se regeneran automáticamente mediante GitHub Actions cuando se modifican requisitos en `docs/implementacion/`.

## Índices Disponibles

- [BRS - Business Requirements Specification](brs_business_requirements.md) (ISO 29148 Clause 9.3)
- [StRS - Stakeholder Requirements Specification](strs_stakeholder_requirements.md) (ISO 29148 Clause 9.4)
- [SRS - Software Requirements Specification](srs_software_requirements.md) (ISO 29148 Clause 9.6)
- [RTM - Requirements Traceability Matrix](matriz_trazabilidad_rtm.md)

## Estadísticas

"""

    for req_type, reqs in requirements.items():
        readme_content += f"- **{req_type.capitalize()}**: {len(reqs)} requisitos\n"

    readme_content += "\n---\n\n**Última generación**: Automática por CI/CD\n"

    (OUTPUT_PATH / "README.md").write_text(readme_content, encoding='utf-8')

    print("✅ Índices generados exitosamente en docs/requisitos/")

    # Estadísticas
    total = sum(len(reqs) for reqs in requirements.values())
    print(f"\n📊 Estadísticas:")
    print(f"   Total de requisitos: {total}")
    for req_type, reqs in requirements.items():
        if reqs:
            print(f"   - {req_type.capitalize()}: {len(reqs)}")

if __name__ == "__main__":
    main()
