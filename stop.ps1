$PidFile = Join-Path $PSScriptRoot ".finetuning-api.pid"
if (-not (Test-Path -LiteralPath $PidFile)) { Write-Host "API is not running."; exit 0 }
$ServerPid = [int](Get-Content -LiteralPath $PidFile -Raw)
$Process = Get-Process -Id $ServerPid -ErrorAction SilentlyContinue
if ($null -ne $Process) { Stop-Process -Id $ServerPid; $null = $Process.WaitForExit(10000) }
Remove-Item -LiteralPath $PidFile -Force
Write-Host "Fine-tuning API stopped."
