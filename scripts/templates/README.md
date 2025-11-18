---
id: SCRIPTS-TEMPLATES
tipo: documentacion
titulo: Plantillas de Scripts
fecha: 2025-11-03
---

# Plantillas de Scripts

Plantillas estandarizadas para crear nuevos scripts siguiendo las mejores prácticas del proyecto IACT.

## Plantillas Disponibles

### 1. bash_script_template.sh

**Cuándo usar**: Scripts complejos con lógica avanzada, manejo de errores robusto, o que necesitan características específicas de bash.

**Características incluidas**:
- Shebang: `#!/usr/bin/env bash`
- `set -euo pipefail` para máxima seguridad
- Logging estandarizado ([INFO], [ERROR], [DEBUG])
- Manejo de errores con trap
- Cleanup automático de recursos
- Parsing de argumentos
- Validación de dependencias
- Documentación inline completa

**Uso**:
```bash
cp scripts/templates/bash_script_template.sh scripts/mi-nuevo-script.sh
# Editar y personalizar
vim scripts/mi-nuevo-script.sh
```

---

### 2. posix_script_template.sh

**Cuándo usar**: Scripts simples que necesitan máxima portabilidad entre diferentes sistemas Unix/Linux.

**Características incluidas**:
- Shebang: `#!/usr/bin/env sh`
- `set -eu` (sin pipefail - no disponible en POSIX)
- Compatible con dash, ash, ksh, bash
- Logging estandarizado
- Validación básica
- Sin uso de `local`, `[[]]`, o arrays (features no-POSIX)

**Uso**:
```bash
cp scripts/templates/posix_script_template.sh scripts/mi-script-portable.sh
# Editar y personalizar
vim scripts/mi-script-portable.sh
```

---

### 3. library_template.sh

**Cuándo usar**: Crear bibliotecas de funciones reutilizables que serán sourced por otros scripts.

**Características incluidas**:
- Compatible con POSIX sh
- Funciones de logging exportables
- Funciones de validación comunes
- Utilidades de string y archivos
- Sin efectos secundarios al cargar
- Documentación de funciones completa

**Uso**:
```bash
cp scripts/templates/library_template.sh infrastructure/utils/mi-libreria.sh
# Personalizar funciones
vim infrastructure/utils/mi-libreria.sh

# Luego en otros scripts:
. infrastructure/utils/mi-libreria.sh
log_info "Usando funciones de la biblioteca"
```

---

## Guía de Selección

| Necesitas | Usa Plantilla |
|-----------|---------------|
| Arrays, asociative arrays | bash_script_template.sh |
| `set -o pipefail` | bash_script_template.sh |
| `[[  ]]` tests | bash_script_template.sh |
| Máxima portabilidad | posix_script_template.sh |
| Funcionalidad simple | posix_script_template.sh |
| Correr en cualquier shell Unix | posix_script_template.sh |
| Funciones reutilizables | library_template.sh |
| Utilidades compartidas | library_template.sh |

---

## Checklist de Personalización

Al usar una plantilla, asegúrate de:

- [ ] Cambiar el nombre del archivo al nombre descriptivo del script
- [ ] Actualizar el bloque de comentarios del header
- [ ] Modificar la descripción y documentación de uso
- [ ] Actualizar códigos de salida documentados
- [ ] Listar dependencias reales del script
- [ ] Eliminar funciones de ejemplo no utilizadas
- [ ] Agregar la lógica específica de tu script
- [ ] Verificar que se sigan los [Estándares de Salida](../../docs/gobernanza/estandares_codigo.md#regla-de-oro-output-profesional)
- [ ] Validar con shellcheck: `shellcheck mi-script.sh`
- [ ] Probar el script en ambiente de desarrollo
- [ ] Agregar tests si aplica

---

## Estándares de Output

**CRÍTICO**: Todos los scripts deben seguir la Regla Fundamental de Output Profesional.

NUNCA usar:
- Emojis (OK NO START FILE etc.)
- Iconos Unicode (> - -> * etc.)
- Box drawing characters (╔ ║ ═ etc.)

SIEMPRE usar:
- Prefijos de texto: `[INFO]`, `[ERROR]`, `[SUCCESS]`, `[WARN]`
- Separadores ASCII: `----`, `====`, `____`
- Bullets simples: `-`, `*`, `1.`, `2.`

Ver documentación completa: [Estándares de Código](../../docs/gobernanza/estandares_codigo.md)

---

## Validación

Antes de commit, validar el script:

```bash
# Validar sintaxis
bash -n mi-script.sh

# Shellcheck
shellcheck mi-script.sh

# Validar que no tenga emojis
../../infrastructure/devcontainer/scripts/check_no_emojis.sh mi-script.sh

# Probar ejecución
./mi-script.sh --help
```

---

## Ejemplos en el Proyecto

Scripts existentes que siguen estos estándares:

- `scripts/requisitos/generar_indices.py` - Script Python con output profesional
- `scripts/requisitos/contar_requisitos.sh` - Script bash con formato limpio
- `infrastructure/devcontainer/scripts/post_create.sh` - Script complejo bien estructurado

---

## Recursos

- [Shell Scripting Guide Completa](../../docs/gobernanza/shell_scripting_guide.md)
- [Estándares de Código](../../docs/gobernanza/estandares_codigo.md)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [ShellCheck](https://www.shellcheck.net/)

---

**Última actualización**: 2025-11-03
**Mantenedor**: Equipo de Infraestructura
