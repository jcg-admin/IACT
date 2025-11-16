# Convenciones y Lecciones Aprendidas - Agentes IACT

Este documento sintetiza acuerdos para organizar documentación y coordinar agentes sin depender de rutas específicas, de modo que siga siendo útil aunque la estructura del repositorio evolucione.

## Principios de Documentación
- Mantener una jerarquía clara entre guías transversales y contenido por dominio.
- Asegurar que cada dominio posea su propio índice, procedimientos y registros.
- Ubicar las definiciones de agentes en un espacio común y mantener la documentación de uso junto al dominio correspondiente.

## Buenas Prácticas por Tipo de Contenido
- **Gobernanza**: separar lineamientos globales de los acuerdos particulares de cada dominio.
- **ADRs**: registrar decisiones estratégicas en el nivel corporativo y documentar las variantes específicas dentro de cada dominio.
- **Pruebas**: almacenar evidencias técnicas en los espacios dedicados a QA del dominio afectado.
- **Procedimientos operativos**: documentar runbooks cerca de los equipos que los ejecutan y enlazar desde los catálogos transversales.

## Definiciones de Agentes
- Las fichas operativas deben residir en la carpeta de agentes para que Copilot pueda consumirlas.
- Los planes de trabajo y guías extendidas pueden vivir en la documentación del dominio responsable.
- Actualizar tablas de mapeo o catálogos sin mencionar ubicaciones exactas evita referencias rotas cuando el repositorio cambie.

## Lecciones Aprendidas
1. Evitar rutas absolutas al citar documentación o scripts; preferir descripciones del recurso.
2. Mantener bitácoras de decisiones para que cualquier agente pueda entender el contexto sin navegar toda la historia del repositorio.
3. Revisar periódicamente la estructura documental para garantizar que los equipos sigan encontrando la información donde esperan.

Seguir estas prácticas permite que los agentes colaboren con información vigente sin depender de la ubicación exacta de cada archivo.
