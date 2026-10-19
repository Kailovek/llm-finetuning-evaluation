$ErrorActionPreference = "Stop"
$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
Push-Location $PSScriptRoot
try { & $Python -m ruff check .; & $Python -m pytest } finally { Pop-Location }
