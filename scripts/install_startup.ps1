$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$StartupDir = [Environment]::GetFolderPath([Environment+SpecialFolder]::Startup)
$CmdPath = Join-Path $StartupDir "OfertaTelegramWorker.cmd"
$RunWorker = Join-Path $ProjectRoot "scripts\run_worker.ps1"

$Content = @"
@echo off
cd /d "$ProjectRoot"
powershell.exe -NoExit -ExecutionPolicy Bypass -File "$RunWorker"
"@

Set-Content -LiteralPath $CmdPath -Value $Content -Encoding ASCII

Write-Host "Inicializacao instalada:"
Write-Host $CmdPath
Write-Host "Na proxima entrada do Windows, um terminal abrira rodando o worker."

