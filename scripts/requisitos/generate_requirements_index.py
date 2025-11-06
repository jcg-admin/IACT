#!/usr/bin/env python3
"""
Generador de Índices ISO 29148:2018

Este script escanea todos los requisitos en docs/implementacion/**/requisitos/
y genera los siguientes índices:
- BRS (Business Requirements Specification) - ISO 29148 Clause 9.3
- StRS (Stakeholder Requirements Specification) - ISO 29148 Clause 9.4
- SyRS (System Requirements Specification) - ISO 29148 Clause 9.5
- SRS (Software Requirements Specification) - ISO 29148 Clause 9.6
- RTM (Requirements Traceability Matrix)

Estándares: BABOK v3, PMBOK 7th Ed, ISO/IEC/IEEE 29148:2018
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Agregar ruta del proyecto al PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class Requisito:
    """Representa un requisito con su metadata"""
    id: str
    tipo: str
    titulo: str
    dominio: str
    owner: str
    prioridad: str
    estado: str
    fecha_creacion: str
    trazabilidad_upward: List[str] = field(default_factory=list)
    trazabilidad_downward: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    iso29148_clause: Optional[str] = None
    verificacion_metodo: Optional[str] = None
    file_path: Optional[str] = None
    contenido: Optional[str] = None


def parse_frontmatter(content: str) -> Dict:
    """
    Parsea frontmatter YAML de un archivo markdown

    Args:
        content: Contenido completo del archivo markdown

    Returns:
        Diccionario con los campos del frontmatter
    """
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(frontmatter_pattern, content, re.DOTALL)

    if not match:
        return {}

    yaml_content = match.group(1)
    metadata = {}

    # Parser YAML simple (sin dependencias externas)
    current_key = None
    current_list = None

    for line in yaml_content.split('\n'):
        line = line.rstrip()

        # Lista (con guiones)
        if current_list is not None and line.startswith('  - '):
            value = line[4:].strip()
            metadata[current_list].append(value)
            continue
        else:
            current_list = None

        # Key-value
        if ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Lista vacía
            if value == '[]' or value == '':
                if line.endswith(':'):
                    metadata[key] = []
                    current_list = key
                else:
                    metadata[key] = value.strip('"\'')
            # String con comillas
            elif value.startswith('"') and value.endswith('"'):
                metadata[key] = value.strip('"')
            elif value.startswith("'") and value.endswith("'"):
                metadata[key] = value.strip("'")
            else:
                metadata[key] = value

    return metadata


def scan_requisitos(base_path: Path) -> List[Requisito]:
    """
    Escanea todos los archivos .md en docs/implementacion/**/requisitos/

    Args:
        base_path: Ruta base del proyecto

    Returns:
        Lista de objetos Requisito
    """
    requisitos = []
    implementacion_path = base_path / 'docs' / 'implementacion'

    if not implementacion_path.exists():
        print(f"ADVERTENCIA: No existe {implementacion_path}")
        return requisitos

    # Buscar todos los archivos .md en requisitos/
    for md_file in implementacion_path.rglob('requisitos/**/*.md'):
        # Saltar archivos especiales
        if md_file.name.startswith('_') or md_file.name == 'README.md':
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata = parse_frontmatter(content)

            if not metadata.get('id'):
                print(f"ADVERTENCIA: {md_file} no tiene campo 'id' en frontmatter")
                continue

            req = Requisito(
                id=metadata.get('id', ''),
                tipo=metadata.get('tipo', ''),
                titulo=metadata.get('titulo', ''),
                dominio=metadata.get('dominio', ''),
                owner=metadata.get('owner', ''),
                prioridad=metadata.get('prioridad', ''),
                estado=metadata.get('estado', ''),
                fecha_creacion=metadata.get('fecha_creacion', ''),
                trazabilidad_upward=metadata.get('trazabilidad_upward', []),
                trazabilidad_downward=metadata.get('trazabilidad_downward', []),
                stakeholders=metadata.get('stakeholders', []),
                iso29148_clause=metadata.get('iso29148_clause'),
                verificacion_metodo=metadata.get('verificacion_metodo'),
                file_path=str(md_file.relative_to(base_path)),
                contenido=content
            )

            requisitos.append(req)

        except Exception as e:
            print(f"ERROR al procesar {md_file}: {e}")

    return requisitos


def generar_brs(requisitos: List[Requisito], output_path: Path):
    """Genera Business Requirements Specification (ISO 29148 Clause 9.3)"""
    reqs_negocio = [r for r in requisitos if r.tipo == 'negocio']

    content = f"""---
