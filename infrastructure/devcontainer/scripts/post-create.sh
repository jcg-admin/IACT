#!/usr/bin/env bash
set -euo pipefail

log_dir="$(dirname "${BASH_SOURCE[0]}")/../logs"
mkdir -p "$log_dir"
log_file="$log_dir/post-create.log"

{
  echo "[post-create] Inicio: $(date --iso-8601=seconds)"
  workspace="/workspaces/${localWorkspaceFolderBasename:-$(basename "$PWD")}"
  project_dir="$workspace/api/callcentersite"

  if [ ! -d "$project_dir" ]; then
    echo "[post-create] Directorio de proyecto no encontrado: $project_dir" >&2
    exit 1
  fi

  cd "$project_dir"

  echo "[post-create] Actualizando pip"
  if ! python -m pip install --upgrade pip; then
    echo "[post-create] Advertencia: no fue posible actualizar pip" >&2
  fi

  install_requirements() {
    local req_file="$1"
    if [ -f "$req_file" ]; then
      echo "[post-create] Instalando dependencias desde $req_file"
      if ! python -m pip install -r "$req_file"; then
        echo "[post-create] Error: pip install falló para $req_file" >&2
        return 1
      fi
    else
      echo "[post-create] Archivo $req_file no encontrado, se omite la instalación"
    fi
  }

  install_requirements "requirements/dev.txt"
  install_requirements "requirements/test.txt"

  if [ -f "env.example" ] && [ ! -f "env" ]; then
    echo "[post-create] Copiando env.example → env"
    cp env.example env
  else
    echo "[post-create] No se requiere copiar env (ya existe o falta env.example)"
  fi

  if [ -f "manage.py" ]; then
    echo "[post-create] Ejecutando manage.py check"
    python manage.py check
  else
    echo "[post-create] manage.py no encontrado, se omite django check"
  fi

  if command -v pytest >/dev/null 2>&1; then
    echo "[post-create] Ejecutando pytest (smoke test)"
    if ! python -m pytest --maxfail=1 --disable-warnings -q; then
      echo "[post-create] Advertencia: pytest finalizó con errores" >&2
    fi
  else
    echo "[post-create] pytest no está instalado todavía"
  fi

  echo "[post-create] Fin: $(date --iso-8601=seconds)"
} | tee "$log_file"
