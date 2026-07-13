$ErrorActionPreference = "Stop"
$StartupDir = [Environment]::GetFolderPath([Environment+SpecialFolder]::Startup)
$CmdPath = Join-Path $StartupDir "OfertaTelegramWorker.cmd"

if (Test-Path -LiteralPath $CmdPath) {
    Remove-Item -LiteralPath $CmdPath -Force
    Write-Host "Inicializacao removida:"
    Write-Host $CmdPath
} else {
    Write-Host "Inicializacao nao estava instalada."
}

