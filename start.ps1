param([int]$Port = 8103)
$ErrorActionPreference = "Stop"
$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$PidFile = Join-Path $PSScriptRoot ".finetuning-api.pid"
if (-not (Test-Path -LiteralPath $Python)) { throw "Run .\setup.ps1 first." }
if (Test-Path -LiteralPath $PidFile) {
    $ExistingPid = [int](Get-Content -LiteralPath $PidFile -Raw)
    if (Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue) { throw "API already running." }
    Remove-Item -LiteralPath $PidFile -Force
}
$Process = Start-Process -FilePath $Python `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $Port) `
    -WorkingDirectory $PSScriptRoot `
    -RedirectStandardOutput (Join-Path $PSScriptRoot "finetuning-api.log") `
    -RedirectStandardError (Join-Path $PSScriptRoot "finetuning-api-error.log") `
    -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $Process.Id -Encoding ascii
Write-Host "Fine-tuning API started at http://127.0.0.1:$Port (PID $($Process.Id))."
