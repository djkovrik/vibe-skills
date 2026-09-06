[CmdletBinding()]
param([string]$OutputRoot, [int]$TimeoutSeconds = 600)
$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$python = Join-Path $packageRoot '.tooling/venv/Scripts/python.exe'
$runner = Join-Path $PSScriptRoot 'stateful_evals.py'
$arguments = @('-B', $runner, '--timeout', $TimeoutSeconds)
if ($OutputRoot) { $arguments += @('--output', $OutputRoot) }
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw "Stateful recovery agent evaluations failed: $LASTEXITCODE" }
Write-Host 'STATEFUL AGENT EVALS PASSED'
