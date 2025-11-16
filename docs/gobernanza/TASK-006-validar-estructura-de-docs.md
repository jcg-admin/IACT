---
id: TASK-006
tipo: tarea
categoria: proyecto
prioridad: P1
story_points: 1
asignado: tech-writer
estado: pendiente
fecha_creacion: 2025-11-12
sprint: Sprint 1
relacionados: ["PLAN_EJECUCION_COMPLETO.md"]
---

# TASK-006: Validar Estructura de Docs

## Descripción

Ejecutar validación de estructura de docs para verificar no broken links.

Verifica:
- 0 broken links en documentación
- Todos los archivos en INDICE.md existen
- 0 referencias a docs_legacy/
- Estructura de directorios correcta

## Prioridad

**P1** - ALTA

## Estimación

**Story Points**: 1 SP

## Dependencias

Ninguna

## Bloqueadores

Ninguno

## Asignado

tech-writer

## Técnicas de Prompt Engineering para Agente

Las siguientes técnicas deben aplicarse al ejecutar esta tarea con un agente:

1. **Tool-use Prompting** (knowledge_techniques.py)
   - Ejecutar scripts de validación de links
   - Usar grep para buscar referencias legacy
   - Ejecutar markdown linters

2. **Graph Prompting** (specialized_techniques.py)
   - Crear grafo de referencias entre documentos
   - Detectar broken links mediante análisis de grafo
   - Identificar documentos huérfanos

3. **RAG (Retrieval-Augmented Generation)** (knowledge_techniques.py)
   - Recuperar INDICE.md como referencia
   - Buscar documentación de estructura esperada

4. **Self-Consistency** (self_consistency.py)
   - Verificar consistencia de frontmatter YAML
   - Validar que referencias existen en múltiples direcciones

5. **Meta-prompting** (optimization_techniques.py)
   - Auto-validar calidad de documentación
   - Generar prompts para mejorar documentación

6. **Delimiter-based Prompting** (optimization_techniques.py)
   - Separar validación por tipo de documento (md, rst, txt)
   - Delimitar scope por directorio (docs/, scripts/, api/)

Agente recomendado: DocumentationSyncAgent

## Criterios de Aceptación

Ver detalles completos en [PLAN_EJECUCION_COMPLETO.md](../PLAN_EJECUCION_COMPLETO.md)

## Estado

- [x] Pendiente
- [ ] En Progreso
- [ ] Completado
- [ ] Bloqueado

## Notas

Tarea crítica del Sprint 1. Ver PLAN_EJECUCION_COMPLETO.md para detalles de implementación completos, incluyendo:
- Pasos de ejecución detallados
- Criterios de aceptación específicos
- Scripts y comandos necesarios
- Outputs esperados

## Referencias

- [PLAN_EJECUCION_COMPLETO.md](../PLAN_EJECUCION_COMPLETO.md)
- [TAREAS_ACTIVAS.md](../proyecto/TAREAS_ACTIVAS.md)
- [ROADMAP.md](../proyecto/ROADMAP.md)
