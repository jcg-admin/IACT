# ExecPlan: Stabilizar scripts CI locales sin dependencias externas

Esta ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log`, y `Outcomes & Retrospective` deben mantenerse al día conforme avance el trabajo. Se rige por las pautas de `.agent/PLANS.md`.

## Purpose / Big Picture

Queremos que los desarrolladores puedan ejecutar los scripts `scripts/ci/*.sh` sin que fallen inmediatamente cuando faltan dependencias como Django, Bandit o Docker. El objetivo es que `scripts/ci/run-all-checks.sh` entregue un resumen verde o con advertencias en entornos locales desconectados, reflejando los "skips" en lugar de fallos duros. Así reducimos la brecha entre lo que reportan los GitHub Actions y lo que se puede depurar localmente.

## Progress

- [x] (2025-11-16 10:30Z) ExecPlan redactada, alcance validado contra `.agent/PLANS.md` y expectativas del repositorio.
- [x] (2025-11-16 11:10Z) Ajustar pruebas en `scripts/tests/test_ci_shell_scripts.py` para reflejar los nuevos comportamientos (salidas exitosas con avisos/"skip").
- [x] (2025-11-16 11:20Z) Endurecer `scripts/ci/infrastructure/health-check.sh` para que degrade con advertencias cuando falte Django en vez de fallar.
- [x] (2025-11-16 11:25Z) Corregir rutas en `scripts/ci/security/csrf-check.sh` y `scripts/ci/security/django-security-check.sh`, incluyendo manejo de dependencias ausentes.
- [x] (2025-11-16 11:30Z) Hacer que `scripts/ci/security/bandit-scan.sh` detecte entornos sin Bandit o sin red y devuelva un "skip" trazable.
- [x] (2025-11-16 11:45Z) Normalizar `scripts/ci/infrastructure/validate-config.sh` y los hooks de `scripts/git-hooks/*.sh` (permisos + sintaxis) para que pasen la validación de scripts.
- [x] (2025-11-16 11:55Z) Confirmar que `scripts/ci/run-all-checks.sh` termina con código 0 y reporta secciones con PASS/SKIP según corresponda.
- [x] (2025-11-16 12:05Z) Documentar hallazgos y resultados en las secciones vivas antes de cerrar la ExecPlan.
- [x] (2025-11-16 12:40Z) Revisar `bandit-scan.sh`, `npm-audit.sh` y `test-execution-time.sh` para eliminar dependencias implícitas en GitHub Actions (instalaciones automáticas, pipelines con `tee` sin `pipefail`).
- [x] (2025-11-16 12:42Z) Ampliar las pruebas de `scripts/tests/test_ci_shell_scripts.py` cubriendo los degradados esperados para Bandit, npm y el test pyramid en entornos sin dependencias.

## Surprises & Discoveries

- Observación: la especificación OpenAPI (`docs/api/openapi_permisos.yaml`) contenía descripciones sin comillas con dos puntos, lo que rompía el parser YAML. Se resolvió citando los literales problemáticos.
- Observación: `.devcontainer/devcontainer.json` incluye comentarios estilo JavaScript; el validador JSON se detuvo hasta que se agregó una lista de exclusión controlada.
- Observación: algunos workflows (`requirements_validate_traceability.yml`) se generan dinámicamente y no son YAML puro, de modo que se marcaron como `skip` para evitar falsos positivos.
- Observación: `npm audit` requiere `package-lock.json` y acceso al registro; en entornos locales sin dependencias instaladas o sin red es preferible degradar a `skip` para no bloquear desarrolladores.

## Decision Log

- Decisión: Tratar los chequeos que dependen de Django/Bandit como "skip" cuando las dependencias no estén presentes. Rationale: el entorno local y de CI desconectado no puede instalarlas, pero necesitamos que el pipeline continúe. Fecha: 2025-11-16 / Autor: Codex.
- Decisión: Excluir `.devcontainer/devcontainer.json` y `requirements_validate_traceability.yml` de la validación estricta (registrando advertencias). Rationale: ambos archivos usan sintaxis extendida intencional (comentarios y plantillas) y romperían la verificación en frío. Fecha: 2025-11-16 / Autor: Codex.
- Decisión: No intentar instalaciones automáticas (`pip install bandit`, `npm audit fix`) dentro de los scripts; en su lugar, degradar con mensajes accionables cuando la CLI o la red no estén disponibles. Rationale: evitar bloqueos en entornos air-gapped y mantener tiempos de ejecución acotados. Fecha: 2025-11-16 / Autor: Codex.

## Outcomes & Retrospective

- `scripts/ci/run-all-checks.sh` ahora finaliza con código 0 en entornos sin Django/Bandit, marcando seis chequeos como SKIP y manteniendo el reporte final completo.
- Los scripts de infraestructura y seguridad reportan advertencias claras ("Skipping Django checks", "Bandit installation failed - skipping") en lugar de stack traces, mejorando la depuración local.
- Las pruebas `pytest scripts/tests/test_ci_shell_scripts.py` verifican el nuevo flujo (3/3 en 26.9s) confirmando el comportamiento degradado.
- Los scripts de seguridad y validación del test pyramid ahora detectan la ausencia de `bandit`, `npm`, Django o la red antes de ejecutar comandos costosos, retornando `SKIP` en segundos y evitando depender de GitHub Actions para descubrir estos casos.

## Context and Orientation

Los GitHub Actions listados por el usuario mapean casi uno-a-uno a scripts dentro de `scripts/ci/`. Actualmente `scripts/ci/run-all-checks.sh` concluye con código 1 porque:

1. `scripts/ci/infrastructure/health-check.sh` ejecuta `python3 manage.py check` y falla por `ModuleNotFoundError: No module named 'django'` en entornos sin dependencias instaladas.
2. `scripts/ci/security/bandit-scan.sh` intenta instalar Bandit con pip, pero la red está restringida y el script termina con error.
3. `scripts/ci/security/csrf-check.sh` y `scripts/ci/security/django-security-check.sh` referencian `callcentersite/settings.py`, archivo que no existe porque la configuración está fragmentada bajo `callcentersite/settings/base.py` y otros módulos.
4. `scripts/ci/infrastructure/validate-scripts.sh` falla porque varios `.sh` en `scripts/examples/`, `scripts/coding/ai/` y `scripts/git-hooks/` no tienen bit ejecutable y uno (`validate-environment.sh`) tiene un `fi` duplicado.

Esto provoca que la suite de infraestructura registre múltiples FAIL en cascada y que los jobs de GitHub Actions mueran en segundos. Necesitamos:

- Ajustar los scripts para distinguir entre fallas reales y prerequisitos ausentes, devolviendo exit code 2 (que tratamos como SKIP) o 0 con advertencias cuando corresponda.
- Reparar permisos/sintaxis para que `validate-scripts.sh` no detone errores triviales.
- Actualizar las pruebas para reflejar la expectativa: "salida agregada con PASS/SKIP" en vez de "falla asegurada".

## Plan of Work

1. Modificar `scripts/tests/test_ci_shell_scripts.py` para:
   - Esperar que `run-all-checks.sh` devuelva 0 y siempre muestre el resumen final.
   - Validar que el resumen incluya conteos de skipped cuando falten prerequisitos.
   - Ajustar la prueba del health check para buscar el mensaje de degradación controlada (p. ej. "Skipping Django checks"), aceptando exit code 0 o 2 según la implementación.
2. Aplicar permisos ejecutables (`chmod +x`) a los scripts listados por `find scripts -name '*.sh' ! -perm -u+x` y corregir el bloque duplicado en `scripts/git-hooks/validate-environment.sh`.
3. Editar `scripts/ci/infrastructure/health-check.sh` para:
   - Comprobar si `python3 -m django --version` o `python3 -c 'import django'` es posible; si no, marcar los chequeos de Django/DB como skipped y continuar con las demás verificaciones.
   - Emitir mensajes claros indicando que se omiten pasos por falta de dependencias.
   - Evitar salir con código 1 cuando la única causa es falta de Django.
4. Ajustar `scripts/ci/security/csrf-check.sh` para localizar `callcentersite/settings/base.py` (o la ruta correcta según `PYTHONPATH`) y no fallar por archivos inexistentes.
5. Modificar `scripts/ci/security/django-security-check.sh` para:
   - Usar la ruta correcta de settings.
   - Detectar `ModuleNotFoundError` de Django y convertir la comprobación en un SKIP (exit 2) manteniendo un log con la causa.
6. Cambiar `scripts/ci/security/bandit-scan.sh` de modo que si Bandit no está disponible y la instalación falla, se registre un skip en vez de un fail.
7. Revisar `scripts/ci/infrastructure/validate-config.sh` para que el chequeo de settings degrade a skip cuando falte Django, manteniendo las validaciones de JSON/YAML.
8. Ejecutar `scripts/ci/run-all-checks.sh` y las pruebas unitarias para verificar que el pipeline regresa exit 0 y que los mensajes de skip están presentes.
9. Ajustar `scripts/ci/security/npm-audit.sh` para detectar el frontend bajo `ui/`, degradar a skip cuando `npm` no esté disponible o la red falle y evitar `npm audit fix` en entornos locales.
10. Simplificar `scripts/ci/security/bandit-scan.sh` para que omita instalaciones automáticas y degrade inmediatamente si la CLI no está presente.
11. Incorporar una guardia en `scripts/ci/testing/test-execution-time.sh` (Django + pytest) y habilitar `set -o pipefail` para evitar falsos positivos al canalizar la salida.

## Concrete Steps

- Ejecutar `pytest scripts/tests/test_ci_shell_scripts.py` después de cada modificación clave.
- Ejecutar `scripts/ci/run-all-checks.sh --only infrastructure` y `--only security` para observar los nuevos resultados.
- Utilizar `git status` para confirmar los cambios y `git diff` para inspeccionar el contenido antes de commitear.

## Validation and Acceptance

Se considerará que el trabajo está completo cuando:

- `pytest scripts/tests/test_ci_shell_scripts.py` pase en un entorno sin dependencias externas.
- `scripts/ci/run-all-checks.sh` retorne 0, muestre el reporte final y marque como SKIP los chequeos que dependen de Django/Bandit sin abortar la ejecución.
- `scripts/ci/infrastructure/validate-scripts.sh` termine sin errores de sintaxis ni permisos.

## Idempotence and Recovery

Las modificaciones son idempotentes: volver a ejecutar los scripts y pruebas no generará efectos secundarios (p. ej., los permisos ejecutables se pueden aplicar múltiples veces). Si un cambio rompe el pipeline, se puede restaurar ejecutando `git restore <archivo>` o `git checkout -- <archivo>` para regresar al estado previo.

## Artifacts and Notes

- Mantener capturas de la salida de `run-all-checks.sh` en `/tmp` para comparaciones si es necesario.
- Registrar en el `Decision Log` cualquier ajuste adicional requerido por scripts auxiliares.

## Interfaces and Dependencies

- Scripts principales: `scripts/ci/run-all-checks.sh`, `scripts/ci/infrastructure/health-check.sh`, `scripts/ci/security/*.sh`.
- Pruebas: `scripts/tests/test_ci_shell_scripts.py`.
- Dependencias Python: opcionales; los scripts deben comportarse correctamente incluso cuando `django` o `bandit` no estén instalados.

