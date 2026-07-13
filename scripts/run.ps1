$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv")) {
    throw "Ambiente .venv nao encontrado. Execute .\scripts\setup.ps1"
}
Write-Host "API: http://127.0.0.1:8000"
Write-Host "Painel: http://127.0.0.1:8000/admin"
& ".\.venv\Scripts\python.exe" -m app.main serve
