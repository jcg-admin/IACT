---
title: Low-Level Design: ShellScriptAnalysisAgent
date: 2025-11-13
domain: ai
status: active
---

# Low-Level Design: ShellScriptAnalysisAgent

**Issue ID**: FEATURE-SHELL-ANALYSIS-001
**Fecha**: 2025-11-13
**Fase SDLC**: Design (LLD)
**Autor**: Claude (SDLCDesignAgent usando Auto-CoT)
**Versión**: 1.0.0

---

## Razonamiento Auto-CoT Aplicado

Este documento fue generado usando **Auto-CoT (Automatic Chain-of-Thought)** para razonamiento sistemático.

### Clustering de Problemas:

#### Cluster A: Estructura de Clases
- ¿Qué clases principales necesitamos?
- ¿Qué dataclasses para resultados?
- ¿Qué hereda de Agent base?

#### Cluster B: Métodos y Signatures
- ¿Qué métodos públicos exponer?
- ¿Qué métodos privados internos?
- ¿Qué signatures de input/output?

#### Cluster C: Integración
- ¿Cómo integrar con Agent framework?
- ¿Cómo invocar herramientas existentes?
- ¿Cómo manejar dependencies?

---

## 1. Módulo Principal

### 1.1 ShellScriptAnalysisAgent

**Archivo**: `scripts/coding/ai/agents/quality/shell_analysis_agent.py`

**Razonamiento Paso a Paso (Auto-CoT)**:
```
Paso 1: Identificar responsabilidad principal
  → Orquestar pipeline de análisis de scripts shell

Paso 2: Determinar herencia
  → Debe heredar de Agent (scripts/coding/ai/shared/agent_base.py)
  → Obtiene: constitution loading, guardrails, execute() lifecycle

Paso 3: Definir configuración
  → analysis_depth: "quick" | "standard" | "deep"
  → constitutional_rules: List[int] (1-8)
  → output_format: "markdown" | "json" | "both"
  → parallel_workers: int (para batch)

Paso 4: Diseñar método run()
  → Input: script_path o directory
  → Proceso: load → preprocess → analyze → consolidate → report
  → Output: ConsolidatedResult

Paso 5: Identificar sub-componentes
  → Constitutional Analyzer
  → Quality Analyzer
  → Security Analyzer
  → Report Generator
```

**Implementación**:

