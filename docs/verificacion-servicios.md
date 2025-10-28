# Verificación y restablecimiento de servicios de bases de datos

Esta guía describe cómo levantar los servicios requeridos por la aplicación (PostgreSQL y MariaDB) en un entorno de desarrollo basado en Vagrant y cómo comprobar su disponibilidad desde el repositorio.

## 1. Preparar la máquina virtual de servicios

1. Instala [Vagrant](https://developer.hashicorp.com/vagrant/install) y VirtualBox en tu máquina anfitriona.
2. Desde la raíz del proyecto ejecuta:

   ```bash
   vagrant up
   ```

   El archivo [`Vagrantfile`](../Vagrantfile) crea una VM Ubuntu con 2 vCPU y 4 GB de RAM, expone los puertos `15432` (PostgreSQL) y `13306` (MariaDB) hacia tu host y provisiona ambos motores mediante [`provisioning/bootstrap.sh`](../provisioning/bootstrap.sh).

3. Una vez finalizado el aprovisionamiento, los servicios quedarán escuchando dentro de la VM en los puertos estándar (`5432` y `3306`).

> **Nota:** Si necesitas reiniciar los servicios puedes usar `vagrant reload --provision` para reaplicar el _bootstrap_ completo o `vagrant ssh -- sudo systemctl restart postgresql mariadb` para un reinicio rápido.

## 2. Configurar credenciales en el proyecto

El aprovisionamiento crea las siguientes credenciales de desarrollo:

| Motor     | Host             | Puerto host | Base de datos | Usuario      | Contraseña   |
|-----------|------------------|-------------|---------------|--------------|--------------|
| PostgreSQL| `127.0.0.1`      | `15432`     | `callcenterdb`| `django_user`| `django_pass`|
| MariaDB   | `127.0.0.1`      | `13306`     | `ivrdb`       | `django_user`| `django_pass`|

Incluye estas variables en tu `.env` o exporta las variables de entorno equivalentes para que Django pueda conectarse.

## 3. Verificar conectividad desde el repositorio

1. Asegúrate de contar con los clientes de línea de comando:

   ```bash
   sudo apt-get install postgresql-client mariadb-client
   ```

2. Ejecuta el script de verificación incluido en [`scripts/verificar_servicios.sh`](../scripts/verificar_servicios.sh):

   ```bash
   ./scripts/verificar_servicios.sh
   ```

   El script lee las variables de entorno disponibles, intenta conectar con ambos motores y reporta el resultado. En caso de fallo indica qué dependencia falta o qué servicio no responde.

## 4. Solución de problemas frecuentes

| Síntoma | Posible causa | Acción recomendada |
|---------|---------------|--------------------|
| `psql: could not connect to server: Connection refused` | La VM no está en ejecución | Ejecutar `vagrant up` y repetir la verificación. |
| `mysql: command not found` | El cliente de MariaDB no está instalado en tu máquina | Instalar `mariadb-client` usando tu gestor de paquetes. |
| `verificacion[WARN] Verificación finalizada con 2 fallo(s)` | Ambos motores inaccesibles | Confirmar que los puertos `15432/13306` no estén ocupados y que la VM esté activa. |

Con estos pasos dispondrás de una infraestructura local reproducible, alineada con la topología de producción (PostgreSQL para escritura y MariaDB en modo lectura), permitiendo ejecutar pruebas y tareas analíticas sin depender de Docker.
