#!/bin/bash
set -e

# Check if a GitHub release already exists for the given version
# Usage: ./check-release-exists.sh v1.2.3

VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "❌ Error: Version argument required"
    echo "Usage: $0 v1.2.3"
    exit 1
fi

echo "🔍 Checking if release $VERSION already exists..."

# Check using gh CLI if available
if command -v gh &> /dev/null; then
    if gh release view "$VERSION" &> /dev/null; then
        echo "❌ Release $VERSION already exists!"
        echo "To view: gh release view $VERSION"
        exit 1
    else
        echo "✅ Release $VERSION does not exist yet"
        exit 0
    fi
fi

# Fallback: Check using git tags
if git rev-parse "$VERSION" &> /dev/null; then
    echo "⚠️  Tag $VERSION exists locally"

    # Check if tag exists on remote
    if git ls-remote --tags origin | grep -q "refs/tags/$VERSION"; then
        echo "❌ Tag $VERSION already exists on remote!"
        exit 1
    else
        echo "⚠️  Tag exists locally but not on remote. Push pending."
        exit 0
    fi
else
    echo "✅ Release $VERSION does not exist"
    exit 0
fi
