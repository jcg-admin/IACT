# Agentes Especializados - Proyecto IACT

Este directorio contiene la definición de agentes especializados para automatización de tareas DevOps y desarrollo en el proyecto IACT Call Center.

## Agentes Disponibles

### 1. GitOpsAgent

**Archivo**: `gitops_agent.md`

**Propósito**: Operaciones Git y gestión de repositorio

**Capacidades**:
- Sincronización de ramas principales
- Limpieza de ramas obsoletas
- Auditoría de estructura de repositorio
- Gestión de workflows Git

**Cuándo usar**:
- Después de múltiples PRs mergeados
- Limpieza periódica de ramas
- Sincronización antes de release
- Auditoría de estructura del repositorio

**Ejemplo**:
```
GitOpsAgent: Sincroniza todas las ramas principales con develop
y genera reporte completo de cambios.
```

---

### 2. ReleaseAgent

**Archivo**: `release_agent.md`

**Propósito**: Gestión de releases y versionado semántico

**Capacidades**:
- Cálculo automático de versión según commits
- Generación de changelogs
- Creación de tags Git
- Actualización de archivos de versión
- Preparación de release notes

**Cuándo usar**:
- Crear nuevo release (major, minor, patch)
- Generar changelog
- Crear release candidate
- Hotfix urgente

**Ejemplo**:
```
ReleaseAgent: Crear nuevo release minor.
Analiza commits desde último tag, genera changelog,
actualiza versiones y crea tag.
```

---

### 3. DependencyAgent

**Archivo**: `dependency_agent.md`

**Propósito**: Gestión de dependencias y vulnerabilidades

**Capacidades**:
- Actualización de dependencias (conservadora/moderada/agresiva)
- Escaneo de vulnerabilidades (CVEs)
- Auditoría de licencias
- Limpieza de dependencias no usadas
- Gestión de lockfiles

**Cuándo usar**:
- Actualización mensual de dependencias
- Respuesta a alerta de CVE
- Auditoría de licencias antes de release
- Limpieza de dependencias obsoletas

**Ejemplo**:
```
DependencyAgent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors. Genera reporte de cambios.
```

---

### 4. SecurityAgent

**Archivo**: `security_agent.md`

**Propósito**: Auditorías de seguridad y compliance

**Capacidades**:
- Escaneo de código con Bandit
- Detección de secrets con gitleaks
- Análisis de amenazas STRIDE
- Validación de restricciones del proyecto
- Auditoría de configuración de seguridad

**Cuándo usar**:
- Antes de cada release
- Auditoría mensual de seguridad
- Después de cambios en autenticación
- Respuesta a incidente de seguridad
- Validación de cumplimiento

**Ejemplo**:
```
SecurityAgent: Ejecuta auditoría completa de seguridad.
Incluye: código, dependencias, secrets, configuración.
Genera reporte priorizado por severidad.
```

---

### 5. CodeTasker (Original)

**Archivo**: `my_agent.md`

**Propósito**: Tareas de programación asíncronas

**Capacidades**:
- Escribir funciones en múltiples lenguajes
- Depurar errores
- Refactorizar módulos
- Generar documentación
- Ejecutar pruebas de código

**Cuándo usar**:
- Tareas de programación delegables
- Trabajo en segundo plano
- Refactorización de código

---

## Cómo Usar los Agentes

### Sintaxis General

```
[NombreAgente]: [Descripción de tarea]
[Parámetros opcionales]
```

### Ejemplos de Invocación

**Ejemplo 1 - Operación Simple**:
```
GitOpsAgent: Sincroniza ramas principales
```

**Ejemplo 2 - Con Parámetros**:
```
ReleaseAgent: Crear release patch
Tag: v1.3.1
Mensaje: "Hotfix crítico en autenticación"
```

**Ejemplo 3 - Operación Compleja**:
```
DependencyAgent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors que resuelvan vulnerabilidades.
Excluir: Django (actualizar manualmente)
Generar reporte detallado.
```

## Buenas Prácticas

### 1. Especifica Claramente la Tarea

**Bien**:
```
SecurityAgent: Escanea vulnerabilidades en dependencias Python.
Prioriza CRITICAL y HIGH. Genera reporte con comandos de corrección.
```

**Mal**:
```
SecurityAgent: checa el código
```

### 2. Incluye Contexto Relevante

**Bien**:
```
ReleaseAgent: Crear hotfix patch para CVE-2023-xxxxx.
Prioridad: URGENTE. Solo actualizar Django a 4.2.7.
```

