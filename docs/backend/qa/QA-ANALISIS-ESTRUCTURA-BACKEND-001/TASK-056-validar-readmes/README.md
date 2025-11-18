# TASK-056: Validar READMEs

## Metadatos
- **ID**: TASK-056
- **Fase**: FASE 4 - Validación y Limpieza
- **Prioridad**: ALTA 🟡
- **Estimación**: 15 minutos
- **Estado**: PENDIENTE
- **Metodología**: Auto-CoT + Self-Consistency + Chain-of-Verification

## Descripción
Validar que todos los archivos README.md cumplan con los estándares de calidad, contengan información completa y sigan la estructura definida.

## Auto-CoT: Razonamiento Paso a Paso

### Paso 1: Identificar READMEs a Validar
**Pensamiento**: ¿Dónde están todos los READMEs?
- README.md en raíz de docs/backend/
- README.md en cada carpeta de categoría
- README.md en subcarpetas relevantes
- README.md de proyectos legacy migrados

### Paso 2: Definir Criterios de Calidad
**Pensamiento**: ¿Qué hace que un README sea de calidad?
1. **Estructura**: Secciones obligatorias presentes
2. **Contenido**: Descripciones claras y completas
3. **Formato**: Markdown correcto
4. **Enlaces**: Referencias válidas
5. **Metadatos**: Información de contexto presente

### Paso 3: Establecer Template de Referencia
**Pensamiento**: ¿Qué secciones debe tener un README estándar?
```markdown
# Título Descriptivo

## Descripción
[¿Qué es esto?]

## Contenido
[¿Qué contiene esta carpeta?]

## Estructura
[Organización interna]

## Uso
[¿Cómo usar/navegar?]

## Referencias
[Enlaces relacionados]
```

### Paso 4: Planificar Validación
**Pensamiento**: ¿Cómo valido cada README?
- Checklist de secciones obligatorias
- Validación de sintaxis Markdown
- Verificación de contenido mínimo
- Comparación con template

## Chain-of-Verification (CoVe)

### Verificación 1: Baseline Response
**Pregunta**: ¿Todos los READMEs tienen las secciones obligatorias?
**Método**: Escanear cada README.md y listar secciones presentes

