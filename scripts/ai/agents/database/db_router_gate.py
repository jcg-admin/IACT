#!/usr/bin/env python3
"""
Database Router Gate

Validates that database router never writes to IVR database (read-only restriction).
Critical gate for project compliance.
"""

import sys
import ast
from pathlib import Path
from typing import List, Dict


class DBRouterGate:
    """Gate that validates database router doesn't write to IVR."""

    def __init__(self):
        self.violations = []
        self.project_root = self._find_project_root()

    def _find_project_root(self) -> Path:
        """Find project root."""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists():
                return parent
        return current.parent.parent.parent.parent

    def validate_router(self) -> bool:
        """Validate database router."""
        # Find database router file
        router_file = self.project_root / "api" / "callcentersite" / "callcentersite" / "routers.py"

        if not router_file.exists():
            self.violations.append({
                "type": "router_not_found",
                "path": str(router_file),
                "message": "Database router file not found"
            })
            return False

        # Parse router file
        content = router_file.read_text()
        tree = ast.parse(content)

        # Find IVRRouter class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Router" in node.name:
                self._validate_router_class(node, router_file)

        return len(self.violations) == 0

    def _validate_router_class(self, class_node: ast.ClassDef, file_path: Path):
        """Validate router class methods."""
        # Find db_for_write method
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "db_for_write":
                self._validate_db_for_write(item, file_path)

    def _validate_db_for_write(self, func_node: ast.FunctionDef, file_path: Path):
        """Validate db_for_write never returns 'ivr'."""
        # Check for return statements
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value:
                # Check if return value is 'ivr' string
                if isinstance(node.value, ast.Constant) and node.value.value == 'ivr':
                    self.violations.append({
                        "type": "ivr_write_violation",
                        "path": str(file_path),
                        "line": node.lineno,
                        "message": "CRITICAL: db_for_write returns 'ivr' - IVR database is READ-ONLY"
                    })

                # Check for conditional returns with 'ivr'
                elif isinstance(node.value, ast.IfExp):
                    if self._contains_ivr_return(node.value):
                        self.violations.append({
                            "type": "ivr_write_violation",
                            "path": str(file_path),
                            "line": node.lineno,
                            "message": "CRITICAL: db_for_write may return 'ivr' - IVR database is READ-ONLY"
                        })

    def _contains_ivr_return(self, node) -> bool:
        """Check if node contains 'ivr' return."""
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and child.value == 'ivr':
                return True
        return False

    def report(self):
        """Print violations report."""
        if not self.violations:
            print("[OK] Database router is compliant (IVR is READ-ONLY)")
            return

        print(f"[CRITICAL] Found {len(self.violations)} database router violations")
        print()

        for v in self.violations:
            severity = "CRITICAL" if v['type'] == 'ivr_write_violation' else "ERROR"
            print(f"[{severity}] {v['type']}")
            print(f"  File: {v['path']}")
            if 'line' in v:
                print(f"  Line: {v['line']}")
            print(f"  Message: {v['message']}")
            print()

        print("[!] REMINDER: BD IVR (MySQL) is READ-ONLY")
        print("[!] REMINDER: BD Analytics (PostgreSQL) is READ/WRITE")


def main():
    """Entry point."""
    gate = DBRouterGate()

    if gate.validate_router():
        gate.report()
        sys.exit(0)
    else:
        gate.report()
        sys.exit(1)


if __name__ == "__main__":
    main()
