$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv")) {
    throw "Ambiente .venv nao encontrado. Execute .\scripts\setup.ps1"
}
& ".\.venv\Scripts\python.exe" -m app.main run-once

