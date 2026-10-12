# DDLC-MoreMonika uninstaller
# Usage:
#   powershell -ExecutionPolicy Bypass -File uninstall.ps1 [-GameDir "path\to\DDLC\game"]
param(
    [string]$GameDir = ""
)
$ErrorActionPreference = "Continue"

if (-not $GameDir) {
    $candidates = @(
        (Join-Path $PSScriptRoot "game"),
        $PSScriptRoot,
        "Z:\dicksheplane\Doki Doki Literature Club\game",
        "C:\Program Files (x86)\Steam\steamapps\common\Doki Doki Literature Club\game",
        (Join-Path $env:USERPROFILE "Desktop\Doki Doki Literature Club\game")
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path $c) -and (Test-Path (Join-Path $c "..\DDLC.exe"))) { $GameDir = $c; break }
    }
}
if (-not $GameDir) { $GameDir = Read-Host "Enter the full path to your DDLC 'game' folder" }
if (-not (Test-Path $GameDir)) { Write-Host "[X] Game folder not found: $GameDir"; exit 1 }

Write-Host "[*] Uninstalling from: $GameDir"

foreach ($f in @("zz_moremonika.rpy", "zz_moremonika.rpyc", "poemsentences.txt", "monika_cam_system.bat")) {
    $p = Join-Path $GameDir $f
    if (Test-Path $p) { Remove-Item $p -Force; Write-Host "[-] $f" }
}

# restore original script-ch30 bytecode
$bak = Join-Path $GameDir "script-ch30.rpyc.mmbackup"
if (Test-Path $bak) {
    Copy-Item $bak (Join-Path $GameDir "script-ch30.rpyc") -Force
    Remove-Item $bak -Force
    Write-Host "[+] script-ch30.rpyc restored from backup"
}
$ch30rpy = Join-Path $GameDir "script-ch30.rpy"
if (Test-Path $ch30rpy) { Remove-Item $ch30rpy -Force; Write-Host "[-] script-ch30.rpy" }

# scheduled task cleanup (ignore errors)
schtasks /Delete /TN DDLC_MonikaCam /F 2>$null | Out-Null

Write-Host ""
Write-Host "[OK] MoreMonika removed."
