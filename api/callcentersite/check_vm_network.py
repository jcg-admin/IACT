#!/usr/bin/env python3
import socket
import platform
import subprocess
import mysql.connector
import psycopg2

# Configuración
MARIADB_PORT = 13306
POSTGRES_PORT = 15432
MARIADB_USER = "django_user"
MARIADB_PASS = "django_pass"
MARIADB_DB = "ivr_legacy"
POSTGRES_USER = "django_user"
POSTGRES_PASS = "django_pass"
POSTGRES_DB = "iact_analytics"

def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=2):
            return "[ESCUCHANDO]"
    except Exception:
        return "[NO DISPONIBLE]"

def check_ping(host):
    try:
        output = subprocess.check_output(f"ping -n 1 {host}", shell=True, text=True)
        return "[OK]" if "TTL=" in output else "[FALLO]"
    except Exception:
        return "[FALLO]"

def check_mysql(user, password, db=None, port=3306):
    try:
        conn = mysql.connector.connect(user=user, password=password, host="127.0.0.1", port=port, database=db)
        conn.close()
        return "[OK]"
    except Exception as e:
        return f"[FALLO] {str(e).splitlines()[0]}"

def check_postgres(user, password, db=None, port=5432):
    try:
        conn = psycopg2.connect(user=user, password=password, host="127.0.0.1", port=port, dbname=db)
        conn.close()
        return "[OK]"
    except Exception as e:
        return f"[FALLO] {str(e).splitlines()[0]}"

def section(title):
    print("\n" + "="*66)
    print(title)
    print("="*66)

def main():
    section("VERIFICACION DE PUERTOS Y CONEXIONES DESDE HOST WINDOWS")

    section("1. INFORMACION DEL SISTEMA")
    print(f"Hostname: {platform.node()}")
    print(f"Sistema: {platform.platform()}")
    print(f"Arquitectura: {platform.machine()}")

    section("2. CONECTIVIDAD BASICA")
    print("Loopback (127.0.0.1):", check_ping("127.0.0.1"))
    print("Gateway por defecto (10.0.2.2):", check_ping("10.0.2.2"))
    print("Internet (8.8.8.8):", check_ping("8.8.8.8"))

    section("3. PUERTOS REDIRECCIONADOS HACIA VM")
    print(f"MariaDB puerto {MARIADB_PORT}:", check_port("127.0.0.1", MARIADB_PORT))
    print(f"PostgreSQL puerto {POSTGRES_PORT}:", check_port("127.0.0.1", POSTGRES_PORT))

    section("4. PRUEBAS DE CONEXION A BASES DE DATOS EN VM")
    print(f"MariaDB ({MARIADB_USER}):", check_mysql(MARIADB_USER, MARIADB_PASS, db=MARIADB_DB, port=MARIADB_PORT))
    print(f"PostgreSQL ({POSTGRES_USER}):", check_postgres(POSTGRES_USER, POSTGRES_PASS, db=POSTGRES_DB, port=POSTGRES_PORT))

    section("5. RESOLUCION DNS")
    print("Resolucion DNS (google.com):", check_ping("google.com"))

if __name__ == "__main__":
    main()
