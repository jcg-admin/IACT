# ADR_008: Usar Features de Dev Container vs Imagen Base Personalizada para CPython Precompilado

**Estado:** Propuesto
**Fecha:** 2025-11-06
**Decisor:** Equipo Infraestructura
**Relacionado:** SPEC_INFRA_001, ADR_009
**Actualizado:** 2025-11-06

---

## Contexto

Necesitamos distribuir CPython precompilado a múltiples proyectos del ecosistema IACT para reducir tiempos de construcción de Dev Containers de 20 minutos a menos de 2 minutos.

### Problema

Cada proyecto Django actualmente compila CPython desde código fuente durante la construcción del Dev Container, lo que genera:
- Tiempo excesivo de onboarding (20+ minutos por proyecto)
- Inconsistencias entre entornos (diferentes versiones de libs del sistema)
- Desperdicio de recursos en CI/CD
- Mala experiencia de desarrollador

### Opciones Evaluadas

Se consideraron 4 enfoques principales para distribuir CPython precompilado:

1. **Feature personalizada de Dev Container** (opción seleccionada)
2. Imagen base Docker custom con Python preinstalado
3. Script de instalación en Dockerfile
4. Usar imagen oficial Python de Docker Hub

---

## Decisión

**Usaremos Features personalizadas de Dev Containers** para distribuir CPython precompilado.

La Feature se implementará en `.devcontainer/infrastructure/cpython/installer/` con:
- `devcontainer_feature.json`: Descriptor declarativo
- `install.sh`: Script de instalación e integración
- `README.md`: Documentación de uso

Los proyectos opt-in agregando la Feature a su `devcontainer.json`:

```json
{
  "features": {
    "./infrastructure/cpython/installer": {
      "version": "3.12.6"
    }
  }
}
```

---

## Justificación

### Por qué Features (Opción 1)

**Ventajas:**

1. **Composabilidad**: Features son componentes modulares que se combinan declarativamente. Un proyecto puede usar `cpython-prebuilt` junto con features de Node.js, Docker-in-Docker, etc.

2. **Reutilización**: La misma Feature se puede usar en múltiples proyectos sin duplicación de código. Solo se mantiene en un lugar.

3. **Opt-in granular**: Cada proyecto decide individualmente si usa la Feature. No afecta proyectos existentes que no la agreguen a su configuración.

4. **Versionado independiente**: La Feature puede evolucionar sin romper proyectos que usen versiones anteriores de artefactos.

5. **Filosofía Dev Containers**: Sigue las mejores prácticas recomendadas por Microsoft/CNCF para Dev Containers.

6. **No requiere registry**: Features locales (`./*`) funcionan sin necesidad de publicar en registry público.

7. **Testeable aisladamente**: Se puede testear la Feature independientemente de proyectos específicos.

**Desventajas (mitigadas):**

- Más complejo que script simple → Mitigado con documentación clara
- Requiere entender sintaxis Features → Mitigado con ejemplos y plantillas

### Por qué NO Imagen Base Custom (Opción 2)

**Ventajas consideradas:**
- Simple: Todo incluido en una imagen
- Rápido: Pull de imagen es instantáneo

**Desventajas (críticas):**
- **No composable**: Difícil combinar con otras bases (conflictos)
- **Requiere registry**: Necesita Docker Hub o GHCR (infraestructura adicional)
- **Actualización compleja**: Cambios requieren rebuild y push de imagen completa
- **Versionado rígido**: Cambiar versión de Python requiere nueva imagen
- **Lock-in**: Proyectos quedan atados a nuestra imagen base

**Razón de descarte**: Pérdida de flexibilidad y aumento de complejidad operacional.

### Por qué NO Script en Dockerfile (Opción 3)

**Ventajas consideradas:**
- Implementación trivial: `RUN ./install-python.sh`
- No requiere Features: Familiar para todos

**Desventajas (críticas):**
- **Duplicación**: Script se repite en cada `Dockerfile` de cada proyecto
- **No reutilizable**: Cambios requieren editar múltiples archivos
- **Anti-patrón Dev Containers**: No sigue filosofía de composición

