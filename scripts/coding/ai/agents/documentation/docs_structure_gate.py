#!/usr/bin/env python3
"""
Documentation Structure Gate

Validates that documentation follows expected structure and conventions.
"""

import sys
from pathlib import Path
from typing import List, Dict
import re


class DocsStructureGate:
    """Gate that validates documentation structure."""

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

    def validate_structure(self) -> bool:
        """Validate docs structure."""
        docs_root = self.project_root / "docs"

        if not docs_root.exists():
            self.violations.append({
                "type": "missing_directory",
                "path": str(docs_root),
                "message": "docs/ directory not found"
            })
            return False

        # Check required directories
        required_dirs = [
            "backend",
            "backend/permisos",
            "backend/permisos/promptops"
        ]

        for req_dir in required_dirs:
            dir_path = docs_root / req_dir
            if not dir_path.exists():
                self.violations.append({
                    "type": "missing_directory",
                    "path": str(dir_path),
                    "message": f"Required directory missing: {req_dir}"
                })

        # Check markdown files have proper structure
        md_files = list(docs_root.rglob("*.md"))

        for md_file in md_files:
            self._validate_markdown_file(md_file)

        return len(self.violations) == 0

    def _validate_markdown_file(self, md_file: Path):
        """Validate individual markdown file."""
        content = md_file.read_text()

        # Check 1: Has title (# heading)
        if not re.search(r'^# .+', content, re.MULTILINE):
            self.violations.append({
                "type": "missing_title",
                "path": str(md_file),
                "message": "Markdown file missing H1 title"
            })

        # Check 2: No emojis
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251]+",
            flags=re.UNICODE
        )

        if emoji_pattern.search(content):
            self.violations.append({
                "type": "emoji_found",
                "path": str(md_file),
                "message": "Emoji found in documentation (project restriction)"
            })

        # Check 3: Valid internal links
        internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for link_text, link_url in internal_links:
            if link_url.startswith(('http://', 'https://', '#')):
                continue  # External or anchor link

            # Resolve relative link
            target = (md_file.parent / link_url).resolve()

            if not target.exists():
                self.violations.append({
                    "type": "broken_link",
                    "path": str(md_file),
                    "message": f"Broken link: {link_url} (target not found)"
                })

    def report(self):
        """Print violations report."""
        if not self.violations:
            print("[OK] Documentation structure is valid")
            return

        print(f"[ERROR] Found {len(self.violations)} documentation violations")
        print()

        for v in self.violations:
            print(f"Type: {v['type']}")
            print(f"File: {v['path']}")
            print(f"Message: {v['message']}")
            print()


def main():
    """Entry point."""
    gate = DocsStructureGate()

    if gate.validate_structure():
        gate.report()
        sys.exit(0)
    else:
        gate.report()
        sys.exit(1)


if __name__ == "__main__":
    main()
