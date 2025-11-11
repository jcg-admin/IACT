"""
DocumentSplitter Agent

Responsabilidad: Dividir documentos grandes en módulos manejables manteniendo coherencia.
Input: Documento monolítico grande (Markdown)
Output: Múltiples documentos modulares + cross-references + índice maestro

Estrategia de división:
- Divide por secciones principales (headers de nivel 1-2)
- Agrupa secciones relacionadas en módulos lógicos
- Genera cross-references entre documentos
- Crea índice maestro con estructura completa
- Mantiene trazabilidad entre módulos
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from datetime import datetime
from .base import Agent


class DocumentSplitter(Agent):
    """
    Agente especializado en división inteligente de documentos.

    Divide documentos grandes en módulos lógicos manteniendo:
    - Coherencia temática (secciones relacionadas juntas)
    - Cross-references entre documentos
    - Trazabilidad completa
    - Índice maestro navegable
    - Balance de tamaño entre módulos

    Características:
    - Análisis de estructura Markdown (headers H1, H2, H3)
    - Agrupación inteligente por tema
    - Generación automática de referencias cruzadas
    - Índice maestro con resumen de cada módulo
    - Preservación de metadatos y estándares
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="DocumentSplitter", config=config)

        # Configuración
        self.max_lines_per_module = self.get_config("max_lines", 1000)
        self.min_lines_per_module = self.get_config("min_lines", 200)
        self.preserve_metadata = self.get_config("preserve_metadata", True)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Valida que exista documento para dividir.

        Args:
            input_data: Datos de entrada

        Returns:
            Lista de errores de validación
        """
        errors = []

        if "document" not in input_data:
            errors.append("Campo obligatorio faltante: 'document'")
        elif not input_data["document"]:
            errors.append("Documento está vacío")
        elif len(input_data["document"].split('\n')) < self.min_lines_per_module:
            doc_lines = len(input_data['document'].split('\n'))
            errors.append(
                f"Documento muy pequeño para dividir: "
                f"{doc_lines} líneas "
                f"< {self.min_lines_per_module} líneas mínimas"
            )

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la división del documento.

        Args:
            input_data: Datos de entrada validados

        Returns:
            Diccionario con módulos, cross-refs e índice
        """
        document = input_data["document"]
        component_name = input_data.get("component_name", "Documento")

        self.logger.info(f"Analizando documento: {len(document)} caracteres")

        # Paso 1: Analizar estructura del documento
        sections = self._analyze_sections(document)
        self.logger.info(f"Identificadas {len(sections)} secciones")

        # Paso 2: Agrupar secciones en módulos lógicos
        modules = self._group_into_modules(sections, component_name)
        self.logger.info(f"Creados {len(modules)} módulos")

        # Paso 3: Generar cross-references
        cross_refs = self._generate_cross_references(modules)
        self.logger.info(f"Generadas {len(cross_refs)} referencias cruzadas")

        # Paso 4: Insertar cross-references en módulos
        modules_with_refs = self._insert_cross_references(modules, cross_refs)

        # Paso 5: Crear índice maestro
        master_index = self._create_master_index(modules_with_refs, component_name)
        self.logger.info("Índice maestro creado")

        # Calcular métricas
        total_original_lines = len(document.split('\n'))
        total_module_lines = sum(len(m["content"].split('\n')) for m in modules_with_refs)
        avg_module_lines = total_module_lines / len(modules_with_refs)

        return {
            "modules": modules_with_refs,
            "module_count": len(modules_with_refs),
            "cross_references": cross_refs,
            "master_index": master_index,
            "original_size_lines": total_original_lines,
            "total_module_size_lines": total_module_lines,
            "average_module_size_lines": int(avg_module_lines),
            "overhead_lines": total_module_lines - total_original_lines,
        }

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Valida que la división sea adecuada.

        Args:
            output_data: Datos de salida

        Returns:
            Lista de errores de guardrails
        """
        errors = []

        modules = output_data.get("modules", [])

        # Guardrail 1: Debe haber al menos 2 módulos
        if len(modules) < 2:
            errors.append(
                f"División ineficaz: solo {len(modules)} módulo(s). "
                f"Se esperan al menos 2."
            )

        # Guardrail 2: Ningún módulo debe ser muy grande
        for module in modules:
            lines = len(module["content"].split('\n'))
            if lines > self.max_lines_per_module * 1.5:
                errors.append(
                    f"Módulo '{module['filename']}' muy grande: {lines} líneas "
                    f"> {self.max_lines_per_module * 1.5} límite"
                )

        # Guardrail 3: Balance razonable entre módulos
        sizes = [len(m["content"].split('\n')) for m in modules]
        if sizes:
            avg = sum(sizes) / len(sizes)
            for i, size in enumerate(sizes):
                if size > avg * 3:  # Módulo 3x más grande que el promedio
                    errors.append(
                        f"Módulo {i} desbalanceado: {size} líneas vs promedio {avg:.0f}"
                    )

        return errors

    # Métodos internos

    def _analyze_sections(self, document: str) -> List[Dict[str, Any]]:
        """
        Analiza la estructura del documento Markdown.

        Args:
            document: Contenido del documento

        Returns:
            Lista de secciones con metadata
        """
        sections = []
        lines = document.split('\n')

        current_section = None
        current_content_lines = []

        for i, line in enumerate(lines):
            # Detectar headers
            header_match = re.match(r'^(#{1,3})\s+(.+)$', line)

            if header_match:
                # Guardar sección anterior si existe
                if current_section:
                    current_section["content"] = '\n'.join(current_content_lines)
                    current_section["end_line"] = i - 1
                    current_section["line_count"] = len(current_content_lines)
                    sections.append(current_section)

                # Iniciar nueva sección
                level = len(header_match.group(1))
                title = header_match.group(2)

                current_section = {
                    "level": level,
                    "title": title,
                    "start_line": i,
                    "header_line": line,
                }
                current_content_lines = [line]
            else:
                # Agregar línea al contenido actual
                if current_section:
                    current_content_lines.append(line)

        # Guardar última sección
        if current_section:
            current_section["content"] = '\n'.join(current_content_lines)
            current_section["end_line"] = len(lines) - 1
            current_section["line_count"] = len(current_content_lines)
            sections.append(current_section)

        return sections

    def _group_into_modules(
        self,
        sections: List[Dict[str, Any]],
        component_name: str
    ) -> List[Dict[str, Any]]:
        """
        Agrupa secciones en módulos lógicos.

        Estrategia:
        - Secciones de nivel 1 (H1) inician nuevo módulo
        - Agrupar hasta alcanzar max_lines_per_module
        - Mantener secciones relacionadas juntas

        Args:
            sections: Lista de secciones
            component_name: Nombre del componente

        Returns:
            Lista de módulos
        """
        modules = []
        current_module_sections = []
        current_module_lines = 0
        module_number = 0

        for section in sections:
            section_lines = section["line_count"]

            # Iniciar nuevo módulo si:
            # 1. Es H1 y ya hay contenido acumulado
            # 2. Supera el límite de líneas
            if current_module_sections and (
                section["level"] == 1 or
                (current_module_lines + section_lines > self.max_lines_per_module)
            ):
                # Guardar módulo actual
                module = self._create_module(
                    module_number,
                    current_module_sections,
                    component_name
                )
                modules.append(module)

                # Resetear para nuevo módulo
                module_number += 1
                current_module_sections = []
                current_module_lines = 0

            # Agregar sección al módulo actual
            current_module_sections.append(section)
            current_module_lines += section_lines

        # Guardar último módulo
        if current_module_sections:
            module = self._create_module(
                module_number,
                current_module_sections,
                component_name
            )
            modules.append(module)

        return modules

    def _create_module(
        self,
        module_number: int,
        sections: List[Dict[str, Any]],
        component_name: str
    ) -> Dict[str, Any]:
        """
        Crea un módulo a partir de secciones.

        Args:
            module_number: Número del módulo
            sections: Secciones que componen el módulo
            component_name: Nombre del componente

        Returns:
            Diccionario con metadata del módulo
        """
        # Generar filename
        first_section_title = sections[0]["title"]
        slug = self._slugify(first_section_title)
        filename = f"{module_number:02d}_{slug}.md"

        # Combinar contenido
        content_parts = [section["content"] for section in sections]
        content = '\n\n'.join(content_parts)

        # Extraer títulos de secciones
        section_titles = [
            f"{'#' * section['level']} {section['title']}"
            for section in sections
        ]

        return {
            "module_number": module_number,
            "filename": filename,
            "title": first_section_title,
            "sections": section_titles,
            "section_count": len(sections),
            "content": content,
            "line_count": len(content.split('\n')),
        }

    def _slugify(self, text: str) -> str:
        """Convierte texto a slug válido para filename."""
        # Remover caracteres especiales
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        # Reemplazar espacios con guiones
        slug = re.sub(r'[\s_]+', '_', slug)
        # Limitar longitud
        slug = slug[:50]
        return slug

    def _generate_cross_references(
        self,
        modules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Genera referencias cruzadas entre módulos.

        Args:
            modules: Lista de módulos

        Returns:
            Lista de referencias cruzadas
        """
        cross_refs = []

        # Generar referencias secuenciales (anterior/siguiente)
        for i, module in enumerate(modules):
            ref = {
                "source_module": i,
                "source_filename": module["filename"],
                "references": {}
            }

            if i > 0:
                ref["references"]["previous"] = {
                    "filename": modules[i-1]["filename"],
                    "title": modules[i-1]["title"]
                }

            if i < len(modules) - 1:
                ref["references"]["next"] = {
                    "filename": modules[i+1]["filename"],
                    "title": modules[i+1]["title"]
                }

            # Referencia al índice maestro
            ref["references"]["index"] = {
                "filename": "00_indice_maestro.md",
                "title": "Índice Maestro"
            }

            cross_refs.append(ref)

        return cross_refs

    def _insert_cross_references(
        self,
        modules: List[Dict[str, Any]],
        cross_refs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Inserta referencias cruzadas en los módulos.

        Args:
            modules: Lista de módulos
            cross_refs: Referencias cruzadas

        Returns:
            Módulos con referencias insertadas
        """
        updated_modules = []

        for i, module in enumerate(modules):
            ref = cross_refs[i]
            refs = ref["references"]

            # Construir sección de navegación
            nav_lines = ["\n---\n", "\n## Navegación\n"]

            if "previous" in refs:
                nav_lines.append(
                    f"**← Anterior:** [{refs['previous']['title']}]({refs['previous']['filename']})\n"
                )

            nav_lines.append(
                f"**↑ Índice:** [{refs['index']['title']}]({refs['index']['filename']})\n"
            )

            if "next" in refs:
                nav_lines.append(
                    f"**→ Siguiente:** [{refs['next']['title']}]({refs['next']['filename']})\n"
                )

            # Insertar navegación al final del módulo
            updated_content = module["content"] + ''.join(nav_lines)

            updated_module = module.copy()
            updated_module["content"] = updated_content

            updated_modules.append(updated_module)

        return updated_modules

    def _create_master_index(
        self,
        modules: List[Dict[str, Any]],
        component_name: str
    ) -> str:
        """
        Crea índice maestro del documento dividido.

        Args:
            modules: Lista de módulos
            component_name: Nombre del componente

        Returns:
            Contenido del índice maestro
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")

        sections = []

        # Header
        sections.append(f"# Índice Maestro: {component_name}\n\n")
        sections.append(f"**Fecha:** {timestamp}\n")
        sections.append(f"**Módulos:** {len(modules)}\n")
        sections.append(
            f"**Total de líneas:** {sum(m['line_count'] for m in modules)}\n\n"
        )

        # Descripción
        sections.append("## Descripción\n\n")
        sections.append(
            "Este documento ha sido dividido en módulos para facilitar "
            "su navegación y mantenimiento.\n\n"
        )

        # Tabla de contenidos
        sections.append("## Tabla de Contenidos\n\n")
        sections.append("| # | Módulo | Secciones | Líneas |\n")
        sections.append("|---|--------|-----------|--------|\n")

        for module in modules:
            sections.append(
                f"| {module['module_number']:02d} | "
                f"[{module['title']}]({module['filename']}) | "
                f"{module['section_count']} | "
                f"{module['line_count']} |\n"
            )

        sections.append("\n")

        # Detalle de módulos
        sections.append("## Detalle de Módulos\n\n")

        for module in modules:
            sections.append(f"### {module['module_number']:02d}. {module['title']}\n\n")
            sections.append(f"**Archivo:** `{module['filename']}`\n\n")
            sections.append("**Secciones incluidas:**\n\n")

            for section_title in module["sections"]:
                sections.append(f"- {section_title}\n")

            sections.append("\n")

        # Footer
        sections.append("---\n\n")
        sections.append(f"**Generado por:** DocumentSplitter\n")
        sections.append(f"**Fecha:** {timestamp}\n")

        return "".join(sections)
