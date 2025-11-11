# CI/CD Integration Scripts

Automated architecture analysis scripts for GitHub Actions integration.

## Overview

These scripts enable automated code quality checks using the IACT meta-development agents in CI/CD pipelines.

## Scripts

### `run_architecture_analysis.py`

Analyzes changed Python files in a PR or commit using the complete architecture improvement pipeline.

**What it does:**
- Detects changed Python files via git
- Runs all 5 meta-development agents on each file
- Generates JSON and Markdown reports
- Creates PR comments with recommendations

**Output files:**
- `architecture_analysis_results.json` - Structured analysis data
- `architecture_analysis_results.md` - Human-readable report

**Usage:**
```bash
python scripts/ci/run_architecture_analysis.py
```

### `check_critical_issues.py`

Validates that no critical architecture issues exist.

**What it does:**
- Reads analysis results
- Counts critical issues
- Fails CI build if critical issues found

**Exit codes:**
- `0` - No critical issues
- `1` - Critical issues found (fails build)

**Usage:**
```bash
python scripts/ci/check_critical_issues.py
```

### `evaluate_quality_score.py`

Calculates overall code quality score for changed files.

**What it does:**
- Aggregates scores from all analyzed files
- Writes score to `quality_score.txt`
- Provides quality guidance

**Output file:**
- `quality_score.txt` - Quality score (0.00 to 1.00)

**Usage:**
```bash
python scripts/ci/evaluate_quality_score.py
```

## GitHub Actions Workflow

The `.github/workflows/meta-architecture-check.yml` workflow orchestrates these scripts.

## Local Testing

Test the CI scripts locally before pushing:

```bash
# Run analysis on specific files
python scripts/ci/run_architecture_analysis.py

# Check for critical issues
python scripts/ci/check_critical_issues.py

# Evaluate quality score
python scripts/ci/evaluate_quality_score.py
```

## Configuration

### Quality Threshold

Adjust the quality threshold in `.github/workflows/meta-architecture-check.yml`:

```yaml
THRESHOLD=0.7  # Default: 0.7 (70%)
```
