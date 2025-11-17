#!/usr/bin/env python3
"""
Script: generar-matriz-trazabilidad.py
Descripción: Genera matrices de trazabilidad entre artefactos de requisitos
Autor: Claude Code (Sonnet 4.5)
Fecha: 2025-11-17
Versión: 1.0.0
Basado en: ADR-GOB-009 - Trazabilidad entre Artefactos de Requisitos

Este script analiza archivos markdown de requisitos y genera matrices de
trazabilidad en diferentes formatos para visualizar relaciones entre artefactos.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime


# Tipos de artefactos válidos
TIPOS_VALIDOS = ['RN', 'RNEG', 'UC', 'RF', 'RNF']
DOMINIOS_VALIDOS = ['BACK', 'FRONT', 'DEVOPS', 'QA', 'AI', 'GOB']

# Patrón regex para IDs: TIPO-DOMINIO-###
ID_PATTERN = re.compile(r'(RN|RNEG|UC|RF|RNF)-(BACK|FRONT|DEVOPS|QA|AI|GOB)-(\d{3})')


class Artefacto:
    """Representa un artefacto de requisitos con su ID y referencias."""

    def __init__(self, id: str, archivo: Path, titulo: str = ""):
        self.id = id
        self.archivo = archivo
        self.titulo = titulo
        self.tipo, self.dominio, self.numero = self._parse_id(id)
        self.referencias: Set[str] = set()
        self.referenciado_por: Set[str] = set()

    def _parse_id(self, id: str) -> Tuple[str, str, str]:
        """Parse ID en componentes: tipo, dominio, número."""
        match = ID_PATTERN.match(id)
        if match:
            return match.group(1), match.group(2), match.group(3)
        return "", "", ""

    def agregar_referencia(self, ref_id: str):
        """Agrega una referencia saliente."""
        self.referencias.add(ref_id)

    def agregar_referenciado_por(self, ref_id: str):
        """Agrega una referencia entrante."""
        self.referenciado_por.add(ref_id)

    def __repr__(self):
        return f"Artefacto({self.id}, refs={len(self.referencias)}, ref_by={len(self.referenciado_por)})"


class GrafoTrazabilidad:
    """Grafo de trazabilidad entre artefactos de requisitos."""

    def __init__(self, requisitos_dir: Path):
        self.requisitos_dir = requisitos_dir
        self.artefactos: Dict[str, Artefacto] = {}
        self._cargar_artefactos()
        self._construir_referencias()

    def _cargar_artefactos(self):
        """Escanea directorio y carga todos los artefactos."""
        if not self.requisitos_dir.exists():
            print(f"ERROR: Directorio no existe: {self.requisitos_dir}", file=sys.stderr)
            sys.exit(1)

        archivos_md = list(self.requisitos_dir.rglob("*.md"))
        print(f"Escaneando {len(archivos_md)} archivos markdown...", file=sys.stderr)

        for archivo in archivos_md:
            id_artefacto = self._extraer_id_de_archivo(archivo)
            if id_artefacto:
                titulo = self._extraer_titulo(archivo)
                self.artefactos[id_artefacto] = Artefacto(id_artefacto, archivo, titulo)

        print(f"Artefactos cargados: {len(self.artefactos)}", file=sys.stderr)

    def _extraer_id_de_archivo(self, archivo: Path) -> Optional[str]:
        """Extrae ID del frontmatter, nombre o título del archivo."""
        try:
            contenido = archivo.read_text(encoding='utf-8')

            # Buscar en frontmatter (id: XXX)
            match = re.search(r'^id:\s*([A-Z0-9-]+)', contenido, re.MULTILINE)
            if match:
                id_candidato = match.group(1)
                if ID_PATTERN.match(id_candidato):
                    return id_candidato

            # Buscar en nombre de archivo
            match = ID_PATTERN.search(archivo.name)
            if match:
                return match.group(0)

            # Buscar en título (# TIPO-DOMINIO-###: ...)
            match = re.search(r'^#\s+(' + ID_PATTERN.pattern + r')', contenido, re.MULTILINE)
            if match:
                return match.group(1)

        except Exception as e:
            print(f"WARNING: Error leyendo {archivo}: {e}", file=sys.stderr)

        return None

    def _extraer_titulo(self, archivo: Path) -> str:
        """Extrae el título del artefacto."""
        try:
            contenido = archivo.read_text(encoding='utf-8')

            # Buscar primer título markdown
            match = re.search(r'^#\s+(.+)$', contenido, re.MULTILINE)
            if match:
                titulo = match.group(1).strip()
                # Remover ID si está al inicio
                titulo = re.sub(r'^[A-Z0-9-]+:\s*', '', titulo)
                return titulo[:80]  # Limitar longitud
        except:
            pass

        return ""

    def _construir_referencias(self):
        """Construye el grafo de referencias entre artefactos."""
        print("Construyendo grafo de referencias...", file=sys.stderr)

        for id_artefacto, artefacto in self.artefactos.items():
            try:
                contenido = artefacto.archivo.read_text(encoding='utf-8')

                # Buscar todas las referencias a otros IDs
                referencias = ID_PATTERN.findall(contenido)

                for tipo, dominio, numero in referencias:
                    ref_id = f"{tipo}-{dominio}-{numero}"

                    # No agregar auto-referencias
                    if ref_id != id_artefacto:
                        artefacto.agregar_referencia(ref_id)

                        # Agregar referencia inversa si el artefacto existe
                        if ref_id in self.artefactos:
                            self.artefactos[ref_id].agregar_referenciado_por(id_artefacto)

            except Exception as e:
                print(f"WARNING: Error procesando {artefacto.archivo}: {e}", file=sys.stderr)

        total_refs = sum(len(a.referencias) for a in self.artefactos.values())
        print(f"Referencias totales: {total_refs}", file=sys.stderr)

    def filtrar_por_dominio(self, dominio: str) -> Dict[str, Artefacto]:
        """Filtra artefactos por dominio."""
        return {id: art for id, art in self.artefactos.items() if art.dominio == dominio}

    def obtener_artefacto(self, id: str) -> Optional[Artefacto]:
        """Obtiene un artefacto por su ID."""
        return self.artefactos.get(id)


class GeneradorMatriz:
    """Genera matrices de trazabilidad en formato Markdown."""

    def __init__(self, grafo: GrafoTrazabilidad):
        self.grafo = grafo

    def generar_matriz_vertical(self, dominio: Optional[str] = None) -> str:
        """
        Genera matriz vertical: RN → RNEG → UC → RF → RNF

        Args:
            dominio: Dominio a filtrar (BACK, FRONT, etc.) o None para todos

        Returns:
            String con la matriz en formato Markdown
        """
        artefactos = self.grafo.artefactos
        if dominio:
            artefactos = self.grafo.filtrar_por_dominio(dominio)

        # Agrupar por tipo
        por_tipo = defaultdict(list)
        for id, art in artefactos.items():
            por_tipo[art.tipo].append(art)

        # Ordenar cada grupo
        for tipo in por_tipo:
            por_tipo[tipo].sort(key=lambda a: a.id)

        # Construir matriz
        output = []
        output.append(f"# Matriz de Trazabilidad Vertical")
        if dominio:
            output.append(f"**Dominio:** {dominio}")
        output.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        output.append("Esta matriz muestra la cadena de trazabilidad vertical desde reglas de negocio hasta atributos de calidad.")
        output.append("")

        # Estadísticas
        output.append("## Estadísticas")
        output.append("")
        output.append("| Tipo | Cantidad |")
        output.append("|------|----------|")
        for tipo in ['RN', 'RNEG', 'UC', 'RF', 'RNF']:
            cantidad = len(por_tipo.get(tipo, []))
            output.append(f"| {tipo} | {cantidad} |")
        output.append("")

        # Matriz principal
        output.append("## Matriz de Relaciones")
        output.append("")
        output.append("| RN | RNEG | UC | RF | RNF |")
        output.append("|----|------|----|----|-----|")

        # Crear filas de la matriz
        max_count = max(len(por_tipo.get(t, [])) for t in ['RN', 'RNEG', 'UC', 'RF', 'RNF'])

        for i in range(max_count):
            fila = []
            for tipo in ['RN', 'RNEG', 'UC', 'RF', 'RNF']:
                artefactos_tipo = por_tipo.get(tipo, [])
                if i < len(artefactos_tipo):
                    art = artefactos_tipo[i]
                    fila.append(f"{art.id}")
                else:
                    fila.append("")
            output.append("| " + " | ".join(fila) + " |")

        output.append("")

        # Detalles de cada artefacto
        output.append("## Detalles de Artefactos")
        output.append("")

        for tipo in ['RN', 'RNEG', 'UC', 'RF', 'RNF']:
            artefactos_tipo = por_tipo.get(tipo, [])
            if artefactos_tipo:
                output.append(f"### {tipo}")
                output.append("")
                for art in artefactos_tipo:
                    output.append(f"**{art.id}**: {art.titulo}")
                    if art.referencias:
                        refs = sorted(art.referencias)
                        output.append(f"  - Referencias: {', '.join(refs)}")
                    if art.referenciado_por:
                        refs_by = sorted(art.referenciado_por)
                        output.append(f"  - Referenciado por: {', '.join(refs_by)}")
                    output.append("")

        return "\n".join(output)

    def generar_matriz_horizontal(self, id_artefacto: str) -> str:
        """
        Genera matriz horizontal para un artefacto específico.

        Args:
            id_artefacto: ID del artefacto (ej: UC-BACK-001)

        Returns:
            String con la matriz en formato Markdown
        """
        artefacto = self.grafo.obtener_artefacto(id_artefacto)

        if not artefacto:
            return f"ERROR: Artefacto no encontrado: {id_artefacto}"

        output = []
        output.append(f"# Matriz de Trazabilidad: {id_artefacto}")
        output.append(f"**Título:** {artefacto.titulo}")
        output.append(f"**Archivo:** {artefacto.archivo.name}")
        output.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        output.append("Esta matriz muestra todos los artefactos relacionados con este elemento.")
        output.append("")

        # Referencias que hace este artefacto
        output.append("## Referencias Salientes")
        output.append("")
        output.append("Artefactos referenciados por este elemento:")
        output.append("")

        if artefacto.referencias:
            output.append("| ID | Tipo | Título |")
            output.append("|----|------|--------|")

            for ref_id in sorted(artefacto.referencias):
                ref_art = self.grafo.obtener_artefacto(ref_id)
                if ref_art:
                    output.append(f"| {ref_id} | {ref_art.tipo} | {ref_art.titulo} |")
                else:
                    output.append(f"| {ref_id} | ? | *(no encontrado)* |")
        else:
            output.append("*No hay referencias salientes.*")

        output.append("")

        # Referencias entrantes (quién referencia a este artefacto)
        output.append("## Referencias Entrantes")
        output.append("")
        output.append("Artefactos que referencian este elemento:")
        output.append("")

        if artefacto.referenciado_por:
            output.append("| ID | Tipo | Título |")
            output.append("|----|------|--------|")

            for ref_id in sorted(artefacto.referenciado_por):
                ref_art = self.grafo.obtener_artefacto(ref_id)
                if ref_art:
                    output.append(f"| {ref_id} | {ref_art.tipo} | {ref_art.titulo} |")
                else:
                    output.append(f"| {ref_id} | ? | *(no encontrado)* |")
        else:
            output.append("*No hay referencias entrantes.*")

        output.append("")

        # Árbol de trazabilidad (análisis profundo)
        output.append("## Árbol de Trazabilidad")
        output.append("")
        output.append("### Cadena Ascendente (Por qué existe)")
        output.append("")
        self._agregar_cadena_ascendente(output, artefacto, nivel=0, visitados=set())
        output.append("")

        output.append("### Cadena Descendente (Qué implementa)")
        output.append("")
        self._agregar_cadena_descendente(output, artefacto, nivel=0, visitados=set())
        output.append("")

        return "\n".join(output)

    def _agregar_cadena_ascendente(self, output: List[str], artefacto: Artefacto, nivel: int, visitados: Set[str]):
        """Agrega cadena ascendente de trazabilidad (hacia arriba en la jerarquía)."""
        if artefacto.id in visitados or nivel > 5:  # Evitar ciclos y profundidad excesiva
            return

        visitados.add(artefacto.id)
        indent = "  " * nivel

        # Buscar referencias a tipos de nivel superior
        tipos_superiores = {
            'RNF': ['RF', 'UC', 'RNEG', 'RN'],
            'RF': ['UC', 'RNEG', 'RN'],
            'UC': ['RNEG', 'RN'],
            'RNEG': ['RN'],
            'RN': []
        }

        refs_superiores = []
        for ref_id in artefacto.referencias:
            ref_art = self.grafo.obtener_artefacto(ref_id)
            if ref_art and ref_art.tipo in tipos_superiores.get(artefacto.tipo, []):
                refs_superiores.append(ref_art)

        if refs_superiores:
            for ref_art in sorted(refs_superiores, key=lambda a: a.id):
                output.append(f"{indent}- **{ref_art.id}**: {ref_art.titulo}")
                self._agregar_cadena_ascendente(output, ref_art, nivel + 1, visitados)
        elif nivel == 0:
            output.append(f"{indent}*(Sin referencias a niveles superiores)*")

    def _agregar_cadena_descendente(self, output: List[str], artefacto: Artefacto, nivel: int, visitados: Set[str]):
        """Agrega cadena descendente de trazabilidad (hacia abajo en la jerarquía)."""
        if artefacto.id in visitados or nivel > 5:
            return

        visitados.add(artefacto.id)
        indent = "  " * nivel

        # Buscar referencias de tipos de nivel inferior
        tipos_inferiores = {
            'RN': ['RNEG', 'UC', 'RF', 'RNF'],
            'RNEG': ['UC', 'RF', 'RNF'],
            'UC': ['RF', 'RNF'],
            'RF': ['RNF'],
            'RNF': []
        }

        refs_inferiores = []
        for ref_id in artefacto.referenciado_por:
            ref_art = self.grafo.obtener_artefacto(ref_id)
            if ref_art and ref_art.tipo in tipos_inferiores.get(artefacto.tipo, []):
                refs_inferiores.append(ref_art)

        if refs_inferiores:
            for ref_art in sorted(refs_inferiores, key=lambda a: a.id):
                output.append(f"{indent}- **{ref_art.id}**: {ref_art.titulo}")
                self._agregar_cadena_descendente(output, ref_art, nivel + 1, visitados)
        elif nivel == 0:
            output.append(f"{indent}*(Sin implementaciones en niveles inferiores)*")

    def generar_matriz_dominio(self, dominio: str, output_file: Optional[Path] = None) -> str:
        """
        Genera matriz completa para un dominio específico.

        Args:
            dominio: Dominio (BACK, FRONT, etc.)
            output_file: Ruta del archivo de salida (opcional)

        Returns:
            String con la matriz en formato Markdown
        """
        artefactos = self.grafo.filtrar_por_dominio(dominio)

        if not artefactos:
            return f"ERROR: No hay artefactos para el dominio {dominio}"

        output = []
        output.append(f"# Matriz de Trazabilidad - Dominio {dominio}")
        output.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**Total de artefactos:** {len(artefactos)}")
        output.append("")

        # Tabla de contenidos
        output.append("## Tabla de Contenidos")
        output.append("")
        output.append("1. [Resumen Ejecutivo](#resumen-ejecutivo)")
        output.append("2. [Matriz Vertical](#matriz-vertical)")
        output.append("3. [Artefactos por Tipo](#artefactos-por-tipo)")
        output.append("4. [Análisis de Cobertura](#analisis-de-cobertura)")
        output.append("")

        # Resumen ejecutivo
        output.append("## Resumen Ejecutivo")
        output.append("")

        por_tipo = defaultdict(list)
        for id, art in artefactos.items():
            por_tipo[art.tipo].append(art)

        output.append("| Tipo | Cantidad | Descripción |")
        output.append("|------|----------|-------------|")
        descripciones = {
            'RN': 'Reglas de Negocio',
            'RNEG': 'Requerimientos de Negocio',
            'UC': 'Casos de Uso',
            'RF': 'Requisitos Funcionales',
            'RNF': 'Atributos de Calidad'
        }
        for tipo in ['RN', 'RNEG', 'UC', 'RF', 'RNF']:
            cantidad = len(por_tipo[tipo])
            desc = descripciones.get(tipo, '')
            output.append(f"| {tipo} | {cantidad} | {desc} |")
        output.append("")

        # Matriz vertical
        output.append("## Matriz Vertical")
        output.append("")
        matriz_vertical = self.generar_matriz_vertical(dominio)
        # Extraer solo la tabla de la matriz vertical
        lineas_matriz = matriz_vertical.split('\n')
        en_tabla = False
        for linea in lineas_matriz:
            if linea.startswith('| RN |'):
                en_tabla = True
            if en_tabla:
                output.append(linea)
                if linea == '':
                    break
        output.append("")

        # Artefactos por tipo
        output.append("## Artefactos por Tipo")
        output.append("")

        for tipo in ['RN', 'RNEG', 'UC', 'RF', 'RNF']:
            artefactos_tipo = por_tipo[tipo]
            if artefactos_tipo:
                output.append(f"### {tipo} - {descripciones[tipo]}")
                output.append("")
                output.append("| ID | Título | Referencias | Referenciado Por |")
                output.append("|----|--------|-------------|------------------|")

                for art in sorted(artefactos_tipo, key=lambda a: a.id):
                    num_refs = len(art.referencias)
                    num_ref_by = len(art.referenciado_por)
                    output.append(f"| {art.id} | {art.titulo} | {num_refs} | {num_ref_by} |")
                output.append("")

        # Análisis de cobertura
        output.append("## Análisis de Cobertura")
        output.append("")

        # Identificar artefactos sin referencias
        sin_refs_salientes = [a for a in artefactos.values() if not a.referencias]
        sin_refs_entrantes = [a for a in artefactos.values() if not a.referenciado_por]

        output.append("### Artefactos Sin Referencias Salientes")
        output.append("")
        if sin_refs_salientes:
            for art in sorted(sin_refs_salientes, key=lambda a: a.id):
                output.append(f"- **{art.id}**: {art.titulo}")
        else:
            output.append("*Todos los artefactos tienen referencias salientes.*")
        output.append("")

        output.append("### Artefactos Sin Referencias Entrantes (Huérfanos)")
        output.append("")
        if sin_refs_entrantes:
            for art in sorted(sin_refs_entrantes, key=lambda a: a.id):
                output.append(f"- **{art.id}**: {art.titulo}")
        else:
            output.append("*Todos los artefactos tienen referencias entrantes.*")
        output.append("")

        resultado = "\n".join(output)

        # Escribir a archivo si se especificó
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(resultado, encoding='utf-8')
            print(f"Matriz generada: {output_file}", file=sys.stderr)

        return resultado


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Genera matrices de trazabilidad entre artefactos de requisitos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s --tipo vertical --dominio BACK
  %(prog)s --tipo horizontal --id UC-BACK-001
  %(prog)s --tipo dominio --dominio BACK --output docs/gobernanza/trazabilidad/matrices/MATRIZ-BACK.md

Basado en:
  ADR-GOB-009: Trazabilidad entre Artefactos de Requisitos
        """
    )

    parser.add_argument(
        '--tipo',
        choices=['vertical', 'horizontal', 'dominio'],
        required=True,
        help='Tipo de matriz a generar'
    )

    parser.add_argument(
        '--dominio',
        choices=DOMINIOS_VALIDOS,
        help='Dominio a analizar (requerido para tipo vertical y dominio)'
    )

    parser.add_argument(
        '--id',
        help='ID del artefacto para matriz horizontal (ej: UC-BACK-001)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Archivo de salida (default: stdout)'
    )

    parser.add_argument(
        '--dir',
        type=Path,
        default=Path('docs/gobernanza/requisitos'),
        help='Directorio de requisitos (default: docs/gobernanza/requisitos)'
    )

    args = parser.parse_args()

    # Validaciones
    if args.tipo in ['vertical', 'dominio'] and not args.dominio:
        parser.error(f"--dominio es requerido para tipo {args.tipo}")

    if args.tipo == 'horizontal' and not args.id:
        parser.error("--id es requerido para tipo horizontal")

    if args.tipo == 'horizontal' and args.id:
        if not ID_PATTERN.match(args.id):
            parser.error(f"Formato de ID inválido: {args.id}")

    # Construir grafo de trazabilidad
    print(f"Construyendo grafo de trazabilidad desde {args.dir}...", file=sys.stderr)
    grafo = GrafoTrazabilidad(args.dir)

    # Generar matriz
    generador = GeneradorMatriz(grafo)

    if args.tipo == 'vertical':
        resultado = generador.generar_matriz_vertical(args.dominio)
    elif args.tipo == 'horizontal':
        resultado = generador.generar_matriz_horizontal(args.id)
    elif args.tipo == 'dominio':
        resultado = generador.generar_matriz_dominio(args.dominio, args.output)

    # Output
    if args.output and args.tipo != 'dominio':
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(resultado, encoding='utf-8')
        print(f"Matriz generada: {args.output}", file=sys.stderr)
    elif args.tipo != 'dominio':
        print(resultado)

    print("\nGeneración completada exitosamente.", file=sys.stderr)


if __name__ == '__main__':
    main()
