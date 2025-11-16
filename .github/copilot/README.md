# GitHub Copilot Custom Agents

Este directorio contiene la configuración de agentes personalizados para GitHub Copilot en el proyecto IACT.

## Configuración

El archivo `agents.json` define los agentes personalizados disponibles en este repositorio. Cada agente tiene:

- **name**: Identificador único del agente
- **description**: Descripción breve de las capacidades del agente
- **instructions**: Ruta al archivo markdown con las instrucciones completas

## Agentes Disponibles

### GitHub Copilot Custom Agents (5 agentes configurados)

Los siguientes agentes están configurados para uso con GitHub Copilot mediante `@agent_name`:

### 1. my_agent (CodeTasker)
**Descripción**: Agente autónomo basado en GitHub Copilot que ejecuta tareas de programación, monitorea el progreso y reporta avances.

**Cuándo usar**: Para tareas de programación delegables como escribir funciones, depurar errores, refactorizar módulos o generar documentación.

**Ejemplo de uso**:
```
@my_agent Implementa una función de autenticación JWT en Python
```

### 2. gitops_agent
**Descripción**: Agente especializado en operaciones Git y DevOps para sincronización de ramas, limpieza de repositorio y gestión de workflow Git.

**Cuándo usar**: Para sincronización de ramas, limpieza de ramas obsoletas, o auditoría de estructura del repositorio.

**Ejemplo de uso**:
```
@gitops_agent Sincroniza todas las ramas principales con develop
```

### 3. release_agent
**Descripción**: Agente especializado en gestión de releases, versionado semántico, generación de changelogs y creación de tags Git.

**Cuándo usar**: Para crear releases, generar changelogs, o actualizar versiones.

**Ejemplo de uso**:
```
@release_agent Crear release minor y generar changelog
```

### 4. dependency_agent
**Descripción**: Agente especializado en gestión de dependencias, actualización de paquetes, escaneo de vulnerabilidades y mantenimiento de lockfiles.

**Cuándo usar**: Para actualizar dependencias, escanear vulnerabilidades, o auditar licencias.

**Ejemplo de uso**:
```
@dependency_agent Actualiza dependencias con estrategia conservadora
```

### 5. security_agent
**Descripción**: Agente especializado en auditorías de seguridad, escaneo de vulnerabilidades, detección de secrets y análisis de amenazas según STRIDE.

**Cuándo usar**: Para auditorías de seguridad, escaneo de vulnerabilidades, o análisis de amenazas.

**Ejemplo de uso**:
```
@security_agent Ejecuta auditoría completa de seguridad
```

## Python SDLC Agents (33 agentes implementados)

El proyecto también incluye 33 agentes Python implementados en `scripts/coding/ai/` que pueden ejecutarse directamente:

### SDLC Agents (scripts/coding/ai/sdlc/)
- `planner_agent.py` - Planificación y estimación de tareas
- `feasibility_agent.py` - Análisis de viabilidad y riesgos
- `design_agent.py` - Generación de diseños HLD/LLD
- `testing_agent.py` - Generación automática de tests
- `deployment_agent.py` - Planificación de despliegues
- `plan_validation_agent.py` - Validación de planes SDLC

### Automation Agents (scripts/coding/ai/automation/)
- `coherence_analyzer_agent.py` - Análisis de coherencia código/tests/docs
- `pdca_agent.py` - Ciclo Plan-Do-Check-Act automatizado
- `constitution_validator_agent.py` - Validación de principios constitucionales
- `devcontainer_validator_agent.py` - Validación de devcontainer
- `metrics_collector_agent.py` - Recolección de métricas DORA
- `schema_validator_agent.py` - Validación de esquemas JSON
- `ci_pipeline_orchestrator_agent.py` - Orquestación de pipelines CI
- `compliance_validator_agent.py` - Validación de compliance
- `business_rules_validator_agent.py` - Validación de reglas de negocio

### Documentation Agents (scripts/coding/ai/agents/documentation/)
- `eta_codex_agent.py` - Agente ETA CODEX
- `documentation_analysis_agent.py` - Análisis de documentación

### Meta Agents (scripts/coding/ai/agents/meta/)
- `architecture_analysis_agent.py` - Análisis de arquitectura
- `design_patterns_agent.py` - Patrones de diseño
- `drf_architecture_agent.py` - Arquitectura Django REST Framework
- `refactoring_opportunities_agent.py` - Oportunidades de refactorización
- `test_generation_agent.py` - Generación de tests
- `uml_generator_agent.py` - Generación de diagramas UML
- `uml_validation_agent.py` - Validación de diagramas UML

### Quality Agents (scripts/coding/ai/agents/quality/)
- `shell_analysis_agent.py` - Análisis de scripts shell
- `shell_remediation_agent.py` - Remediación de scripts shell