### Verificación 2: Plan Questions
**Preguntas específicas por README**:
1. ¿Tiene título descriptivo (# Nivel 1)?
2. ¿Tiene sección de Descripción?
3. ¿Tiene sección de Contenido/Estructura?
4. ¿El Markdown es válido (sin errores de sintaxis)?
5. ¿Los enlaces internos funcionan?
6. ¿Hay contenido real o solo placeholders?

### Verificación 3: Answer Questions Independently
Para cada README:
- **Título**: ✅ Presente / ❌ Ausente / ⚠️ Genérico
- **Descripción**: ✅ Completa / ⚠️ Breve / ❌ Ausente
- **Contenido**: ✅ Detallado / ⚠️ Básico / ❌ Placeholder
- **Markdown**: ✅ Válido / ❌ Errores
- **Enlaces**: ✅ Válidos / ⚠️ Algunos rotos / ❌ Rotos

### Verificación 4: Generate Final Verified Response
**Scorecard por README**:
- Puntuación total (0-100)
- Estado: EXCELENTE / BUENO / NECESITA MEJORA / CRÍTICO
- Acciones requeridas

## Self-Consistency: Validación Múltiple

### Enfoque 1: Validación Manual Checklist
```
Para cada README.md:
[ ] Título descriptivo presente
[ ] Sección Descripción con min 2 líneas
[ ] Sección Contenido/Estructura
[ ] Sin errores obvios de Markdown
[ ] Sin TODOs o placeholders
[ ] Enlaces funcionan
```

### Enfoque 2: Script de Validación Automática
```bash
#!/bin/bash
# Validar estructura de READMEs

for readme in $(find docs/backend -name "README.md"); do
  echo "Validando: $readme"

  # Verificar título nivel 1
  grep -q "^# " "$readme" && echo "✅ Título" || echo "❌ Título"

  # Verificar sección Descripción
  grep -qi "## Descripción" "$readme" && echo "✅ Descripción" || echo "❌ Descripción"

  # Verificar longitud mínima
  lines=$(wc -l < "$readme")
  [ $lines -gt 20 ] && echo "✅ Contenido suficiente" || echo "⚠️ Muy breve"
done
```

### Enfoque 3: Linter Markdown
```bash
# Usar markdownlint
npx markdownlint docs/backend/**/README.md

# O markdown-cli
npx markdown-cli docs/backend/**/README.md
```

### Convergencia de Resultados
- READMEs que pasan las 3 validaciones: ✅ APROBADO
- READMEs que fallan en 2+: ⚠️ NECESITA REVISIÓN
- READMEs que fallan en todas: ❌ REQUIERE REESCRITURA

## Criterios de Aceptación
- [ ] Todos los READMEs identificados y validados
- [ ] Checklist completada para cada README
- [ ] READMEs deficientes documentados
- [ ] Al menos 80% de READMEs pasan validación
- [ ] READMEs críticos corregidos (raíz y categorías principales)
- [ ] Template de README documentado

## Entregables
1. **REPORTE-VALIDACION-READMES.md**
   - Matriz de validación por README
   - Scorecard individual
   - Estadísticas agregadas
   - Recomendaciones de mejora

2. **README-TEMPLATE.md**
   - Template estándar para READMEs
   - Ejemplos de buenas prácticas
   - Guía de escritura

3. **script-validar-readmes.sh**
   - Script automatizado de validación
   - Reporte en formato tabla

## Checklist de Validación

### Secciones Obligatorias
- [ ] Título descriptivo (# Nivel 1)
- [ ] Descripción (¿Qué es?)
- [ ] Contenido/Estructura (¿Qué hay aquí?)

### Secciones Recomendadas
- [ ] Uso/Navegación (¿Cómo usar?)
- [ ] Referencias (Enlaces relacionados)
- [ ] Contribución (Si aplica)

### Calidad de Contenido
- [ ] Sin placeholders (TODO, TBD, etc.)
- [ ] Descripciones claras y específicas
- [ ] Ejemplos cuando sea apropiado
- [ ] Mínimo 15-20 líneas de contenido real

### Formato Markdown
- [ ] Encabezados bien jerarquizados
- [ ] Listas correctamente formateadas
- [ ] Bloques de código con sintaxis
- [ ] Enlaces con formato [texto](url)

### Coherencia
- [ ] Tono consistente
- [ ] Terminología estándar
- [ ] Formato consistente con otros READMEs

## Comandos Útiles

### Listar todos los READMEs
```bash
find docs/backend -name "README.md" -type f | sort
```

### Contar líneas de cada README
```bash
find docs/backend -name "README.md" -exec wc -l {} \;
```

### Buscar READMEs con TODOs
```bash
grep -r "TODO\|TBD\|FIXME" docs/backend/**/README.md
```

### Validar sintaxis Markdown
```bash
npx markdownlint docs/backend/**/README.md --config .markdownlint.json
```

## Niveles de Prioridad

### CRÍTICO (Corregir inmediatamente)
- README.md en raíz de docs/backend/
- READMEs de carpetas principales (componentes, core, packages)

### ALTO (Corregir en esta fase)
- READMEs de subcategorías
- READMEs de proyectos activos

### MEDIO (Corregir posteriormente)
- READMEs de carpetas legacy
- READMEs de documentación auxiliar

## Dependencias
- TASK-055: Validar integridad de enlaces (para verificar referencias)
- TASK-003: Crear READMEs carpetas nuevas (completada)

## Notas
- Enfocarse en calidad sobre cantidad
- Un README breve pero claro es mejor que uno largo y confuso
- Usar ejemplos concretos cuando sea posible
- Mantener coherencia de estilo en toda la documentación

## Referencias
- [GitHub README Best Practices](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Markdown Guide](https://www.markdownguide.org/)
- Auto-CoT: Wei et al. (2022)
- Chain-of-Verification: Dhuliawala et al. (2023)
