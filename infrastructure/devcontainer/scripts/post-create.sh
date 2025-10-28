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

  install_copilot_cli="${DEVCONTAINER_INSTALL_COPILOT_CLI:-1}"
  if [ "$install_copilot_cli" = "1" ]; then
    if command -v npm >/dev/null 2>&1; then
      echo "[post-create] Instalando GitHub Copilot CLI"
      install_log=$(mktemp)
      alias_log=$(mktemp)
      if npm install -g @githubnext/github-copilot-cli >"$install_log" 2>&1; then
        echo "[post-create] GitHub Copilot CLI instalado correctamente"
        if command -v github-copilot-cli >/dev/null 2>&1; then
          alias_dir="$HOME/.config/github-copilot-cli"
          alias_file="$alias_dir/alias.sh"
          mkdir -p "$alias_dir"
          if github-copilot-cli alias -- bash >"$alias_file" 2>"$alias_log"; then
            if ! grep -Fq "github-copilot-cli" "$HOME/.bashrc" 2>/dev/null; then
              echo "source \"$alias_file\"" >> "$HOME/.bashrc"
              echo "[post-create] Alias de Copilot CLI añadidos a ~/.bashrc"
            else
              echo "[post-create] Alias de Copilot CLI ya presentes en ~/.bashrc"
            fi
          else
            echo "[post-create] Advertencia: no fue posible generar alias para Copilot CLI" >&2
            cat "$alias_log" >&2
          fi
        else
          echo "[post-create] Advertencia: github-copilot-cli no está en PATH tras la instalación" >&2
        fi
      else
        echo "[post-create] Advertencia: npm no pudo instalar github-copilot-cli" >&2
        cat "$install_log" >&2
      fi
      rm -f "$install_log" "$alias_log"
    else
      echo "[post-create] npm no está disponible; se omite GitHub Copilot CLI"
    fi
  else
    echo "[post-create] Instalación de Copilot CLI omitida (DEVCONTAINER_INSTALL_COPILOT_CLI=$install_copilot_cli)"
  fi

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

  run_tests="${DEVCONTAINER_RUN_TESTS:-0}"
  if [ "$run_tests" = "1" ]; then
    if command -v pytest >/dev/null 2>&1; then
      echo "[post-create] Ejecutando pytest (smoke test)"
      if ! python -m pytest --maxfail=1 --disable-warnings -q; then
        echo "[post-create] Advertencia: pytest finalizó con errores" >&2
      fi
    else
      echo "[post-create] pytest no está instalado todavía"
    fi
  else
    echo "[post-create] Pruebas omitidas (DEVCONTAINER_RUN_TESTS=$run_tests)"
  fi

  echo "[post-create] Fin: $(date --iso-8601=seconds)"
} | tee "$log_file"
