#!/usr/bin/env python3
"""
Project Restrictions Gate

Validates critical project restrictions are followed:
- NO Redis for sessions
- NO Sentry/external monitoring
- NO SMTP/Email
- NO GitHub Actions
- Sessions in database
- Etc.
"""

import sys
import re
from pathlib import Path
from typing import List, Dict


class RestrictionsGate:
    """Gate that validates project restrictions."""

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

    def validate_restrictions(self) -> bool:
        """Validate all project restrictions."""
        self._check_no_redis()
        self._check_no_sentry()
        self._check_no_smtp()
        self._check_no_github_actions()
        self._check_sessions_in_db()

        return len(self.violations) == 0

    def _check_no_redis(self):
        """Check NO Redis usage."""
        settings_file = self.project_root / "api" / "callcentersite" / "callcentersite" / "settings.py"

        if not settings_file.exists():
            return

        content = settings_file.read_text()

        # Check for Redis in CACHES
        if re.search(r"CACHES.*redis", content, re.IGNORECASE | re.DOTALL):
            self.violations.append({
                "type": "redis_forbidden",
                "path": str(settings_file),
                "message": "Redis usage detected - PROJECT RESTRICTION: NO Redis for sessions"
            })

        # Check for redis imports
        if re.search(r"import\s+redis|from\s+redis", content):
            self.violations.append({
                "type": "redis_forbidden",
                "path": str(settings_file),
                "message": "Redis import detected - PROJECT RESTRICTION: NO Redis"
            })

    def _check_no_sentry(self):
        """Check NO Sentry usage."""
        settings_file = self.project_root / "api" / "callcentersite" / "callcentersite" / "settings.py"

        if not settings_file.exists():
            return

        content = settings_file.read_text()

        if re.search(r"sentry", content, re.IGNORECASE):
            self.violations.append({
                "type": "sentry_forbidden",
                "path": str(settings_file),
                "message": "Sentry usage detected - PROJECT RESTRICTION: NO external monitoring"
            })

    def _check_no_smtp(self):
        """Check NO SMTP/Email usage."""
        settings_file = self.project_root / "api" / "callcentersite" / "callcentersite" / "settings.py"

        if not settings_file.exists():
            return

        content = settings_file.read_text()

        if re.search(r"EMAIL_BACKEND|SMTP", content):
            self.violations.append({
                "type": "smtp_forbidden",
                "path": str(settings_file),
                "message": "SMTP/Email detected - PROJECT RESTRICTION: NO Email"
            })

    def _check_no_github_actions(self):
        """Check NO GitHub Actions."""
        github_workflows = self.project_root / ".github" / "workflows"

        if github_workflows.exists():
            yaml_files = list(github_workflows.glob("*.yml")) + list(github_workflows.glob("*.yaml"))

            if yaml_files:
                self.violations.append({
                    "type": "github_actions_forbidden",
                    "path": str(github_workflows),
                    "message": f"GitHub Actions detected ({len(yaml_files)} workflows) - PROJECT RESTRICTION: Use shell scripts in scripts/ci/"
                })

    def _check_sessions_in_db(self):
        """Check sessions are in database."""
        settings_file = self.project_root / "api" / "callcentersite" / "callcentersite" / "settings.py"

        if not settings_file.exists():
            return

        content = settings_file.read_text()

        # Session backend should be database
        if not re.search(r"SESSION_ENGINE.*django\.contrib\.sessions\.backends\.db", content):
            self.violations.append({
                "type": "session_not_in_db",
                "path": str(settings_file),
                "message": "Sessions not in database - PROJECT REQUIREMENT: Sessions must use DB backend"
            })

    def report(self):
        """Print violations report."""
        if not self.violations:
            print("[OK] All project restrictions are followed")
            return

        print(f"[ERROR] Found {len(self.violations)} restriction violations")
        print()

        for v in self.violations:
            print(f"Type: {v['type']}")
            print(f"File: {v['path']}")
            print(f"Message: {v['message']}")
            print()

        print("[!] PROJECT RESTRICTIONS:")
        print("    - NO Redis for sessions")
        print("    - NO Sentry/external monitoring")
        print("    - NO SMTP/Email")
        print("    - NO GitHub Actions (use shell scripts)")
        print("    - Sessions in database (PostgreSQL/MySQL)")


def main():
    """Entry point."""
    gate = RestrictionsGate()

    if gate.validate_restrictions():
        gate.report()
        sys.exit(0)
    else:
        gate.report()
        sys.exit(1)


if __name__ == "__main__":
    main()
