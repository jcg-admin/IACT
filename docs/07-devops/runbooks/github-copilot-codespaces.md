---
id: RB-DEVOPS-004
estado: vigente
propietario: equipo-devops
ultima_actualizacion: 2025-02-15
relacionados: ["DOC-OPS-001", "tasks/copilot-codespaces.md"]
---
# Runbook de verificación: GitHub Copilot y Codespaces

Este runbook confirma que el Codespace corporativo deja lista la integración con GitHub Copilot y registra las evidencias clave descritas en `tasks/copilot-codespaces.md`.

## 1. Matriz de cumplimiento

| Requisito | Evidencia | Validación |
|-----------|-----------|------------|
| Extensiones `github.copilot` y `github.copilot-chat` preinstaladas | `.devcontainer/devcontainer.json` → `customizations.vscode.extensions` | Ambas extensiones figuran junto al stack Python/SQL y se distribuyen en cada Codespace. |
| Políticas `github.copilot.enable` aplicadas | `.devcontainer/devcontainer.json` → `customizations.vscode.settings` | El ajuste deshabilita Copilot en texto plano y entradas de commit conforme a las políticas de seguridad. |
| Scripts centralizados para aprovisionamiento | `infrastructure/devcontainer/scripts/post-create.sh` y `post-start.sh` | Los comandos de bootstrap se ejecutan desde el repositorio y persisten logs en `infrastructure/devcontainer/logs/`. |
| Validación automática de Django | `post-create.sh` ejecuta `python manage.py check` tras instalar dependencias. | El resultado queda trazado en `post-create.log`. |
| Smoke test de `pytest` no bloqueante | `post-create.sh` ejecuta `python -m pytest --maxfail=1 --disable-warnings -q` por defecto y solo registra advertencias ante fallos. | Garantiza visibilidad temprana sin frenar la creación del Codespace. |
| Verificación en el arranque | `post-start.sh` relanza `python manage.py check` al iniciarse el contenedor remoto. | La salida se guarda en `post-start.log` para diagnóstico. |
| Copilot CLI preparado | `post-create.sh` instala `@githubnext/github-copilot-cli` vía `npm` cuando está disponible y añade alias en `~/.bashrc`. | Las personas usuarias pueden invocar `github-copilot-cli` sin pasos manuales. |
| Bootstrap de variables de entorno | `post-create.sh` copia `env.example` → `env` en `api/callcentersite/` si el archivo no existe. | Evita errores en `manage.py` tras el primer arranque. |

## 2. Procedimiento de auditoría rápida

1. **Reconstruir Codespace**
   ```bash
   Codespaces: Rebuild Container
   ```
   - Revisar `infrastructure/devcontainer/logs/post-create.log` y confirmar que no existan errores fatales de `pip`.
   - Verificar que el bloque `[post-create] Ejecutando pytest` aparezca incluso cuando existan fallos en las pruebas.
2. **Verificar Copilot CLI**
   ```bash
   gh auth status
   gh copilot status
   github-copilot-cli help
   ```
   - Confirmar que la CLI responda y que la sesión pertenezca a la cuenta corporativa.
3. **Solicitar sugerencia en VS Code**
   - Abrir un archivo Python y usar `Ctrl+Enter` para pedir una propuesta de código.
   - Comprobar la barra de estado de VS Code: debe mostrar “GitHub Copilot: conectado”.
4. **Ejecutar pruebas manuales**
   ```bash
   cd api/callcentersite
   python -m pytest --maxfail=1
   ```
   - Registrar cobertura ≥80 % y adjuntar la salida al ticket o wiki correspondiente.
5. **Actualizar documentación**
   - Registrar fecha, persona responsable y hallazgos en la wiki interna.
   - Escalar incidentes de firewall con logs adjuntos y referencias a dominios bloqueados.

## 3. Manejo de incidentes

1. **Diagnóstico inicial**
   - Ejecutar `gh auth status` y `gh copilot status` para confirmar autenticación.
   - Validar que las variables de entorno de proxy sigan presentes en el Codespace (`printenv | grep -i proxy`).
2. **Recolección de evidencias**
   - Guardar capturas de los mensajes de la extensión y de la barra de estado.
   - Documentar dominios o puertos bloqueados reportados en el firewall.
3. **Contención**
   - Indicar a la persona desarrolladora que continúe con el flujo TDD estándar mientras se gestiona la apertura de red.
   - Mantener actualizado el ticket hasta recibir confirmación de que Copilot vuelve a conectarse.

## 4. Checklist para entrega semanal

- [ ] `post-create.log` y `post-start.log` sin errores críticos.
- [ ] Copilot CLI instalado y alias disponible (`type github-copilot-cli`).
- [ ] Extensiones de Copilot visibles en VS Code.
- [ ] `pytest` ejecutado automáticamente tras la reconstrucción del contenedor.
- [ ] Documentación interna actualizada con hallazgos y bloqueos.

> **Tip:** ante restricciones de red persistentes, coordinar con TI la creación de un túnel temporal usando la VPN corporativa oficial antes de iniciar Codespaces.
