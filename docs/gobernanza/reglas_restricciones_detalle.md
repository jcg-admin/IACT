# Reglas y restricciones: detalle operativo

## Objetivo

Proveer un punto único donde se describan las restricciones críticas vigentes, su nivel de severidad y cómo se hacen cumplir en el proyecto. Esta vista complementa el inventario de artefactos documentado en `resumen_artefactos_reglas_restricciones.md`.

## Clasificación y criticidad

- **Críticas (P0)**: bloquean merges y despliegues si se incumplen. Incluyen prohibiciones tecnológicas y salvaguardas operativas.
- **Mayores (P1)**: deben resolverse en el mismo sprint, afectan calidad o seguridad.
- **Informativas (P2)**: guías que no bloquean, pero se auditan en QA.

## Restricción crítica: Prohibición de envío de correos electrónicos reales

- **Descripción**: El envío de correos electrónicos reales está prohibido; solo se permite mensajería interna o mecanismos simulados.
- **Dónde se controla**:
  - `scripts/validate_critical_restrictions.sh` detecta imports/uso de librerías de email y falla si se encuentran.
  - `scripts/ci/gate-restrictions.sh` ejecuta los chequeos en CI y bloquea merges.
  - `docs/gobernanza/guias/scripts/validate_critical_restrictions.md` documenta los patrones prohibidos y las alternativas (`InternalMessage`).
- **Aplicación esperada**:
  - Configuraciones de aplicaciones deben deshabilitar backends SMTP reales y usar mensajería interna.
  - Los tests deben mockear cualquier interacción con correo externo.
  - Las plantillas y checklists deben registrar evidencia de que no se envían correos reales en ningún entorno.

## Checklist de cobertura rápida

1. **Inventario**: confirmar que `resumen_artefactos_reglas_restricciones.md` refleja los artefactos actuales y su fecha de revisión.
2. **Severidad**: marcar cada restricción como crítica, mayor o informativa.
3. **Trazabilidad**: para cada restricción crítica, enlazar los artefactos donde se define y los scripts que la validan.
4. **Evidencia**: adjuntar logs de `scripts/validate_critical_restrictions.sh` y resultados de `scripts/ci/gate-restrictions.sh` en las carpetas de QA.
5. **Operacionalización**: documentar cómo se aplica la restricción en configuración (ej. deshabilitar SMTP) y en pruebas (mocks de email).
6. **Plantillas/procesos**: asegurar que las plantillas de reglas de negocio y checklists de QA exigen evidencias actualizadas.
7. **Excepciones**: registrar cualquier excepción aprobada con su ADR o issue de referencia.
8. **Gobernanza**: fechar este documento y asignar responsable de mantener la trazabilidad.

## Registro y responsables

- **Última actualización**: completar con la fecha de la próxima revisión.
- **Responsable**: equipo de arquitectura y QA de gobernanza.
- **Próxima acción**: al agregar nuevas restricciones críticas, actualizar este documento y el resumen para mantener la cobertura.
