# GitHub Actions Workflow Scripts

This directory contains utility scripts used by GitHub Actions workflows for automating release management, documentation deployment, and code quality checks.

## Scripts Overview

### 1. `check-release-exists.sh`

**Purpose**: Verify if a release/tag already exists before creating a new one.

**Usage**:
```bash
./check-release-exists.sh v1.2.3
```

**Used by**: `release.yml` workflow

**Exit codes**:
- `0`: Release doesn't exist (safe to proceed)
- `1`: Release already exists (abort)

---

### 2. `create-github-release.sh`

**Purpose**: Create a GitHub release using `gh` CLI.

**Usage**:
```bash
export GITHUB_TOKEN="ghp_xxx"
export VERSION="v1.2.3"
export PRERELEASE="false"  # optional

./create-github-release.sh
```

**Requirements**:
- `gh` CLI installed
- `GITHUB_TOKEN` environment variable
- Changelog file: `CHANGELOG-${VERSION}.md`

**Used by**: `release.yml` workflow

---

### 3. `create-release-packages.sh`

**Purpose**: Create distribution packages (ZIP and TAR.GZ) for releases.

**Usage**:
```bash
./create-release-packages.sh v1.2.3
```

**Output**:
- `dist/iact-docs-1.2.3.zip`
- `dist/iact-docs-1.2.3.tar.gz`
- `dist/iact-docs-1.2.3.sha256` (checksums)

**Package contents**:
- `docs/` - Complete documentation
- `VERSION` - Version number
- `RELEASE_INFO.txt` - Release metadata
- `README.md`, `LICENSE` (if present)

**Used by**: `release.yml` workflow

---

### 4. `generate-release-notes.sh`

**Purpose**: Generate structured release notes from git commit history.

**Usage**:
```bash
./generate-release-notes.sh v1.2.3
```

**Output**: `CHANGELOG-v1.2.3.md` with sections:
- ✨ Features (`feat:` commits)
- 🐛 Bug Fixes (`fix:` commits)
- 📚 Documentation (`docs:` commits)
- 🔧 Maintenance (`chore:`, `refactor:` commits)
- 📋 All Commits

**Used by**: `release.yml` workflow

---

### 5. `get-next-version.sh`

**Purpose**: Calculate the next semantic version based on commits.

**Usage**:
```bash
# Auto-detect from commits
./get-next-version.sh auto

# Specify bump type
./get-next-version.sh major   # 1.0.0 → 2.0.0
./get-next-version.sh minor   # 1.0.0 → 1.1.0
./get-next-version.sh patch   # 1.0.0 → 1.0.1
```

**Auto-detection rules**:
- `BREAKING CHANGE` in commit → **major** bump
- `feat:` commits → **minor** bump
- Other commits → **patch** bump

**Output**: `v1.2.3` (to stdout and `$GITHUB_OUTPUT`)

**Used by**: Manual release preparation

---

### 6. `update-version.sh`

**Purpose**: Update version number across project files.

**Usage**:
```bash
./update-version.sh 1.2.3  # without 'v' prefix
```

**Files updated**:
- `docs/mkdocs.yml` (MkDocs config)
- `package.json` (Node.js)
- `pyproject.toml` (Python)
- `Cargo.toml` (Rust)
- `VERSION` (plain text file)
- `README.md` (if version mentioned)

**Used by**: `release.yml` workflow

---

## Workflow Integration

These scripts are called by the following workflows:

### `release.yml` (Release Management)

```
validate-version (check-release-exists.sh)
    ↓
generate-changelog (generate-release-notes.sh)
    ↓
create-packages (create-release-packages.sh)
    ↓
update-versions (update-version.sh)
    ↓
create-release (create-github-release.sh)
```

### Manual Release Process

```bash
# 1. Get next version
NEXT_VERSION=$(./get-next-version.sh auto)
echo "Next version: $NEXT_VERSION"

# 2. Check if it already exists
./check-release-exists.sh $NEXT_VERSION

# 3. Update version files
./update-version.sh ${NEXT_VERSION#v}

# 4. Commit changes
git add -A
git commit -m "chore(release): bump version to $NEXT_VERSION"

# 5. Create tag
git tag $NEXT_VERSION

# 6. Push (triggers automated release workflow)
git push origin main --tags
```

---

## Requirements

### System Tools

- `bash` 4.0+
- `git` 2.0+
- `gh` CLI (GitHub CLI) - for release creation
- Standard UNIX tools: `sed`, `awk`, `grep`, `tar`, `zip`

### Optional Tools

- `jq` - for JSON processing (package.json updates)
- `sha256sum` - for checksum generation

### GitHub Permissions

Workflows require the following permissions:
```yaml
permissions:
  contents: write        # For creating releases and tags
  pull-requests: write   # For commenting on PRs
  issues: write          # For release announcements
```

---

## Testing Scripts Locally

```bash
# Test version detection
./get-next-version.sh auto

# Test release notes generation
./generate-release-notes.sh v1.0.0

# Test package creation
./create-release-packages.sh v1.0.0
ls -lh dist/

# Test version update (dry-run)
git stash  # save your changes
./update-version.sh 1.0.0
git diff   # review changes
git reset --hard  # revert
git stash pop
```

---

## Troubleshooting

### Error: "gh: command not found"

Install GitHub CLI:
```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Manual installation
https://cli.github.com/
```

### Error: "GITHUB_TOKEN not set"

Set token for local testing:
```bash
export GITHUB_TOKEN=$(gh auth token)
```

### Error: "Permission denied"

Make scripts executable:
```bash
chmod +x .github/workflows/scripts/*.sh
```

### Error: "Release already exists"

Delete existing release/tag:
```bash
gh release delete v1.2.3 --yes
git tag -d v1.2.3
git push origin :refs/tags/v1.2.3
```

---

## Contributing

When modifying scripts:

1. Test locally before committing
2. Update this README with changes
3. Follow existing error handling patterns
4. Use `set -e` for fail-fast behavior
5. Add descriptive echo messages
6. Document required environment variables

---

## License

These scripts are part of the IACT project and follow the same license.

---

**Maintained by**: DevOps Team
**Last Updated**: 2025-11-02
**Version**: 1.0.0
