#!/bin/bash
set -e

# Calculate next semantic version based on commit messages
# Usage: ./get-next-version.sh [major|minor|patch]

BUMP_TYPE="${1:-auto}"

echo "🔍 Calculating next version..."

# Get current version from latest tag
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Current version: $CURRENT_VERSION"

# Remove 'v' prefix for processing
CURRENT_VERSION_NUMBER="${CURRENT_VERSION#v}"

# Split version into major.minor.patch
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION_NUMBER"

# Auto-detect bump type from commits
if [ "$BUMP_TYPE" = "auto" ]; then
    echo "🤖 Auto-detecting version bump type from commits..."

    # Get commits since last tag
    if [ "$CURRENT_VERSION" = "v0.0.0" ]; then
        COMMIT_RANGE="HEAD"
    else
        COMMIT_RANGE="${CURRENT_VERSION}..HEAD"
    fi

    # Check for breaking changes (BREAKING CHANGE in commit body)
    if git log $COMMIT_RANGE --pretty=%B | grep -qi "BREAKING CHANGE"; then
        BUMP_TYPE="major"
        echo "  Found BREAKING CHANGE → major version bump"
    # Check for features
    elif git log $COMMIT_RANGE --pretty=%s | grep -qi "^feat"; then
        BUMP_TYPE="minor"
        echo "  Found feat: commits → minor version bump"
    # Default to patch
    else
        BUMP_TYPE="patch"
        echo "  Default → patch version bump"
    fi
fi

# Calculate next version
case $BUMP_TYPE in
    major)
        NEXT_MAJOR=$((MAJOR + 1))
        NEXT_MINOR=0
        NEXT_PATCH=0
        ;;
    minor)
        NEXT_MAJOR=$MAJOR
        NEXT_MINOR=$((MINOR + 1))
        NEXT_PATCH=0
        ;;
    patch)
        NEXT_MAJOR=$MAJOR
        NEXT_MINOR=$MINOR
        NEXT_PATCH=$((PATCH + 1))
        ;;
    *)
        echo "❌ Invalid bump type: $BUMP_TYPE"
        echo "Valid types: major, minor, patch, auto"
        exit 1
        ;;
esac

NEXT_VERSION="v${NEXT_MAJOR}.${NEXT_MINOR}.${NEXT_PATCH}"

echo ""
echo "📦 Version Calculation:"
echo "  Current: $CURRENT_VERSION"
echo "  Bump Type: $BUMP_TYPE"
echo "  Next: $NEXT_VERSION"

# Set output for GitHub Actions
if [ -n "$GITHUB_OUTPUT" ]; then
    echo "current_version=$CURRENT_VERSION" >> $GITHUB_OUTPUT
    echo "next_version=$NEXT_VERSION" >> $GITHUB_OUTPUT
    echo "bump_type=$BUMP_TYPE" >> $GITHUB_OUTPUT
fi

# Also output to stdout for shell scripts
echo "$NEXT_VERSION"