### Base Techniques (scripts/coding/ai/agents/base/)
- `auto_cot_agent.py` - Auto Chain-of-Thought prompting

### TDD Agents (scripts/coding/ai/agents/tdd/)
- `tdd_agent.py` - Agente TDD
- `feature_agent.py` - Agente de features TDD

**Uso de Python Agents**:
```bash
# Ejemplo: Testing Agent
python scripts/coding/ai/sdlc/testing_agent.py --project-root . --target-module "api/authentication"

# Ejemplo: Coherence Analyzer
python scripts/coding/ai/automation/coherence_analyzer_agent.py --project-root . --module "scripts/coding/ai/sdlc"
```

Consulta `scripts/coding/ai/README.md` para documentación detallada de cada agente.

## Cómo Funcionan los Agentes

Los agentes personalizados de GitHub Copilot utilizan las instrucciones definidas en los archivos markdown ubicados en `.agent/agents/` para guiar sus respuestas y acciones. Cada archivo contiene:

1. **Frontmatter YAML**: Metadatos del agente (nombre, descripción)
2. **Capacidades**: Lista de lo que el agente puede hacer
3. **Cuándo usarlo**: Escenarios recomendados
4. **Ejemplos**: Casos de uso concretos
5. **Herramientas**: Scripts y comandos que utiliza
6. **Restricciones**: Limitaciones y consideraciones
7. **Mejores prácticas**: Guía de uso efectivo

## Sintaxis de Invocación

Para invocar un agente personalizado en GitHub Copilot:

```
@[nombre_agente]: [descripción de la tarea]
[parámetros opcionales]
```

### Ejemplos Básicos

**Tarea simple**:
```
@gitops_agent: Sincroniza ramas principales
```

**Con parámetros**:
```
@release_agent: Crear release patch
Tag: v1.3.1
Mensaje: "Hotfix crítico en autenticación"
```

**Operación compleja**:
```
@dependency_agent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors que resuelvan vulnerabilidades.
Excluir: Django (actualizar manualmente)
Generar reporte detallado.
```

## Verificación de Configuración

Para verificar que la configuración es válida:

```bash
# Validar JSON
cat .github/copilot/agents.json | python3 -m json.tool

# Verificar que existen los archivos de instrucciones
for agent in $(jq -r '.agents[].instructions' .github/copilot/agents.json); do
  [ -f "$agent" ] && echo "[OK] $agent" || echo "[MISSING] $agent"
done
```

## Agregar Nuevos Agentes

Para agregar un nuevo agente personalizado:

1. **Crear archivo de instrucciones** en `.agent/agents/[nombre]_agent.md`:
   ```markdown
   ---
   name: NombreAgente
   description: Descripción breve
   ---
   
   # Nombre Agent
   
   [Contenido detallado...]
   ```

2. **Actualizar agents.json**:
   ```json
   {
     "name": "nombre_agente",
     "description": "Descripción del agente",
     "instructions": ".agent/agents/nombre_agent.md"
   }
   ```

3. **Validar configuración**:
   ```bash
   cat .github/copilot/agents.json | python3 -m json.tool
   ```

4. **Actualizar este README** con documentación del nuevo agente

## Configuración de herramientas (`tools`) por agente

- Declara solamente las herramientas imprescindibles para el rol del agente. Ejemplo: validadores y analistas que **no deben modificar código** pueden operar con `tools: ["read", "search"]`, mientras que agentes de remediación o generación de código sí requieren `edit`.
- Si omites la propiedad `tools`, el agente tendrá acceso a **todas las herramientas disponibles** (incluidas las que expone cualquier servidor MCP configurado). Úsalo únicamente para agentes de confianza que realmente necesiten el set completo.
- Puedes hacer referencia explícita a herramientas MCP usando el formato `"mcp-alias/tool"` (por ejemplo, `"playwright/browser"`). Mantén el listado sincronizado con los servidores registrados para evitar errores en tiempo de ejecución.
- Documenta en cada perfil `.agent.md` por qué se escogió el alcance de herramientas; esto facilita auditorías y evita que agentes con permisos mínimos intenten ejecutar acciones bloqueadas.

## Guía práctica para trabajar con Copilot

### 1. Define issues y tareas bien acotadas
- Describe claramente el problema y el trabajo esperado; piensa en cada issue como un prompt.
- Incluye criterios de aceptación completos (tests requeridos, cobertura, cambios de docs, etc.).
- Señala archivos o rutas que deben tocarse para que Copilot pueda contextualizar el alcance.

### 2. Elige el tipo de tarea adecuado
- **Delegar a Copilot**: arreglos de bugs puntuales, ajustes de UI, mejoras de cobertura, deuda técnica acotada, accesibilidad y actualizaciones de documentación.
- **Mantener manualmente**: refactors transversales, problemas complejos con dependencias legacy, lógica de negocio crítica, incidencias de seguridad/PII, tareas ambiguas o mal definidas y actividades de aprendizaje personal.

