# Call Center Analytics

Repositorio monolítico para la plataforma de analítica de centros de contacto (IACT). El sistema opera con Django 5, PostgreSQL para persistencia analítica y MariaDB para lectura de IVR.

## Requisitos locales

- Python 3.11+
- [Vagrant](https://developer.hashicorp.com/vagrant/install)
- VirtualBox 7+
- Cliente PostgreSQL (`postgresql-client`)
- Cliente MariaDB (`mariadb-client`)

## Levantar infraestructura de datos

```bash
vagrant up
```

El `Vagrantfile` provisiona una VM Ubuntu que instala PostgreSQL y MariaDB mediante `provisioning/bootstrap.sh`. Los puertos expuestos en la máquina anfitriona son:

- PostgreSQL: `127.0.0.1:15432`
- MariaDB: `127.0.0.1:13306`

Las credenciales creadas son `django_user` / `django_pass` para ambos motores. Puedes ajustar las variables de entorno en tu `.env` siguiendo la tabla incluida en [docs/verificacion-servicios.md](docs/verificacion-servicios.md).

## Verificar servicios

Una vez que la VM esté en ejecución:

```bash
./scripts/verificar_servicios.sh
```

El script prueba la conectividad contra las bases de datos utilizando las variables de entorno disponibles y reporta cualquier dependencia faltante.

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

## Recursos adicionales

- [Guía de verificación de servicios](docs/verificacion-servicios.md)
- [ADR de arquitectura](docs/architecture-decision-records/Arquitectura%20GitHub%20Codespaces.md)

