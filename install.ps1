# DDLC-MoreMonika installer
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1 [-GameDir "path\to\DDLC\game"]
param(
    [string]$GameDir = ""
)
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Repo = "https://raw.githubusercontent.com/ciallo0721-cmd/DDLC-moremonika/main/mod"

# --- locate the game folder ---
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
if (-not (Test-Path (Join-Path $GameDir "..\DDLC.exe"))) { Write-Host "[X] DDLC.exe not found next to: $GameDir"; exit 1 }

Write-Host "[*] Installing into: $GameDir"

function Get-ModFile([string]$name, [string]$dest) {
    $url = "$Repo/$name"
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
    Write-Host "[+] $name"
}

# --- plain mod files ---
Get-ModFile "zz_moremonika.rpy"      (Join-Path $GameDir "zz_moremonika.rpy")
Get-ModFile "poemsentences.txt"      (Join-Path $GameDir "poemsentences.txt")
Get-ModFile "monika_cam_system.bat"  (Join-Path $GameDir "monika_cam_system.bat")

# --- patched script-ch30.rpy (camera trigger); backup original bytecode ---
$ch30rpy  = Join-Path $GameDir "script-ch30.rpy"
$ch30rpyc = Join-Path $GameDir "script-ch30.rpyc"
$bak      = Join-Path $GameDir "script-ch30.rpyc.mmbackup"
if (Test-Path $ch30rpyc) { Copy-Item $ch30rpyc $bak -Force }
Get-ModFile "script-ch30.rpy" $ch30rpy
Write-Host "[+] script-ch30.rpy (original .rpyc backed up as .mmbackup)"

# remove stale compiled mod bytecode so Ren'Py recompiles cleanly
Get-ChildItem $GameDir -Filter "zz_moremonika.rpyc" -ErrorAction SilentlyContinue | Remove-Item -Force

Write-Host ""
Write-Host "[OK] MoreMonika installed. Launch DDLC normally."
Write-Host "     - Poem minigame now picks sentences"
Write-Host "     - F9 opens the Monika observation panel"
Write-Host "     - Uninstall: run uninstall.ps1"
