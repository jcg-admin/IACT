#!/bin/bash
# scripts/install_hooks.sh
# Installs Git hooks automatically from scripts/git-hooks/
# Reference: ESTRATEGIA_GIT_HOOKS.md

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
readonly HOOKS_TEMPLATES="$PROJECT_ROOT/scripts/git-hooks"

echo "Installing Git Hooks"
echo "===================="
echo ""

# Check if we're in a Git repository
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "ERROR: Not a Git repository"
    echo "Run this script from within the Git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install hooks
INSTALLED=0
SKIPPED=0

for hook in pre-commit commit-msg pre-push pre-rebase; do
    if [ -f "$HOOKS_TEMPLATES/$hook" ]; then
        # Check if hook already exists
        if [ -f "$HOOKS_DIR/$hook" ]; then
            echo "[$hook] Already exists, backing up..."
            mv "$HOOKS_DIR/$hook" "$HOOKS_DIR/$hook.backup.$(date +%Y%m%d_%H%M%S)"
        fi

        echo "[$hook] Installing..."
        cp "$HOOKS_TEMPLATES/$hook" "$HOOKS_DIR/$hook"
        chmod +x "$HOOKS_DIR/$hook"
        echo "  Installed: $HOOKS_DIR/$hook"
        INSTALLED=$((INSTALLED + 1))
    else
        echo "[$hook] Template not found, skipping"
        SKIPPED=$((SKIPPED + 1))
    fi
done

echo ""
echo "===================="
echo "INSTALLATION COMPLETE"
echo "===================="
echo "Installed: $INSTALLED hook(s)"
echo "Skipped: $SKIPPED hook(s)"
echo ""

echo "Hooks installed:"
echo "  - pre-commit:  Fast validations (emojis, syntax, debug, file size)"
echo "  - commit-msg:  Conventional Commits format validation"
echo "  - pre-push:    Tests and linting before push"
echo "  - pre-rebase:  Protection for main/develop branches"
echo ""

echo "To test:"
echo "  1. Make a change:     echo '# test' >> README.md"
echo "  2. Stage it:          git add README.md"
echo "  3. Commit:            git commit -m 'test: validate hooks'"
echo "     (pre-commit and commit-msg will run)"
echo "  4. Push:              git push"
echo "     (pre-push will run)"
echo ""

echo "To bypass hooks (NOT recommended):"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""

echo "To uninstall hooks:"
echo "  rm $HOOKS_DIR/pre-commit"
echo "  rm $HOOKS_DIR/commit-msg"
echo "  rm $HOOKS_DIR/pre-push"
echo "  rm $HOOKS_DIR/pre-rebase"
echo ""

exit 0
