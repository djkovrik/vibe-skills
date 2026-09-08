[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$packageRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$runner = Join-Path $packageRoot 'vibe-developer\scripts\run-gradle.ps1'
$testBase = Join-Path $packageRoot '.tooling\run-gradle-tests'
$testRoot = Join-Path $testBase ([Guid]::NewGuid().ToString('N'))
$shell = (Get-Process -Id $PID).Path

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "ASSERTION FAILED: $Message" }
}

function Quote-Argument {
    param([string]$Value)
    return '"' + ($Value -replace '"', '\"') + '"'
}

function Start-Runner {
    param(
        [string]$Task,
        [string]$LogName,
        [string]$ReceiptName,
        [int]$TimeoutSeconds = 10,
        [int]$LockTimeoutSeconds = 10
    )
    $arguments = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Quote-Argument $runner),
        '-ProjectRoot', (Quote-Argument $testRoot),
        '-Tasks', $Task,
        '-ReceiptKind', 'integration',
        '-LogPath', (Quote-Argument (Join-Path $testRoot ".vibe\$LogName")),
        '-TimeoutSeconds', $TimeoutSeconds,
        '-LockTimeoutSeconds', $LockTimeoutSeconds
    )
    if ($ReceiptName) {
        $arguments += @(
            '-ReceiptPath', (Quote-Argument (Join-Path $testRoot ".vibe\receipts\$ReceiptName")),
            '-AcceptanceScenarioIds', 'AC-001',
            '-QualityGateIds', 'QG-001'
        )
    }
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $shell
    $startInfo.Arguments = $arguments -join ' '
    $startInfo.WorkingDirectory = $testRoot
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) { throw 'failed to start isolated runner process' }
    return $process
}

New-Item -ItemType Directory -Path (Join-Path $testRoot '.vibe\receipts') -Force | Out-Null
try {
    $batch = @'
@echo off
if "%1"=="slow" (
  echo slow-start>>order.txt
  powershell -NoProfile -Command "Start-Sleep -Milliseconds 1200"
  echo slow-end>>order.txt
  exit /b 0
)
if "%1"=="fast" (
  echo fast>>order.txt
  exit /b 0
)
if "%1"=="fail" (
  echo deliberate failure 1>&2
  exit /b 7
)
if "%1"=="hang" (
  powershell -NoProfile -Command "Start-Sleep -Seconds 5"
  exit /b 0
)
exit /b 0
'@
    [System.IO.File]::WriteAllText((Join-Path $testRoot 'gradlew.bat'), $batch, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText((Join-Path $testRoot '.gitignore'), ".vibe/`n", [System.Text.UTF8Encoding]::new($false))
    & git -C $testRoot init -q
    if ($LASTEXITCODE -ne 0) { throw 'git init failed' }

    $slow = Start-Runner -Task 'slow' -LogName 'slow.log' -ReceiptName ''
    Start-Sleep -Milliseconds 150
    $fast = Start-Runner -Task 'fast' -LogName 'fast.log' -ReceiptName ''
    $slow.WaitForExit()
    $fast.WaitForExit()
    $slow.Refresh()
    $fast.Refresh()
    Assert-True ($slow.HasExited -and $fast.HasExited) 'serialized runner processes must finish'
    Assert-True ($slow.ExitCode -eq 0) "slow runner exit was $($slow.ExitCode)"
    Assert-True ($fast.ExitCode -eq 0) "fast runner exit was $($fast.ExitCode)"
    $order = @(Get-Content -LiteralPath (Join-Path $testRoot 'order.txt'))
    Assert-True (($order -join ',') -eq 'slow-start,slow-end,fast') 'named mutex must serialize one canonical project path'

    $failed = Start-Runner -Task 'fail' -LogName 'fail.log' -ReceiptName 'fail-receipt.json'
    $failed.WaitForExit()
    $failed.Refresh()
    $failureReceipt = Get-Content -LiteralPath (Join-Path $testRoot '.vibe\receipts\fail-receipt.json') -Raw | ConvertFrom-Json
    Assert-True ($failureReceipt.exitCode -eq 7) 'completed failure receipt must keep real exit code'
    Assert-True ($failureReceipt.schemaVersion -eq '2.0') 'receipt must use Protocol 2.0'
    Assert-True ($failureReceipt.kind -eq 'integration') 'receipt kind must be explicit'
    Assert-True ('AC-001' -in @($failureReceipt.coveredObligations.obligationId)) 'receipt must name assigned AC'
    Assert-True ($failureReceipt.log.sha256 -match '^[a-f0-9]{64}$') 'receipt must hash its log'
    $receiptBytes = [System.IO.File]::ReadAllBytes((Join-Path $testRoot '.vibe\receipts\fail-receipt.json'))
    $overwrite = Start-Runner -Task 'fail' -LogName 'fail-again.log' -ReceiptName 'fail-receipt.json'
    $overwrite.WaitForExit(); $overwrite.Refresh()
    Assert-True ($overwrite.ExitCode -ne 0) 'runner must refuse to overwrite an immutable receipt'
    Assert-True ([Convert]::ToBase64String($receiptBytes) -eq [Convert]::ToBase64String([System.IO.File]::ReadAllBytes((Join-Path $testRoot '.vibe\receipts\fail-receipt.json')))) 'refused overwrite must preserve receipt bytes'

    $timedOut = Start-Runner -Task 'hang' -LogName 'timeout.log' -ReceiptName 'timeout-receipt.json' -TimeoutSeconds 1
    $timedOut.WaitForExit()
    $timedOut.Refresh()
    Assert-True ($timedOut.HasExited) 'timed-out runner process must finish'
    $timeoutReceipt = Get-Content -LiteralPath (Join-Path $testRoot '.vibe\receipts\timeout-receipt.json') -Raw | ConvertFrom-Json
    Assert-True ($timeoutReceipt.executionStatus -eq 'interrupted') 'timeout must leave durable interrupted evidence'
    Assert-True ($timedOut.ExitCode -ne 0) 'timeout must fail the runner'
    Assert-True ($failureReceipt.startWorkspaceFingerprint.digest -eq $failureReceipt.workspaceFingerprint.digest) 'completed unchanged check must carry both fingerprints'

    $afterTimeout = Start-Runner -Task 'fast' -LogName 'after-timeout.log' -ReceiptName '' -LockTimeoutSeconds 2
    $afterTimeout.WaitForExit()
    $afterTimeout.Refresh()
    Assert-True ($afterTimeout.HasExited) 'mutex must be released after timeout exception'
    $finalOrder = @(Get-Content -LiteralPath (Join-Path $testRoot 'order.txt'))
    Assert-True ($finalOrder[-1] -eq 'fast') 'a new run must acquire the mutex after timeout cleanup'

    Write-Host 'run-gradle tests passed'
} finally {
    $resolvedBase = [System.IO.Path]::GetFullPath($testBase)
    $resolvedTest = [System.IO.Path]::GetFullPath($testRoot)
    if ($resolvedTest.StartsWith($resolvedBase + [System.IO.Path]::DirectorySeparatorChar) -and (Test-Path -LiteralPath $resolvedTest)) {
        Remove-Item -LiteralPath $resolvedTest -Recurse -Force
    }
}
