$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

if (-not (Test-Path ".venv")) {
    throw "Ambiente .venv nao encontrado. Execute .\scripts\setup.ps1"
}

Write-Host "Iniciando worker continuo de ofertas..."
Write-Host "Terminal interativo ativo. Use Ctrl+C para parar."
& ".\.venv\Scripts\python.exe" -m app.main worker