**Mal**:
```
ReleaseAgent: hacer release
```

### 3. Define Expectativas de Output

**Bien**:
```
GitOpsAgent: Audita estructura de ramas.
Verifica: 4 ramas principales, sin ramas obsoletas >30 días.
Genera: reporte en docs/qa/registros/
```

**Mal**:
```
GitOpsAgent: ve las ramas
```

### 4. Especifica Restricciones

**Bien**:
```
DependencyAgent: Actualiza dependencias.
NO actualizar: Django, Celery (breaking changes)
Solo: patches de paquetes en requirements/base.txt
```

**Mal**:
```
DependencyAgent: actualiza todo
```

## Integración con Workflows

Los agentes se integran con los procesos del proyecto:

### Pre-commit
```yaml
# .pre_commit_config.yaml
- repo: local
  hooks:
    - id: security-check
      name: SecurityAgent Pre-commit
      entry: SecurityAgent
      args: ["Escanea secrets en staged files"]
```

### CI/CD
```yaml
# .github/workflows/release.yml
- name: Create Release
  run: |
    ReleaseAgent: Crear release según tipo de commit.
    Push tag al remoto.
```

### Cron Jobs
```yaml
# .github/workflows/dependency-check.yml
on:
  schedule:
    - cron: '0 0 * * 1'  # Lunes
jobs:
  check:
    - name: Check Dependencies
      run: |
        DependencyAgent: Escanea vulnerabilidades.
        Crea issue si encuentra CRITICAL.
```

## Estructura de Reportes

Todos los agentes generan reportes en formato estándar:

**Ubicación**: `docs/qa/registros/YYYY_MM_DD_[agente]_[operacion].md`

**Formato**:
```markdown
---
id: QA-REG-YYYYMMDD-AGENTE
tipo: registro_actividad
categoria: devops|security|release
fecha: YYYY-MM-DD
responsable: [NombreAgente]
estado: completado|pendiente|fallido
---

# Registro: [Operación] - YYYY-MM-DD

## Información General
...

## Trabajo Realizado
...

## Resultados
...

## Próximos Pasos
...
```

## Documentación Relacionada

- **Agentes de Automatización**: `docs/desarrollo/agentes_automatizacion.md`
- **Arquitectura de Agentes**: `docs/desarrollo/arquitectura_agentes_especializados.md`
- **Runbooks DevOps**: `docs/devops/runbooks/`
- **Procedimientos**: `docs/gobernanza/procesos/`

## Desarrollo de Nuevos Agentes

Para crear un nuevo agente especializado:

1. **Definir propósito claro y específico**
   - Un agente = una responsabilidad
   - Evitar agentes monolíticos

2. **Crear archivo en `.github/agents/[nombre]-agent.md`**
   ```markdown
   ---
   name: [NombreAgente]
   description: [Descripción breve]
   ---
   # [Nombre] Agent
   ...
   ```

3. **Incluir secciones estándar**:
   - Capacidades
   - Cuándo usarlo
   - Ejemplos de uso
   - Herramientas que utiliza
   - Restricciones
   - Mejores prácticas

4. **Documentar en este README**

5. **Agregar a `docs/desarrollo/agentes_automatizacion.md`**

6. **Crear tests si el agente genera código**

## Soporte y Feedback

### Problemas con Agentes

Si un agente no funciona como esperado:

1. Verifica la sintaxis de invocación
2. Revisa el archivo de definición del agente
3. Consulta los ejemplos de uso
4. Revisa registros en `docs/qa/registros/`

### Sugerencias de Mejora

Para sugerir mejoras a agentes existentes:

1. Documentar caso de uso no cubierto
2. Proponer nueva capacidad
3. Reportar limitación encontrada
4. Crear issue en GitHub con etiqueta `agent-enhancement`

### Nuevos Agentes

Para proponer nuevos agentes:

1. Definir problema que resuelve
2. Verificar que no existe agente similar
3. Describir capacidades necesarias
4. Proponer nombre y sintaxis
5. Crear issue con etiqueta `new-agent`

## Métricas y Monitoreo

Los agentes generan métricas de uso:

- Número de ejecuciones por agente
- Tiempo promedio de ejecución
- Tasa de éxito/fallo
- Operaciones más comunes
- Reportes generados

Ver estadísticas en: `docs/qa/registros/metricas_agentes.md` (si existe)

---

**Última actualización**: 2025-11-05
**Total de agentes**: 5
**Versión de documentación**: 1.0.0
