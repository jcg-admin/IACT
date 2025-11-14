#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DELEGATE="$REPO_ROOT/infrastructure/cpython/scripts/build_cpython.sh"

if [[ ! -x "$DELEGATE" ]]; then
    echo "[build_cpython] ERROR: expected executable delegate at $DELEGATE" >&2
    exit 1
fi

exec "$DELEGATE" "$@"
