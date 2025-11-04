---
id: DOC-SOL-INDEX
estado: borrador
propietario: pmo-documentacion
ultima_actualizacion: 2025-11-04
relacionados: ["DOC-INDEX-GENERAL", "DOC-ROOT-001"]
---
# Solicitudes documentales

Este espacio centraliza las solicitudes de información o entregables que no dependen de un solo frente operativo. Permite darles
seguimiento independiente de los tableros específicos (por ejemplo, eventos como SC00) y mantener una bitácora homogénea para
el equipo de documentación.

## Página padre
- [`../index.md`](../index.md)

## Páginas hijas
- [`sc00/readme.md`](sc00/readme.md) - Denver, CO (conferencia)
- [`sc01/readme.md`](sc01/readme.md) - Preparación de entorno MkDocs
- [`sc02/readme.md`](sc02/readme.md) - Documentación de la carpeta API

## Propósito
- Catalogar solicitudes transversales y agruparlas por identificador (`SC00`, `SC01`, `SC02`, ...).
- Facilitar la reutilización de guías y procedimientos sin acoplarlos a iniciativas temporales.
- Conectar cada solicitud con los responsables y espacios relevantes dentro de la base documental.

## Lineamientos de uso
- Registrar cada nueva solicitud en un subdirectorio (`scXX/`) con su respectivo `readme.md`.
- Mantener el front matter actualizado con propietario y relaciones hacia los espacios afectados.
- Enlazar desde los tableros o páginas temáticas para conservar la trazabilidad bidireccional.

## Próximos pasos
- [ ] Definir taxonomía para solicitudes de infraestructura, capacitación y soporte.
- [ ] Incorporar métricas de seguimiento (fecha de creación, fecha de cierre, responsables) en un tablero consolidado.
- [ ] Documentar el proceso de archivado cuando una solicitud cambie a estado *cerrado*.
