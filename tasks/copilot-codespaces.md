# Playbook: habilitar GitHub Copilot y estabilizar Codespaces

> **Nota**: la verificación operativa y la bitácora viva se mantienen en `docs/07-devops/runbooks/github-copilot-codespaces.md`.

## Contexto
El objetivo es asegurar que los desarrolladores dispongan de asistencia con GitHub Copilot dentro de Codespaces y que el contenedor remoto se configure sin pasos manuales adicionales. Las tareas se organizan en completadas y pendientes para facilitar el seguimiento.

### Problema de las redes corporativas/escolares

- Los equipos de pruebas ejecutan el proyecto desde laboratorios corporativos y aulas universitarias en los que todo el tráfico hacia servicios de IA (GitHub Copilot, OpenAI, Azure AI) se bloquea a nivel de firewall.
- El personal no puede iniciar sesión en la extensión de Copilot porque la ventana de autenticación y las solicitudes `api.githubcopilot.com` quedan filtradas; después de varios intentos la interfaz de VS Code queda inutilizable.
- Las políticas de seguridad impiden instalar software adicional o modificar la configuración del proxy del sistema, por lo que las personas no tienen forma de habilitar Copilot por cuenta propia.
- Para no perder productividad en esos entornos cerrados, el devcontainer debe preparar de antemano la CLI de Copilot y dejar mensajes claros cuando la autenticación falle, de modo que soporte técnico pueda gestionar una lista blanca o una conexión alternativa.
- En resumen, el problema raíz es que la red corporativa/escolar actúa como un bloqueo total hacia los dominios de GitHub Copilot; esto deja a las personas desarrolladoras sin la herramienta pese a tener acceso autorizado, genera fricción operativa al soporte y retrasa la entrega de tareas mientras se consigue una excepción en el firewall.

### Impacto para las personas usuarias

- **Imposibilidad de usar Copilot**: el IDE muestra errores de autenticación y deja de sugerir código porque no puede contactar a los servidores de GitHub Copilot.
- **Cuellos de botella en soporte**: el equipo de TI debe gestionar excepciones de firewall caso por caso, lo que puede tardar días y deja al personal sin asistencia inteligente mientras tanto.
- **Pérdida de productividad**: sin sugerencias automáticas ni chat contextual, el trabajo sobre el monolito Django se vuelve más lento, especialmente para quienes están en capacitación.
- **Riesgo de configuraciones manuales**: ante la urgencia, algunas personas intentan instalar clientes no autorizados o modificar proxies locales, lo que viola políticas internas y puede provocar sanciones.

## Tareas completadas
- [x] Añadir las extensiones `github.copilot` y `github.copilot-chat` en `.devcontainer/devcontainer.json` para que estén disponibles al abrir el Codespace.
- [x] Configurar `github.copilot.enable` con políticas predeterminadas (deshabilitar en texto plano y entradas de commit) para cumplir buenas prácticas de seguridad.
- [x] Centralizar la instalación de dependencias y la copia del `env` en el script `infrastructure/devcontainer/scripts/post-create.sh`, reutilizado por el `postCreateCommand`.
- [x] Registrar la validación de `manage.py check` y del humo de `pytest` desde el `postCreateCommand`, almacenando la salida en `infrastructure/devcontainer/logs/post-create.log`.
- [x] Ejecutar `python manage.py check` en el arranque mediante `infrastructure/devcontainer/scripts/post-start.sh`, dejando evidencia en `infrastructure/devcontainer/logs/post-start.log`.

## Automatizaciones nuevas

| Tarea | Script | Resultado esperado |
|-------|--------|--------------------|
| Instalación de dependencias dev/test | `post-create.sh` | Detiene la creación del Codespace si falla `pip` (se documenta el error en el log). |
| Bootstrap de variables de entorno | `post-create.sh` | Crea `api/callcentersite/env` si no existía. |
| Verificación de salud de Django | `post-create.sh` y `post-start.sh` | Ejecutan `python manage.py check` y guardan la salida en logs persistentes. |
| Smoke test de pruebas automatizadas | `post-create.sh` | Corre `pytest --maxfail=1` (no bloqueante; advierte en el log si hay fallos). |

Los logs generados pueden consultarse ejecutando `cat infrastructure/devcontainer/logs/post-create.log` o `cat infrastructure/devcontainer/logs/post-start.log` desde dentro del Codespace.

## Validaciones manuales y seguimiento operativo

Las comprobaciones manuales se agrupan por objetivo para facilitar su reparto entre las personas responsables de plataforma y el equipo de desarrollo. Cada bloque puede ejecutarse de manera independiente, pero se recomienda seguir el orden propuesto para detectar problemas de forma temprana.

### Checklist resumido

1. **Reconstrucción del Codespace**
   - Ejecutar `Codespaces: Rebuild Container` (o `F1` → _Rebuild Container_).
   - Confirmar que no se muestren errores fatales al finalizar la reconstrucción.
   - Revisar `infrastructure/devcontainer/logs/post-create.log` y `infrastructure/devcontainer/logs/post-start.log`.
2. **Autenticación de Copilot/Codex**
   - Abrir cualquier archivo Python y solicitar una sugerencia con `Ctrl+Enter`.
   - Validar en la barra de estado que la sesión corresponde a la cuenta corporativa.
   - En caso de error, ejecutar `gh auth status` y `gh copilot status` para recopilar diagnósticos.
3. **Pruebas automatizadas**
   - Desde `api/callcentersite`, ejecutar `pytest`.
   - Registrar la cobertura reportada y adjuntar la salida al ticket de seguimiento.
4. **Documentación y traza**
   - Actualizar la wiki interna con los hallazgos, capturas de pantalla y cualquier incidencia reportada.
   - Indicar si fue necesario contactar a soporte de red o solicitar aperturas en el firewall.

### Seguimiento detallado por responsable

| Responsable | Objetivo | Pasos clave | Evidencia requerida |
|-------------|----------|-------------|---------------------|
| Plataforma | Reconstrucción del Codespace | Comando de reconstrucción, revisión de logs, verificación de hooks | Capturas de `post-create.log` y `post-start.log` sin errores críticos |
| Desarrollo | Validación de Copilot/Codex | Solicitar sugerencias, verificar sesión corporativa, ejecutar `gh copilot status` | Captura de la barra de estado conectada y salida de la CLI |
| QA | Ejecución de pruebas | `cd api/callcentersite && pytest`, revisión de cobertura | Salida completa de `pytest` con cobertura ≥80 % |
| PM/Coordinación | Documentación | Actualización de la wiki, centralización de hallazgos | Enlace al registro actualizado y resumen de bloqueos |

### Procedimiento de diagnóstico cuando falle Copilot/Codex

1. **Revisión rápida**
   - Ejecutar `gh auth status` para validar la sesión de GitHub CLI.
   - Ejecutar `gh copilot status` para revisar el estado de la conexión hacia los servicios de Copilot/Codex.
   - Confirmar que las variables de entorno relacionadas con el proxy (si aplica) estén presentes en el Codespace.
2. **Registro de incidentes**
   - Documentar el mensaje de error literal mostrado por la extensión y adjuntar capturas.
   - Si la autenticación falla por firewall, registrar el segmento de red y el dominio bloqueado para acelerar la apertura de puertos.
   - Escalar al equipo de TI con los registros anteriores y un resumen del impacto.
3. **Restauración temporal**
   - Indicar a la persona desarrolladora que continúe con la guía TDD estándar mientras se resuelve el incidente.
   - Mantener actualizado el ticket hasta confirmar que Copilot/Codex vuelve a ofrecer sugerencias y chat contextual.
