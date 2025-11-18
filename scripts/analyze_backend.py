#!/usr/bin/env python3
"""
Backend Analysis: Analyze api/callcentersite with meta-development pipeline.

This script analyzes the Django backend code for architecture quality,
SOLID compliance, refactoring opportunities, and design patterns.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Añadir rutas de proyecto para imports opcionales
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
ANALYSIS_OUTPUT_RELATIVE = "logs_data/analysis/backend_analysis_results.json"
sys.path.insert(0, str(SCRIPTS_DIR))

from scripts.ai.agents.meta import create_architecture_improvement_pipeline


def find_python_files(directory: str, exclude_patterns: List[str] = None) -> List[Path]:
    """Find all Python files in directory, excluding patterns."""
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', 'migrations', 'tests', '.pyc']

    python_files = []
    base_path = Path(directory).resolve()  # Make absolute

    for py_file in base_path.rglob('*.py'):
        # Skip if matches any exclude pattern
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
        python_files.append(py_file)

    return sorted(python_files)


def analyze_file(file_path: Path, pipeline) -> Dict[str, Any]:
    """Analyze a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Skip very small files (likely just __init__.py)
        if len(code) < 100:
            return None

        # Run analysis without test generation for speed
        result = pipeline.analyze_code(code, include_test_generation=False)

        return {
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'lines': len(code.splitlines()),
            'quality_score': result.overall_score,
            'solid_violations': len(result.solid_analysis.violations) if result.solid_analysis else 0,
            'refactoring_opportunities': len(result.refactoring_opportunities),
            'pattern_recommendations': len(result.pattern_recommendations),
            'total_recommendations': len(result.consolidated_recommendations),
            'critical_issues': sum(1 for r in result.consolidated_recommendations if r.priority.name == 'CRITICAL'),
            'high_issues': sum(1 for r in result.consolidated_recommendations if r.priority.name == 'HIGH'),
            'result': result  # Store full result for detailed reporting
        }

    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None


def print_summary_table(results: List[Dict[str, Any]]):
    """Print summary table of all analyzed files."""
    print(f"\n{'='*100}")
    print("BACKEND ANALYSIS SUMMARY")
    print(f"{'='*100}\n")

    # Calculate totals
    total_files = len(results)
    total_lines = sum(r['lines'] for r in results)
    avg_score = sum(r['quality_score'] for r in results) / total_files if total_files > 0 else 0
    total_violations = sum(r['solid_violations'] for r in results)
    total_critical = sum(r['critical_issues'] for r in results)
    total_high = sum(r['high_issues'] for r in results)

    print(f"Files Analyzed: {total_files}")
    print(f"Total Lines: {total_lines:,}")
    print(f"Average Quality Score: {avg_score:.2f}/1.00")
    print(f"SOLID Violations: {total_violations}")
    print(f"Critical Issues: {total_critical}")
    print(f"High Priority Issues: {total_high}")
    print()

    # Sort by quality score (worst first)
    sorted_results = sorted(results, key=lambda r: r['quality_score'])

    print(f"\n{'='*100}")
    print("FILES BY QUALITY SCORE (worst first)")
    print(f"{'='*100}\n")
    print(f"{'Score':<8} {'SOLID':<7} {'Crit':<6} {'High':<6} {'Recs':<6} {'Lines':<7} File")
    print(f"{'-'*100}")

    for r in sorted_results[:20]:  # Top 20 worst files
        filename = Path(r['file']).name
        app_name = Path(r['file']).parts[2] if len(Path(r['file']).parts) > 2 else ''
        display_name = f"{app_name}/{filename}"[:60]

        print(f"{r['quality_score']:.2f}    "
              f"{r['solid_violations']:<7} "
              f"{r['critical_issues']:<6} "
              f"{r['high_issues']:<6} "
              f"{r['total_recommendations']:<6} "
              f"{r['lines']:<7} "
              f"{display_name}")


