$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv")) {
    throw "Ambiente .venv nao encontrado. Execute .\scripts\setup.ps1"
}
& ".\.venv\Scripts\ruff.exe" check .
& ".\.venv\Scripts\mypy.exe" app tests
& ".\.venv\Scripts\pytest.exe"

