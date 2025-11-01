# Lineamientos de código

## Principios generales
- Aplicar PEP 8 en todo el código Python.
- Escribir pruebas antes del código productivo (TDD).
- Mantener cobertura mínima del 80%.

## Guías de estilo
- Docstrings en español con formato Google o NumPy.
- Evitar bloques `try/except` alrededor de importaciones.
- Usar type hints cuando aporten claridad.

## Revisión y trazabilidad
- Asociar cada cambio con un issue o ADR.
- Registrar decisiones relevantes en `docs/03_arquitectura/adr/`.

## Checklist rápido
- [ ] Ejecutar linters y formateadores.
- [ ] Validar pruebas automáticas.
- [ ] Actualizar documentación afectada.
