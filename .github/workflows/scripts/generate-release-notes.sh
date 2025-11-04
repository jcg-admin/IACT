#!/bin/bash
set -e

# Generate release notes from git history
# Usage: ./generate-release-notes.sh v1.2.3

VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "ERROR: Version argument required"
    echo "Usage: $0 v1.2.3"
    exit 1
fi

CHANGELOG_FILE="CHANGELOG-${VERSION}.md"

echo "Generating release notes for $VERSION..."

# Get previous tag
PREVIOUS_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [ -z "$PREVIOUS_TAG" ]; then
    echo "WARNING: No previous tag found. Generating notes from all commits."
    COMMIT_RANGE="HEAD"
else
    echo "Previous tag: $PREVIOUS_TAG"
    COMMIT_RANGE="${PREVIOUS_TAG}..HEAD"
fi

# Generate changelog
cat > "$CHANGELOG_FILE" << EOF
# Release ${VERSION}

**Release Date**: $(date -u +"%Y-%m-%d")

## What's Changed

EOF

# Categorize commits
echo "### Features" >> "$CHANGELOG_FILE"
git log $COMMIT_RANGE --pretty=format:"- %s (%h)" --grep="feat" --grep="feature" -i >> "$CHANGELOG_FILE" || echo "- No new features" >> "$CHANGELOG_FILE"
echo "" >> "$CHANGELOG_FILE"

echo "" >> "$CHANGELOG_FILE"
echo "### Bug Fixes" >> "$CHANGELOG_FILE"
git log $COMMIT_RANGE --pretty=format:"- %s (%h)" --grep="fix" --grep="bug" -i >> "$CHANGELOG_FILE" || echo "- No bug fixes" >> "$CHANGELOG_FILE"
echo "" >> "$CHANGELOG_FILE"

echo "" >> "$CHANGELOG_FILE"
echo "### Documentation" >> "$CHANGELOG_FILE"
git log $COMMIT_RANGE --pretty=format:"- %s (%h)" --grep="docs" --grep="documentation" -i >> "$CHANGELOG_FILE" || echo "- No documentation changes" >> "$CHANGELOG_FILE"
echo "" >> "$CHANGELOG_FILE"

echo "" >> "$CHANGELOG_FILE"
echo "### Maintenance" >> "$CHANGELOG_FILE"
git log $COMMIT_RANGE --pretty=format:"- %s (%h)" --grep="chore" --grep="refactor" -i >> "$CHANGELOG_FILE" || echo "- No maintenance changes" >> "$CHANGELOG_FILE"
echo "" >> "$CHANGELOG_FILE"

# Add all commits section
echo "" >> "$CHANGELOG_FILE"
echo "### All Commits" >> "$CHANGELOG_FILE"
echo "" >> "$CHANGELOG_FILE"
git log $COMMIT_RANGE --pretty=format:"- %s (%h) by @%an" >> "$CHANGELOG_FILE"
echo "" >> "$CHANGELOG_FILE"

# Add footer
cat >> "$CHANGELOG_FILE" << EOF

---

**Full Changelog**: https://github.com/2-Coatl/IACT---project/compare/${PREVIOUS_TAG}...${VERSION}
EOF

echo "Release notes generated: $CHANGELOG_FILE"

# Display preview
echo ""
echo "Preview:"
echo "-----------------------------------"
head -30 "$CHANGELOG_FILE"
echo "..."
echo "-----------------------------------"

# Set output for GitHub Actions
if [ -n "$GITHUB_OUTPUT" ]; then
    echo "changelog<<EOF" >> $GITHUB_OUTPUT
    cat "$CHANGELOG_FILE" >> $GITHUB_OUTPUT
    echo "EOF" >> $GITHUB_OUTPUT
fi
