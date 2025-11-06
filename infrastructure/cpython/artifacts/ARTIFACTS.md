# Registro de Artefactos CPython Precompilados

**Proyecto**: IACT - CPython Precompilado
**Referencia**: SPEC_INFRA_001
**Propósito**: Registro centralizado de artefactos de CPython compilados

---

## Formato

| Versión | Build | Distro | Fecha | SHA256 | URL Release | Estado |
|---------|-------|--------|-------|--------|-------------|--------|

**Campos**:
- **Versión**: Versión de Python (X.Y.Z)
- **Build**: Número de build
- **Distro**: Distribución de Ubuntu (ubuntu22.04, ubuntu24.04, etc.)
- **Fecha**: Fecha de compilación (YYYY-MM-DD)
- **SHA256**: Primeros 12 caracteres del checksum SHA256
- **URL Release**: URL del GitHub Release donde está publicado
- **Estado**: Activo / Deprecado / Archivado

---

## Artefactos Disponibles

| Versión | Build | Distro | Fecha | SHA256 | URL Release | Estado |
|---------|-------|--------|-------|--------|-------------|--------|
| - | - | - | - | - | Ningún artefacto generado aún | - |

---

## Instrucciones de Uso

### Agregar Nuevo Artefacto

Después de compilar y validar:

```bash
# Obtener checksum
SHA256_FULL=$(cat artifacts/cpython/cpython-X.Y.Z-ubuntuNN.NN-buildM.tgz.sha256 | cut -d' ' -f1)
SHA256_SHORT=$(echo $SHA256_FULL | cut -c1-12)

# Agregar línea a la tabla
echo "| X.Y.Z | M | ubuntuNN.NN | $(date +%Y-%m-%d) | $SHA256_SHORT... | https://github.com/2-Coatl/IACT---project/releases/tag/cpython-X.Y.Z-buildM | Activo |" >> artifacts/ARTIFACTS.md
```

### Marcar Artefacto como Deprecado

Cambiar estado de "Activo" a "Deprecado" en la tabla.

Los artefactos deprecados siguen disponibles pero no reciben actualizaciones de seguridad.

### Archivar Artefacto

Cambiar estado de "Deprecado" a "Archivado".

Artefactos archivados pueden ser eliminados del release (después de >1 año sin uso).

---

## Política de Retención

Según SPEC_INFRA_001:

- **Activos**: Últimas 3 versiones de Python
- **Deprecados**: Versiones con >6 meses de antigüedad
- **Archivados**: Versiones con >1 año sin uso

**Ejemplo**:
- Python 3.12.6 build 1: Activo
- Python 3.12.5 build 1: Deprecado
- Python 3.11.9 build 1: Deprecado
- Python 3.10.x: Archivado

---

## Rebuilds Programados

Calendario de rebuilds semestrales:

- **Próximo rebuild**: TBD
- **Versiones a rebuild**: TBD

---

## Changelog

| Fecha | Acción | Descripción |
|-------|--------|-------------|
| 2025-11-06 | Creación | Registro de artefactos creado |

---

## Notas

- Todos los artefactos DEBEN incluir checksum SHA256
- Todos los artefactos DEBEN pasar validación completa (11 checks)
- Todos los artefactos DEBEN incluir LICENSE de Python (PSF)
- Artefactos publicados son INMUTABLES (no editar releases)

---

**Mantenido por**: Equipo Infraestructura IACT
