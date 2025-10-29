#!/usr/bin/env bash
set -euo pipefail

script_dir="$(dirname "${BASH_SOURCE[0]}")"
log_dir="$script_dir/../logs"
mkdir -p "$log_dir"

timestamp="$(date +%Y%m%d_%H%M%S)"
log_file="$log_dir/npm-diagnostics-$timestamp.log"

dry_run="${DEVCONTAINER_NPM_DIAGNOSTICS_DRY_RUN:-0}"

{
  echo "[npm-diagnostics] Inicio: $(date --iso-8601=seconds)"

  if command -v node >/dev/null 2>&1; then
    echo "[npm-diagnostics] node --version: $(node --version 2>/dev/null)"
  else
    echo "[npm-diagnostics] node no está disponible en PATH" >&2
  fi

  if command -v npm >/dev/null 2>&1; then
    echo "[npm-diagnostics] npm --version: $(npm --version 2>/dev/null)"
    echo "[npm-diagnostics] npm config get registry: $(npm config get registry 2>/dev/null || echo 'error al obtener registry')"
    echo "[npm-diagnostics] npm config get proxy: $(npm config get proxy 2>/dev/null || echo 'error al obtener proxy')"
    echo "[npm-diagnostics] npm config get https-proxy: $(npm config get https-proxy 2>/dev/null || echo 'error al obtener https-proxy')"

    echo "[npm-diagnostics] Contenido de ~/.npmrc"
    if [ -f "$HOME/.npmrc" ]; then
      sed 's/^/  /' "$HOME/.npmrc"
    else
      echo "  (archivo inexistente)"
    fi

    global_config="$(npm config get globalconfig 2>/dev/null || echo '')"
    if [ -n "$global_config" ] && [ -f "$global_config" ]; then
      echo "[npm-diagnostics] Contenido de $global_config"
      sed 's/^/  /' "$global_config"
    else
      echo "[npm-diagnostics] Archivo global de npm no encontrado o no disponible"
    fi

    echo "[npm-diagnostics] npm config list"
    npm config list || echo "[npm-diagnostics] npm config list devolvió un error" >&2

    echo "[npm-diagnostics] Resultado de npm ping"
    if ping_output="$(npm ping 2>&1)"; then
      echo "  Éxito"
      printf '  %s\n' "$ping_output"
    else
      echo "  Falló" >&2
      printf '  %s\n' "$ping_output"
    fi

    if [ "$dry_run" = "1" ]; then
      echo "[npm-diagnostics] Ejecutando npm install --dry-run --verbose"
      install_log="$(mktemp)"
      if npm install -g @github/copilot --dry-run --verbose >"$install_log" 2>&1; then
        echo "  Dry run completado"
      else
        echo "  Dry run falló" >&2
      fi
      sed 's/^/  /' "$install_log"
      rm -f "$install_log"
    else
      echo "[npm-diagnostics] Dry run omitido (DEVCONTAINER_NPM_DIAGNOSTICS_DRY_RUN=$dry_run)"
    fi
  else
    echo "[npm-diagnostics] npm no está disponible en PATH" >&2
  fi

  echo "[npm-diagnostics] Fin: $(date --iso-8601=seconds)"
} | tee "$log_file"

