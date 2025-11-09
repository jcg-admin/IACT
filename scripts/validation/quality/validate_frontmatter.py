#!/usr/bin/env python3
"""
Validates YAML frontmatter in Markdown requirement files.

Migrated from: .github/workflows/lint.yml (lines 27-112)
Constitution: Complies with Migration Strategy principles
Version: 1.0.0
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

VERSION = "1.0.0"

EXIT_SUCCESS = 0
EXIT_FAIL = 1
EXIT_WARNING = 2

# Required frontmatter fields
REQUIRED_FIELDS = [
    'id', 'tipo', 'titulo', 'dominio',
    'owner', 'prioridad', 'estado', 'fecha_creacion'
]

# Valid ID format regex
ID_PATTERN = re.compile(r'^(N|RN|RS|RF|RNF)-\d{3}$')


class FrontmatterValidator:
    """Validates YAML frontmatter in Markdown files."""

    def __init__(self, output_format: str = "text", base_path: str = "."):
        self.output_format = output_format
        self.base_path = Path(base_path)
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.valid_count = 0

    def validate_directory(self, directory: Path) -> Tuple[int, int, int]:
        """
        Validates all .md files in directory.

        Returns: (valid_count, error_count, warning_count)
        """
        md_files = self._find_markdown_files(directory)

        for md_file in md_files:
            self._validate_file(md_file)

        return (self.valid_count, len(self.errors), len(self.warnings))

    def _find_markdown_files(self, directory: Path) -> List[Path]:
        """Find all requirement markdown files."""
        files = []
        for root, dirs, filenames in os.walk(directory):
            # Skip if not in requisitos directory
            if 'requisitos' not in root:
                continue

            for filename in filenames:
                # Skip special files
                if filename.endswith('.md') and not filename.startswith('_'):
                    files.append(Path(root) / filename)

        return files

    def _validate_file(self, filepath: Path) -> None:
        """Validate single markdown file."""
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append({
                "file": str(filepath),
                "severity": "ERROR",
                "message": f"Failed to read file: {e}"
            })
            return

        # Check frontmatter exists
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            self.errors.append({
                "file": str(filepath),
                "severity": "ERROR",
                "message": "No frontmatter found"
            })
            return

        yaml_content = match.group(1)
        fields = self._parse_simple_yaml(yaml_content)

        # Check required fields
        missing = [f for f in REQUIRED_FIELDS if f not in fields or not fields[f]]

        if missing:
            self.errors.append({
                "file": str(filepath),
                "severity": "ERROR",
                "message": f"Missing required fields: {', '.join(missing)}",
                "missing_fields": missing
            })
        else:
            self.valid_count += 1

        # Check ID format
        if 'id' in fields:
            req_id = fields['id']
            if not ID_PATTERN.match(req_id):
                self.warnings.append({
                    "file": str(filepath),
                    "severity": "WARNING",
                    "message": f"ID '{req_id}' does not follow standard format (N|RN|RS|RF|RNF)-XXX"
                })

    def _parse_simple_yaml(self, yaml_content: str) -> Dict[str, str]:
        """Simple YAML parser for frontmatter."""
        fields = {}
        for line in yaml_content.split('\n'):
            if ':' in line and not line.startswith(' '):
                key, value = line.split(':', 1)
                fields[key.strip()] = value.strip()
        return fields

    def report(self) -> int:
        """Generate report and return exit code."""
        if self.output_format == "json":
            return self._report_json()
        else:
            return self._report_text()

    def _report_json(self) -> int:
        """JSON report for CI/CD."""
        output = {
            "validator": "validate_frontmatter",
            "version": VERSION,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "valid_files": self.valid_count,
                "errors": len(self.errors),
                "warnings": len(self.warnings)
            },
            "errors": self.errors,
            "warnings": self.warnings
        }

        if len(self.errors) > 0:
            output["status"] = "FAIL"
            output["exit_code"] = EXIT_FAIL
        elif len(self.warnings) > 0:
            output["status"] = "WARNING"
            output["exit_code"] = EXIT_WARNING
        else:
            output["status"] = "PASS"
            output["exit_code"] = EXIT_SUCCESS

        print(json.dumps(output, indent=2))
        return output["exit_code"]

    def _report_text(self) -> int:
        """Human-readable text report."""
        print("Validating requirements frontmatter...")
        print("=" * 80)
        print()

        # Print errors
        if self.errors:
            print("ERRORS:")
            for error in self.errors:
                print(f"  {error['severity']}: {error['file']}")
                print(f"    {error['message']}")
            print()

        # Print warnings
        if self.warnings:
            print("WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning['severity']}: {warning['file']}")
                print(f"    {warning['message']}")
            print()

        # Print summary
        print("Validation Results:")
        print(f"  Valid files: {self.valid_count}")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        print()

        if len(self.errors) > 0:
            print("VALIDATION FAILED")
            return EXIT_FAIL
        else:
            print("VALIDATION PASSED")
            return EXIT_SUCCESS


def main():
    """Entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Validate YAML frontmatter in requirement Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate requirements directory
  %(prog)s --path implementacion/

  # Validate with JSON output
  %(prog)s --path implementacion/ --output json

  # Show version
  %(prog)s --version

Exit Codes:
  0    All files valid
  1    Errors found (missing required fields)
  2    Warnings found (ID format issues)

Required Frontmatter Fields:
  - id, tipo, titulo, dominio, owner, prioridad, estado, fecha_creacion

ID Format:
  - Pattern: (N|RN|RS|RF|RNF)-XXX
  - Examples: N-001, RN-042, RF-123
        """
    )
    parser.add_argument("--path", required=True,
                        help="Base path to search for requirement files")
    parser.add_argument("--output", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {VERSION}")

    args = parser.parse_args()

    # Validate path exists
    path = Path(args.path)
    if not path.exists():
        print(f"ERROR: Path does not exist: {args.path}", file=sys.stderr)
        return EXIT_FAIL

    # Run validation
    validator = FrontmatterValidator(
        output_format=args.output,
        base_path=args.path
    )

    validator.validate_directory(path)
    return validator.report()


if __name__ == "__main__":
    sys.exit(main())
