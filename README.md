# Call Center Analytics

Repositorio monolítico para la plataforma de analítica de centros de contacto (IACT). El sistema opera con Django 5, PostgreSQL para persistencia analítica y MariaDB para lectura de IVR.

## Inicio rápido

El proyecto incluye un `Makefile` con comandos comunes:

```bash
make help          # Ver todos los comandos disponibles
make setup         # Configurar entorno completo
make vagrant-up    # Levantar bases de datos
make docs-serve    # Ver documentación
```

## Requisitos locales

- Python 3.11+
- [Vagrant](https://developer.hashicorp.com/vagrant/install)
- VirtualBox 7+
- Cliente PostgreSQL (`postgresql-client`)
- Cliente MariaDB (`mariadb-client`)
- GNU Make (para usar el Makefile)

## Levantar infraestructura de datos

```bash
vagrant up
```

El `vagrantfile` provisiona una VM Ubuntu que instala PostgreSQL y MariaDB mediante `provisioning/bootstrap.sh`. Los puertos expuestos en la máquina anfitriona son:

- PostgreSQL: `127.0.0.1:15432`
- MariaDB: `127.0.0.1:13306`

Las credenciales creadas son `django_user` / `django_pass` para ambos motores. Puedes ajustar las variables de entorno en tu `.env` siguiendo la tabla incluida en [docs/devops/runbooks/verificar_servicios.md](docs/devops/runbooks/verificar_servicios.md).

## Verificar servicios

Una vez que la VM esté en ejecución:

```bash
./scripts/verificar_servicios.sh
```

El script prueba la conectividad contra las bases de datos utilizando las variables de entorno disponibles y reporta cualquier dependencia faltante.

## Artefacto CPython precompilado

Para acelerar los entornos de desarrollo y CI, el proyecto distribuye un build precompilado de CPython generado con la VM de `infrastructure/cpython`.

1. **Generar artefacto** (desde el host):
   ```bash
   make build_cpython VERSION=3.12.6
   ```
2. **Validar integridad**:
   ```bash
   make validate_cpython ARTIFACT=cpython-3.12.6-ubuntu20.04-build1.tgz
   ```
3. **Ubicación**: Los archivos `.tgz` y `.sha256` quedan en `infrastructure/cpython/artifacts/` y son consumidos por el Dev Container mediante el feature `infrastructure/cpython/installer`.
4. **Distribución**: Publica los mismos archivos en GitHub Releases cuando prepares un release estable y actualiza la referencia en `.devcontainer/devcontainer.json` si cambias de versión.

Consulta la [documentación del builder](docs/infrastructure/cpython-builder.md) y su [CHANGELOG dedicado](docs/infrastructure/CHANGELOG-cpython.md) para conocer el flujo completo y los cambios históricos.

## Documentación

El proyecto utiliza MkDocs para generar documentación estática. Usa el Makefile para gestionar la documentación:

```bash
# Instalar dependencias de documentación
make docs-install

# Construir documentación
make docs-build

# Servir documentación con live reload
make docs-serve

# Limpiar archivos generados
make docs-clean

# Desplegar a GitHub Pages
make docs-deploy
```

La documentación estará disponible en:
- **Local**: http://127.0.0.1:8000 (con `make docs-serve`)
- **GitHub Pages**: https://2-coatl.github.io/IACT---project/

## Flujo de desarrollo

1. Configura tu entorno virtual de Python e instala dependencias:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Ejecuta la suite de tests antes de proponer cambios.
3. Sigue TDD para nuevas funcionalidades.
4. Mantén una cobertura mínima del 80%.

Ver [Guía Completa de Desarrollo de Features](docs/gobernanza/procesos/guia_completa_desarrollo_features.md) para proceso detallado paso a paso.

## Spec-Driven Development

El proyecto implementa desarrollo guiado por especificaciones formales. Para features complejas:

**1. Crear especificación**:
```bash
# Usar plantilla de spec
cp docs/plantillas/desarrollo/plantilla_spec.md docs/specs/mi-feature.md

# Validar spec
make validate_spec SPEC=docs/specs/mi-feature.md
```

**2. Generar plan de implementación**:
```bash
# Auto-generar plan desde spec
make generate_plan SPEC=docs/specs/mi-feature.md
```

**3. Validar código antes de commit**:
```bash
# Ejecutar todos los checks (pre-commit, emojis, specs)
make check_all

# Con auto-corrección
make check_all-fix
```

**Comandos disponibles**:
- `make validate_spec` - Validar todas las especificaciones
- `make generate_plan SPEC=<file>` - Generar plan desde spec
- `make check_all` - Ejecutar todos los checks de calidad
- `make check_all-fix` - Ejecutar checks con auto-corrección

**Referencias**:
- [Plantilla de Especificación](docs/plantillas/desarrollo/plantilla_spec.md)
- [Plantilla de Plan](docs/plantillas/desarrollo/plantilla_plan.md)
- [Constitution para Agentes AI](docs/gobernanza/agentes/constitution.md)

## Guías y estándares

- **[Guía de Estilo](docs/gobernanza/GUIA_ESTILO.md)** - Convenciones obligatorias del proyecto (incluyendo prohibición de emojis)
- [Procedimiento de Gestión de Cambios](docs/gobernanza/procesos/procedimiento_gestion_cambios.md) - Workflow Git estándar
- [Procedimiento de Desarrollo Local](docs/gobernanza/procesos/procedimiento_desarrollo_local.md) - Setup entorno local

## Recursos adicionales

- [Guía de verificación de servicios](docs/devops/runbooks/verificar_servicios.md)
- [ADR de arquitectura](docs/arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md)
- [Playbooks operativos](docs/infrastructure/devops/runbooks/playbooks_operativos/readme.md)

