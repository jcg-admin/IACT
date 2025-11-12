#!/usr/bin/env python3
"""
Ejemplo: Conexion a Base de Datos Adaptativa

Muestra como conectarse a la base de datos correcta segun el ambiente:
- Desarrollo: VM via localhost
- Staging: Servidor de staging
- Produccion: Servidor de produccion con SSL

Uso:
    python3 examples/backend_database_example.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ai.shared.environment_config import get_environment_config


def create_database_connection():
    """
    Crea conexion a base de datos segun ambiente.

    Returns:
        dict: Configuracion de conexion
    """
    config = get_environment_config()
    db_config = config.get_database_config()

    print(f"\n{'='*70}")
    print(f" CONEXION A BASE DE DATOS - {config.environment.upper()}")
    print(f"{'='*70}\n")

    if config.is_dev:
        # DESARROLLO: Usar VM
        print("Modo Desarrollo - Conectando a VM")
        print(f"  Host: {db_config['host']}")
        print(f"  Port: {db_config['port']}")
        print(f"  Database: {db_config['database']}")
        print(f"  User: {db_config['user']}")

        if db_config.get("ssh_tunnel", {}).get("enabled"):
            print("\n  SSH Tunnel habilitado:")
            tunnel = db_config["ssh_tunnel"]
            print(f"    SSH Host: {tunnel['host']}")
            print(f"    SSH Port: {tunnel['port']}")
            print(f"    SSH User: {tunnel['user']}")

            # En caso real, crear SSH tunnel
            connection_str = f"""
# Conexion via SSH tunnel:
ssh -L {db_config['port']}:localhost:{db_config['port']} \\
    {tunnel['user']}@{tunnel['host']} -p {tunnel['port']}

# Luego conectar:
psql -h localhost -p {db_config['port']} \\
     -U {db_config['user']} -d {db_config['database']}
"""
            print(connection_str)

        else:
            # Conexion directa a VM
            connection_str = f"""
# Conexion directa:
psql -h {db_config['host']} -p {db_config['port']} \\
     -U {db_config['user']} -d {db_config['database']}
"""
            print(connection_str)

        # Django settings equivalente
        print("\nDjango settings.py equivalente:")
        print("""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '%s',
        'USER': '%s',
        'PASSWORD': '%s',
        'HOST': '%s',
        'PORT': %d,
    }
}
""" % (db_config['database'], db_config['user'],
       db_config['password'], db_config['host'], db_config['port']))

    elif config.is_staging:
        # STAGING: Servidor de staging
        print("Modo Staging - Conectando a servidor de staging")
        print(f"  Host: {db_config['host']}")
        print(f"  Port: {db_config['port']}")
        print(f"  Database: {db_config['database']}")
        print(f"  SSL Mode: {db_config.get('ssl_mode', 'prefer')}")

        connection_str = f"""
# Conexion a staging:
psql "host={db_config['host']} \\
      port={db_config['port']} \\
      dbname={db_config['database']} \\
      user={db_config['user']} \\
      sslmode={db_config.get('ssl_mode', 'prefer')}"
"""
        print(connection_str)

        print("\nDjango settings.py equivalente:")
        print("""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '%s',
        'USER': '%s',
        'PASSWORD': os.getenv('DB_STAGING_PASSWORD'),
        'HOST': '%s',
        'PORT': %d,
        'OPTIONS': {
            'sslmode': '%s',
        },
    }
}
""" % (db_config['database'], db_config['user'],
       db_config['host'], db_config['port'],
       db_config.get('ssl_mode', 'prefer')))

    elif config.is_prod:
        # PRODUCCION: Credenciales directas con SSL
        print("Modo Produccion - Conectando DIRECTAMENTE (no VM)")
        print(f"  Host: {db_config['host']}")
        print(f"  Port: {db_config['port']}")
        print(f"  Database: {db_config['database']}")
        print(f"  SSL Mode: {db_config.get('ssl_mode', 'require')}")

        if db_config.get('ssl_ca'):
            print(f"  SSL CA: {db_config['ssl_ca']}")

        connection_str = f"""
# Conexion a produccion (con SSL):
psql "host={db_config['host']} \\
      port={db_config['port']} \\
      dbname={db_config['database']} \\
      user={db_config['user']} \\
      sslmode={db_config.get('ssl_mode', 'require')}"