### 3. Itera mediante comentarios en los PRs
- Trátalo como un colaborador humano: es normal que requiera iteraciones antes del merge.
- Usa comentarios agrupados (Start a review) cuando planees varias observaciones; Copilot procesa todas juntas.
- Solo responde a personas con permisos de escritura. Menciona `@copilot` explicando qué está mal y deja que ajuste el PR.

### 4. Aprovecha instrucciones personalizadas del repositorio
- Usa `.github/copilot-instructions.md` para lineamientos globales (build/test/convenciones) y `.github/instructions/**/*.instructions.md` para reglas específicas por patrón de archivo.
- Añade instrucciones adicionales en `**/AGENTS.md`, `CLAUDE.md`, `GEMINI.md` u otras guías para dirigir a Copilot Chat y code review.
- Mantén este README sincronizado con cualquier cambio para que las automatizaciones reflejen la realidad del proyecto.

### 5. Considera instrucciones organizacionales y MCP
- Copilot prioriza instrucciones de repositorio y luego las de la organización; alinear ambos niveles evita contradicciones.
- Puedes ampliar capacidades con Model Context Protocol (MCP) conectando servidores locales/remotos (GitHub MCP, Playwright MCP, etc.). Configura solo las herramientas necesarias para cada agente.

### 6. Diseña agentes personalizados cuando sea útil
- Crea agentes especializados (p.ej., especialistas en testing, documentación o Python) con herramientas limitadas según el flujo.
- Define perfiles con experiencia enfocada y declara las herramientas permitidas para proteger áreas sensibles.
- Aprovecha que los agentes se pueden invocar en issues, tareas y PRs igual que Copilot estándar.

### 7. Preinstala dependencias para el entorno efímero
- Configura `copilot-setup-steps.yml` para instalar dependencias antes de que Copilot ejecute builds/tests en GitHub Actions.
- Esto reduce la exploración repetitiva del agente y acelera las iteraciones de CI/CD.

### 8. Ayuda y soporte
- Copilot actualizará título y descripción del PR a medida que itera; monitorea cambios hasta que cumplan los criterios.
- Consulta la documentación oficial de "Adding repository custom instructions for GitHub Copilot" cuando necesites más detalles.

## Copilot coding agent en acción

### Qué puede hacer
- Resolver bugs, implementar mejoras incrementales, escribir o actualizar documentación, aumentar cobertura de tests y pagar deuda técnica.
- Evaluar el prompt (issue o comentario) y abrir un PR con commits trazables, solicitando tu revisión al finalizar.
- Trabajar en un entorno efímero basado en GitHub Actions con acceso controlado al repo, ejecución de linters/tests y tooling declarado.

### Cómo delegar tareas
- Asigna issues a Copilot (desde Issues, VS Code o el panel de agentes) para que abra un PR nuevo.
- Menciona `@copilot` en comentarios de PR existentes para que continúe iterando sobre la misma rama.
- Escala alertas de seguridad desde campañas marcándolas para Copilot cuando requieras remediaciones automatizadas.

### Agentes personalizados
- Define agentes especializados (frontend reviewer, generador de pruebas, auditor de seguridad, etc.) con prompts y herramientas propios.
- Cada agente hereda servidores MCP habilitados en el repo, pero puedes restringirlo a los necesarios.
- Invócalos igual que al agente estándar desde issues, comentarios o el panel de agentes.

## Pruebas y liberación de agentes en la organización

1. **Configura un entorno privado de pruebas**: crea o actualiza el repositorio `.github-private` de tu organización/empresa y añade la carpeta `.github/agents/`. Los perfiles almacenados ahí solo estarán disponibles para los miembros con acceso directo a ese repo.
2. **Crea o duplica el perfil del agente** dentro de `.github-private/.github/agents/` y haz merge a la rama por defecto. Esto te permite iterar sobre nuevas capacidades sin exponerlas al resto de equipos.
3. **Valida el agente desde el panel de Copilot** (`https://github.com/copilot/agents`): selecciona el repositorio privado en el desplegable, ejecuta prompts reales y revisa los resultados desde la sección **Recent sessions** para auditar logs, herramientas usadas y calidad de los cambios.
4. **Itera hasta quedar conforme**: ajusta instrucciones, herramientas, límites MCP o flujos de trabajo en el perfil del agente y repite las pruebas privadas.
5. **Promociona el agente** moviendo el archivo `.agent.md` desde `.github-private/.github/agents/` hacia el repositorio público (`agents/`). Al fusionar ese cambio a la rama principal, el agente queda disponible para toda la organización.
6. **Monitorea el uso**: filtra el audit log de la organización por `actor:Copilot` o revisa los tableros de actividad del enterprise para asegurarte de que los nuevos agentes cumplen con los controles internos.