```python
#!/usr/bin/env python3
"""
Shell Script Analysis Agent

Analyzes shell scripts against constitutional rules, code quality metrics,
and security vulnerabilities.

Trazabilidad:
- Issue: FEATURE-SHELL-ANALYSIS-001
- HLD: docs/sdlc_outputs/design/hld-shell-script-analysis-agent.md
- Planning: docs/sdlc_outputs/planning/issue-shell-script-analysis-agent.md
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import hashlib
import json
import logging

# Import Agent framework
from scripts.coding.ai.shared.agent_base import Agent, AgentResult, AgentStatus


# ============================================================================
# ENUMS
# ============================================================================

class AnalysisMode(Enum):
    """Analysis depth modes."""
    QUICK = "quick"        # ~0.5s/script - Basic validation
    STANDARD = "standard"  # ~2s/script - Full heuristic analysis
    DEEP = "deep"         # ~10s/script - LLM-powered analysis


class Severity(Enum):
    """Issue severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# DATACLASSES (Results)
# ============================================================================

@dataclass
class Violation:
    """Represents a constitutional rule violation."""
    rule_number: int  # 1-8
    line_number: Optional[int]
    severity: Severity
    description: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_number": self.rule_number,
            "line_number": self.line_number,
            "severity": self.severity.value,
            "description": self.description,
            "recommendation": self.recommendation
        }


@dataclass
class RuleResult:
    """Result for a single constitutional rule."""
    rule_number: int
    compliant: bool
    score: float  # 0-100
    violations: List[Violation] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_number": self.rule_number,
            "compliant": self.compliant,
            "score": self.score,
            "violations": [v.to_dict() for v in self.violations],
            "recommendations": self.recommendations
        }


@dataclass
class ConstitutionalResult:
    """Result of constitutional compliance analysis."""
    overall_compliance: bool
    compliance_score: float  # 0-100
    rule_results: Dict[int, RuleResult]
    total_violations: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_compliance": self.overall_compliance,
            "compliance_score": self.compliance_score,
            "rule_results": {k: v.to_dict() for k, v in self.rule_results.items()},
            "total_violations": self.total_violations
        }


@dataclass
class CodeMetrics:
    """Code quality metrics."""
    lines_of_code: int
    lines_of_comments: int
    number_of_functions: int
    max_function_length: int
    average_function_length: float
    cyclomatic_complexity: float
    comment_ratio: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lines_of_code": self.lines_of_code,
            "lines_of_comments": self.lines_of_comments,
            "number_of_functions": self.number_of_functions,
            "max_function_length": self.max_function_length,
            "average_function_length": self.average_function_length,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "comment_ratio": self.comment_ratio
        }


@dataclass
class CodeSmell:
    """Detected code smell."""
    type: str  # "long_function", "deep_nesting", "magic_number", etc.
    location: str  # "line 45-120" or "function do_something"
    severity: Severity
    description: str
    recommendation: str
    priority: int  # 1-5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "location": self.location,
            "severity": self.severity.value,
            "description": self.description,
            "recommendation": self.recommendation,
            "priority": self.priority
        }


@dataclass
class RefactoringOpportunity:
    """Refactoring opportunity."""
    type: str  # "extract_function", "simplify_conditional", "remove_duplication"
    location: str
    effort: str  # "low", "medium", "high"
    impact: str  # "low", "medium", "high"
    description: str
    example: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "location": self.location,
            "effort": self.effort,
            "impact": self.impact,
            "description": self.description,
            "example": self.example
        }


@dataclass
class QualityResult:
    """Result of code quality analysis."""
    metrics: CodeMetrics
    code_smells: List[CodeSmell]
    refactoring_opportunities: List[RefactoringOpportunity]
    quality_score: float  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics.to_dict(),
            "code_smells": [cs.to_dict() for cs in self.code_smells],
            "refactoring_opportunities": [ro.to_dict() for ro in self.refactoring_opportunities],
            "quality_score": self.quality_score
        }


@dataclass
class SecurityIssue:
    """Security vulnerability."""
    type: str  # "command_injection", "sql_injection", "path_traversal"
    severity: Severity
    location: str
    description: str
    cwe_id: Optional[str]  # CWE-78, CWE-89, etc.
    recommendation: str
    exploitability: str  # "easy", "medium", "hard"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity.value,
            "location": self.location,
            "description": self.description,
            "cwe_id": self.cwe_id,
            "recommendation": self.recommendation,
            "exploitability": self.exploitability
        }


@dataclass
class SecurityResult:
    """Result of security analysis."""
    issues: List[SecurityIssue]
    severity_counts: Dict[str, int]
    security_score: float  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issues": [issue.to_dict() for issue in self.issues],
            "severity_counts": self.severity_counts,
            "security_score": self.security_score
        }


@dataclass
class ConsolidatedResult:
    """Consolidated analysis result."""
    script_name: str
    script_path: str
    analysis_timestamp: str
    analysis_mode: AnalysisMode
    overall_score: float  # 0-100
    constitutional: ConstitutionalResult
    quality: QualityResult
    security: SecurityResult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "script_name": self.script_name,
            "script_path": self.script_path,
            "analysis_timestamp": self.analysis_timestamp,
            "analysis_mode": self.analysis_mode.value,
            "overall_score": self.overall_score,
            "constitutional": self.constitutional.to_dict(),
            "quality": self.quality.to_dict(),
            "security": self.security.to_dict()
        }


@dataclass
class PreprocessedScript:
    """Preprocessed script with metadata."""
    raw_content: str
    normalized_lines: List[str]
    functions: List[Dict[str, Any]]  # {"name": str, "start_line": int, "end_line": int}
    metadata: Dict[str, Any]
    content_hash: str  # SHA256 for caching


# ============================================================================
# MAIN AGENT CLASS
# ============================================================================

class ShellScriptAnalysisAgent(Agent):
    """
    Agent that analyzes shell scripts for constitutional compliance,
    code quality, and security vulnerabilities.

    Inherits from Agent base class for:
    - Constitution loading
    - Guardrails enforcement
    - Lifecycle management (execute())

    Techniques:
    - Chain-of-Verification (constitutional analysis)
    - Auto-CoT (complexity reasoning)
    - Search Optimization (code smell detection)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the shell script analysis agent.

        Args:
            config: Configuration dictionary with options:
                - analysis_depth: "quick" | "standard" | "deep"
                - constitutional_rules: List[int] (1-8)
                - include_security: bool
                - parallel_workers: int
                - output_format: "markdown" | "json" | "both"
                - cache_enabled: bool
        """
        super().__init__(name="ShellScriptAnalysisAgent", config=config)

        # Parse configuration
        self.analysis_mode = AnalysisMode(
            self.config.get("analysis_depth", "standard")
        )
        self.constitutional_rules = self.config.get(
            "constitutional_rules", [1, 2, 3, 4, 5, 6, 7, 8]
        )
        self.include_security = self.config.get("include_security", True)
        self.parallel_workers = self.config.get("parallel_workers", 10)
        self.output_format = self.config.get("output_format", "both")
        self.cache_enabled = self.config.get("cache_enabled", True)

        # Cache directory
        self.cache_dir = Path(".cache/shell_analysis")
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initialized with mode={self.analysis_mode.value}")

    # ========================================================================
    # PUBLIC METHODS (Agent Interface)
    # ========================================================================

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute shell script analysis.

        Args:
            input_data: {
                "script_path": str or List[str],
                "output_dir": Optional[str]
            }

        Returns:
            {
                "results": List[ConsolidatedResult],
                "summary": Dict[str, Any]
            }
        """
        script_paths = input_data.get("script_path")
        output_dir = Path(input_data.get("output_dir", "docs/scripts/analisis"))

        # Normalize to list
        if isinstance(script_paths, str):
            script_paths = [script_paths]
        elif isinstance(script_paths, Path):
            if script_paths.is_dir():
                # Find all .sh files
                script_paths = list(script_paths.glob("**/*.sh"))
            else:
                script_paths = [script_paths]

        self.logger.info(f"Analyzing {len(script_paths)} scripts")

        # Analyze scripts
        if self.parallel_workers > 1 and len(script_paths) > 1:
            results = self._analyze_parallel(script_paths)
        else:
            results = [self._analyze_single(path) for path in script_paths]

        # Generate reports
        self._generate_reports(results, output_dir)

        # Calculate summary
        summary = self._calculate_summary(results)

        return {
            "results": [r.to_dict() for r in results],
            "summary": summary
        }

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Validate input data.

        Args:
            input_data: Input to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if "script_path" not in input_data:
            errors.append("Missing required field: script_path")

        script_path = input_data.get("script_path")
        if script_path:
            if isinstance(script_path, list):
                for path in script_path:
                    if not Path(path).exists():
                        errors.append(f"Script not found: {path}")
            elif isinstance(script_path, (str, Path)):
                if not Path(script_path).exists():
                    errors.append(f"Script not found: {script_path}")

        return errors

    # ========================================================================
    # PRIVATE METHODS (Internal Implementation)
    # ========================================================================

    def _analyze_single(self, script_path: Path) -> ConsolidatedResult:
        """Analyze a single script."""
        from datetime import datetime

        self.logger.info(f"Analyzing: {script_path}")

        # Check cache
        if self.cache_enabled:
            cached = self._check_cache(script_path)
            if cached:
                self.logger.info(f"Cache hit: {script_path}")
                return cached

        # Load and preprocess
        script = self._load_script(script_path)
        preprocessed = self._preprocess(script, script_path)

        # Analyze
        constitutional = self._analyze_constitutional(preprocessed)
        quality = self._analyze_quality(preprocessed)
        security = self._analyze_security(preprocessed) if self.include_security else None

        # Consolidate
        result = self._consolidate_results(
            script_path=script_path,
            constitutional=constitutional,
            quality=quality,
            security=security,
            timestamp=datetime.now().isoformat()
        )

        # Cache result
        if self.cache_enabled:
            self._save_to_cache(preprocessed.content_hash, result)

        return result

    def _analyze_parallel(self, script_paths: List[Path]) -> List[ConsolidatedResult]:
        """Analyze multiple scripts in parallel."""
        results = []

        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            future_to_path = {
                executor.submit(self._analyze_single, path): path
                for path in script_paths
            }

            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error analyzing {path}: {e}")

        return results

    def _load_script(self, script_path: Path) -> str:
        """Load script from file."""
        return script_path.read_text()

    def _preprocess(self, script: str, script_path: Path) -> PreprocessedScript:
        """
        Preprocess script for analysis.

        Returns:
            PreprocessedScript with normalized lines, extracted functions, metadata
        """
        lines = script.splitlines()

        # Extract functions
        functions = self._extract_functions(lines)

        # Calculate content hash
        content_hash = hashlib.sha256(script.encode()).hexdigest()

        # Metadata
        metadata = {
            "total_lines": len(lines),
            "function_count": len(functions),
            "has_shebang": lines[0].startswith("#!") if lines else False
        }

        return PreprocessedScript(
            raw_content=script,
            normalized_lines=lines,
            functions=functions,
            metadata=metadata,
            content_hash=content_hash
        )

    def _extract_functions(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract function definitions from script."""
        import re

        functions = []
        func_pattern = re.compile(r'^(\w+)\s*\(\)\s*\{')

        for i, line in enumerate(lines, 1):
            match = func_pattern.match(line.strip())
            if match:
                func_name = match.group(1)
                # Find end of function (simplistic: next function or end)
                end_line = i  # TODO: Implement proper brace matching
                functions.append({
                    "name": func_name,
                    "start_line": i,
                    "end_line": end_line
                })

        return functions

    def _analyze_constitutional(self, script: PreprocessedScript) -> ConstitutionalResult:
        """
        Analyze constitutional compliance.

        Uses Chain-of-Verification for accuracy.
        """
        # TODO: Implement Chain-of-Verification
        # For now, use heuristics

        rule_results = {}
        total_violations = 0

        for rule_num in self.constitutional_rules:
            result = self._check_rule(rule_num, script)
            rule_results[rule_num] = result
            total_violations += len(result.violations)

        overall_score = sum(r.score for r in rule_results.values()) / len(rule_results)

        return ConstitutionalResult(
            overall_compliance=total_violations == 0,
            compliance_score=overall_score,
            rule_results=rule_results,
            total_violations=total_violations
        )

    def _check_rule(self, rule_number: int, script: PreprocessedScript) -> RuleResult:
        """Check a specific constitutional rule."""
        # Delegate to rule-specific checkers
        checkers = {
            1: self._check_rule_1_single_responsibility,
            2: self._check_rule_2_backward_compatibility,
            3: self._check_rule_3_error_handling,
            4: self._check_rule_4_tests_without_deps,
            5: self._check_rule_5_clean_naming,
            6: self._check_rule_6_size_limits,
            7: self._check_rule_7_documentation,
            8: self._check_rule_8_idempotence
        }

        checker = checkers.get(rule_number)
        if checker:
            return checker(script)
        else:
            return RuleResult(rule_number=rule_number, compliant=True, score=100.0)

    def _check_rule_3_error_handling(self, script: PreprocessedScript) -> RuleResult:
        """Check Rule 3: Explicit Error Handling."""
        violations = []

        # Check for 'set -e'
        has_set_e = any('set -e' in line for line in script.normalized_lines)
        if not has_set_e:
            violations.append(Violation(
                rule_number=3,
                line_number=None,
                severity=Severity.CRITICAL,
                description="Missing 'set -e' or 'set -euo pipefail'",
                recommendation="Add 'set -euo pipefail' at the beginning of the script"
            ))

        # Check for '|| true' (silent errors)
        for i, line in enumerate(script.normalized_lines, 1):
            if '|| true' in line:
                violations.append(Violation(
                    rule_number=3,
                    line_number=i,
                    severity=Severity.HIGH,
                    description="Silent error handling with '|| true'",
                    recommendation="Use explicit error handling instead"
                ))

        score = max(0, 100 - (len(violations) * 20))

        return RuleResult(
            rule_number=3,
            compliant=len(violations) == 0,
            score=score,
            violations=violations,
            recommendations=[]
        )

    # Stubs for other rule checkers
    def _check_rule_1_single_responsibility(self, script) -> RuleResult:
        return RuleResult(1, True, 100.0)  # TODO

    def _check_rule_2_backward_compatibility(self, script) -> RuleResult:
        return RuleResult(2, True, 100.0)  # TODO

    def _check_rule_4_tests_without_deps(self, script) -> RuleResult:
        return RuleResult(4, True, 100.0)  # TODO

    def _check_rule_5_clean_naming(self, script) -> RuleResult:
        return RuleResult(5, True, 100.0)  # TODO

    def _check_rule_6_size_limits(self, script) -> RuleResult:
        return RuleResult(6, True, 100.0)  # TODO

    def _check_rule_7_documentation(self, script) -> RuleResult:
        return RuleResult(7, True, 100.0)  # TODO

    def _check_rule_8_idempotence(self, script) -> RuleResult:
        return RuleResult(8, True, 100.0)  # TODO

    def _analyze_quality(self, script: PreprocessedScript) -> QualityResult:
        """Analyze code quality."""
        metrics = self._calculate_metrics(script)
        code_smells = self._detect_code_smells(script, metrics)
        refactoring_opps = self._identify_refactoring_opportunities(code_smells)

        quality_score = self._calculate_quality_score(metrics, code_smells)

        return QualityResult(
            metrics=metrics,
            code_smells=code_smells,
            refactoring_opportunities=refactoring_opps,
            quality_score=quality_score
        )

    def _calculate_metrics(self, script: PreprocessedScript) -> CodeMetrics:
        """Calculate code metrics."""
        loc = script.metadata["total_lines"]
        comments = sum(1 for line in script.normalized_lines if line.strip().startswith("#"))

        return CodeMetrics(
            lines_of_code=loc,
            lines_of_comments=comments,
            number_of_functions=len(script.functions),
            max_function_length=0,  # TODO
            average_function_length=0.0,  # TODO
            cyclomatic_complexity=0.0,  # TODO
            comment_ratio=comments / loc if loc > 0 else 0
        )

    def _detect_code_smells(self, script, metrics) -> List[CodeSmell]:
        """Detect code smells."""
        # TODO: Implement
        return []

    def _identify_refactoring_opportunities(self, code_smells) -> List[RefactoringOpportunity]:
        """Identify refactoring opportunities from code smells."""
        # TODO: Implement
        return []

    def _calculate_quality_score(self, metrics, code_smells) -> float:
        """Calculate overall quality score."""
        # Simple heuristic
        base_score = 100.0
        penalty = len(code_smells) * 5
        return max(0, base_score - penalty)

    def _analyze_security(self, script: PreprocessedScript) -> SecurityResult:
        """Analyze security vulnerabilities."""
        issues = []

        # Check for command injection patterns
        for i, line in enumerate(script.normalized_lines, 1):
            if '$(' in line and '"' not in line:
                issues.append(SecurityIssue(
                    type="potential_command_injection",
                    severity=Severity.HIGH,
                    location=f"line {i}",
                    description="Unquoted variable in command substitution",
                    cwe_id="CWE-78",
                    recommendation="Quote variables to prevent injection",
                    exploitability="medium"
                ))

        severity_counts = {
            "critical": sum(1 for i in issues if i.severity == Severity.CRITICAL),
            "high": sum(1 for i in issues if i.severity == Severity.HIGH),
            "medium": sum(1 for i in issues if i.severity == Severity.MEDIUM),
            "low": sum(1 for i in issues if i.severity == Severity.LOW)
        }

        security_score = max(0, 100 - (len(issues) * 10))

        return SecurityResult(
            issues=issues,
            severity_counts=severity_counts,
            security_score=security_score
        )

    def _consolidate_results(
        self,
        script_path: Path,
        constitutional: ConstitutionalResult,
        quality: QualityResult,
        security: Optional[SecurityResult],
        timestamp: str
    ) -> ConsolidatedResult:
        """Consolidate all analysis results."""
        # Calculate overall score
        overall_score = (
            constitutional.compliance_score * 0.4 +
            quality.quality_score * 0.3 +
            (security.security_score if security else 100) * 0.3
        )

        return ConsolidatedResult(
            script_name=script_path.name,
            script_path=str(script_path),
            analysis_timestamp=timestamp,
            analysis_mode=self.analysis_mode,
            overall_score=overall_score,
            constitutional=constitutional,
            quality=quality,
            security=security or SecurityResult([], {}, 100.0)
        )

    def _generate_reports(self, results: List[ConsolidatedResult], output_dir: Path):
        """Generate markdown and JSON reports."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Individual reports
        for result in results:
            self._generate_individual_report(result, output_dir)

        # Consolidated report
        self._generate_consolidated_report(results, output_dir)

    def _generate_individual_report(self, result: ConsolidatedResult, output_dir: Path):
        """Generate individual script report."""
        # JSON
        json_path = output_dir / f"{result.script_name}_analysis.json"
        json_path.write_text(json.dumps(result.to_dict(), indent=2))

        # Markdown
        md_path = output_dir / f"{result.script_name}_analysis.md"
        md_content = self._format_markdown_report(result)
        md_path.write_text(md_content)

    def _format_markdown_report(self, result: ConsolidatedResult) -> str:
        """Format result as markdown report."""
        # TODO: Implement full markdown formatting
        return f"""# Analysis: {result.script_name}

## Summary
- **Overall Score**: {result.overall_score:.1f}/100
- **Timestamp**: {result.analysis_timestamp}
- **Mode**: {result.analysis_mode.value}

## Constitutional Compliance
- **Compliant**: {result.constitutional.overall_compliance}
- **Score**: {result.constitutional.compliance_score:.1f}/100
- **Violations**: {result.constitutional.total_violations}

## Code Quality
- **Score**: {result.quality.quality_score:.1f}/100
- **Code Smells**: {len(result.quality.code_smells)}

## Security
- **Score**: {result.security.security_score:.1f}/100
- **Issues**: {len(result.security.issues)}
"""

    def _generate_consolidated_report(self, results: List[ConsolidatedResult], output_dir: Path):
        """Generate consolidated report for all scripts."""
        summary = self._calculate_summary(results)

        json_path = output_dir / "consolidated_analysis.json"
        json_path.write_text(json.dumps(summary, indent=2))

    def _calculate_summary(self, results: List[ConsolidatedResult]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not results:
            return {}

        return {
            "total_scripts": len(results),
            "average_score": sum(r.overall_score for r in results) / len(results),
            "compliant_scripts": sum(1 for r in results if r.constitutional.overall_compliance),
            "total_violations": sum(r.constitutional.total_violations for r in results),
            "total_security_issues": sum(len(r.security.issues) for r in results)
        }

    def _check_cache(self, script_path: Path) -> Optional[ConsolidatedResult]:
        """Check if cached result exists."""
        # TODO: Implement caching
        return None

    def _save_to_cache(self, content_hash: str, result: ConsolidatedResult):
        """Save result to cache."""
        # TODO: Implement caching
        pass


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Shell Script Analysis Agent")
    parser.add_argument("script_path", help="Path to script or directory")
    parser.add_argument("--mode", choices=["quick", "standard", "deep"], default="standard")
    parser.add_argument("--output-dir", default="docs/scripts/analisis")
    parser.add_argument("--workers", type=int, default=10)

    args = parser.parse_args()

    config = {
        "analysis_depth": args.mode,
        "parallel_workers": args.workers
    }

    agent = ShellScriptAnalysisAgent(config=config)
    result = agent.execute({
        "script_path": args.script_path,
        "output_dir": args.output_dir
    })

    if result.is_success():
        summary = result.data["summary"]
        print(f"\nAnalysis complete!")
        print(f"Scripts analyzed: {summary.get('total_scripts', 0)}")
        print(f"Average score: {summary.get('average_score', 0):.1f}/100")
    else:
        print(f"\nAnalysis failed: {result.errors}")
```