"""
        print(connection_str)

        print("\nDjango settings.py equivalente:")
        ssl_options = """
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': '%s',
        },
""" % db_config.get('ssl_ca', '/path/to/ca-cert.crt')

        print("""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '%s',
        'USER': '%s',
        'PASSWORD': os.getenv('DB_PROD_PASSWORD'),
        'HOST': '%s',
        'PORT': %d,%s
        'CONN_MAX_AGE': 600,  # Conexion persistente
    }
}
""" % (db_config['database'], db_config['user'],
       db_config['host'], db_config['port'], ssl_options))

    print(f"\n{'='*70}")

    # Verificaciones de seguridad
    print("\nVERIFICACIONES DE SEGURIDAD:")

    if config.is_prod:
        checks = []

        if not db_config.get('password'):
            checks.append("[ERROR] Password no configurada")

        if db_config.get('ssl_mode') != 'require':
            checks.append("[WARNING] SSL no es obligatorio")

        if not db_config.get('ssl_ca'):
            checks.append("[WARNING] Certificado SSL CA no configurado")

        if db_config.get('use_vm'):
            checks.append("[ERROR] Produccion NO debe usar VM")

        if checks:
            for check in checks:
                print(f"  {check}")
        else:
            print("  [OK] Todas las verificaciones pasaron")

    elif config.is_dev:
        print("  [INFO] Modo desarrollo - verificaciones relajadas")

    print(f"{'='*70}\n")

    return db_config


def test_connection():
    """
    Intenta conectarse a la base de datos.
    (Solo simula, no hace conexion real)
    """
    config = get_environment_config()
    db_config = create_database_connection()

    print("SIMULACION DE CONEXION:")

    try:
        # En caso real, aqui iria:
        # import psycopg2
        # conn = psycopg2.connect(**db_config)

        print(f"  [OK] Conexion exitosa a {db_config['database']}")
        print(f"       en {db_config['host']}:{db_config['port']}")

        # Queries de ejemplo
        if config.is_dev:
            print("\n  Queries de desarrollo:")
            print("    - SELECT COUNT(*) FROM users;")
            print("    - INSERT INTO test_data (...);")
            print("    - TRUNCATE test_table;")

        elif config.is_prod:
            print("\n  [WARNING] En produccion, usar queries READ-ONLY:")
            print("    - SELECT COUNT(*) FROM users;")
            print("    - SELECT * FROM orders WHERE date > NOW() - INTERVAL '1 day';")

    except Exception as e:
        print(f"  [ERROR] No se pudo conectar: {e}")


def main():
    """Ejecuta ejemplo de conexion."""
    print("\n" + "="*70)
    print(" EJEMPLO: CONEXION ADAPTATIVA A BASE DE DATOS")
    print("="*70)

    config = get_environment_config()
    print(f"\nAmbiente actual: {config.environment.upper()}")

    # Crear conexion
    db_config = create_database_connection()

    # Test de conexion
    test_connection()

    # Recomendaciones
    print("\nRECOMENDACIONES:")

    if config.is_dev:
        print("""
Para desarrollo local:

1. Levantar PostgreSQL en Docker:
   docker-compose -f docker-compose.dev.yml up -d db

2. Verificar que este corriendo:
   docker ps | grep postgres

3. Conectarse:
   psql -h localhost -p 5432 -U dev_user -d iact_dev

4. Si usas SSH tunnel:
   ssh -L 5432:localhost:5432 vagrant@192.168.1.100
""")

    elif config.is_staging:
        print("""
Para staging:

1. Verificar acceso al servidor:
   ping staging-db.internal

2. Probar conexion:
   psql -h staging-db.internal -U staging_user -d iact_staging

3. Si falla, verificar:
   - Firewall permite puerto 5432
   - Credenciales correctas en .env
   - VPN conectada (si aplica)
""")

    elif config.is_prod:
        print("""
Para produccion:

[IMPORTANTE] Solo personal autorizado debe acceder a produccion

1. Verificar credenciales en .env:
   cat .env | grep DB_PROD

2. SIEMPRE usar conexiones SSL:
   sslmode=require

3. Usar solo queries READ-ONLY si es posible:
   SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY;

4. Monitorear queries:
   SELECT * FROM pg_stat_activity WHERE state = 'active';
""")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