id: DOC-BRS
titulo: Business Requirements Specification (BRS)
generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
estandar: ISO/IEC/IEEE 29148:2018 - Clause 9.3
conformance: Full Conformance
---

# Business Requirements Specification (BRS)

GENERADO AUTOMATICAMENTE - NO EDITAR MANUALMENTE

Este documento consolida todos los requisitos de negocio del proyecto IACT.

Conforme a: ISO/IEC/IEEE 29148:2018 - Clause 9.3

---

## Resumen Ejecutivo

Total de requisitos de negocio: {len(reqs_negocio)}

Por dominio:
"""

    # Agrupar por dominio
    por_dominio = {}
    for req in reqs_negocio:
        if req.dominio not in por_dominio:
            por_dominio[req.dominio] = []
        por_dominio[req.dominio].append(req)

    for dominio, reqs in sorted(por_dominio.items()):
        content += f"- {dominio}: {len(reqs)} requisitos\n"

    content += "\n---\n\n"

    # Detalles por dominio
    for dominio, reqs in sorted(por_dominio.items()):
        content += f"## Dominio: {dominio.upper()}\n\n"

        for req in sorted(reqs, key=lambda r: r.id):
            content += f"### {req.id}: {req.titulo}\n\n"
            content += f"- **Owner**: {req.owner}\n"
            content += f"- **Prioridad**: {req.prioridad}\n"
            content += f"- **Estado**: {req.estado}\n"
            content += f"- **Archivo**: `{req.file_path}`\n"

            if req.trazabilidad_upward:
                content += f"- **Trazabilidad Upward**: {', '.join(req.trazabilidad_upward)}\n"

            if req.stakeholders:
                content += f"- **Stakeholders**: {', '.join(req.stakeholders)}\n"

            content += "\n"

    content += f"\n---\n\nGenerado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"OK Generado: {output_path}")


def generar_strs(requisitos: List[Requisito], output_path: Path):
    """Genera Stakeholder Requirements Specification (ISO 29148 Clause 9.4)"""
    reqs_stakeholder = [r for r in requisitos if r.tipo == 'stakeholder']

    content = f"""---
id: DOC-STRS
titulo: Stakeholder Requirements Specification (StRS)
generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
estandar: ISO/IEC/IEEE 29148:2018 - Clause 9.4
conformance: Full Conformance
---

# Stakeholder Requirements Specification (StRS)

GENERADO AUTOMATICAMENTE - NO EDITAR MANUALMENTE

Este documento consolida todos los requisitos de stakeholders del proyecto IACT.

Conforme a: ISO/IEC/IEEE 29148:2018 - Clause 9.4

---

## Resumen Ejecutivo

Total de requisitos de stakeholders: {len(reqs_stakeholder)}

Por dominio:
"""

    por_dominio = {}
    for req in reqs_stakeholder:
        if req.dominio not in por_dominio:
            por_dominio[req.dominio] = []
        por_dominio[req.dominio].append(req)

    for dominio, reqs in sorted(por_dominio.items()):
        content += f"- {dominio}: {len(reqs)} requisitos\n"

    content += "\n---\n\n"

    for dominio, reqs in sorted(por_dominio.items()):
        content += f"## Dominio: {dominio.upper()}\n\n"

        for req in sorted(reqs, key=lambda r: r.id):
            content += f"### {req.id}: {req.titulo}\n\n"
            content += f"- **Owner**: {req.owner}\n"
            content += f"- **Prioridad**: {req.prioridad}\n"
            content += f"- **Estado**: {req.estado}\n"
            content += f"- **Archivo**: `{req.file_path}`\n"

            if req.trazabilidad_upward:
                content += f"- **Deriva de**: {', '.join(req.trazabilidad_upward)}\n"

            if req.stakeholders:
                content += f"- **Stakeholders**: {', '.join(req.stakeholders)}\n"

            content += "\n"

    content += f"\n---\n\nGenerado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"OK Generado: {output_path}")


def generar_srs(requisitos: List[Requisito], output_path: Path):
    """Genera Software Requirements Specification (ISO 29148 Clause 9.6)"""
    reqs_funcionales = [r for r in requisitos if r.tipo == 'funcional']

    content = f"""---
