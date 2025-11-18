#!/usr/bin/env python3
# Script: validate_frontmatter.py
# Proposito: Validar frontmatter YAML en archivos markdown
# Uso: python3 validate_frontmatter.py <directorio> [--json] [--strict]
# Ejemplo: python3 scripts/qa/validate_frontmatter.py /home/user/IACT/docs/infraestructura

import os
import sys
import yaml
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Colores
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# Campos requeridos y valores validos
REQUIRED_FIELDS = ['id', 'tipo', 'categoria', 'titulo', 'estado']
VALID_TIPOS = [
    'tarea', 'documentacion', 'adr', 'procedimiento',
    'tarea_preparacion', 'indice_tareas', 'guia', 'plantilla'
]
VALID_ESTADOS = ['pendiente', 'en_progreso', 'completada', 'archivado']

class FrontmatterValidator:
    def __init__(self, target_dir, verbose=False, strict=False, json_output=False):
        self.target_dir = target_dir
        self.verbose = verbose
        self.strict = strict
        self.json_output = json_output

        self.valid_count = 0
        self.error_count = 0
        self.no_frontmatter_count = 0
        self.file_errors = []
        self.duplicate_ids = defaultdict(list)
        self.processed_files = 0

    def extract_frontmatter(self, file_path):
        """Extrae frontmatter YAML de archivo markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return None, f"Error leyendo archivo: {e}"

        # Buscar frontmatter entre --- ---
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None, "Sin frontmatter YAML"

        try:
            fm = yaml.safe_load(match.group(1))
            return fm, None
        except yaml.YAMLError as e:
            return None, f"YAML invalido: {str(e).split(chr(10))[0]}"

    def validate_frontmatter(self, file_path, frontmatter):
        """Valida estructura del frontmatter"""
        errors = []

        if not isinstance(frontmatter, dict):
            return ["Frontmatter no es diccionario YAML valido"]

        # Validar campos requeridos
        for field in REQUIRED_FIELDS:
            if field not in frontmatter:
                errors.append(f"Falta campo requerido: '{field}'")
            elif frontmatter[field] is None or str(frontmatter[field]).strip() == '':
                errors.append(f"Campo vacio: '{field}'")

        # Validar tipo
        if 'tipo' in frontmatter and frontmatter['tipo']:
            if frontmatter['tipo'] not in VALID_TIPOS:
                errors.append(
                    f"Tipo invalido: '{frontmatter['tipo']}' "
                    f"(permitidos: {', '.join(VALID_TIPOS[:3])}...)"
                )

        # Validar estado
        if 'estado' in frontmatter and frontmatter['estado']:
            if frontmatter['estado'] not in VALID_ESTADOS:
                errors.append(
                    f"Estado invalido: '{frontmatter['estado']}' "
                    f"(permitidos: {', '.join(VALID_ESTADOS)})"
                )

        return errors

    def process_directory(self):
        """Procesa todos los archivos markdown en directorio"""
        for root, dirs, files in os.walk(self.target_dir):
            for file in sorted(files):
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    self.processed_files += 1
                    self._process_file(file_path)

    def _process_file(self, file_path):
        """Procesa archivo individual"""
        rel_path = os.path.relpath(file_path, self.target_dir)

        if self.verbose:
            print(f"{BLUE}[PROCESANDO]{NC} {rel_path}")

        fm, extract_error = self.extract_frontmatter(file_path)

        if extract_error:
            self.error_count += 1
            self.file_errors.append({
                'file': rel_path,
                'error': extract_error,
                'type': 'extract'
            })
            if self.verbose:
                print(f"  {RED}[ERROR]{NC} {extract_error}")
            return

        # Validar contenido
        validation_errors = self.validate_frontmatter(file_path, fm)

        if validation_errors:
            self.error_count += 1
            for err in validation_errors:
                self.file_errors.append({
                    'file': rel_path,
                    'error': err,
                    'type': 'validation'
                })
            if self.verbose:
                print(f"  {RED}[ERRORES]{NC}")
                for err in validation_errors:
                    print(f"    - {err}")
        else:
            self.valid_count += 1
            if self.verbose:
                print(f"  {GREEN}[OK]{NC} Frontmatter valido")

        # Track IDs para detectar duplicados
        if 'id' in fm and fm['id']:
            self.duplicate_ids[fm['id']].append(rel_path)

    def get_duplicate_ids(self):
        """Retorna dict de IDs duplicados"""
        return {k: v for k, v in self.duplicate_ids.items() if len(v) > 1}

    def print_report(self):
        """Imprime reporte de validacion"""
        if self.json_output:
            self._print_json_report()
        else:
            self._print_text_report()

    def _print_text_report(self):
        """Imprime reporte en texto"""
        print("")
        print(f"{GREEN}==============================================={NC}")
        print(f"{GREEN}REPORTE DE VALIDACION DE FRONTMATTER YAML{NC}")
        print(f"{GREEN}==============================================={NC}")

        print(f"{GREEN}Archivos procesados:${NC} {self.processed_files}")
        print(f"{GREEN}Frontmatter valido:${NC} {self.valid_count}")

        if self.error_count > 0:
            print(f"{RED}Archivos con errores:${NC} {self.error_count}")

        # Mostrar errores de extraccion
        extract_errors = [e for e in self.file_errors if e['type'] == 'extract']
        if extract_errors:
            print(f"\n{RED}Archivos sin frontmatter YAML:{NC}")
            for err_info in extract_errors:
                print(f"  - {err_info['file']}")

        # Mostrar errores de validacion
        validation_errors = [e for e in self.file_errors if e['type'] == 'validation']
        if validation_errors:
            print(f"\n{RED}Problemas en frontmatter:{NC}")
            for err_info in validation_errors:
                print(f"  - {err_info['file']}: {err_info['error']}")

        # Mostrar IDs duplicados
        duplicates = self.get_duplicate_ids()
        if duplicates:
            print(f"\n{RED}IDs duplicados:{NC}")
            for id_val, paths in sorted(duplicates.items()):
                print(f"  - ID '{id_val}' en {len(paths)} archivos:")
                for path in paths:
                    print(f"    * {path}")

        print("")
        print(f"{GREEN}==============================================={NC}")

        if self.error_count == 0 and not duplicates:
            print(f"{GREEN}RESULTADO: Todas las validaciones pasaron correctamente{NC}")
        else:
            total_issues = self.error_count + len(duplicates)
            print(f"{RED}RESULTADO: {total_issues} problemas encontrados{NC}")

    def _print_json_report(self):
        """Imprime reporte en JSON"""
        duplicates = self.get_duplicate_ids()

        report = {
            'timestamp': datetime.now().isoformat(),
            'directory': self.target_dir,
            'summary': {
                'total_files': self.processed_files,
                'valid': self.valid_count,
                'errors': self.error_count,
                'duplicate_ids': len(duplicates)
            },
            'errors': self.file_errors,
            'duplicates': {k: v for k, v in duplicates.items()}
        }

        print(json.dumps(report, indent=2, ensure_ascii=False))

    def is_valid(self):
        """Retorna True si todas las validaciones pasaron"""
        duplicates = self.get_duplicate_ids()
        return self.error_count == 0 and len(duplicates) == 0


def main():
    parser = argparse.ArgumentParser(
        description='Validador de frontmatter YAML en archivos markdown'
    )
    parser.add_argument('directory', help='Directorio a validar')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar detalles')
    parser.add_argument('-j', '--json', action='store_true', help='Output en JSON')
    parser.add_argument('-s', '--strict', action='store_true', help='Modo strict')

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"{RED}ERROR: Directorio no existe: {args.directory}{NC}")
        sys.exit(1)

    if args.verbose:
        print(f"{GREEN}[INFO] Validando frontmatter YAML en: {args.directory}{NC}")

    validator = FrontmatterValidator(
        args.directory,
        verbose=args.verbose,
        strict=args.strict,
        json_output=args.json
    )

    validator.process_directory()
    validator.print_report()

    sys.exit(0 if validator.is_valid() else 1)


if __name__ == "__main__":
    main()
