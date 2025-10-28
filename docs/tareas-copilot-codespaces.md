# Tareas para habilitar GitHub Copilot y estabilizar Codespaces

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

## Tareas pendientes / validaciones manuales
- [ ] Reconstruir un Codespace nuevo y verificar la ejecución correcta de los hooks `postCreateCommand` y `postStartCommand`, confirmando que no haya errores en la terminal inicial.
- [ ] Validar interactivamente que GitHub Copilot y Copilot Chat se conecten a la cuenta corporativa y sugieran código dentro de VS Code.
- [ ] Ejecutar `pytest` desde el Codespace para comprobar que las dependencias de prueba instaladas durante el `postCreateCommand` funcionan correctamente (el script ya deja preparada la ejecución).
- [ ] Documentar en la wiki del proyecto el flujo recomendado de trabajo dentro de Codespaces (apertura, verificación de Copilot, ejecución de pruebas y despliegue local), enlazando a los scripts de automatización generados.

### Procedimiento sugerido para completar las validaciones manuales

1. **Reconstrucción del Codespace**
   - Comando: `Codespaces: Rebuild Container` en VS Code o `F1` → _Rebuild Container_.
   - Revisar los logs `post-create.log` y `post-start.log` para confirmar que no hay errores.
2. **Prueba de GitHub Copilot**
   - Abrir cualquier archivo Python y solicitar una sugerencia con `Ctrl+Enter`.
   - Confirmar en la barra de estado que la cuenta autenticada corresponde a la organización.
3. **Ejecución de pruebas**
   - Desde el terminal del Codespace ejecutar `cd api/callcentersite && pytest`.
   - Verificar que el comando finalice sin errores y con cobertura mínima del 80 %.
4. **Documentación en la wiki**
   - Registrar en la wiki corporativa el flujo de trabajo, referenciando los scripts:
     - `infrastructure/devcontainer/scripts/post-create.sh`
     - `infrastructure/devcontainer/scripts/post-start.sh`
   - Adjuntar capturas de pantalla del estado conectado de Copilot y la salida de `pytest`.
