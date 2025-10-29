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
    if command -v npm >/dev/null 2>&1 && command -v node >/dev/null 2>&1; then
      node_version_raw="$(node --version 2>/dev/null || echo "v0.0.0")"
      node_major="${node_version_raw#v}"
      node_major="${node_major%%.*}"
      npm_version_raw="$(npm --version 2>/dev/null || echo "0.0.0")"
      npm_major="${npm_version_raw%%.*}"

      echo "[post-create] Node detectado: $node_version_raw"
      echo "[post-create] npm detectado: $npm_version_raw"

      echo "[post-create] Registry configurado: $(npm config get registry 2>/dev/null || echo 'desconocido')"
      echo "[post-create] Proxy HTTP: $(npm config get proxy 2>/dev/null || echo 'no configurado')"
      echo "[post-create] Proxy HTTPS: $(npm config get https-proxy 2>/dev/null || echo 'no configurado')"

      echo "[post-create] Ejecutando npm ping para validar conectividad"
      if ping_output="$(npm ping 2>&1)"; then
        echo "[post-create] npm ping exitoso"
        printf '%s\n' "$ping_output"
      else
        echo "[post-create] Advertencia: npm ping falló" >&2
        printf '%s\n' "$ping_output" >&2
      fi

      diagnostics_enabled="${DEVCONTAINER_CAPTURE_NPM_DIAGNOSTICS:-1}"
      diagnostics_script="$(dirname "${BASH_SOURCE[0]}")/npm-diagnostics.sh"
      if [ "$diagnostics_enabled" = "1" ]; then
        if [ -x "$diagnostics_script" ]; then
          echo "[post-create] Ejecutando script de diagnóstico npm"
          if ! "$diagnostics_script"; then
            echo "[post-create] Advertencia: el script npm-diagnostics devolvió un error" >&2
          fi
        else
          echo "[post-create] Advertencia: npm-diagnostics.sh no es ejecutable o no existe" >&2
        fi
      else
        echo "[post-create] Diagnóstico npm omitido (DEVCONTAINER_CAPTURE_NPM_DIAGNOSTICS=$diagnostics_enabled)"
      fi

      if [ "${node_major:-0}" -ge 22 ] && [ "${npm_major:-0}" -ge 10 ]; then
        echo "[post-create] Instalando GitHub Copilot CLI (@github/copilot)"
        install_log=$(mktemp)
        if npm install -g @github/copilot >"$install_log" 2>&1; then
          if command -v copilot >/dev/null 2>&1; then
            echo "[post-create] Copilot CLI disponible (comando copilot)"
          else
            echo "[post-create] Advertencia: copilot no está en PATH tras la instalación" >&2
          fi
        else
          echo "[post-create] Advertencia: npm no pudo instalar @github/copilot" >&2
          cat "$install_log" >&2
        fi
        rm -f "$install_log"
      else
        echo "[post-create] Advertencia: se requiere Node >=22 y npm >=10 para Copilot CLI (versiones detectadas: node $node_version_raw, npm $npm_version_raw)" >&2
      fi
    else
      echo "[post-create] Node.js o npm no están disponibles; se omite la instalación de Copilot CLI"
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

  run_tests="${DEVCONTAINER_RUN_TESTS:-1}"
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
