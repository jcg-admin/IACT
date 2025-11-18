#!/bin/bash
# ============================================================
# Ejemplo: Setup completo con Vagrant para desarrollo
# ============================================================
#
# Este script muestra como configurar el proyecto completo
# usando Vagrant para la base de datos en desarrollo.
#
# NOTA: Ejecutar en tu maquina local, no en Claude Code
# ============================================================

echo "================================================================"
echo " SETUP VAGRANT + BASE DE DATOS + AGENTES AI"
echo "================================================================"
echo

# 1. VERIFICAR VAGRANT
echo "Paso 1: Verificando Vagrant..."
if command -v vagrant &> /dev/null; then
    echo "  [OK] Vagrant instalado: $(vagrant --version)"
else
    echo "  [ERROR] Vagrant no instalado"
    echo "  Instalar: https://www.vagrantup.com/downloads"
    exit 1
fi

# 2. VERIFICAR VIRTUALBOX (o tu provider)
echo
echo "Paso 2: Verificando VirtualBox..."
if command -v vboxmanage &> /dev/null; then
    echo "  [OK] VirtualBox instalado"
else
    echo "  [WARNING] VirtualBox no detectado"
    echo "  Si usas otro provider (VMware, Parallels), ignorar"
fi

# 3. CREAR/VERIFICAR VAGRANTFILE
echo
echo "Paso 3: Vagrantfile para PostgreSQL..."

if [ ! -f "Vagrantfile" ]; then
    echo "  Creando Vagrantfile..."

cat > Vagrantfile << 'VAGRANTFILE'
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Ubuntu 22.04 LTS
  config.vm.box = "ubuntu/jammy64"

  # Port forwarding para PostgreSQL
  config.vm.network "forwarded_port", guest: 5432, host: 5432

  # Configuracion de recursos
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 2
  end

  # Provisioning: instalar PostgreSQL
  config.vm.provision "shell", inline: <<-SHELL
    # Actualizar sistema
    apt-get update

    # Instalar PostgreSQL
    apt-get install -y postgresql postgresql-contrib

    # Configurar PostgreSQL para aceptar conexiones externas
    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'dev_password';"
    sudo -u postgres psql -c "CREATE DATABASE iact_dev;"
    sudo -u postgres psql -c "CREATE USER dev_user WITH PASSWORD 'dev_password';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE iact_dev TO dev_user;"

    # Permitir conexiones desde host
    echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/*/main/pg_hba.conf
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf

    # Reiniciar PostgreSQL
    systemctl restart postgresql

    echo "PostgreSQL instalado y configurado!"
    echo "Database: iact_dev"
    echo "User: dev_user"
    echo "Password: dev_password"
  SHELL
end
VAGRANTFILE

    echo "  [OK] Vagrantfile creado"
else
    echo "  [OK] Vagrantfile ya existe"
fi

# 4. LEVANTAR VAGRANT
echo
echo "Paso 4: Levantando Vagrant VM..."
echo "  (Esto puede tomar varios minutos la primera vez)"
echo

# Descomentar para ejecutar realmente:
# vagrant up

echo "  Comando para ejecutar manualmente:"
echo "    vagrant up"
echo

# 5. CONFIGURAR .env
echo "Paso 5: Configurando .env para desarrollo..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  [OK] .env creado desde .env.example"
else
    echo "  [OK] .env ya existe"
fi

# Actualizar valores para desarrollo con Vagrant
cat >> .env << 'ENVFILE'

# ============================================
# CONFIGURACION PARA VAGRANT (Development)
# ============================================
ENVIRONMENT=development

# Base de datos en VM
DB_VM_HOST=localhost
DB_VM_PORT=5432
DB_VM_NAME=iact_dev
DB_VM_USER=dev_user
DB_VM_PASSWORD=dev_password

# LLM local
PREFER_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
ENVFILE

echo "  [OK] .env configurado para Vagrant"

# 6. INSTALAR DEPENDENCIAS PYTHON
echo
echo "Paso 6: Instalando dependencias Python..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  [OK] Virtual environment creado"
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
echo "  [OK] Dependencias instaladas"

# 7. VERIFICAR CONEXION
echo
echo "Paso 7: Verificando conexion a base de datos..."
echo

python3 << 'PYTHON'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").absolute()))

try:
    # Intentar importar psycopg2
    import psycopg2

    # Intentar conectar
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="iact_dev",
        user="dev_user",
        password="dev_password"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]

    print(f"  [OK] Conexion exitosa!")
    print(f"  PostgreSQL: {version[:50]}...")

    conn.close()

except ImportError:
    print("  [INFO] psycopg2 no instalado (se instalara con requirements.txt)")
    print("        pip install psycopg2-binary")

except Exception as e:
    print(f"  [WARNING] No se pudo conectar: {e}")
    print(f"  Asegurate de que Vagrant este corriendo: vagrant status")
PYTHON

# 8. INSTALAR OLLAMA (opcional)
echo
echo "Paso 8: Ollama para LLM local (opcional)..."

if command -v ollama &> /dev/null; then
    echo "  [OK] Ollama instalado"

    # Verificar si modelo esta descargado
    if ollama list | grep -q "llama3.1:8b"; then
        echo "  [OK] Modelo llama3.1:8b disponible"
    else
        echo "  [INFO] Descargar modelo: ollama pull llama3.1:8b"
    fi
else
    echo "  [INFO] Ollama no instalado"
    echo "  Instalar (Mac): brew install ollama"
    echo "  Instalar (Linux): curl -fsSL https://ollama.com/install.sh | sh"
fi

# 9. VERIFICAR TODO EL AMBIENTE
echo
echo "Paso 9: Verificacion completa del ambiente..."
echo

python3 examples/verify_environment.py

# 10. COMANDOS UTILES
echo
echo "================================================================"
echo " SETUP COMPLETO"
echo "================================================================"
echo
echo "Comandos utiles:"
echo
echo "  # Vagrant"
echo "  vagrant up              # Levantar VM"
echo "  vagrant halt            # Apagar VM"
echo "  vagrant ssh             # Conectar a VM"
echo "  vagrant destroy         # Eliminar VM"
echo
echo "  # Base de datos"
echo "  psql -h localhost -p 5432 -U dev_user -d iact_dev"
echo
echo "  # Agentes AI"
echo "  python3 test_case1_viabilidad.py"
echo "  python3 examples/agent_environment_example.py"
echo
echo "  # Verificar config"
echo "  python3 examples/verify_environment.py"
echo
echo "================================================================"
echo " Para ejecutar este setup:"
echo "   bash examples/vagrant_setup_example.sh"
echo "================================================================"
echo