id: DOC-SRS
titulo: Software Requirements Specification (SRS)
generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
estandar: ISO/IEC/IEEE 29148:2018 - Clause 9.6
conformance: Full Conformance
---

# Software Requirements Specification (SRS)

GENERADO AUTOMATICAMENTE - NO EDITAR MANUALMENTE

Este documento consolida todos los requisitos funcionales del proyecto IACT.

Conforme a: ISO/IEC/IEEE 29148:2018 - Clause 9.6

---

## Resumen Ejecutivo

Total de requisitos funcionales: {len(reqs_funcionales)}

Por dominio:
"""

    por_dominio = {}
    for req in reqs_funcionales:
        if req.dominio not in por_dominio:
            por_dominio[req.dominio] = []
        por_dominio[req.dominio].append(req)

    for dominio, reqs in sorted(por_dominio.items()):
        content += f"- {dominio}: {len(reqs)} requisitos\n"

    content += "\n---\n\n"

    for dominio, reqs in sorted(por_dominio.items()):
        content += f"## Dominio: {dominio.upper()}\n\n"

        for req in sorted(reqs, key=lambda r: r.id):
            content += f"### {req.id}: {req.titulo}\n\n"
            content += f"- **Owner**: {req.owner}\n"
            content += f"- **Prioridad**: {req.prioridad}\n"
            content += f"- **Estado**: {req.estado}\n"
            content += f"- **Archivo**: `{req.file_path}`\n"

            if req.trazabilidad_upward:
                content += f"- **Deriva de**: {', '.join(req.trazabilidad_upward)}\n"

            if req.verificacion_metodo:
                content += f"- **Verificación**: {req.verificacion_metodo}\n"

            content += "\n"

    content += f"\n---\n\nGenerado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"OK Generado: {output_path}")


def generar_rtm(requisitos: List[Requisito], output_path: Path):
    """Genera Requirements Traceability Matrix"""
    content = f"""---
id: DOC-RTM
titulo: Requirements Traceability Matrix (RTM)
generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
estandar: ISO/IEC/IEEE 29148:2018 - Clause 5.2.8
---

# Requirements Traceability Matrix (RTM)

GENERADO AUTOMATICAMENTE - NO EDITAR MANUALMENTE

Matriz de trazabilidad bidireccional de todos los requisitos.

---

## Trazabilidad Completa

| ID | Título | Tipo | Dominio | Estado | Upward (Deriva de) | Downward (Genera) |
|----|--------|------|---------|--------|-------------------|------------------|
"""

    for req in sorted(requisitos, key=lambda r: r.id):
        upward = ', '.join(req.trazabilidad_upward) if req.trazabilidad_upward else '-'
        downward = ', '.join(req.trazabilidad_downward) if req.trazabilidad_downward else '-'

        content += f"| {req.id} | {req.titulo} | {req.tipo} | {req.dominio} | {req.estado} | {upward} | {downward} |\n"

    content += f"\n---\n\nGenerado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"Total requisitos: {len(requisitos)}\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"OK Generado: {output_path}")


def main():
    """Función principal"""
    print("=" * 80)
    print("Generador de Índices ISO 29148:2018")
    print("=" * 80)

    base_path = PROJECT_ROOT
    docs_requisitos_path = base_path / 'docs' / 'requisitos'

    # Crear directorio si no existe
    docs_requisitos_path.mkdir(parents=True, exist_ok=True)

    # Escanear requisitos
    print(f"\nEscaneando requisitos en: {base_path / 'docs' / 'implementacion'}")
    requisitos = scan_requisitos(base_path)
    print(f"Total requisitos encontrados: {len(requisitos)}")

    if not requisitos:
        print("ADVERTENCIA: No se encontraron requisitos para procesar")
        return

    # Generar índices
    print("\nGenerando índices ISO 29148...")

    generar_brs(requisitos, docs_requisitos_path / 'brs_business_requirements.md')
    generar_strs(requisitos, docs_requisitos_path / 'strs_stakeholder_requirements.md')
    generar_srs(requisitos, docs_requisitos_path / 'srs_software_requirements.md')
    generar_rtm(requisitos, docs_requisitos_path / 'matriz_trazabilidad_rtm.md')

    print("\n" + "=" * 80)
    print("COMPLETADO: Índices generados exitosamente")
    print("=" * 80)


if __name__ == '__main__':
    main()
