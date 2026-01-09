# clean-logs.ps1
# Script de limpieza y archivo de logs antiguos
# Version: 1.0.6

#Requires -Version 5.1

[CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
param(
    [int]$DaysToKeep = 30,
    [switch]$Compress,
    [switch]$Help
)

# Configuracion
$script:LogsPath = "logs"
$script:ArchivePath = "logs\archive"

# Colores
$script:SuccessColor = "Green"
$script:ErrorColor = "Red"
$script:WarningColor = "Yellow"
$script:InfoColor = "Cyan"

# Funcion para mostrar header
function Show-Header {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $InfoColor
    Write-Host " IACT DevBox - Log Cleanup Utility" -ForegroundColor $InfoColor
    Write-Host " Version: 1.0.6" -ForegroundColor $InfoColor
    Write-Host "========================================" -ForegroundColor $InfoColor
    Write-Host ""
}

# Funcion para mostrar resultado OK
function Show-OK {
    param([string]$Message)
    Write-Host "  [OK]" -ForegroundColor $SuccessColor -NoNewline
    Write-Host " $Message"
}

# Funcion para mostrar error
function Show-Error {
    param([string]$Message)
    Write-Host "  [ERROR]" -ForegroundColor $ErrorColor -NoNewline
    Write-Host " $Message"
}

# Funcion para mostrar advertencia
function Show-Warning {
    param([string]$Message)
    Write-Host "  [WARNING]" -ForegroundColor $WarningColor -NoNewline
    Write-Host " $Message"
}

# Funcion para mostrar informacion
function Show-Info {
    param([string]$Message)
    Write-Host "  [INFO]" -ForegroundColor $InfoColor -NoNewline
    Write-Host " $Message"
}

# Funcion para mostrar ayuda
function Show-Help {
    Show-Header

    Write-Host "USO:"
    Write-Host "  .\clean-logs.ps1 [-DaysToKeep <dias>] [-Compress] [-WhatIf] [-Confirm] [-Help]"
    Write-Host ""
    Write-Host "PARAMETROS:"
    Write-Host "  -DaysToKeep <int>   Dias a mantener (default: 30)"
    Write-Host "  -Compress           Comprimir logs en archive/"
    Write-Host "  -WhatIf             Simular sin hacer cambios (automatico)"
    Write-Host "  -Confirm            Pedir confirmacion UNA VEZ antes de ejecutar"
    Write-Host "  -Help               Mostrar esta ayuda"
    Write-Host ""
    Write-Host "EJEMPLOS:"
    Write-Host "  .\clean-logs.ps1"
    Write-Host "    Limpiar logs de mas de 30 dias"
    Write-Host ""
    Write-Host "  .\clean-logs.ps1 -DaysToKeep 7"
    Write-Host "    Limpiar logs de mas de 7 dias"
    Write-Host ""
    Write-Host "  .\clean-logs.ps1 -WhatIf"
    Write-Host "    Ver que se haria sin hacer cambios (simulacion)"
    Write-Host ""
    Write-Host "  .\clean-logs.ps1 -Compress"
    Write-Host "    Comprimir logs en archive/"
    Write-Host ""
    Write-Host "  .\clean-logs.ps1 -Compress -WhatIf"
    Write-Host "    Ver que se comprimiria sin hacer cambios"
    Write-Host ""
    Write-Host "  .\clean-logs.ps1 -DaysToKeep 15 -Compress -Confirm"
    Write-Host "    Limpiar, comprimir y pedir confirmacion"
    Write-Host ""
    Write-Host "NOTA:"
    Write-Host "  -WhatIf y -Confirm son parametros estandar de PowerShell."
    Write-Host "  -Confirm pide confirmacion UNA sola vez por operacion completa."
    Write-Host ""
}

# Funcion para verificar directorio de logs
function Test-LogsDirectory {
    if (-not (Test-Path $script:LogsPath)) {
        Show-Error "Directorio de logs no encontrado: $script:LogsPath"
        Show-Info "Asegurate de ejecutar este script desde la raiz del proyecto"
        return $false
    }
    return $true
}

# Funcion para crear directorio de archivo
function Initialize-ArchiveDirectory {
    if (-not (Test-Path $script:ArchivePath)) {
        if ($PSCmdlet.ShouldProcess($script:ArchivePath, "Crear directorio de archivo")) {
            try {
                New-Item -ItemType Directory -Path $script:ArchivePath -Force | Out-Null
                Show-OK "Directorio de archivo creado: $script:ArchivePath"
            }
            catch {
                Show-Error "No se pudo crear directorio de archivo: $_"
                return $false
            }
        }
    }
    return $true
}

# Funcion para obtener logs antiguos
function Get-OldLogs {
    param([int]$Days)

    $cutoffDate = (Get-Date).AddDays(-$Days)

    Get-ChildItem -Path $script:LogsPath -Filter "*.log" |
        Where-Object { $_.LastWriteTime -lt $cutoffDate }
}

# Funcion para mover logs al archivo
function Move-LogsToArchive {
    param(
        [Parameter(Mandatory)]
        [System.IO.FileInfo[]]$Logs
    )

    $movedCount = 0

    foreach ($log in $Logs) {
        $destPath = Join-Path $script:ArchivePath $log.Name

        if ($PSCmdlet.ShouldProcess($log.Name, "Mover a archive")) {
            try {
                Move-Item -Path $log.FullName -Destination $destPath -Force
                Show-OK "Movido: $($log.Name)"
                $movedCount++
            }
            catch {
                Show-Error "Error moviendo $($log.Name): $_"
            }
        }
        else {
            Show-Info "[WHATIF] Moveria: $($log.Name)"
        }
    }

    return $movedCount
}

# Funcion para comprimir logs archivados
function Compress-ArchivedLogs {
    $logFiles = Get-ChildItem -Path $script:ArchivePath -Filter "*.log"

    if ($logFiles.Count -eq 0) {
        Show-Info "No hay logs para comprimir en archive/"
        return 0
    }

    $compressedCount = 0
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $zipPath = Join-Path $script:ArchivePath "logs_$timestamp.zip"
    $zipName = "logs_$timestamp.zip"

    # Confirmacion UNA SOLA VEZ para toda la operacion
    $compressionTarget = "$($logFiles.Count) archivos -> $zipName (y eliminar originales)"

    if ($PSCmdlet.ShouldProcess($compressionTarget, "Comprimir y limpiar logs")) {
        try {
            Show-Info "Comprimiendo $($logFiles.Count) logs..."

            # Comprimir
            Compress-Archive -Path $logFiles.FullName -DestinationPath $zipPath -Force
            Show-OK "Logs comprimidos: $zipName"

            $zipSize = (Get-Item $zipPath).Length
            $zipSizeKB = [math]::Round($zipSize / 1KB, 2)
            Show-Info "Tamano del archivo: $zipSizeKB KB"

            # Eliminar logs originales SIN confirmaciones adicionales
            # -Confirm:$false es CRÍTICO para evitar confirmaciones redundantes
            foreach ($log in $logFiles) {
                Remove-Item -Path $log.FullName -Force -Confirm:$false -ErrorAction SilentlyContinue
            }
            Show-OK "$($logFiles.Count) logs originales eliminados despues de comprimir"

            $compressedCount = $logFiles.Count
        }
        catch {
            Show-Error "Error comprimiendo logs: $_"
        }
    }
    else {
        Write-Host ""
        Show-Info "[WHATIF] Archivos que se comprimirian:"
        foreach ($log in $logFiles) {
            Write-Host "    - $($log.Name)" -ForegroundColor Gray
        }
        Write-Host ""
        Show-Info "[WHATIF] Se crearia: $zipName"
        Show-Info "[WHATIF] Se eliminarian $($logFiles.Count) archivos .log"
    }

    return $compressedCount
}

# Funcion para mostrar estadisticas
function Show-Statistics {
    param(
        [int]$OldLogsCount,
        [int]$MovedCount,
        [int]$CompressedCount
    )

    Write-Host ""
    Write-Host "========================================" -ForegroundColor $InfoColor
    Write-Host " ESTADISTICAS" -ForegroundColor $InfoColor
    Write-Host "========================================" -ForegroundColor $InfoColor
    Write-Host ""

    if ($WhatIfPreference) {
        Write-Host "  Modo: WHATIF (simulacion)" -ForegroundColor $WarningColor
    }
    else {
        Write-Host "  Modo: EJECUCION REAL" -ForegroundColor $SuccessColor
    }

    Write-Host ""
    Write-Host "  Logs antiguos encontrados: $OldLogsCount"
    Write-Host "  Logs movidos a archivo: $MovedCount"

    if ($CompressedCount -gt 0) {
        Write-Host "  Logs comprimidos: $CompressedCount"
    }

    Write-Host ""

    $logsSize = (Get-ChildItem -Path $script:LogsPath -File -Recurse |
                 Measure-Object -Property Length -Sum).Sum

    $logsSizeMB = [math]::Round($logsSize / 1MB, 2)
    Write-Host "  Tamano actual de logs/: $logsSizeMB MB"

    $zipFiles = Get-ChildItem -Path $script:ArchivePath -Filter "*.zip" -ErrorAction SilentlyContinue
    if ($zipFiles.Count -gt 0) {
        Write-Host "  Archivos ZIP en archive/: $($zipFiles.Count)"
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

    if (-not (Test-LogsDirectory)) {
        return
    }

    if (-not (Initialize-ArchiveDirectory)) {
        return
    }

    # Mostrar modo WhatIf si esta activo
    if ($WhatIfPreference) {
        Show-Warning "Modo WHATIF: No se haran cambios reales"
        Write-Host ""
    }

    # MODO 1: Solo comprimir
    if ($Compress -and -not $PSBoundParameters.ContainsKey('DaysToKeep')) {
        Show-Info "Modo: Solo compresion de logs en archive/"
        Write-Host ""

        $compressedCount = Compress-ArchivedLogs

        Write-Host ""

        if ($compressedCount -gt 0 -and -not $WhatIfPreference) {
            Show-OK "Compresion completada"
        }

        Write-Host ""
        return
    }

    # MODO 2: Limpiar logs antiguos
    Show-Info "Limpiando logs de mas de $DaysToKeep dias..."
    Write-Host ""

    $oldLogs = Get-OldLogs -Days $DaysToKeep

    if ($oldLogs.Count -eq 0) {
        Show-OK "No se encontraron logs antiguos"

        if ($Compress) {
            Write-Host ""
            Show-Info "Comprimiendo logs existentes en archive/..."
            $compressedCount = Compress-ArchivedLogs

            Write-Host ""

            if ($compressedCount -gt 0 -and -not $WhatIfPreference) {
                Show-OK "Compresion completada"
            }
        }

        Write-Host ""
        return
    }

    Show-Info "Encontrados $($oldLogs.Count) logs antiguos"
    Write-Host ""

    $movedCount = Move-LogsToArchive -Logs $oldLogs

    $compressedCount = 0
    if ($Compress) {
        Write-Host ""
        Show-Info "Comprimiendo logs archivados..."
        $compressedCount = Compress-ArchivedLogs
    }

    Show-Statistics -OldLogsCount $oldLogs.Count -MovedCount $movedCount -CompressedCount $compressedCount

    if (-not $WhatIfPreference -and ($movedCount -gt 0 -or $compressedCount -gt 0)) {
        Show-OK "Limpieza completada"
    }

    Write-Host ""
}

# EJECUTAR
Main