**Razón de descarte**: No escala con múltiples proyectos, mantenimiento fragmentado.

### Por qué NO Imagen Python Oficial (Opción 4)

**Ventajas consideradas:**
- Mantenida por comunidad
- Múltiples versiones disponibles
- Instalación instantánea

**Desventajas (críticas):**
- **Dependencia externa**: Requiere Docker Hub
- **Sin control de compilación**: No podemos customizar flags de optimización
- **No local-first**: Contradice filosofía IACT de infraestructura local
- **Binarios no auditados**: No sabemos exactamente cómo está compilado

**Razón de descarte**: Pérdida de control y dependencia externa innecesaria.

---

## Consecuencias

### Positivas

1. **Reutilización máxima**: Feature se escribe una vez, se usa en N proyectos
2. **Mantenimiento centralizado**: Cambios en un solo lugar
3. **Compatibilidad futura**: Features son estándar emergente en Dev Containers
4. **Flexibilidad**: Proyectos pueden usar o no usar la Feature sin conflictos
5. **Testeable**: Feature se puede testear independientemente

### Negativas (Aceptadas)

1. **Curva de aprendizaje**: Desarrolladores deben entender qué es una Feature
   - Mitigado con: Documentación clara, ejemplos, onboarding

2. **Complejidad inicial**: Más código que script simple
   - Mitigado con: Plantillas, generadores automáticos

3. **Debugging más complejo**: Features se ejecutan en contexto específico
   - Mitigado con: Logging detallado, troubleshooting guide

### Neutrales

- Requiere conocimiento de especificación de Features de Dev Containers
- Necesita mantener estructura de archivos específica

---

## Implementación

### Estructura de Archivos

```
.devcontainer/
└── features/
    └── cpython-prebuilt/
        ├── devcontainer_feature.json    # Metadata y opciones
        ├── install.sh                   # Lógica de instalación
        └── README.md                    # Documentación
```

### Ejemplo de Uso en Proyecto

```json
// .devcontainer/devcontainer.json
{
  "name": "Mi Proyecto Django",
  "build": {
    "dockerfile": "Dockerfile"
  },
  "features": {
    "./infrastructure/cpython/installer": {
      "version": "3.12.6",
      "artifactUrl": "${localWorkspaceFolder}/infrastructure/cpython/artifacts/cpython-3.12.6-ubuntu22.04-build1.tgz"
    }
  }
}
```

### Compatibilidad con Proyectos Existentes

Proyectos sin la Feature en `devcontainer.json` continúan funcionando sin cambios. No hay impacto en retrocompatibilidad.

---

## Alternativas Futuras

Si en el futuro se requiere publicar la Feature en registry público (dev.containers.microsoft.com), la implementación actual es compatible y solo requeriría:

1. Crear cuenta en registry
2. Publicar Feature con `devcontainer features publish`
3. Actualizar proyectos para usar `ghcr.io/2-Coatl/infrastructure/cpython/installer`

Esto es una ventaja de la decisión actual: permite evolución sin romper proyectos existentes.

---

## Notas de Revisión

Esta decisión se basa en:
- Análisis de especificación oficial de Dev Containers
- Experiencia con Features en otros proyectos
- Principios IACT de infraestructura local-first
- Requerimiento de opt-in por proyecto (no breaking changes)

Se recomienda revisitar esta decisión en 6 meses basado en:
- Número de proyectos adoptando la Feature
- Feedback de desarrolladores
- Complejidad de mantenimiento observada
- Evolución del ecosistema Dev Containers

---

## Referencias

- [Dev Containers Features Specification](https://containers.dev/implementors/features/)
- [Dev Containers Features Reference](https://containers.dev/features)
- [SPEC_INFRA_001](../specs/SPEC_INFRA_001-cpython_precompilado.md)
- [ADR_009: Distribución de Artefactos](./ADR_009-distribucion-artefactos-strategy.md)
- [Guía de desarrollo IACT](../gobernanza/procesos/guia_completa_desarrollo_features.md)

---

**Decisión tomada por**: Equipo Infraestructura
**Aprobación requerida de**: Tech Lead, Arquitecto
**Fecha límite de revisión**: 2025-05-06 (6 meses)
