# Vagrant Bootstrap: Entorno Inteligente para Bases de Datos

Este proyecto automatiza la instalación, configuración y verificación de servicios de bases de datos (MariaDB y PostgreSQL) en una máquina virtual Vagrant, usando shell puro y una estrategia basada en idempotencia, modularidad y trazabilidad.

## Características

- Instalación automática solo si es necesaria
- Configuración segura y auditada
- Verificación completa del entorno
- Modularidad por servicio
- Logs con timestamp para auditoría
- Fácilmente extensible (Redis, Nginx, etc.)

## Estructura del proyecto

```
vagrant/
├── bootstrap.sh              # Orquestador principal
├── verify_connections.sh     # Diagnóstico completo del entorno
├── install/                  # Scripts por servicio
│   ├── mariadb.sh
│   ├── postgresql.sh
├── config/                   # Archivos de configuración segura
│   ├── mariadb/50-server.cnf
│   ├── postgresql/postgresql.conf
│   └── postgresql/pg_hba.conf
├── utils/                    # Funciones auxiliares
│   ├── logging.sh
│   ├── validation.sh
│   └── common.sh
├── logs/                     # Logs generados por bootstrap
```

## Requisitos

- Ubuntu 20.04 / 22.04 / 24.04
- Vagrant + VirtualBox
- Acceso sudo sin contraseña
- RAM mínima: 1 GB
- Espacio libre: 2 GB

## Estrategia del pipeline

1. `bootstrap.sh` ejecuta `verify_connections.sh`
2. Si el entorno está completo, no hace nada
3. Si hay fallos, ejecuta scripts en `install/`
4. Aplica configuración segura solo si es diferente
5. Crea usuarios y bases solo si no existen
6. Ejecuta verificación final y guarda log

## Uso

```
vagrant up
vagrant ssh
cd /vagrant
bash bootstrap.sh
```

## Verificación manual

```
bash verify_connections.sh
```

Este script muestra:

- Estado de servicios
- Puertos abiertos
- Conexiones válidas
- Usuarios y bases
- Configuración activa
- Resumen final

## Extensión del entorno

Para agregar nuevos servicios:

1. Crear `install/redis.sh`
2. Crear `config/redis/redis.conf`
3. Usar funciones de `utils/`
4. Integrar en `bootstrap.sh`

## Licencia

MIT License. Puedes usar, modificar y distribuir libremente.

## Autor

David — CDMX, México  
Pipeline diseñado con Copilot
