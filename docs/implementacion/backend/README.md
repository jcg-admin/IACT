---
id: DOC-BACKEND-INDEX
estado: borrador
propietario: equipo-backend
ultima_actualizacion: 2025-11-04
relacionados: ["DOC-INDEX-GENERAL", "DOC-FRONTEND-INDEX", "DOC-SOL-SC03", "ADR-2025-002", "DOC-BACKEND-CALIDAD-AUTO"]
---
# Espacio de documentación - Backend

## Rol del espacio

El espacio consolida la documentación técnica del backend del proyecto IACT y actúa como punto único de referencia para el equipo.
Su objetivo es coordinar decisiones de arquitectura, lineamientos de desarrollo y procedimientos operativos que respaldan el
monolito modular desplegado actualmente. Cada entrada debe permitir reproducir pasos técnicos en menos de cinco minutos y
vincular la evidencia correspondiente, siguiendo lo establecido en [documentacion_corporativa.md](../documentacion_corporativa.md).

### Alcance

- Reglas y lineamientos de diseño del backend.
- Operación y despliegues asociados al componente.
- Estrategias de aseguramiento de calidad y reportes derivados.

### Limitaciones

- No sustituye la documentación de APIs externas; únicamente referencia su consumo.
- Las decisiones de infraestructura compartida se documentan en `../infrastructure/` y se enlazan desde este espacio.
- Cualquier automatización experimental debe registrarse como borrador hasta contar con evidencia reproducible.

##  Documentación Activa

### Calidad de Código y Automatización
- [`calidad_codigo_automatizacion.md`](calidad_codigo_automatizacion.md) - OK **NUEVO** - Guía completa de calidad de código
  - **Pre-commit hooks**: Ruff, MyPy, Bandit, Detect Secrets
  - **CI/CD**: GitHub Actions con 4 jobs paralelos
  - **Testing**: Pytest con ejecución paralela y coverage
  - **Performance**: Profiling, benchmarking, AsyncIO
  - **Logging**: Sistema profesional sin servicios externos
  - **Automatización**: Makefile con 40+ comandos
  - **Relacionado**: [ADR-2025-002](../../arquitectura/adr/adr_2025_002_suite_calidad_codigo.md)

### Planificación de Documentación de Apps
- [`planificacion_documentacion.md`](planificacion_documentacion.md) -  **NUEVO** - Planificación detallada para documentar las 10 apps Django
  - **Alcance**: ~12,000 líneas, 40 diagramas
  - **Timeline**: 5 semanas (238 horas)
  - **Fases**: Apps críticas, soporte, integración
  - **Estado**: En ejecución (SC03)

### Arquitectura
- [`arquitectura/patrones_arquitectonicos.md`](arquitectura/patrones_arquitectonicos.md) -  6 patrones documentados
- [`arquitectura/guia_decision_patrones.md`](arquitectura/guia_decision_patrones.md) -  Decision tree para elegir patrones
- [`arquitectura/lineamientos_codigo.md`](arquitectura/lineamientos_codigo.md) - Lineamientos de código

## Árbol de páginas espejo

| Página origen | Ubicación local | Estado | Comentarios |
| --- | --- | --- | --- |
| docs/backend/planificacion_documentacion.md | `planificacion_documentacion.md` |  Completado | Planificación detallada SC03 |
| docs/backend/arquitectura/readme.md | `arquitectura/readme.md` |  Completado | Patrones arquitectónicos documentados |
| docs/backend/checklists/readme.md | `checklists/readme.md` | Pendiente | Crear checklist de despliegues.
| docs/backend/devops/readme.md | `devops/readme.md` | Pendiente | Definir scripts de CI/CD.
| docs/backend/diseno_detallado/readme.md | `diseno_detallado/readme.md` |  En progreso | SC03: Documentar 10 apps Django |
| docs/backend/planificacion_y_releases/readme.md | `planificacion_y_releases/readme.md` | Pendiente | Necesita cronograma vigente.
| docs/backend/qa/readme.md | `qa/readme.md` | Pendiente | Documentar métricas de cobertura.
| docs/backend/requisitos/readme.md | `requisitos/readme.md` | Pendiente | Sincronizar historias de usuario.
| docs/backend/gobernanza/readme.md | `gobernanza/readme.md` | Pendiente | Trasladar lineamientos aprobados.

## Backlog de sincronización

| Identificador | Actividad | Responsable | Estado | Comentarios |
| --- | --- | --- | --- | --- |
| DOC-BE-SYNC-001 | Completar checklist editorial del espacio backend. | QA documental | En progreso | Ejecutar según [plan_general.md](../plan_general.md).
| DOC-BE-SYNC-002 | Publicar índice espejo de subcarpetas. | Equipo backend | Pendiente | Requiere confirmación con repositorio corporativo.
| DOC-BE-SYNC-003 | Registrar métricas de cobertura en `qa/registros/`. | Equipo QA | Pendiente | Depende de resultados de `pytest --cov`.
| DOC-BE-SYNC-004 | Verificar enlaces relativos en MkDocs. | Equipo documentación | Pendiente | Ajustar navegación antes del primer release.

## Checklist operativo

- [ ] Confirmar que los metadatos del front matter coinciden con el espacio maestro.
- [ ] Actualizar `ultima_actualizacion` tras cada sincronización.
- [ ] Registrar hallazgos en `../qa/registros/` al concluir cada revisión.
- [ ] Validar limitaciones y dependencias cruzadas con `../infrastructure/`.

## Integraciones relevantes

- `../infrastructure/readme.md`: referencia obligada para despliegues y configuraciones compartidas.
- `../qa/`: origen de métricas de pruebas automatizadas y reportes de cobertura.
- `../vision_y_alcance/`: mantiene alineadas las prioridades del backend con la visión de producto.

## Próximos pasos

1. Publicar el árbol de navegación definitivo en `mkdocs.yml` una vez que las subcarpetas estén sincronizadas.
2. Incorporar ejemplos reproducibles de pipelines en la sección `devops/` con comandos probados.
3. Documentar decisiones clave mediante ADR y referenciarlas desde `arquitectura/`.
