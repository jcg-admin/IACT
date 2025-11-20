---
id: ADR-BACK-006
tipo: adr
estado: aceptada
fecha: 2025-11-20
contexto: |
  Existen dos implementaciones del dominio de configuraciones: la app legacy `configuracion` (en español)
  y la app moderna `configuration` (en inglés). La duplicidad generaba rutas paralelas, modelos distintos
  y esfuerzos duplicados de mantenimiento. La consolidación previa eliminó la app en español y expuso las
  rutas heredadas desde el módulo en inglés, produciendo un diff con -862 líneas y +324, lo que generó dudas
  sobre si se perdió funcionalidad.
decision: |
  Mantener únicamente la app `configuration` como fuente de verdad y mapear las rutas en español hacia sus
  vistas. No se recrearon los archivos eliminados porque los comportamientos existentes en `configuration`
  cubren los casos de uso de la app legacy; las pruebas unitarias validan que los endpoints en español se
  resuelven a la lógica en inglés.
consecuencias: |
  - Se reduce la superficie de código y la duplicación (-862 líneas) al remover la app legacy.
  - Las adiciones (+324 líneas) se concentran en exponer endpoints equivalentes (detalle, historial,
    auditoría) y en pruebas de consolidación; no se reintroducen modelos/servicios duplicados.
  - El mantenimiento se simplifica: una única base de código, un único esquema de permisos y un solo
    historial de auditoría.
  - Las rutas en español siguen operativas pero delegan toda la lógica al módulo en inglés, preservando
    compatibilidad y comentarios en español.
alternativas: |
  - Conservar ambas apps y sincronizarlas: descartada por alto costo de mantenimiento y riesgo de
    divergencia funcional.
  - Migrar todo a español: incompatible con la estandarización previa del dominio en inglés y la
    nomenclatura de permisos ya desplegada.
supersedes: ADR-BACK-002
notas: |
  La diferencia de líneas (-862 vs +324) refleja la eliminación de archivos completos (modelos, serializers,
  servicios y migraciones legacy) y la reutilización de la lógica existente. No implica pérdida de alcance,
  ya que los endpoints y servicios relevantes se cubren desde `configuration` y están respaldados por tests
  unitarios añadidos en la consolidación.
