#!/usr/bin/env python3
"""
Emoji Lint Gate

Validates that NO emojis are used in code or documentation.
Project restriction: NO emojis/icons.
"""

import sys
import re
from pathlib import Path
from typing import List, Dict


class EmojiLintGate:
    """Gate that validates no emojis in project files."""

    def __init__(self):
        self.violations = []
        self.project_root = self._find_project_root()

        # Emoji pattern
        self.emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251]+",
            flags=re.UNICODE
        )

    def _find_project_root(self) -> Path:
        """Find project root."""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists():
                return parent
        return current.parent.parent.parent.parent

    def validate_no_emojis(self) -> bool:
        """Validate no emojis in project."""
        # Scan documentation
        docs_files = list((self.project_root / "docs").rglob("*.md"))

        for doc_file in docs_files:
            self._check_file_for_emojis(doc_file)

        # Scan Python files
        python_files = list((self.project_root / "api").rglob("*.py"))
        python_files += list((self.project_root / "scripts").rglob("*.py"))

        for py_file in python_files:
            # Skip migrations
            if "migrations" in str(py_file):
                continue
            self._check_file_for_emojis(py_file)

        # Scan shell scripts
        shell_files = list((self.project_root / "scripts").rglob("*.sh"))

        for sh_file in shell_files:
            self._check_file_for_emojis(sh_file)

        return len(self.violations) == 0

    def _check_file_for_emojis(self, file_path: Path):
        """Check single file for emojis."""
        try:
            content = file_path.read_text()
        except UnicodeDecodeError:
            # Skip binary files
            return

        matches = list(self.emoji_pattern.finditer(content))

        if matches:
            for match in matches:
                # Find line number
                line_num = content[:match.start()].count('\n') + 1

                self.violations.append({
                    "type": "emoji_found",
                    "path": str(file_path.relative_to(self.project_root)),
                    "line": line_num,
                    "emoji": match.group(),
                    "message": f"Emoji found: {match.group()}"
                })

    def report(self):
        """Print violations report."""
        if not self.violations:
            print("[OK] No emojis found (project restriction complied)")
            return

        print(f"[ERROR] Found {len(self.violations)} emoji violations")
        print()

        for v in self.violations:
            print(f"File: {v['path']}:{v['line']}")
            print(f"Emoji: {v['emoji']}")
            print(f"Message: {v['message']}")
            print()

        print("[!] PROJECT RESTRICTION: NO emojis/icons allowed")
        print("[!] Use text equivalents: [OK], [ERROR], [WARNING], [HIGH], [MEDIUM], [LOW]")


def main():
    """Entry point."""
    gate = EmojiLintGate()

    if gate.validate_no_emojis():
        gate.report()
        sys.exit(0)
    else:
        gate.report()
        sys.exit(1)


if __name__ == "__main__":
    main()
