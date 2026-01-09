<#
.SYNOPSIS
    Script de automatización para migraciones y seeding de IACT.
    Versión con fix de entorno virtual (SIMPLE)
#>

$ErrorActionPreference = "Stop"
$system = "IACT"
$dateSuffix = Get-Date -Format 'yyyyMMdd'
$logFile = "logs/full_setup_iso_$dateSuffix.log"

# Asegurar que existe la carpeta de logs
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }

function Write-Log {
    param([string]$message, [string]$process, [string]$level = "INFO")
    $iso = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $logLine = "$iso [LEVEL=$level] [PROCESS=$process] [SYSTEM=$system] [SOURCE=django.mgmt] $message"
    Write-Host $logLine
    $logLine | Out-File -FilePath $logFile -Append -Encoding UTF8
}

Write-Log "INICIANDO PROCESO DE RECONSTRUCCIÓN DE BASE DE DATOS" "SETUP"

# ====== FIX: ACTIVAR ENTORNO VIRTUAL ======
Write-Log "Buscando y activando entorno virtual..." "SETUP"

$venvPaths = @("venv\Scripts\Activate.ps1", ".venv\Scripts\Activate.ps1", "env\Scripts\Activate.ps1")
$venvFound = $false

foreach ($venvPath in $venvPaths) {
    if (Test-Path $venvPath) {
        Write-Log "Activando entorno virtual: $venvPath" "SETUP"
        try {
            & $venvPath
            $venvFound = $true
            break
        }
        catch {
            Write-Log "Error al activar $venvPath : $_" "SETUP" "WARN"
        }
    }
}

if (-not $venvFound) {
    Write-Log "ERROR: No se encontró ningún entorno virtual" "SETUP" "ERROR"
    Write-Log "Por favor crea un entorno virtual con: python -m venv venv" "SETUP" "ERROR"
    exit 1
}

# Verificar Django
try {
    $djangoVersion = python -c "import django; print(django.get_version())" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Django $djangoVersion detectado correctamente" "SETUP"
    }
    else {
        throw "Django no está disponible"
    }
}
catch {
    Write-Log "ERROR: Django no está instalado. Ejecuta: pip install -r requirements/base.txt" "SETUP" "ERROR"
    exit 1
}
# ====== FIN DEL FIX ======

# 1. MAKEMIGRATIONS
Write-Log "Detectando cambios en modelos..." "MAKEMIGRATIONS"
python manage.py makemigrations 2>&1 | ForEach-Object { Write-Log $_ "MAKEMIGRATIONS" }
if ($LASTEXITCODE -ne 0) {
    Write-Log "ERROR en makemigrations" "MAKEMIGRATIONS" "ERROR"
    exit 1
}

# 2. MIGRATE
Write-Log "Aplicando migraciones a PostgreSQL..." "MIGRATE"
python manage.py migrate 2>&1 | ForEach-Object { Write-Log $_ "MIGRATE" }
if ($LASTEXITCODE -ne 0) {
    Write-Log "ERROR en migrate" "MIGRATE" "ERROR"
    exit 1
}

# 3. SEEDING
Write-Log "Iniciando población de datos (Seeding)..." "SEED_MASTER"
python manage.py seed_permisos_completo 2>&1 | ForEach-Object { Write-Log $_ "SEED_MASTER" }
if ($LASTEXITCODE -ne 0) {
    Write-Log "ERROR en seeding" "SEED_MASTER" "ERROR"
    exit 1
}

Write-Log "PROCESO FINALIZADO EXITOSAMENTE" "SETUP"
exit 0
