#!/usr/bin/env python3
"""
Evaluate overall code quality score from analysis results.

This script calculates an aggregate quality score for all changed files
and writes it to quality_score.txt for the quality gate check.
"""

import sys
import json
from pathlib import Path


def main():
    """Calculate and save quality score."""
    results_file = Path('architecture_analysis_results.json')

    if not results_file.exists():
        print("No analysis results found. Using default score.")
        score = 1.0  # No changes = perfect score
    else:
        with open(results_file, 'r') as f:
            results = json.load(f)

        if not results:
            print("No files analyzed. Using default score.")
            score = 1.0
        else:
            # Calculate average score across all files
            scores = [r.get('score', 0) for r in results if 'score' in r]

            if scores:
                score = sum(scores) / len(scores)
            else:
                score = 0.0

    # Save score
    with open('quality_score.txt', 'w') as f:
        f.write(f"{score:.2f}")

    print(f"Overall Quality Score: {score:.2f}/1.00")

    # Provide guidance
    if score < 0.5:
        print("⚠️  Quality score is low. Significant improvements needed.")
    elif score < 0.7:
        print("⚠️  Quality score is below recommended threshold. Consider addressing recommendations.")
    elif score < 0.9:
        print("✅ Quality score is acceptable. Minor improvements possible.")
    else:
        print("✅ Excellent quality score!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
