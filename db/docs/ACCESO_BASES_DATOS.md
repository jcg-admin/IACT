# Guía de Acceso a Bases de Datos

Documentación completa para conectarse a las bases de datos MariaDB y PostgreSQL desde diferentes clientes y lenguajes de programación.

---

## Índice

1. [Parámetros de Conexión](#parametros-de-conexion)
2. [Acceso desde Línea de Comando](#acceso-desde-linea-de-comando)
3. [Clientes GUI](#clientes-gui)
4. [Python](#python)
5. [PHP](#php)
6. [Node.js](#nodejs)
7. [Java](#java)
8. [C#](#csharp)
9. [Ruby](#ruby)
10. [Go](#go)
11. [Adminer Web Interface](#adminer-web-interface)
12. [Connection Strings](#connection-strings)
13. [Configuración Multi-Base de Datos](#configuracion-multi-base-de-datos)
14. [Solución de Problemas](#solucion-de-problemas)

---

## Parámetros de Conexión

### MariaDB

| Parámetro | Valor |
|-----------|-------|
| Host | 192.168.56.10 |
| Puerto | 3306 |
| Base de datos | ivr_legacy |
| Usuario aplicación | django_user |
| Contraseña aplicación | django_pass |
| Usuario root | root |
| Contraseña root | rootpass123 |
| Character Set | utf8mb4 |
| Collation | utf8mb4_unicode_ci |

### PostgreSQL

| Parámetro | Valor |
|-----------|-------|
| Host | 192.168.56.11 |
| Puerto | 5432 |
| Base de datos | iact_analytics |
| Usuario aplicación | django_user |
| Contraseña aplicación | django_pass |
| Usuario superusuario | postgres |
| Contraseña superusuario | postgrespass123 |
| Encoding | UTF8 |
| Locale | en_US.UTF-8 |

---

## Acceso desde Línea de Comando

### MariaDB - Desde el Host

Conexión como usuario de aplicación:
```bash
mysql -h 192.168.56.10 -u django_user -p'django_pass' ivr_legacy
```

Conexión como root:
```bash
mysql -h 192.168.56.10 -u root -p'rootpass123'
```

Ejecutar consulta única:
```bash
mysql -h 192.168.56.10 -u django_user -p'django_pass' ivr_legacy -e "SHOW TABLES;"
```

Ejecutar archivo SQL:
```bash
mysql -h 192.168.56.10 -u django_user -p'django_pass' ivr_legacy < script.sql
```

### MariaDB - Desde la VM

Conectar por SSH y luego a MySQL:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123'
mysql -u django_user -p'django_pass' ivr_legacy
```

### PostgreSQL - Desde el Host

Conexión como usuario de aplicación:
```bash
PGPASSWORD='django_pass' psql -h 192.168.56.11 -U django_user -d iact_analytics
```

Conexión como superusuario:
```bash
PGPASSWORD='postgrespass123' psql -h 192.168.56.11 -U postgres
```

Ejecutar consulta única:
```bash
PGPASSWORD='django_pass' psql -h 192.168.56.11 -U django_user -d iact_analytics -c "SELECT version();"
```

Ejecutar archivo SQL:
```bash
PGPASSWORD='django_pass' psql -h 192.168.56.11 -U django_user -d iact_analytics -f script.sql
```

### PostgreSQL - Desde la VM

Conectar por SSH y cambiar a usuario postgres:
```bash
vagrant ssh postgresql
sudo -i -u postgres
psql
```

O directamente a la base de datos:
```bash
vagrant ssh postgresql
sudo -u postgres psql -d iact_analytics
```

---

## Clientes GUI

### MySQL Workbench (MariaDB)

Configuración de nueva conexión:

```
Connection Name:    IACT DevBox - MariaDB
Connection Method:  Standard (TCP/IP)
Hostname:           192.168.56.10
Port:               3306
Username:           django_user
Password:           django_pass (Store in Vault)
Default Schema:     ivr_legacy
```

Pasos de configuración:
1. Abrir MySQL Workbench
2. Click en "+" junto a "MySQL Connections"
3. Ingresar los parámetros anteriores
4. Test Connection
5. OK

### pgAdmin 4 (PostgreSQL)

Configuración de nuevo servidor:

```
General Tab:
  Name: IACT DevBox - PostgreSQL

Connection Tab:
  Host name/address:    192.168.56.11
  Port:                 5432
  Maintenance database: postgres
  Username:             django_user
  Password:             django_pass
  Save password:        Yes
```

Pasos de configuración:
1. Abrir pgAdmin 4
2. Click derecho en "Servers" → Create → Server
3. Ingresar los parámetros anteriores
4. Save

### DBeaver (Universal)

Configuración para MariaDB:
```
Database:       MySQL/MariaDB
Server Host:    192.168.56.10
Port:           3306
Database:       ivr_legacy
Username:       django_user
Password:       django_pass
Driver:         MariaDB (o MySQL)
```

Configuración para PostgreSQL:
```
Database:       PostgreSQL
Host:           192.168.56.11
Port:           5432
Database:       iact_analytics
Username:       django_user
Password:       django_pass
```

Pasos de configuración:
1. Abrir DBeaver
2. Database → New Database Connection
3. Seleccionar tipo de base de datos
4. Ingresar parámetros
5. Test Connection
6. Finish

### HeidiSQL (MariaDB)

Configuración de nueva sesión:

```
Network type:   MariaDB or MySQL (TCP/IP)
Library:        libmariadb.dll
Hostname / IP:  192.168.56.10
User:           django_user
Password:       django_pass
Port:           3306
Databases:      ivr_legacy
```

### DataGrip (JetBrains)

Configuración para MariaDB:
```
Data Source:    MariaDB
Host:           192.168.56.10
Port:           3306
Database:       ivr_legacy
User:           django_user
Password:       django_pass
```

Configuración para PostgreSQL:
```
Data Source:    PostgreSQL
Host:           192.168.56.11
Port:           5432
Database:       iact_analytics
User:           django_user
Password:       django_pass
```

---

## Python

### Django - settings.py

Configuración con una sola base de datos (PostgreSQL):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iact_analytics',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.11',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

Configuración con múltiples bases de datos:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iact_analytics',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.11',
        'PORT': '5432',
    },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_legacy',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.10',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

Ver sección [Configuración Multi-Base de Datos](#configuracion-multi-base-de-datos) para routers.

### PyMySQL (MariaDB)

Instalación:
```bash
pip install pymysql
```

Uso básico:
```python
import pymysql

# Crear conexión
connection = pymysql.connect(
    host='192.168.56.10',
    port=3306,
    user='django_user',
    password='django_pass',
    database='ivr_legacy',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # Ejecutar consulta
        cursor.execute("SELECT * FROM tabla LIMIT 10")
        result = cursor.fetchall()
        print(result)
        
        # Insertar datos
        sql = "INSERT INTO tabla (campo1, campo2) VALUES (%s, %s)"
        cursor.execute(sql, ('valor1', 'valor2'))
    
    # Confirmar cambios
    connection.commit()
finally:
    connection.close()
```

### mysql-connector-python (MariaDB)

Instalación:
```bash
pip install mysql-connector-python
```

Uso:
```python
import mysql.connector

connection = mysql.connector.connect(
    host='192.168.56.10',
    port=3306,
    user='django_user',
    password='django_pass',
    database='ivr_legacy'
)

cursor = connection.cursor(dictionary=True)
cursor.execute("SELECT * FROM tabla LIMIT 10")
result = cursor.fetchall()

for row in result:
    print(row)

cursor.close()
connection.close()
```

### psycopg2 (PostgreSQL)

Instalación:
```bash
pip install psycopg2-binary
```

Uso básico:
```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Crear conexión
connection = psycopg2.connect(
    host='192.168.56.11',
    port=5432,
    user='django_user',
    password='django_pass',
    database='iact_analytics'
)

try:
    # Crear cursor con resultados como diccionarios
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    
    # Ejecutar consulta
    cursor.execute("SELECT * FROM tabla LIMIT 10")
    result = cursor.fetchall()
    
    for row in result:
        print(row)
    
    # Insertar datos
    cursor.execute(
        "INSERT INTO tabla (campo1, campo2) VALUES (%s, %s)",
        ('valor1', 'valor2')
    )
    
    connection.commit()
finally:
    cursor.close()
    connection.close()
```

### SQLAlchemy (ORM Universal)

Instalación:
```bash
pip install sqlalchemy pymysql psycopg2-binary
```

MariaDB:
```python
from sqlalchemy import create_engine

engine = create_engine(
    'mysql+pymysql://django_user:django_pass@192.168.56.10:3306/ivr_legacy',
    echo=True  # Mostrar SQL generado
)

with engine.connect() as connection:
    result = connection.execute("SELECT * FROM tabla LIMIT 10")
    for row in result:
        print(row)
```

PostgreSQL:
```python
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql+psycopg2://django_user:django_pass@192.168.56.11:5432/iact_analytics'
)

with engine.connect() as connection:
    result = connection.execute("SELECT version()")
    print(result.fetchone())
```

---

## PHP

### PDO - MariaDB

```php
<?php
$dsn = 'mysql:host=192.168.56.10;port=3306;dbname=ivr_legacy;charset=utf8mb4';
$username = 'django_user';
$password = 'django_pass';

try {
    $pdo = new PDO($dsn, $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Consulta simple
    $stmt = $pdo->query('SELECT * FROM tabla LIMIT 10');
    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    foreach ($results as $row) {
        print_r($row);
    }
    
    // Consulta preparada
    $stmt = $pdo->prepare('SELECT * FROM tabla WHERE id = :id');
    $stmt->execute(['id' => 1]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    
} catch (PDOException $e) {
    echo 'Error de conexión: ' . $e->getMessage();
}
?>
```

### PDO - PostgreSQL

```php
<?php
$dsn = 'pgsql:host=192.168.56.11;port=5432;dbname=iact_analytics';
$username = 'django_user';
$password = 'django_pass';

try {
    $pdo = new PDO($dsn, $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    $stmt = $pdo->query('SELECT version()');
    $version = $stmt->fetchColumn();
    echo "PostgreSQL Version: $version\n";
    
} catch (PDOException $e) {
    echo 'Error de conexión: ' . $e->getMessage();
}
?>
```

### MySQLi (MariaDB)

```php
<?php
$mysqli = new mysqli(
    '192.168.56.10',
    'django_user',
    'django_pass',
    'ivr_legacy',
    3306
);

if ($mysqli->connect_error) {
    die('Error de conexión: ' . $mysqli->connect_error);
}

$mysqli->set_charset('utf8mb4');

$result = $mysqli->query('SELECT * FROM tabla LIMIT 10');

while ($row = $result->fetch_assoc()) {
    print_r($row);
}

$mysqli->close();
?>
```

### PostgreSQL Extension (deprecated)

```php
<?php
$connection_string = 'host=192.168.56.11 port=5432 dbname=iact_analytics user=django_user password=django_pass';
$connection = pg_connect($connection_string);

if (!$connection) {
    die('Error de conexión');
}

$result = pg_query($connection, 'SELECT * FROM tabla LIMIT 10');

while ($row = pg_fetch_assoc($result)) {
    print_r($row);
}

pg_close($connection);
?>
```

---

## Node.js

### mysql2 (MariaDB)

Instalación:
```bash
npm install mysql2
```

Uso con Promises:
```javascript
const mysql = require('mysql2/promise');

async function main() {
    const connection = await mysql.createConnection({
        host: '192.168.56.10',
        port: 3306,
        user: 'django_user',
        password: 'django_pass',
        database: 'ivr_legacy'
    });
    
    try {
        const [rows, fields] = await connection.execute(
            'SELECT * FROM tabla LIMIT 10'
        );
        console.log(rows);
        
        // Consulta preparada
        const [results] = await connection.execute(
            'SELECT * FROM tabla WHERE id = ?',
            [1]
        );
        console.log(results);
        
    } finally {
        await connection.end();
    }
}

main().catch(console.error);
```

Pool de conexiones:
```javascript
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
    host: '192.168.56.10',
    port: 3306,
    user: 'django_user',
    password: 'django_pass',
    database: 'ivr_legacy',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

async function query() {
    const [rows] = await pool.execute('SELECT * FROM tabla LIMIT 10');
    return rows;
}
```

### pg (PostgreSQL)

Instalación:
```bash
npm install pg
```

Uso básico:
```javascript
const { Client } = require('pg');

const client = new Client({
    host: '192.168.56.11',
    port: 5432,
    user: 'django_user',
    password: 'django_pass',
    database: 'iact_analytics'
});

async function main() {
    await client.connect();
    
    try {
        const res = await client.query('SELECT * FROM tabla LIMIT 10');
        console.log(res.rows);
        
        // Consulta preparada
        const res2 = await client.query(
            'SELECT * FROM tabla WHERE id = $1',
            [1]
        );
        console.log(res2.rows);
        
    } finally {
        await client.end();
    }
}

main().catch(console.error);
```

Pool de conexiones:
```javascript
const { Pool } = require('pg');

const pool = new Pool({
    host: '192.168.56.11',
    port: 5432,
    user: 'django_user',
    password: 'django_pass',
    database: 'iact_analytics',
    max: 10,
    idleTimeoutMillis: 30000,
});

async function query() {
    const client = await pool.connect();
    try {
        const res = await client.query('SELECT * FROM tabla LIMIT 10');
        return res.rows;
    } finally {
        client.release();
    }
}
```

### Sequelize (ORM)

Instalación:
```bash
npm install sequelize mysql2 pg pg-hstore
```

MariaDB:
```javascript
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('ivr_legacy', 'django_user', 'django_pass', {
    host: '192.168.56.10',
    port: 3306,
    dialect: 'mysql'
});

async function testConnection() {
    try {
        await sequelize.authenticate();
        console.log('Conexión establecida');
    } catch (error) {
        console.error('Error de conexión:', error);
    }
}
```

PostgreSQL:
```javascript
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('iact_analytics', 'django_user', 'django_pass', {
    host: '192.168.56.11',
    port: 5432,
    dialect: 'postgres'
});
```

---

## Java

### JDBC - MariaDB

Agregar dependencia Maven:
```xml
<dependency>
    <groupId>org.mariadb.jdbc</groupId>
    <artifactId>mariadb-java-client</artifactId>
    <version>3.0.8</version>
</dependency>
```

Código:
```java
import java.sql.*;

public class MariaDBConnection {
    public static void main(String[] args) {
        String url = "jdbc:mariadb://192.168.56.10:3306/ivr_legacy";
        String user = "django_user";
        String password = "django_pass";
        
        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM tabla LIMIT 10");
            
            while (rs.next()) {
                System.out.println(rs.getString("campo"));
            }
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

### JDBC - PostgreSQL

Agregar dependencia Maven:
```xml
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.5.1</version>
</dependency>
```

Código:
```java
import java.sql.*;

public class PostgreSQLConnection {
    public static void main(String[] args) {
        String url = "jdbc:postgresql://192.168.56.11:5432/iact_analytics";
        String user = "django_user";
        String password = "django_pass";
        
        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            PreparedStatement pstmt = conn.prepareStatement(
                "SELECT * FROM tabla WHERE id = ?"
            );
            pstmt.setInt(1, 1);
            
            ResultSet rs = pstmt.executeQuery();
            
            while (rs.next()) {
                System.out.println(rs.getString("campo"));
            }
            
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

---

## C#

### MySQL.Data (MariaDB)

Instalar paquete NuGet:
```
Install-Package MySql.Data
```

Código:
```csharp
using MySql.Data.MySqlClient;

class Program
{
    static void Main()
    {
        string connString = "Server=192.168.56.10;Port=3306;Database=ivr_legacy;Uid=django_user;Pwd=django_pass;";
        
        using (var conn = new MySqlConnection(connString))
        {
            conn.Open();
            
            var cmd = new MySqlCommand("SELECT * FROM tabla LIMIT 10", conn);
            using (var reader = cmd.ExecuteReader())
            {
                while (reader.Read())
                {
                    Console.WriteLine(reader["campo"]);
                }
            }
        }
    }
}
```

### Npgsql (PostgreSQL)

Instalar paquete NuGet:
```
Install-Package Npgsql
```

Código:
```csharp
using Npgsql;

class Program
{
    static void Main()
    {
        string connString = "Host=192.168.56.11;Port=5432;Database=iact_analytics;Username=django_user;Password=django_pass;";
        
        using (var conn = new NpgsqlConnection(connString))
        {
            conn.Open();
            
            using (var cmd = new NpgsqlCommand("SELECT * FROM tabla LIMIT 10", conn))
            using (var reader = cmd.ExecuteReader())
            {
                while (reader.Read())
                {
                    Console.WriteLine(reader["campo"]);
                }
            }
        }
    }
}
```

---

## Ruby

### mysql2 (MariaDB)

Instalación:
```bash
gem install mysql2
```

Uso:
```ruby
require 'mysql2'

client = Mysql2::Client.new(
  host: '192.168.56.10',
  port: 3306,
  username: 'django_user',
  password: 'django_pass',
  database: 'ivr_legacy'
)

results = client.query('SELECT * FROM tabla LIMIT 10')

results.each do |row|
  puts row.inspect
end

client.close
```

### pg (PostgreSQL)

Instalación:
```bash
gem install pg
```

Uso:
```ruby
require 'pg'

conn = PG.connect(
  host: '192.168.56.11',
  port: 5432,
  dbname: 'iact_analytics',
  user: 'django_user',
  password: 'django_pass'
)

result = conn.exec('SELECT * FROM tabla LIMIT 10')

result.each do |row|
  puts row.inspect
end

conn.close
```

### ActiveRecord (Rails)

config/database.yml:
```yaml
development:
  adapter: mysql2
  encoding: utf8mb4
  database: ivr_legacy
  username: django_user
  password: django_pass
  host: 192.168.56.10
  port: 3306

analytics:
  adapter: postgresql
  encoding: unicode
  database: iact_analytics
  username: django_user
  password: django_pass
  host: 192.168.56.11
  port: 5432
```

---

## Go

### go-sql-driver/mysql (MariaDB)

Instalación:
```bash
go get -u github.com/go-sql-driver/mysql
```

Código:
```go
package main

import (
    "database/sql"
    "fmt"
    _ "github.com/go-sql-driver/mysql"
)

func main() {
    dsn := "django_user:django_pass@tcp(192.168.56.10:3306)/ivr_legacy"
    
    db, err := sql.Open("mysql", dsn)
    if err != nil {
        panic(err)
    }
    defer db.Close()
    
    rows, err := db.Query("SELECT * FROM tabla LIMIT 10")
    if err != nil {
        panic(err)
    }
    defer rows.Close()
    
    for rows.Next() {
        var campo string
        err = rows.Scan(&campo)
        if err != nil {
            panic(err)
        }
        fmt.Println(campo)
    }
}
```

### pq (PostgreSQL)

Instalación:
```bash
go get -u github.com/lib/pq
```

Código:
```go
package main

import (
    "database/sql"
    "fmt"
    _ "github.com/lib/pq"
)

func main() {
    connStr := "host=192.168.56.11 port=5432 user=django_user password=django_pass dbname=iact_analytics sslmode=disable"
    
    db, err := sql.Open("postgres", connStr)
    if err != nil {
        panic(err)
    }
    defer db.Close()
    
    rows, err := db.Query("SELECT * FROM tabla LIMIT 10")
    if err != nil {
        panic(err)
    }
    defer rows.Close()
    
    for rows.Next() {
        var campo string
        err = rows.Scan(&campo)
        if err != nil {
            panic(err)
        }
        fmt.Println(campo)
    }
}
```

---

## Adminer Web Interface

### Acceso

URLs disponibles:
- HTTP: http://192.168.56.12
- HTTPS: https://192.168.56.12

Nota: HTTPS usa certificado autofirmado. El navegador mostrará advertencia de seguridad.

### Conexión a MariaDB

```
Sistema:    MySQL
Servidor:   192.168.56.10
Usuario:    django_user
Contraseña: django_pass
Base de datos: ivr_legacy (opcional)
```

### Conexión a PostgreSQL

```
Sistema:    PostgreSQL
Servidor:   192.168.56.11
Usuario:    django_user
Contraseña: django_pass
Base de datos: iact_analytics (opcional)
```

### Funcionalidades disponibles

- Ejecutar consultas SQL
- Explorar tablas y datos
- Crear/modificar estructura de tablas
- Importar/exportar datos (SQL, CSV)
- Gestión de usuarios y permisos
- Visualización de estructura de base de datos
- Ejecución de comandos administrativos

---

## Connection Strings

### MariaDB

**Formato estándar:**
```
mysql://django_user:django_pass@192.168.56.10:3306/ivr_legacy
```

**JDBC:**
```
jdbc:mysql://192.168.56.10:3306/ivr_legacy?user=django_user&password=django_pass
```

**JDBC (MariaDB driver):**
```
jdbc:mariadb://192.168.56.10:3306/ivr_legacy?user=django_user&password=django_pass
```

**ODBC:**
```
Driver={MySQL ODBC 8.0 Unicode Driver};Server=192.168.56.10;Port=3306;Database=ivr_legacy;Uid=django_user;Pwd=django_pass;
```

**SQLAlchemy:**
```
mysql+pymysql://django_user:django_pass@192.168.56.10:3306/ivr_legacy
```

**Entity Framework (C#):**
```
Server=192.168.56.10;Port=3306;Database=ivr_legacy;Uid=django_user;Pwd=django_pass;
```

### PostgreSQL

**Formato estándar:**
```
postgresql://django_user:django_pass@192.168.56.11:5432/iact_analytics
```

**JDBC:**
```
jdbc:postgresql://192.168.56.11:5432/iact_analytics?user=django_user&password=django_pass
```

**ODBC:**
```
Driver={PostgreSQL Unicode};Server=192.168.56.11;Port=5432;Database=iact_analytics;Uid=django_user;Pwd=django_pass;
```

**SQLAlchemy:**
```
postgresql+psycopg2://django_user:django_pass@192.168.56.11:5432/iact_analytics
```

**libpq (formato URI):**
```
postgres://django_user:django_pass@192.168.56.11:5432/iact_analytics
```

**Entity Framework (C#):**
```
Host=192.168.56.11;Port=5432;Database=iact_analytics;Username=django_user;Password=django_pass;
```

---

## Configuración Multi-Base de Datos

### Django - Uso de Database Routers

Archivo de configuración (settings.py):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iact_analytics',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.11',
        'PORT': '5432',
    },
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_legacy',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.10',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

DATABASE_ROUTERS = ['myapp.routers.DatabaseRouter']
```

Router (myapp/routers.py):
```python
class DatabaseRouter:
    """
    Router para dirigir modelos de legacy_app a base de datos 'legacy',
    y el resto de modelos a base de datos 'default'.
    """
    
    def db_for_read(self, model, **hints):
        """Dirigir lecturas."""
        if model._meta.app_label == 'legacy_app':
            return 'legacy'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Dirigir escrituras."""
        if model._meta.app_label == 'legacy_app':
            return 'legacy'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Permitir relaciones solo dentro de la misma base de datos."""
        db1 = obj1._state.db or 'default'
        db2 = obj2._state.db or 'default'
        return db1 == db2
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Asegurar que migraciones se apliquen a la base correcta."""
        if app_label == 'legacy_app':
            return db == 'legacy'
        return db == 'default'
```

Uso en modelos:
```python
# legacy_app/models.py
from django.db import models

class LegacyModel(models.Model):
    # Este modelo usará automáticamente la BD 'legacy'
    campo = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'legacy_app'
        db_table = 'tabla_legacy'

# myapp/models.py
from django.db import models

class NewModel(models.Model):
    # Este modelo usará la BD 'default'
    campo = models.CharField(max_length=100)
```

Comandos de migración:
```bash
# Aplicar migraciones a base de datos default
python manage.py migrate

# Aplicar migraciones a base de datos legacy
python manage.py migrate --database=legacy

# Crear migraciones para app específica
python manage.py makemigrations legacy_app
```

Consultas manuales:
```python
# Usar base de datos específica
User.objects.using('legacy').all()
LegacyModel.objects.using('legacy').filter(campo='valor')

# Guardar en base de datos específica
instance = MyModel(campo='valor')
instance.save(using='legacy')
```

---

## Solución de Problemas

### No se puede conectar a la base de datos

Verificar que la VM esté corriendo:
```bash
vagrant status
```

Verificar conectividad de red:
```bash
ping 192.168.56.10  # MariaDB
ping 192.168.56.11  # PostgreSQL
```

Verificar que el puerto esté abierto:
```bash
telnet 192.168.56.10 3306  # MariaDB
telnet 192.168.56.11 5432  # PostgreSQL
```

En Windows PowerShell:
```powershell
Test-NetConnection -ComputerName 192.168.56.10 -Port 3306
Test-NetConnection -ComputerName 192.168.56.11 -Port 5432
```

### Error de autenticación

Verificar credenciales:
```bash
# MariaDB
mysql -h 192.168.56.10 -u django_user -p'django_pass' ivr_legacy

# PostgreSQL
PGPASSWORD='django_pass' psql -h 192.168.56.11 -U django_user -d iact_analytics
```

Si falla, conectarse a la VM y verificar usuarios:
```bash
# MariaDB
vagrant ssh mariadb
mysql -u root -p'rootpass123'
SELECT User, Host FROM mysql.user;
SHOW GRANTS FOR 'django_user'@'%';

# PostgreSQL
vagrant ssh postgresql
sudo -i -u postgres psql
\du
\l
```

### Base de datos no existe

Verificar bases de datos disponibles:
```bash
# MariaDB
mysql -h 192.168.56.10 -u root -p'rootpass123' -e "SHOW DATABASES;"

# PostgreSQL
PGPASSWORD='postgrespass123' psql -h 192.168.56.11 -U postgres -l
```

### Timeout de conexión

Posibles causas:
1. Firewall bloqueando conexión
2. Servicio de base de datos no corriendo
3. Configuración de red incorrecta

Verificar servicio:
```bash
# MariaDB
vagrant ssh mariadb -c "sudo systemctl status mariadb"

# PostgreSQL
vagrant ssh postgresql -c "sudo systemctl status postgresql"
```

Verificar configuración de red:
```bash
# MariaDB - debe escuchar en todas las interfaces
vagrant ssh mariadb -c "sudo netstat -tlnp | grep 3306"

# PostgreSQL - debe escuchar en todas las interfaces
vagrant ssh postgresql -c "sudo netstat -tlnp | grep 5432"
```

### Errores de charset/encoding

MariaDB - especificar charset:
```bash
mysql -h 192.168.56.10 -u django_user -p'django_pass' --default-character-set=utf8mb4 ivr_legacy
```

En connection string:
```
mysql://django_user:django_pass@192.168.56.10:3306/ivr_legacy?charset=utf8mb4
```

PostgreSQL - verificar encoding:
```bash
PGPASSWORD='django_pass' psql -h 192.168.56.11 -U django_user -d iact_analytics -c "SHOW client_encoding;"
```

### Permisos insuficientes

Error típico:
```
Access denied for user 'django_user'@'192.168.56.1' to database 'ivr_legacy'
```

Verificar permisos:
```bash
# MariaDB
vagrant ssh mariadb
mysql -u root -p'rootpass123'
SHOW GRANTS FOR 'django_user'@'%';

# PostgreSQL
vagrant ssh postgresql
sudo -i -u postgres psql
\dp  # Permisos de tablas
```

Otorgar permisos faltantes:
```sql
-- MariaDB
GRANT SELECT, INSERT, UPDATE, DELETE ON ivr_legacy.* TO 'django_user'@'%';
FLUSH PRIVILEGES;

-- PostgreSQL
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO django_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO django_user;
```

### SSL/TLS requerido (PostgreSQL)

Si se requiere conexión SSL:
```bash
PGPASSWORD='django_pass' psql "host=192.168.56.11 port=5432 dbname=iact_analytics user=django_user sslmode=require"
```

En connection string:
```
postgresql://django_user:django_pass@192.168.56.11:5432/iact_analytics?sslmode=require
```

### Demasiadas conexiones

Error típico:
```
Too many connections
```

Verificar conexiones activas:
```sql
-- MariaDB
SHOW STATUS WHERE Variable_name = 'Threads_connected';
SHOW PROCESSLIST;

-- PostgreSQL
SELECT count(*) FROM pg_stat_activity;
SELECT * FROM pg_stat_activity;
```

Aumentar límite de conexiones (temporal):
```sql
-- MariaDB
SET GLOBAL max_connections = 200;

-- PostgreSQL
ALTER SYSTEM SET max_connections = 200;
-- Reiniciar servicio después
```

---

## Referencias

- Documentación MariaDB: https://mariadb.com/kb/
- Documentación PostgreSQL: https://www.postgresql.org/docs/16/
- ARCHITECTURE.md - Arquitectura del sistema
- CONFIGURACION.md - Configuración de credenciales
- TROUBLESHOOTING.md - Solución de problemas general
- SEGURIDAD.md - Consideraciones de seguridad

---

Última actualización: 02 de enero de 2026
Versión del documento: 1.0.0