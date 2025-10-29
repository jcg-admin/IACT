---
id: RB-DEVOPS-004
estado: vigente
propietario: equipo-devops
ultima_actualizacion: 2025-02-16
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
| Copilot CLI preparado | `post-create.sh` valida `node >=22` y `npm >=10`, instala `@github/copilot` y verifica que el comando `copilot` quede disponible. | La instalación cumple el flujo "install once, authenticate, work" sin pasos manuales. |
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
   node --version
   npm --version
   copilot
   ```
   - Confirmar que la CLI responda, que las versiones cumplan `node >=22` / `npm >=10` y que la sesión pertenezca a la cuenta corporativa.
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
- [ ] Copilot CLI instalado (`copilot --version`) y accesible desde la terminal.
- [ ] Extensiones de Copilot visibles en VS Code.
- [ ] `pytest` ejecutado automáticamente tras la reconstrucción del contenedor.
- [ ] Documentación interna actualizada con hallazgos y bloqueos.

## 5. Guía rápida para el equipo

1. **Instala y autentica**
   - Ejecuta `copilot` y sigue el flujo `/login`.
   - Concede acceso usando la cuenta con plan Copilot Pro/Business/Enterprise.
   - Valida con `gh auth status` y `gh copilot status` que la sesión quedó enlazada.
2. **Conoce el repositorio**
   - Pregunta “Explain the layout of this project.” para recibir un resumen de directorios y módulos.
   - Solicita “Make sure my environment is ready to build this project.” para que verifique dependencias y versiones.
3. **Encuentra trabajo relevante**
   - Usa “Find good first issues in this repository and rank them by difficulty.” para priorizar tareas.
   - Documenta en la wiki el issue seleccionado y los criterios de decisión.
4. **Implementa con control**
   - Pide “Start implementing issue #<número>. Show me the diff before applying.” para que proponga cambios revisables.
   - Revisa y aprueba antes de ejecutar los comandos sugeridos; mantén el flujo TDD habitual.
5. **Prepara la entrega**
   - Solicita “Stage changes, write a commit referencing #<número>, and open a draft PR.” para automatizar el empaquetado.
   - Asegúrate de editar el mensaje de commit para respetar el formato convencional.
6. **Resuelve incidentes operativos**
   - Pregunta “What process is using port 8080? Kill it and verify the port is free.” para liberar puertos ocupados.
   - Emplea `/session`, `/reset` o `/add-directory` para administrar permisos del asistente.

> **Extensiones MCP:** usa `/mcp` para integrar herramientas adicionales (p. ej. Playwright) siguiendo los lineamientos de seguridad definidos en `tasks/copilot-codespaces.md`.

> **Tip:** ante restricciones de red persistentes, coordinar con TI la creación de un túnel temporal usando la VPN corporativa oficial antes de iniciar Codespaces.
