#!/usr/bin/env python3
"""
Documentation Naming Agent

Automatically standardizes documentation file naming according to ADR-021
conventions and Clean Code principles.

Usage:
    python documentation_naming_agent.py --execute-all
    python documentation_naming_agent.py --dry-run
    python documentation_naming_agent.py --phase sequential
    python documentation_naming_agent.py --audit-only

Features:
- Scans all .md files in docs/ recursively
- Identifies naming violations per ADR-021
- Generates renaming proposals by category
- Executes git mv operations with reference updates
- Creates organized commits per phase
- Generates comprehensive audit report
"""

import argparse
import hashlib
import json
import logging
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class NamingViolationType(Enum):
    """Types of naming violations"""
    SEQUENTIAL_NUMBER = "sequential_number"  # testing_001.md
    UPPERCASE = "uppercase"  # ARCHIVO.md (should be archivo.md)
    ADR_INCONSISTENT = "adr_inconsistent"  # ADR_2025_001 vs ADR-001
    GENERIC_NAME = "generic_name"  # index.md, file.md
    NO_PREFIX = "no_prefix"  # Missing guia_, procedimiento_, etc.


class Priority(Enum):
    """Violation priority levels"""
    CRITICAL = "critical"  # P0 - Blocks understanding
    HIGH = "high"  # P1 - Should fix soon
    MEDIUM = "medium"  # P2 - Nice to have
    LOW = "low"  # P3 - Optional


class Phase(Enum):
    """Renaming phases"""
    SEQUENTIAL = "sequential"  # Phase 1: Numbers → Descriptive
    UPPERCASE = "uppercase"  # Phase 2: UPPERCASE → snake_case
    ADR = "adr"  # Phase 3: ADR standardization
    ALL = "all"  # All phases


@dataclass
class NamingViolation:
    """Represents a naming convention violation"""
    file_path: Path
    violation_type: NamingViolationType
    priority: Priority
    current_name: str
    proposed_name: str
    reason: str
    phase: Phase
    references: List[Path] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'file_path': str(self.file_path),
            'violation_type': self.violation_type.value,
            'priority': self.priority.value,
            'current_name': self.current_name,
            'proposed_name': self.proposed_name,
            'reason': self.reason,
            'phase': self.phase.value,
            'references': [str(r) for r in self.references]
        }


@dataclass
class RenamingOperation:
    """Represents a single file rename operation"""
    old_path: Path
    new_path: Path
    violation: NamingViolation
    references_to_update: List[Tuple[Path, str, str]] = field(default_factory=list)
    executed: bool = False
    git_output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'old_path': str(self.old_path),
            'new_path': str(self.new_path),
            'violation': self.violation.to_dict(),
            'references_to_update': [
                {'file': str(f), 'old': old, 'new': new}
                for f, old, new in self.references_to_update
            ],
            'executed': self.executed,
            'git_output': self.git_output
        }


@dataclass
class AuditReport:
    """Complete audit report"""
    timestamp: str
    total_files_scanned: int
    total_violations: int
    violations_by_type: Dict[str, int]
    violations_by_priority: Dict[str, int]
    violations_by_phase: Dict[str, int]
    violations: List[NamingViolation]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'total_files_scanned': self.total_files_scanned,
            'total_violations': self.total_violations,
            'violations_by_type': self.violations_by_type,
            'violations_by_priority': self.violations_by_priority,
            'violations_by_phase': self.violations_by_phase,
            'violations': [v.to_dict() for v in self.violations]
        }


@dataclass
class ExecutionReport:
    """Execution results report"""
    timestamp: str
    phases_executed: List[str]
    total_operations: int
    successful_operations: int
    failed_operations: int
    commits_created: List[str]
    operations: List[RenamingOperation]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'phases_executed': self.phases_executed,
            'total_operations': self.total_operations,
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'commits_created': self.commits_created,
            'operations': [op.to_dict() for op in self.operations]
        }


# ============================================================================
# VIOLATION DETECTORS
# ============================================================================

