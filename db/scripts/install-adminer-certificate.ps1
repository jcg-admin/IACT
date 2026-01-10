# install-adminer-certificate.ps1
# Script para instalar certificado SSL de Adminer en Windows
# Elimina el warning de "No segura" en el navegador
# Version: 1.0.0

#Requires -Version 5.1
#Requires -RunAsAdministrator

[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
param(
    [switch]$Force,
    [switch]$Remove,
    [switch]$Help
)

# Configuracion de colores
$script:SuccessColor = "Green"
$script:ErrorColor = "Red"
$script:WarningColor = "Yellow"
$script:InfoColor = "Cyan"

# Detectar directorio raiz del proyecto
function Get-ProjectRoot {
    $currentDir = Get-Location
    $maxLevels = 5
    $level = 0
    
    while ($level -lt $maxLevels) {
        if (Test-Path (Join-Path $currentDir "Vagrantfile")) {
            return $currentDir
        }
        
        $parentDir = Split-Path $currentDir -Parent
        if (-not $parentDir -or $parentDir -eq $currentDir) {
            break
        }
        
        $currentDir = $parentDir
        $level++
    }
    
    return Get-Location
}

$script:ProjectRoot = Get-ProjectRoot
$script:TempCertPath = Join-Path $env:TEMP "adminer.cer"
$script:CertSubject = "*192.168.56.12*"

# Funciones de output
function Show-Header {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $InfoColor
    Write-Host " Adminer SSL Certificate Installer" -ForegroundColor $InfoColor
    Write-Host " Version: 1.0.0" -ForegroundColor $InfoColor
    Write-Host "========================================" -ForegroundColor $InfoColor
    Write-Host ""
}

function Show-OK {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor $SuccessColor
}

function Show-Fail {
    param([string]$Message)
    Write-Host "  [FAIL] $Message" -ForegroundColor $ErrorColor
}

function Show-Warn {
    param([string]$Message)
    Write-Host "  [WARN] $Message" -ForegroundColor $WarningColor
}

function Show-Info {
    param([string]$Message)
    Write-Host "  [INFO] $Message" -ForegroundColor $InfoColor
}

function Show-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "$Title" -ForegroundColor $InfoColor
    Write-Host ("-" * $Title.Length) -ForegroundColor $InfoColor
}

# Funcion para mostrar ayuda
function Show-Help {
    Show-Header
    
    Write-Host "DESCRIPCION:"
    Write-Host "  Instala el certificado SSL de Adminer en el almacen de certificados"
    Write-Host "  de Windows para eliminar el warning 'No segura' en el navegador."
    Write-Host ""
    Write-Host "USO:"
    Write-Host "  .\install-adminer-certificate.ps1 [-Force] [-Remove] [-Help]"
    Write-Host ""
    Write-Host "PARAMETROS:"
    Write-Host "  -Force     Instalar sin pedir confirmacion"
    Write-Host "  -Remove    Eliminar certificado instalado"
    Write-Host "  -Help      Mostrar esta ayuda"
    Write-Host ""
    Write-Host "REQUIERE:"
    Write-Host "  - Ejecutar como Administrador"
    Write-Host "  - VM de Adminer corriendo (vagrant status adminer)"
    Write-Host ""
    Write-Host "EJEMPLOS:"
    Write-Host ""
    Write-Host "  .\install-adminer-certificate.ps1"
    Write-Host "    Instalar certificado (con confirmacion)"
    Write-Host ""
    Write-Host "  .\install-adminer-certificate.ps1 -Force"
    Write-Host "    Instalar sin confirmacion"
    Write-Host ""
    Write-Host "  .\install-adminer-certificate.ps1 -Remove"
    Write-Host "    Eliminar certificado instalado"
    Write-Host ""
    Write-Host "NOTA:"
    Write-Host "  Despues de instalar, cierra completamente el navegador y vuelve a abrirlo."
    Write-Host ""
}

# Verificar si ya esta instalado
function Test-CertificateInstalled {
    try {
        $cert = Get-ChildItem -Path Cert:\LocalMachine\Root -ErrorAction SilentlyContinue | 
                Where-Object { $_.Subject -like $script:CertSubject }
        
        return $null -ne $cert
    }
    catch {
        return $false
    }
}

# Obtener certificado instalado
function Get-InstalledCertificate {
    try {
        $cert = Get-ChildItem -Path Cert:\LocalMachine\Root -ErrorAction SilentlyContinue | 
                Where-Object { $_.Subject -like $script:CertSubject }
        
        return $cert
    }
    catch {
        return $null
    }
}

# Exportar certificado desde VM
function Export-CertificateFromVM {
    Show-Section "Exportando Certificado desde Adminer VM"
    
    # Verificar que VM esta corriendo
    try {
        Push-Location $script:ProjectRoot
        $status = & vagrant status adminer 2>&1
        Pop-Location
        
        if ($status -notmatch "running") {
            Show-Fail "VM de Adminer no esta corriendo"
            Show-Info "Ejecutar: vagrant up adminer"
            return $false
        }
        
        Show-OK "VM de Adminer esta corriendo"
        
    }
    catch {
        Pop-Location
        Show-Fail "Error verificando estado de VM: $_"
        return $false
    }
    
    # Exportar certificado
    try {
        Show-Info "Exportando certificado desde VM..."
        
        Push-Location $script:ProjectRoot
        $certContent = & vagrant ssh adminer -c "sudo cat /etc/ssl/certs/adminer-selfsigned.crt" 2>&1
        Pop-Location
        
        if ($LASTEXITCODE -ne 0) {
            Show-Fail "Error exportando certificado desde VM"
            return $false
        }
        
        # Guardar en archivo temporal
        $certContent | Out-File -FilePath $script:TempCertPath -Encoding ASCII
        
        Show-OK "Certificado exportado a: $script:TempCertPath"
        return $true
        
    }
    catch {
        Pop-Location
        Show-Fail "Error exportando certificado: $_"
        return $false
    }
}

