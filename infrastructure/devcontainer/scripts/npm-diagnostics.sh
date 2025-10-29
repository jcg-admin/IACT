#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[npm-diagnostics] %s\n' "$1"
}

log "Inicio: $(date --iso-8601=seconds)"

if ! command -v npm >/dev/null 2>&1; then
  log "npm no está disponible en PATH; se omite la recopilación"
  exit 0
fi

log "Ubicación de npm: $(command -v npm)"
log "Ubicación de node: $(command -v node 2>/dev/null || echo 'no encontrado')"
log "Versión de node: $(node --version 2>/dev/null || echo 'desconocida')"
log "Versión de npm: $(npm --version 2>/dev/null || echo 'desconocida')"

log "Salida de npm config list"
if ! npm config list; then
  log "Advertencia: npm config list finalizó con errores"
fi

print_config_file() {
  local label="$1"
  local file="$2"
  if [ -n "$file" ] && [ -f "$file" ]; then
    log "Contenido de $label ($file)"
    sed 's/^/    /' "$file"
  else
    log "Archivo $label no encontrado ($file)"
  fi
}

user_config="${NPM_CONFIG_USERCONFIG:-}"
workspace_npmrc="${WORKSPACE_NPMRC:-.npmrc}"

print_config_file "NPM_CONFIG_USERCONFIG" "$user_config"
print_config_file "~/.npmrc" "$HOME/.npmrc"
print_config_file "workspace .npmrc" "$workspace_npmrc"

project_npmrc="$PWD/.npmrc"
if [ "$project_npmrc" != "$workspace_npmrc" ]; then
  print_config_file "proyecto .npmrc" "$project_npmrc"
fi

for key in proxy https-proxy; do
  value="$(npm config get "$key" 2>&1 || true)"
  log "npm config get $key → ${value:-<sin definir>}"
done

dry_run="${DEVCONTAINER_NPM_DIAGNOSTICS_DRY_RUN:-0}"
if [ "$dry_run" = "1" ]; then
  log "Ejecutando npm install -g @github/copilot --dry-run --verbose"
  if ! npm install -g @github/copilot --dry-run --verbose; then
    log "Advertencia: npm install --dry-run devolvió un error"
  fi
else
  log "Dry-run de npm install omitido (DEVCONTAINER_NPM_DIAGNOSTICS_DRY_RUN=$dry_run)"
fi

log "Fin: $(date --iso-8601=seconds)"