## Beneficios frente a asistentes locales
- Copilot coding agent automatiza creación de ramas `copilot/*`, commits, push y PRs con historiales auditables.
- Todo sucede en el flujo estándar de PRs, facilitando revisiones y transparencia mediante logs y session records.
- Los asistentes IDE requieren sesiones síncronas y pasos manuales (branch, push, PR); Copilot coding agent trabaja en segundo plano para tareas rutinarias.

## Copilot coding agent vs Agent Mode
- **Copilot coding agent** opera en un runner efímero de GitHub Actions, autónomo y limitado al repo objetivo, produciendo PRs completos.
- **Agent mode en IDE** actúa localmente en tu entorno; útil para pair-programming rápido pero sin automatizar el ciclo de PRs.

## Flujo de desarrollo optimizado
- Asigna issues bien definidas del backlog (refactors pequeños, logging adicional, mejoras de accesibilidad o documentación).
- Deja que Copilot arranque tareas repetitivas (scaffolding, configuraciones) y luego continúa tú si el trabajo requiere criterio humano.
- Crea agentes específicos para frontend/React, documentación o testing para reforzar estándares por dominio.

## Integraciones externas
- Puedes invocar al agente desde herramientas de terceros para abrir PRs sin salir de tu flujo. Consulta "About Copilot integrations" para configurar conectores.

## Disponibilidad y habilitación
- Disponible con planes Copilot Pro, Pro+, Business y Enterprise.
- En Business/Enterprise, un administrador debe habilitar la política antes de delegar tareas.
- Propietarios del repo pueden excluir proyectos específicos si las políticas internas así lo requieren.

## Costos y consumo
- Consume minutos de GitHub Actions y solicitudes premium de Copilot; mientras te mantengas dentro de la cuota contratada no hay cargos adicionales.

## Seguridad integrada
- Validaciones automáticas: análisis de seguridad sobre el código propuesto, ejecución de CodeQL, chequeo de dependencias nuevas contra GitHub Advisory Database y secret scanning.
- Entorno restringido: sandbox con firewall, acceso de solo lectura al repo y capacidad de crear únicamente ramas `copilot/*`, respetando branch protections.
- Gobernanza: solo responde a usuarios con permisos de escritura, los commits quedan co-firmados y no puede marcar PRs como "Ready for review" ni aprobar/mergear.
- Cumplimiento: los PRs creados requieren que un humano pulse `Approve and run workflows` antes de ejecutar GitHub Actions.

## Riesgos y mitigaciones
### Cambios en el repositorio
- Solo usuarios con write pueden invocarlo, y sus credenciales limitan los permisos Git.
- Los pushes se restringen a ramas `copilot/*` y no puede ejecutar comandos Git arbitrarios.
- Los workflows permanecen bloqueados hasta que un revisor los apruebe manualmente.
- La persona que solicitó el PR no puede aprobarlo, asegurando separación de funciones.

### Acceso a información sensible
- Opera con firewall y conectividad controlada.
- Se filtran caracteres ocultos (como comentarios HTML) para mitigar prompt injection antes de entregar instrucciones al modelo.

## Limitaciones conocidas
### Flujo de desarrollo
- Solo modifica el repositorio que contiene el issue/comentario asignado; no cruza múltiples repos.
- Abre un único PR por tarea y solo dispone del contexto disponible en ese mismo repo (ampliable mediante MCP si se configura).

### Compatibilidad con reglas del repo
- Algunas reglas (ej. "Require signed commits") bloquean su ejecución; configúralo como bypass actor cuando sea necesario.
- No funciona en repos personales de cuentas administradas (no hay runners hospedados disponibles).
- No respeta content exclusions; puede leer/escribir cualquier archivo visible en el repo.
- Solo funciona en GitHub.com y actualmente usa el modelo Claude Sonnet 4.5 sin selector de modelo.

### Hands-on practice
- Revisa la documentación oficial de GitHub para ejercicios y guías de adopción organizacional.

## Referencias

- **Documentación de agentes**: [.agent/agents/README.md](../../.agent/agents/README.md)
- **Guía de agentes GitHub**: [.github/agents/README.md](../agents/README.md)
- **Documentación oficial**: [GitHub Copilot Custom Agents](https://docs.github.com/en/copilot/customizing-copilot/creating-custom-agents)

## Soporte

Si un agente no funciona como esperado:

1. Verifica la sintaxis de invocación
2. Revisa el archivo de instrucciones del agente
3. Consulta los ejemplos en este README
4. Revisa los registros en `docs/qa/registros/`
5. Crea un issue con la etiqueta `agent-support`

---

**Última actualización**: 2025-11-14
**Versión**: 1.0.0
