#!/usr/bin/env bash
set -euo pipefail

log_dir="$(dirname "${BASH_SOURCE[0]}")/../logs"
mkdir -p "$log_dir"
log_file="$log_dir/post-start.log"

{
  echo "[post-start] Inicio: $(date --iso-8601=seconds)"
  workspace="/workspaces/${localWorkspaceFolderBasename:-$(basename "$PWD")}"
  project_dir="$workspace/api/callcentersite"

  if [ -d "$project_dir" ]; then
    cd "$project_dir"
    if [ -f "manage.py" ]; then
      echo "[post-start] Ejecutando manage.py check"
      python manage.py check
    else
      echo "[post-start] manage.py no encontrado, se omite django check"
    fi
  else
    echo "[post-start] Directorio de proyecto no encontrado: $project_dir" >&2
    exit 1
  fi

  echo "[post-start] Fin: $(date --iso-8601=seconds)"
} | tee "$log_file"