# Instalar certificado
function Install-Certificate {
    Show-Section "Instalando Certificado en Windows"
    
    if (-not (Test-Path $script:TempCertPath)) {
        Show-Fail "Archivo de certificado no encontrado: $script:TempCertPath"
        return $false
    }
    
    # Confirmar instalacion
    if (-not $Force) {
        Write-Host ""
        Write-Host "  Se instalara el certificado SSL de Adminer en:" -ForegroundColor Yellow
        Write-Host "  Cert:\LocalMachine\Root (Entidades de certificacion raiz de confianza)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Esto permite que el navegador confie en https://192.168.56.12" -ForegroundColor Yellow
        Write-Host ""
        
        $confirm = Read-Host "  Continuar? (S/N)"
        
        if ($confirm -ne "S" -and $confirm -ne "s") {
            Show-Info "Instalacion cancelada"
            return $false
        }
    }
    
    # Importar certificado
    try {
        if ($PSCmdlet.ShouldProcess("Cert:\LocalMachine\Root", "Importar certificado de Adminer")) {
            $cert = Import-Certificate -FilePath $script:TempCertPath -CertStoreLocation Cert:\LocalMachine\Root -ErrorAction Stop
            
            Show-OK "Certificado instalado exitosamente"
            Write-Host ""
            Show-Info "Detalles del certificado:"
            Write-Host "  Subject: $($cert.Subject)" -ForegroundColor Gray
            Write-Host "  Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
            Write-Host "  Valido hasta: $($cert.NotAfter)" -ForegroundColor Gray
            Write-Host ""
            
            return $true
        }
        else {
            Show-Info "Instalacion simulada (WhatIf)"
            return $false
        }
    }
    catch {
        Show-Fail "Error instalando certificado: $_"
        return $false
    }
}

# Eliminar certificado
function Remove-Certificate {
    Show-Section "Eliminando Certificado de Windows"
    
    $cert = Get-InstalledCertificate
    
    if ($null -eq $cert) {
        Show-Warn "Certificado no esta instalado"
        return $true
    }
    
    Show-Info "Certificado encontrado:"
    Write-Host "  Subject: $($cert.Subject)" -ForegroundColor Gray
    Write-Host "  Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
    Write-Host ""
    
    # Confirmar eliminacion
    if (-not $Force) {
        $confirm = Read-Host "  Eliminar certificado? (S/N)"
        
        if ($confirm -ne "S" -and $confirm -ne "s") {
            Show-Info "Eliminacion cancelada"
            return $false
        }
    }
    
    # Eliminar
    try {
        if ($PSCmdlet.ShouldProcess($cert.Thumbprint, "Eliminar certificado")) {
            $cert | Remove-Item -Force -ErrorAction Stop
            Show-OK "Certificado eliminado exitosamente"
            return $true
        }
        else {
            Show-Info "Eliminacion simulada (WhatIf)"
            return $false
        }
    }
    catch {
        Show-Fail "Error eliminando certificado: $_"
        return $false
    }
}

# Limpiar archivo temporal
function Remove-TempFile {
    if (Test-Path $script:TempCertPath) {
        try {
            Remove-Item -Path $script:TempCertPath -Force -ErrorAction SilentlyContinue
        }
        catch {
            # Silently ignore
        }
    }
}

# Mostrar instrucciones finales
function Show-FinalInstructions {
    param([bool]$Installed)
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " SIGUIENTE PASO" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    if ($Installed) {
        Write-Host "  1. Cierra COMPLETAMENTE el navegador (todas las pestanas)" -ForegroundColor Cyan
        Write-Host "  2. Abre el navegador nuevamente" -ForegroundColor Cyan
        Write-Host "  3. Ve a: https://192.168.56.12" -ForegroundColor Cyan
        Write-Host "  4. Ya NO deberia mostrar 'No segura'" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Si aun muestra el warning:" -ForegroundColor Yellow
        Write-Host "  - En Chrome/Edge: chrome://net-internals/#sockets → Flush" -ForegroundColor Gray
        Write-Host "  - Ctrl + Shift + Delete → Limpiar cache" -ForegroundColor Gray
    }
    else {
        Write-Host "  El certificado ha sido eliminado." -ForegroundColor Cyan
        Write-Host "  https://192.168.56.12 volvera a mostrar el warning 'No segura'" -ForegroundColor Cyan
    }
    
    Write-Host ""
}

# Funcion principal
function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Show-Header
    
    # Modo eliminacion
    if ($Remove) {
        $removed = Remove-Certificate
        Show-FinalInstructions -Installed $false
        return
    }
    
    # Verificar si ya esta instalado
    if (Test-CertificateInstalled) {
        $cert = Get-InstalledCertificate
        
        Write-Host ""
        Show-Warn "El certificado ya esta instalado"
        Write-Host "  Subject: $($cert.Subject)" -ForegroundColor Gray
        Write-Host "  Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
        Write-Host "  Valido hasta: $($cert.NotAfter)" -ForegroundColor Gray
        Write-Host ""
        Show-Info "Para reinstalar, primero eliminalo con: -Remove"
        return
    }
    
    # Exportar certificado desde VM
    $exported = Export-CertificateFromVM
    
    if (-not $exported) {
        Show-Fail "No se pudo exportar el certificado"
        return
    }
    
    # Instalar certificado
    $installed = Install-Certificate
    
    # Limpiar archivo temporal
    Remove-TempFile
    
    # Mostrar instrucciones
    if ($installed) {
        Show-FinalInstructions -Installed $true
    }
}

# Ejecutar
Main