class ViolationDetector:
    """Base class for violation detectors"""

    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.violations: List[NamingViolation] = []

    def scan_all_files(self) -> List[Path]:
        """Scan all .md files in docs/"""
        md_files = []
        for md_file in self.docs_root.rglob("*.md"):
            # Skip special files
            if md_file.name in ["README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md"]:
                continue
            md_files.append(md_file)
        return md_files

    def detect(self, file_path: Path) -> Optional[NamingViolation]:
        """Detect violation in file - override in subclass"""
        raise NotImplementedError


class SequentialNumberDetector(ViolationDetector):
    """Detects files with sequential numbers (testing_001.md)"""

    def detect(self, file_path: Path) -> Optional[NamingViolation]:
        """Detect sequential number pattern"""
        pattern = r'_(\d{3})\.md$'
        match = re.search(pattern, file_path.name)

        if match:
            # Read file content to suggest better name
            proposed_name = self._suggest_name(file_path)

            if proposed_name and proposed_name != file_path.name:
                return NamingViolation(
                    file_path=file_path,
                    violation_type=NamingViolationType.SEQUENTIAL_NUMBER,
                    priority=Priority.CRITICAL,
                    current_name=file_path.name,
                    proposed_name=proposed_name,
                    reason=f"Sequential number {match.group(1)} doesn't reveal content",
                    phase=Phase.SEQUENTIAL
                )
        return None

    def _suggest_name(self, file_path: Path) -> Optional[str]:
        """Suggest descriptive name based on file content"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract H1 title
            h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
                # Convert to snake_case
                name = self._to_snake_case(title)
                return f"{name}.md"

            # Extract from frontmatter if exists
            frontmatter_match = re.search(r'^---\n.*?titulo:\s*(.+?)\n.*?---', content, re.DOTALL | re.MULTILINE)
            if frontmatter_match:
                title = frontmatter_match.group(1).strip()
                name = self._to_snake_case(title)
                return f"{name}.md"

        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")

        return None

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        # Remove special chars
        text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces and hyphens with underscores
        text = re.sub(r'[\s-]+', '_', text)
        # Lowercase
        text = text.lower()
        # Remove consecutive underscores
        text = re.sub(r'_+', '_', text)
        # Remove leading/trailing underscores
        text = text.strip('_')
        # Limit length
        if len(text) > 60:
            text = text[:60].rsplit('_', 1)[0]
        return text


class UppercaseDetector(ViolationDetector):
    """Detects UPPERCASE files that should be snake_case"""

    SPECIAL_FILES = {
        "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md",
        "TODO.md", "METRICS.md", "QUICKSTART.md"
    }

    ADR_PATTERN = r'^ADR-\d{3}'
    TASK_PATTERN = r'^TASK-\d{3}'
    SPEC_PATTERN = r'^SPEC-'

    def detect(self, file_path: Path) -> Optional[NamingViolation]:
        """Detect UPPERCASE pattern"""
        name = file_path.name

        # Skip special files
        if name in self.SPECIAL_FILES:
            return None

        # Skip ADR/TASK/SPEC prefixes
        if re.match(self.ADR_PATTERN, name) or \
           re.match(self.TASK_PATTERN, name) or \
           re.match(self.SPEC_PATTERN, name):
            return None

        # Check if filename (without .md) is ALL UPPERCASE
        name_without_ext = name.replace('.md', '')
        if name_without_ext.isupper() and len(name_without_ext) > 2:
            proposed_name = name_without_ext.lower().replace('-', '_') + '.md'

            return NamingViolation(
                file_path=file_path,
                violation_type=NamingViolationType.UPPERCASE,
                priority=Priority.HIGH,
                current_name=name,
                proposed_name=proposed_name,
                reason="Normal files should use snake_case, not UPPERCASE",
                phase=Phase.UPPERCASE
            )

        return None


class ADRDetector(ViolationDetector):
    """Detects ADR naming inconsistencies"""

    OLD_PATTERN = r'^ADR_(\d{4})_(\d{3})_(.+)\.md$'  # ADR_2025_001_name.md
    NEW_PATTERN = r'^ADR-(\d{3})-(.+)\.md$'  # ADR-001-name.md

    def detect(self, file_path: Path) -> Optional[NamingViolation]:
        """Detect ADR inconsistencies"""
        name = file_path.name

        # Check old format
        old_match = re.match(self.OLD_PATTERN, name)
        if old_match:
            year, number, description = old_match.groups()
            # Convert to new format
            desc_kebab = description.replace('_', '-')
            proposed_name = f"ADR-{number}-{desc_kebab}.md"

            # Check if needs to be in domain adr/ subdirectory
            if 'adr' not in str(file_path.parent).lower():
                # Determine domain from path
                domain = self._get_domain(file_path)
                proposed_path = f"{domain}/adr/{proposed_name}"
            else:
                proposed_path = proposed_name

            return NamingViolation(
                file_path=file_path,
                violation_type=NamingViolationType.ADR_INCONSISTENT,
                priority=Priority.HIGH,
                current_name=name,
                proposed_name=proposed_path,
                reason="ADR format should be ADR-NNN-description-kebab-case.md",
                phase=Phase.ADR
            )

        return None

    def _get_domain(self, file_path: Path) -> str:
        """Get domain from file path"""
        path_str = str(file_path)
        if 'backend' in path_str:
            return 'backend'
        elif 'frontend' in path_str:
            return 'frontend'
        elif 'infraestructura' in path_str:
            return 'infraestructura'
        elif 'ai' in path_str:
            return 'ai'
        else:
            return 'gobernanza'


# ============================================================================
# REFERENCE FINDER
# ============================================================================

class ReferenceFinder:
    """Finds references to files in other documents"""

    def __init__(self, docs_root: Path):
        self.docs_root = docs_root

    def find_references(self, file_path: Path) -> List[Path]:
        """Find all files that reference this file"""
        references = []
        filename = file_path.name

        # Search all .md files for this filename
        for md_file in self.docs_root.rglob("*.md"):
            if md_file == file_path:
                continue

            try:
                content = md_file.read_text(encoding='utf-8')
                # Check for markdown links and plain text references
                if filename in content:
                    references.append(md_file)
            except Exception as e:
                logger.warning(f"Could not read {md_file}: {e}")

        return references


# ============================================================================
# NAMING AGENT
# ============================================================================

class DocumentationNamingAgent:
    """Main agent for documentation naming standardization"""

    def __init__(self, docs_root: Path, dry_run: bool = False):
        self.docs_root = docs_root
        self.dry_run = dry_run
        self.detectors = [
            SequentialNumberDetector(docs_root),
            UppercaseDetector(docs_root),
            ADRDetector(docs_root)
        ]
        self.reference_finder = ReferenceFinder(docs_root)
        self.violations: List[NamingViolation] = []
        self.operations: List[RenamingOperation] = []

    def audit(self) -> AuditReport:
        """
        STEP 1: Audit all files and identify violations

        Returns:
            AuditReport with all detected violations
        """
        logger.info("Starting documentation naming audit...")

        # Scan all files
        all_files = []
        for detector in self.detectors:
            all_files.extend(detector.scan_all_files())

        # Deduplicate
        all_files = list(set(all_files))
        logger.info(f"Scanning {len(all_files)} markdown files...")

        # Detect violations
        violations = []
        for file_path in all_files:
            for detector in self.detectors:
                violation = detector.detect(file_path)
                if violation:
                    # Find references
                    violation.references = self.reference_finder.find_references(file_path)
                    violations.append(violation)

        self.violations = violations

        # Calculate statistics
        violations_by_type = {}
        violations_by_priority = {}
        violations_by_phase = {}

        for v in violations:
            violations_by_type[v.violation_type.value] = violations_by_type.get(v.violation_type.value, 0) + 1
            violations_by_priority[v.priority.value] = violations_by_priority.get(v.priority.value, 0) + 1
            violations_by_phase[v.phase.value] = violations_by_phase.get(v.phase.value, 0) + 1

        report = AuditReport(
            timestamp=datetime.now().isoformat(),
            total_files_scanned=len(all_files),
            total_violations=len(violations),
            violations_by_type=violations_by_type,
            violations_by_priority=violations_by_priority,
            violations_by_phase=violations_by_phase,
            violations=violations
        )

        logger.info(f"Audit complete: {len(violations)} violations found")
        return report

    def execute_phase(self, phase: Phase) -> ExecutionReport:
        """
        Execute renaming for specific phase

        Args:
            phase: Which phase to execute

        Returns:
            ExecutionReport with execution results
        """
        logger.info(f"Executing phase: {phase.value}")

        # Filter violations by phase
        if phase == Phase.ALL:
            phase_violations = self.violations
        else:
            phase_violations = [v for v in self.violations if v.phase == phase]

        logger.info(f"Processing {len(phase_violations)} violations for phase {phase.value}")

        # Create operations
        operations = []
        for violation in phase_violations:
            old_path = violation.file_path

            # Determine new path
            if '/' in violation.proposed_name:
                # Path includes directory
                new_path = self.docs_root / violation.proposed_name
            else:
                # Just filename change
                new_path = old_path.parent / violation.proposed_name

            # Find references to update
            references_to_update = []
            for ref_file in violation.references:
                try:
                    content = ref_file.read_text(encoding='utf-8')
                    old_name = old_path.name
                    new_name = new_path.name

                    if old_name in content:
                        references_to_update.append((ref_file, old_name, new_name))
                except Exception as e:
                    logger.warning(f"Could not read reference {ref_file}: {e}")

            operation = RenamingOperation(
                old_path=old_path,
                new_path=new_path,
                violation=violation,
                references_to_update=references_to_update
            )
            operations.append(operation)

        self.operations = operations

        # Execute operations
        successful = 0
        failed = 0
        commits = []

        for operation in operations:
            if self._execute_operation(operation):
                successful += 1
            else:
                failed += 1

        # Create commit if not dry-run
        if not self.dry_run and successful > 0:
            commit_hash = self._create_commit(phase)
            if commit_hash:
                commits.append(commit_hash)

        report = ExecutionReport(
            timestamp=datetime.now().isoformat(),
            phases_executed=[phase.value],
            total_operations=len(operations),
            successful_operations=successful,
            failed_operations=failed,
            commits_created=commits,
            operations=operations
        )

        logger.info(f"Phase {phase.value} complete: {successful} successful, {failed} failed")
        return report

    def _execute_operation(self, operation: RenamingOperation) -> bool:
        """Execute single rename operation"""
        try:
            old_path = operation.old_path
            new_path = operation.new_path

            # Create target directory if needed
            new_path.parent.mkdir(parents=True, exist_ok=True)

            # Execute git mv
            if not self.dry_run:
                cmd = ['git', 'mv', str(old_path), str(new_path)]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.docs_root.parent)

                if result.returncode != 0:
                    logger.error(f"Failed to rename {old_path} → {new_path}: {result.stderr}")
                    operation.git_output = result.stderr
                    return False

                operation.git_output = result.stdout

                # Update references
                for ref_file, old_name, new_name in operation.references_to_update:
                    self._update_reference(ref_file, old_name, new_name)
            else:
                logger.info(f"[DRY-RUN] Would rename: {old_path} → {new_path}")
                logger.info(f"[DRY-RUN] Would update {len(operation.references_to_update)} references")

            operation.executed = True
            return True

        except Exception as e:
            logger.error(f"Error executing operation: {e}")
            return False

    def _update_reference(self, file_path: Path, old_name: str, new_name: str):
        """Update reference in file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            updated_content = content.replace(old_name, new_name)

            if updated_content != content:
                file_path.write_text(updated_content, encoding='utf-8')
                logger.info(f"Updated reference in {file_path}")
        except Exception as e:
            logger.error(f"Failed to update reference in {file_path}: {e}")

    def _create_commit(self, phase: Phase) -> Optional[str]:
        """Create git commit for phase"""
        try:
            # Stage all changes
            subprocess.run(['git', 'add', '-A'], cwd=self.docs_root.parent, check=True)

            # Create commit message
            if phase == Phase.SEQUENTIAL:
                message = "docs: rename sequential numbered files to descriptive names (Phase 1)"
            elif phase == Phase.UPPERCASE:
                message = "docs: convert UPPERCASE files to snake_case (Phase 2)"
            elif phase == Phase.ADR:
                message = "docs: standardize ADR format and organization (Phase 3)"
            else:
                message = f"docs: naming standardization ({phase.value})"

            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                cwd=self.docs_root.parent,
                check=True
            )

            # Get commit hash
            hash_result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.docs_root.parent,
                check=True
            )

            commit_hash = hash_result.stdout.strip()
            logger.info(f"Created commit: {commit_hash}")
            return commit_hash

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create commit: {e}")
            return None


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Documentation Naming Agent - Standardize file naming per ADR-021'
    )

    parser.add_argument(
        '--docs-root',
        type=Path,
        default=Path.cwd() / 'docs',
        help='Path to docs/ directory (default: ./docs)'
    )

    parser.add_argument(
        '--audit-only',
        action='store_true',
        help='Only audit and report violations, do not execute'
    )

    parser.add_argument(
        '--phase',
        choices=['sequential', 'uppercase', 'adr', 'all'],
        default='all',
        help='Which phase to execute (default: all)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode - show what would be done'
    )

    parser.add_argument(
        '--execute-all',
        action='store_true',
        help='Execute all phases sequentially'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Output JSON report to file'
    )

    args = parser.parse_args()

    # Validate docs root
    if not args.docs_root.exists():
        logger.error(f"docs/ directory not found: {args.docs_root}")
        sys.exit(1)

    # Create agent
    agent = DocumentationNamingAgent(
        docs_root=args.docs_root,
        dry_run=args.dry_run
    )

    # Execute audit
    audit_report = agent.audit()

    # Print audit results
    print("\n" + "="*80)
    print("DOCUMENTATION NAMING AUDIT REPORT")
    print("="*80)
    print(f"Timestamp: {audit_report.timestamp}")
    print(f"Files scanned: {audit_report.total_files_scanned}")
    print(f"Violations found: {audit_report.total_violations}")
    print("\nBy Type:")
    for vtype, count in sorted(audit_report.violations_by_type.items()):
        print(f"  {vtype}: {count}")
    print("\nBy Priority:")
    for priority, count in sorted(audit_report.violations_by_priority.items()):
        print(f"  {priority}: {count}")
    print("\nBy Phase:")
    for phase, count in sorted(audit_report.violations_by_phase.items()):
        print(f"  {phase}: {count}")
    print("="*80 + "\n")

    # Save audit report if requested
    if args.output:
        audit_output = args.output.parent / f"{args.output.stem}_audit.json"
        audit_output.write_text(json.dumps(audit_report.to_dict(), indent=2))
        print(f"Audit report saved to: {audit_output}")

    # Stop if audit-only
    if args.audit_only:
        sys.exit(0)

    # Execute phases
    if args.execute_all:
        phases = [Phase.SEQUENTIAL, Phase.UPPERCASE, Phase.ADR]
    else:
        phases = [Phase[args.phase.upper()]]

    all_reports = []
    for phase in phases:
        execution_report = agent.execute_phase(phase)
        all_reports.append(execution_report)

        # Print execution results
        print("\n" + "="*80)
        print(f"PHASE {phase.value.upper()} EXECUTION REPORT")
        print("="*80)
        print(f"Operations: {execution_report.total_operations}")
        print(f"Successful: {execution_report.successful_operations}")
        print(f"Failed: {execution_report.failed_operations}")
        print(f"Commits: {', '.join(execution_report.commits_created)}")
        print("="*80 + "\n")

    # Save execution report if requested
    if args.output:
        exec_output = args.output.parent / f"{args.output.stem}_execution.json"
        combined_report = {
            'timestamp': datetime.now().isoformat(),
            'phases': [r.to_dict() for r in all_reports]
        }
        exec_output.write_text(json.dumps(combined_report, indent=2))
        print(f"Execution report saved to: {exec_output}")

    print("\n✅ Documentation naming standardization complete!")


if __name__ == '__main__':
    main()
