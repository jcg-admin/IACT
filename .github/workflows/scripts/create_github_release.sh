#!/bin/bash
set -e

# Create a GitHub release using gh CLI or API
# Required environment variables:
# - GITHUB_TOKEN
# - VERSION
# - PRERELEASE (optional, default: false)

VERSION="${VERSION}"
PRERELEASE="${PRERELEASE:-false}"
CHANGELOG_FILE="CHANGELOG-${VERSION}.md"

if [ -z "$VERSION" ]; then
    echo "ERROR: VERSION environment variable required"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN environment variable required"
    exit 1
fi

echo "Creating GitHub release for $VERSION..."

# Check if changelog exists
if [ ! -f "$CHANGELOG_FILE" ]; then
    echo "WARNING: Changelog file not found: $CHANGELOG_FILE"
    echo "Creating release with default notes..."
    RELEASE_NOTES="Release $VERSION

See full changelog in the repository.
"
else
    RELEASE_NOTES=$(cat "$CHANGELOG_FILE")
    echo "Using changelog from $CHANGELOG_FILE"
fi

# Create release using gh CLI
if command -v gh &> /dev/null; then
    echo "Using gh CLI to create release..."

    PRERELEASE_FLAG=""
    if [ "$PRERELEASE" = "true" ]; then
        PRERELEASE_FLAG="--prerelease"
    fi

    gh release create "$VERSION" \
        --title "Release $VERSION" \
        --notes "$RELEASE_NOTES" \
        $PRERELEASE_FLAG

    echo "Release $VERSION created successfully"
    echo "View at: $(gh release view $VERSION --json url -q .url)"
else
    echo "ERROR: gh CLI not found. Cannot create release."
    echo "Install gh CLI: https://cli.github.com/"
    exit 1
fi
