# Mitigar error 403 al instalar GitHub Copilot CLI

## Contexto
Incidencia recurrente en estaciones corporativas cuando `npm install -g @github/copilot` intenta descargar desde `registry.npmjs.org` y recibe `403 Forbidden`. El objetivo es reconfigurar `npm` para usar `https://npm.pkg.github.com`, autenticar con un token con scope `read:packages` y registrar evidencias del restablecimiento.

## Requisitos previos
- Token personal de GitHub (PAT) con scope `read:packages`, emitido por la cuenta corporativa.
- Acceso temporal a credenciales de proxy (si aplica) y permiso para editar `~/.npmrc` del usuario afectado.
- Node.js 18+ y npm 9+ instalados (el script corporativo exige `node >=22` y `npm >=10`; actualizar si fuera necesario).
- Comandos disponibles: `node`, `npm`, `gh`, `copilot`.

## Pasos
1. **Verificar versión y conectividad base**
   ```bash
   node --version
   npm --version
   npm ping --registry https://registry.npmjs.org || true
   ```
   - Registrar la salida para adjuntarla al ticket.
2. **Exportar token de GitHub**
   ```bash
   export GITHUB_TOKEN="<token-con-scope-read-packages>"
   ```
   - Guardar el token en el gestor de secretos corporativo y limitar su vigencia.
3. **Generar configuración dedicada de npm**
   ```bash
   cat <<'EONPM' > "$HOME/.npmrc"
   @github:registry=https://npm.pkg.github.com
   //npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
   always-auth=true
   EONPM
   ```
   - Si `$HOME/.npmrc` no es escribible, definir `export NPM_CONFIG_USERCONFIG="$PWD/.npmrc-copilot"` antes del bloque anterior.
4. **Forzar instalación desde el registro privado**
   ```bash
   npm install -g @github/copilot --registry=https://npm.pkg.github.com
   ```
   - En caso de usar proxy, añadir `--proxy` y `--https-proxy` apuntando al host autorizado.
5. **Validar disponibilidad del binario**
   ```bash
   which copilot
   copilot --version
   ```
   - Confirmar que el ejecutable reside dentro del `prefix` global (`npm config get prefix`).
6. **Restablecer configuración sensible**
   ```bash
   unset GITHUB_TOKEN
   shred -u "$HOME/.npmrc"
   ```
   - Si se configuró `NPM_CONFIG_USERCONFIG`, eliminar el archivo temporal y revertir la variable.
7. **Documentar en el runbook**
   - Actualizar el ticket con logs, fecha, responsable y rutas de evidencia (`infrastructure/devcontainer/logs/`).
   - Referenciar `docs/07-devops/runbooks/github-copilot-codespaces.md` sección “Error 403 Forbidden”.

## Validaciones
- `npm install -g @github/copilot` finaliza sin `E403` ni `E401`.
- `which copilot` apunta al directorio global registrado por `npm config get prefix`.
- `copilot --version` devuelve la versión actual y `gh copilot status` refleja autenticación correcta.
- En `post-create.log` aparece la línea `[post-create] Copilot CLI disponible` tras reconstruir el Codespace (si aplica).

## Evidencias sugeridas
- Captura o log de `npm install -g @github/copilot --registry=https://npm.pkg.github.com` mostrando `added`/`updated`.
- Salida de `copilot --version` y `gh copilot status`.
- Registro de eliminación segura del token (`unset` + `shred`).

## Contingencia y escalamiento
- Si el proxy sigue bloqueando `npm.pkg.github.com`, solicitar apertura de dominio adjuntando los logs anteriores.
- En caso de caducidad o permisos insuficientes del token, generar uno nuevo con scope `read:packages` y repetir el procedimiento.
- Documentar la incidencia en la wiki interna y sincronizar con el equipo de seguridad si se requieren tokens de mayor alcance.
