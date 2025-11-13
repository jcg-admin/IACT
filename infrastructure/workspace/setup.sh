#!/bin/bash

set -euo pipefail

echo "=============================================="
echo "  MCP Workflows Infrastructure Setup"
echo "=============================================="

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js is not installed"
  echo "Install from: https://nodejs.org/"
  exit 1
fi

NODE_VERSION_MAJOR=$(node -v | cut -d'.' -f1 | tr -d 'v')
if [ "${NODE_VERSION_MAJOR}" -lt 18 ]; then
  echo "ERROR: Node.js version 18+ required"
  exit 1
fi

echo "[1/5] Node.js $(node -v) detected"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3 is not installed"
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "[2/5] Python ${PYTHON_VERSION} detected"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)

cd "${PROJECT_ROOT}"

echo "[3/5] Installing Node.js dependencies..."
npm install || echo "WARNING: npm install failed (offline environment?)"

echo "[4/5] Setting up Python virtual environment..."
if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
  python3 -m venv "${PROJECT_ROOT}/.venv"
fi

# shellcheck disable=SC1091
source "${PROJECT_ROOT}/.venv/bin/activate"

echo "[5/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure"
echo "  2. Activate Python venv: source .venv/bin/activate"
echo "  3. Run tests: npm test"
echo "  4. Start using: npm run vpn:setup-dev"
echo ""
