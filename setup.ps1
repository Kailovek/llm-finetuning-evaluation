$ErrorActionPreference = "Stop"
$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { python -m venv (Join-Path $PSScriptRoot ".venv") }
& $Python -m pip install -e ".[dev]"
Write-Host "Demo environment ready. Training extras and model weights were not installed."
