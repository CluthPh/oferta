$ErrorActionPreference = "Stop"

Write-Host "Verificando Python..."
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "Python nao encontrado. Instale Python 3.12 ou superior e marque Add to PATH."
}

$versionOutput = python --version
Write-Host $versionOutput

if (-not (Test-Path ".venv")) {
    Write-Host "Criando ambiente virtual..."
    python -m venv .venv
}

Write-Host "Instalando dependencias..."
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\pip.exe" install -r requirements-dev.txt

Write-Host "Instalando Chromium do Playwright..."
& ".\.venv\Scripts\python.exe" -m playwright install chromium

New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Criado .env a partir de .env.example"
}

if (-not (Test-Path "data\niches.yml")) {
    Copy-Item "data\niches.example.yml" "data\niches.yml"
    Write-Host "Criado data\niches.yml a partir do exemplo"
}

Write-Host "Setup concluido."
Write-Host "Edite .env e data\niches.yml antes de publicar de verdade."
Write-Host "Dry run: .\scripts\run_once.ps1"
Write-Host "Worker continuo: .\scripts\run_worker.ps1"
Write-Host "Iniciar com o Windows: .\scripts\install_startup.ps1"