def print_detailed_issues(results: List[Dict[str, Any]], top_n: int = 5):
    """Print detailed issues for worst files."""
    # Sort by quality score
    sorted_results = sorted(results, key=lambda r: r['quality_score'])

    print(f"\n{'='*100}")
    print(f"DETAILED ANALYSIS - TOP {top_n} FILES NEEDING ATTENTION")
    print(f"{'='*100}\n")

    for i, r in enumerate(sorted_results[:top_n], 1):
        result = r['result']
        filename = r['file']

        print(f"\n{i}. {filename}")
        print(f"   Quality Score: {r['quality_score']:.2f}/1.00")
        print(f"   Lines: {r['lines']}")
        print()

        # SOLID violations
        if result.solid_analysis and result.solid_analysis.violations:
            print("   SOLID Violations:")
            for v in result.solid_analysis.violations[:3]:
                print(f"   - {v.principle.value.upper()}: {v.description[:80]}")
            print()

        # Top recommendations
        if result.consolidated_recommendations:
            print("   Top Recommendations:")
            for rec in result.consolidated_recommendations[:3]:
                print(f"   - [{rec.priority.name}] {rec.description[:80]}")
            print()

        print(f"   {'-'*80}")


def print_pattern_opportunities(results: List[Dict[str, Any]]):
    """Print design pattern opportunities across codebase."""
    print(f"\n{'='*100}")
    print("DESIGN PATTERN OPPORTUNITIES")
    print(f"{'='*100}\n")

    # Collect all pattern recommendations
    pattern_counts = {}
    pattern_files = {}

    for r in results:
        result = r['result']
        for pattern in result.pattern_recommendations:
            pattern_name = pattern.pattern_type.value
            if pattern_name not in pattern_counts:
                pattern_counts[pattern_name] = 0
                pattern_files[pattern_name] = []
            pattern_counts[pattern_name] += 1
            pattern_files[pattern_name].append(r['file'])

    # Sort by frequency
    sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)

    for pattern_name, count in sorted_patterns:
        print(f"{pattern_name.upper()} Pattern - {count} opportunities")
        print(f"  Files: {', '.join(Path(f).name for f in pattern_files[pattern_name][:3])}")
        if len(pattern_files[pattern_name]) > 3:
            print(f"  ... and {len(pattern_files[pattern_name]) - 3} more")
        print()


def main():
    """Main entry point."""
    print("="*100)
    print("BACKEND ARCHITECTURE ANALYSIS")
    print("api/callcentersite")
    print("="*100)

    # Find all Python files in backend
    backend_dir = "api/callcentersite"

    if not Path(backend_dir).exists():
        print(f"Error: Directory {backend_dir} not found")
        return 1

    print("\nFinding Python files...")
    python_files = find_python_files(backend_dir)

    print(f"Found {len(python_files)} Python files (excluding tests, migrations, cache)")

    # Create pipeline
    print("\nInitializing analysis pipeline...")
    pipeline = create_architecture_improvement_pipeline()

    # Analyze each file
    print("\nAnalyzing files...")
    results = []

    for i, file_path in enumerate(python_files, 1):
        print(f"  [{i}/{len(python_files)}] {file_path.relative_to(PROJECT_ROOT)}", end='\r')

        result = analyze_file(file_path, pipeline)
        if result:
            results.append(result)

    print("\n")

    if not results:
        print("No files analyzed successfully")
        return 1

    # Print reports
    print_summary_table(results)
    print_detailed_issues(results, top_n=5)
    print_pattern_opportunities(results)

    # Save full results to JSON
    output_dir = PROJECT_ROOT / Path(ANALYSIS_OUTPUT_RELATIVE).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / Path(ANALYSIS_OUTPUT_RELATIVE).name
    with output_file.open('w', encoding='utf-8') as f:
        # Prepare results for JSON (remove non-serializable objects)
        json_results = []
        for r in results:
            json_r = {k: v for k, v in r.items() if k != 'result'}
            json_results.append(json_r)

        json.dump({
            'summary': {
                'total_files': len(results),
                'average_score': sum(r['quality_score'] for r in results) / len(results),
                'total_violations': sum(r['solid_violations'] for r in results),
                'total_critical': sum(r['critical_issues'] for r in results),
                'total_high': sum(r['high_issues'] for r in results)
            },
            'files': json_results
        }, f, indent=2)

    print(f"\n{'='*100}")
    print(f"Full results saved to: {output_file}")
    print(f"{'='*100}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
