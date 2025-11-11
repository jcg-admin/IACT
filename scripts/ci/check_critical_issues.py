#!/usr/bin/env python3
"""
Check for critical architecture issues that should block merging.

This script reads the analysis results and fails the CI build if
critical issues are found.
"""

import sys
import json
from pathlib import Path


def main():
    """Check for critical issues and fail if found."""
    results_file = Path('architecture_analysis_results.json')

    if not results_file.exists():
        print("No analysis results found. Skipping critical issue check.")
        return 0

    with open(results_file, 'r') as f:
        results = json.load(f)

    if not results:
        print("No files analyzed. Skipping critical issue check.")
        return 0

    # Count critical issues
    total_critical = sum(r.get('critical_count', 0) for r in results)

    if total_critical > 0:
        print(f"\n❌ Found {total_critical} critical architecture issue(s)!")
        print("\nCritical issues must be addressed before merging:")

        for result in results:
            critical_count = result.get('critical_count', 0)
            if critical_count > 0:
                print(f"  - {result['file']}: {critical_count} critical issue(s)")

        print("\nPlease review the architecture analysis results and address critical issues.")
        print("You can run the analysis locally with:")
        print("  python scripts/ci/run_architecture_analysis.py")

        return 1

    print("✅ No critical architecture issues found.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