---

## 2. Supporting Components

### 2.1 Constitutional Rules Validator

**File**: `scripts/coding/ai/agents/quality/constitutional_validator.py`

Separate module for constitutional rule validation (implements each of the 8 rules).

### 2.2 Report Generator

**File**: `scripts/coding/ai/agents/quality/report_generator.py`

Dedicated module for report generation (markdown + JSON).

---

## 3. Dependencies

```python
# Standard library
import subprocess
import hashlib
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Project dependencies
from scripts.coding.ai.shared.agent_base import Agent, AgentResult, AgentStatus

# Optional dependencies (for LLM mode)
# from scripts.coding.ai.generators.llm_generator import LLMGenerator
```

---

## 4. Testing Strategy

### 4.1 Unit Tests

**File**: `scripts/coding/tests/ai/agents/quality/test_shell_analysis_agent.py`

```python
import pytest
from scripts.coding.ai.agents.quality.shell_analysis_agent import (
    ShellScriptAnalysisAgent,
    AnalysisMode,
    Severity
)

def test_agent_initialization():
    """Test agent initializes with default config."""
    agent = ShellScriptAnalysisAgent()
    assert agent.name == "ShellScriptAnalysisAgent"
    assert agent.analysis_mode == AnalysisMode.STANDARD

def test_rule_3_error_handling_detects_missing_set_e():
    """Test Rule 3 checker detects missing set -e."""
    agent = ShellScriptAnalysisAgent()
    script = agent._preprocess("#!/bin/bash\necho 'test'", Path("test.sh"))
    result = agent._check_rule_3_error_handling(script)

    assert not result.compliant
    assert len(result.violations) > 0
    assert result.violations[0].description == "Missing 'set -e' or 'set -euo pipefail'"

# ... more tests
```

---

**Generado por**: Claude (SDLCDesignAgent usando Auto-CoT)
**Timestamp**: 2025-11-13T08:40:00Z
**Razonamiento**: Aplicado Auto-CoT para clustering de problemas y razonamiento paso a paso
**Próximo paso**: ADRs con Self-Consistency para decisiones críticas
