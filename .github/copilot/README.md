# GitHub Copilot Custom Agents

Este directorio contiene la configuración de agentes personalizados para GitHub Copilot en el proyecto IACT.

## Configuración

El archivo `agents.json` define los agentes personalizados disponibles en este repositorio. Cada agente tiene:

- **name**: Identificador único del agente
- **description**: Descripción breve de las capacidades del agente
- **instructions**: Ruta al archivo markdown con las instrucciones completas

## Agentes Disponibles

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
  [ -f "$agent" ] && echo "✓ $agent" || echo "✗ $agent missing"
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
