---
id: SCRIPTS-INDEX
tipo: documentacion
titulo: Scripts del Proyecto IACT
fecha: 2025-11-03
---

# Scripts del Proyecto IACT

Scripts organizados por función para facilitar tareas comunes.

**IMPORTANTE**: Al crear nuevos scripts, seguir:
- [Shell Scripting Guide](../docs/gobernanza/shell_scripting_guide.md) - Guía completa de shell scripting
- [Estándares de Código](../docs/gobernanza/estandares_codigo.md) - Regla de Oro de Output Profesional
- [Plantillas de Scripts](templates/README.md) - Templates estandarizados

---

## Estructura

```
scripts/
├── README.md                    ← Este archivo
├── templates/                   ← Plantillas de scripts estandarizadas
│   ├── README.md                ← Guía de plantillas
│   ├── bash-script-template.sh
│   ├── posix-script-template.sh
│   └── library-template.sh
└── requisitos/                  ← Scripts para gestión de requisitos
    ├── README.md                ← Documentación detallada
    ├── generar_indices.py       ← Genera índices ISO 29148
    ├── contar_requisitos.sh     ← Cuenta requisitos por tipo/dominio
    ├── validar_frontmatter.py   ← Valida YAML de requisitos
    └── listar_requisitos.sh     ← Lista todos los requisitos
```

---

## Scripts de Requisitos

### Uso rápido:

```bash
# Contar requisitos
bash scripts/requisitos/contar_requisitos.sh

# Listar todos los requisitos
bash scripts/requisitos/listar_requisitos.sh

# Validar frontmatter
python scripts/requisitos/validar_frontmatter.py

# Generar índices ISO 29148
python scripts/requisitos/generar_indices.py
```

**Documentación completa**: [scripts/requisitos/README.md](requisitos/README.md)

---

## Flujo de Trabajo Recomendado

### Al trabajar con requisitos:

1. **Crear/Editar** requisito en `docs/implementacion/`
2. **Validar** frontmatter: `python scripts/requisitos/validar_frontmatter.py`
3. **Generar** índices: `python scripts/requisitos/generar_indices.py`
4. **Verificar** conteo: `bash scripts/requisitos/contar_requisitos.sh`
5. **Commit** y push

---

## Permisos

Si encuentras problemas de permisos:

```bash
chmod +x scripts/requisitos/*.sh
chmod +x scripts/requisitos/*.py
```

---

## Crear Nuevos Scripts

Para crear un nuevo script en el proyecto:

1. **Seleccionar plantilla apropiada** de `templates/`:
   - `bash-script-template.sh` - Scripts complejos con características bash
   - `posix-script-template.sh` - Scripts simples y portables
   - `library-template.sh` - Bibliotecas de funciones reutilizables

2. **Copiar y personalizar**:
   ```bash
   cp scripts/templates/bash-script-template.sh scripts/mi-nuevo-script.sh
   # Editar y personalizar
   ```

3. **Validar antes de commit**:
   ```bash
   shellcheck scripts/mi-nuevo-script.sh
   bash -n scripts/mi-nuevo-script.sh
   ```

Ver: [Plantillas de Scripts](templates/README.md) para guía completa.

---

## Referencias

**Documentación del Proyecto:**
- [Estructura de Implementación](../docs/implementacion/README.md)
- [Plantillas ISO 29148](../docs/plantillas/readme.md)
- [Propuesta de Reestructuración](../docs/PROPUESTA_FINAL_REESTRUCTURACION.md)

**Estándares y Guías:**
- [Shell Scripting Guide Completa](../docs/gobernanza/shell_scripting_guide.md)
- [Estándares de Código](../docs/gobernanza/estandares_codigo.md)
- [Plantillas de Scripts](templates/README.md)

---

**Última actualización**: 2025-11-03
**Mantenedor**: equipo-arquitectura
