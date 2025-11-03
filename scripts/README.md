---
id: SCRIPTS-INDEX
tipo: documentacion
titulo: Scripts del Proyecto IACT
fecha: 2025-11-03
---

# Scripts del Proyecto IACT

Scripts organizados por función para facilitar tareas comunes.

---

## Estructura

```
scripts/
├── README.md                    ← Este archivo
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

## Referencias

- [Estructura de Implementación](../docs/implementacion/README.md)
- [Plantillas ISO 29148](../docs/plantillas/readme.md)
- [Propuesta de Reestructuración](../docs/PROPUESTA_FINAL_REESTRUCTURACION.md)

---

**Última actualización**: 2025-11-03
**Mantenedor**: equipo-arquitectura
