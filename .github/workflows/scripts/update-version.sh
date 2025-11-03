#!/bin/bash
set -e

# Update version number in project files
# Usage: ./update-version.sh 1.2.3

VERSION="$1"

if [ -z "$VERSION" ]; then
    echo "❌ Error: Version argument required"
    echo "Usage: $0 1.2.3 (without 'v' prefix)"
    exit 1
fi

echo "🔄 Updating version to $VERSION in project files..."

FILES_UPDATED=0

# Update mkdocs.yml if it exists
if [ -f "docs/mkdocs.yml" ]; then
    if grep -q "^extra:" docs/mkdocs.yml; then
        # Update existing version
        sed -i "s/version: .*/version: $VERSION/" docs/mkdocs.yml
    else
        # Add version to extra section
        echo "" >> docs/mkdocs.yml
        echo "extra:" >> docs/mkdocs.yml
        echo "  version: $VERSION" >> docs/mkdocs.yml
    fi
    echo "  ✅ Updated docs/mkdocs.yml"
    FILES_UPDATED=$((FILES_UPDATED + 1))
fi

# Update package.json if it exists
if [ -f "package.json" ]; then
    if command -v jq &> /dev/null; then
        jq --arg version "$VERSION" '.version = $version' package.json > package.json.tmp
        mv package.json.tmp package.json
        echo "  ✅ Updated package.json"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    else
        sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" package.json
        echo "  ✅ Updated package.json"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    fi
fi

# Update pyproject.toml if it exists
if [ -f "pyproject.toml" ]; then
    sed -i "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml
    echo "  ✅ Updated pyproject.toml"
    FILES_UPDATED=$((FILES_UPDATED + 1))
fi

# Update Cargo.toml if it exists
if [ -f "Cargo.toml" ]; then
    sed -i "s/^version = \".*\"/version = \"$VERSION\"/" Cargo.toml
    echo "  ✅ Updated Cargo.toml"
    FILES_UPDATED=$((FILES_UPDATED + 1))
fi

# Create/Update VERSION file
echo "$VERSION" > VERSION
echo "  ✅ Updated VERSION file"
FILES_UPDATED=$((FILES_UPDATED + 1))

# Update version in README if it exists
if [ -f "README.md" ]; then
    if grep -q "Version:" README.md; then
        sed -i "s/Version: .*/Version: $VERSION/" README.md
        echo "  ✅ Updated README.md"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    elif grep -q "version" README.md; then
        sed -i "s/version [0-9]\+\.[0-9]\+\.[0-9]\+/version $VERSION/" README.md
        echo "  ✅ Updated README.md"
        FILES_UPDATED=$((FILES_UPDATED + 1))
    fi
fi

echo ""
if [ $FILES_UPDATED -eq 0 ]; then
    echo "⚠️  No files were updated (no version files found)"
    echo "Consider adding version to:"
    echo "  - docs/mkdocs.yml"
    echo "  - package.json"
    echo "  - pyproject.toml"
    echo "  - README.md"
else
    echo "✅ Updated version in $FILES_UPDATED file(s)"
fi
