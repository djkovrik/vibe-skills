[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ProjectRoot,

    [Parameter(Mandatory)]
    [string[]]$Tasks,

    [Parameter(Mandatory)]
    [string]$LogPath,

    [string[]]$AcceptanceScenarioIds = @(),
    [string[]]$QualityGateIds = @(),
    [string]$ReceiptPath,

    [ValidateSet('targeted', 'final')]
    [string]$ReceiptKind = 'targeted',

    [string]$CoverageJson,

    [ValidateRange(1, 86400)]
    [int]$TimeoutSeconds = 1800,

    [ValidateRange(1, 86400)]
    [int]$LockTimeoutSeconds = 600
)

$ErrorActionPreference = 'Stop'
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

function ConvertTo-ProcessArgument {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '"', '\"') + '"'
}

function Get-CanonicalPathHash {
    param([Parameter(Mandatory)][string]$Path)
    $canonical = [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/').ToUpperInvariant()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($canonical)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '')
    } finally {
        $sha.Dispose()
    }
}

function Write-Receipt {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][int]$ExitCode,
        [Parameter(Mandatory)][datetime]$CompletedAt,
        [Parameter(Mandatory)][double]$DurationSeconds,
        [Parameter(Mandatory)][string[]]$Argv,
        [Parameter(Mandatory)][object]$WorkspaceFingerprint,
        [Parameter(Mandatory)][object]$StartWorkspaceFingerprint,
        [Parameter(Mandatory)][string]$ExecutionStatus,
        [Parameter(Mandatory)][datetime]$StartedAt,
        [Parameter(Mandatory)][object[]]$CoveredObligations
    )
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if (Test-Path -LiteralPath $fullPath) {
        throw "Refusing to overwrite immutable receipt: $fullPath"
    }
    $parent = Split-Path -Parent $fullPath
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        throw "Receipt directory does not exist: $parent"
    }
    $receipt = [ordered]@{
        schemaVersion = '2.0'
        receiptId = "RECEIPT-$([Guid]::NewGuid())"
        kind = $ReceiptKind
        argv = @($Argv)
        tasks = @($Tasks)
        coveredObligations = @($CoveredObligations)
        startedAt = $StartedAt.ToUniversalTime().ToString('o')
        exitCode = $ExitCode
        completedAt = $CompletedAt.ToUniversalTime().ToString('o')
        durationSeconds = [Math]::Round($DurationSeconds, 3)
        workspaceFingerprint = $WorkspaceFingerprint
        startWorkspaceFingerprint = $StartWorkspaceFingerprint
        executionStatus = $ExecutionStatus
        log = [ordered]@{
            path = $(
                $logFull = [System.IO.Path]::GetFullPath($LogPath)
                $rootPrefix = $root.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
                if ($logFull.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                    $logFull.Substring($rootPrefix.Length).Replace('\', '/')
                } else {
                    $logFull
                }
            )
            sha256 = (Get-FileHash -LiteralPath $LogPath -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
    $temporary = "$fullPath.$([Guid]::NewGuid().ToString('N')).tmp"
    try {
        [System.IO.File]::WriteAllText($temporary, ($receipt | ConvertTo-Json -Depth 12), $utf8)
        if (Test-Path -LiteralPath $fullPath) { throw "Refusing to overwrite immutable receipt: $fullPath" }
        Move-Item -LiteralPath $temporary -Destination $fullPath
    } finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
    }
}

$root = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\', '/')
if (-not [System.IO.Path]::IsPathRooted($root) -or -not (Test-Path -LiteralPath $root -PathType Container)) {
    throw "ProjectRoot must be an existing absolute directory: $root"
}
if (-not $Tasks -or @($Tasks | Where-Object { [string]::IsNullOrWhiteSpace($_) }).Count -gt 0) {
    throw 'Tasks must contain at least one non-empty Gradle task or argument.'
}
foreach ($id in $AcceptanceScenarioIds) {
    if ($id -notmatch '^AC-[0-9]{3,}$') { throw "Invalid acceptance scenario ID: $id" }
}
foreach ($id in $QualityGateIds) {
    if ($id -notmatch '^QG-[0-9]{3,}$') { throw "Invalid quality gate ID: $id" }
}

$wrapper = Join-Path $root 'gradlew.bat'
if (-not (Test-Path -LiteralPath $wrapper -PathType Leaf)) { throw "Gradle wrapper not found: $wrapper" }

$log = [System.IO.Path]::GetFullPath($LogPath)
$logParent = Split-Path -Parent $log
if (-not (Test-Path -LiteralPath $logParent -PathType Container)) { throw "Log directory does not exist: $logParent" }

$fingerprintScript = Join-Path $PSScriptRoot 'compute-workspace-fingerprint.py'
if ($ReceiptPath -and -not (Test-Path -LiteralPath $fingerprintScript -PathType Leaf)) {
    throw "Workspace fingerprint script not found: $fingerprintScript"
}
if ($ReceiptPath) {
    $receiptFull = [System.IO.Path]::GetFullPath($ReceiptPath)
    $receiptRoot = [System.IO.Path]::GetFullPath((Join-Path $root '.vibe\receipts')).TrimEnd('\') + '\'
    if (-not $receiptFull.StartsWith($receiptRoot, [System.StringComparison]::OrdinalIgnoreCase) -or [System.IO.Path]::GetExtension($receiptFull) -ne '.json') {
        throw 'ReceiptPath must be a JSON file under <project>\.vibe\receipts.'
    }
}

$mutexName = "VibeGradle_$((Get-CanonicalPathHash -Path $root).Substring(0, 32))"
$mutex = [System.Threading.Mutex]::new($false, $mutexName)
$lockAcquired = $false
$exitCode = $null
$completedAt = $null
$startedAt = $null
$beforeFingerprint = $null
$executionStatus = 'completed'
$stopwatch = [System.Diagnostics.Stopwatch]::new()
$command = ((@($wrapper) + $Tasks) | ForEach-Object { ConvertTo-ProcessArgument -Value $_ }) -join ' '

try {
    try {
        $lockAcquired = $mutex.WaitOne([TimeSpan]::FromSeconds($LockTimeoutSeconds))
    } catch [System.Threading.AbandonedMutexException] {
        $lockAcquired = $true
    }
    if (-not $lockAcquired) { throw "Timed out waiting $LockTimeoutSeconds seconds for Gradle owner lock: $mutexName" }
    if ($ReceiptPath) {
        $beforeText = & python $fingerprintScript $root
        if ($LASTEXITCODE -ne 0) { throw 'Pre-command fingerprint failed' }
        $beforeFingerprint = ($beforeText -join [Environment]::NewLine) | ConvertFrom-Json
    }

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $env:ComSpec
    $startInfo.Arguments = '/d /s /c "' + $command + '"'
    $startInfo.WorkingDirectory = $root
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $stopwatch.Start()
    $startedAt = [DateTime]::UtcNow
    if (-not $process.Start()) { throw 'Failed to start the Gradle wrapper process.' }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        try {
            $killTree = $process.GetType().GetMethod('Kill', [Type[]]@([bool]))
            if ($killTree) {
                $process.Kill($true)
            } else {
                & (Join-Path $env:SystemRoot 'System32\taskkill.exe') /PID $process.Id /T /F *> $null
            }
        } catch {
            Write-Warning "Failed to terminate timed-out Gradle process tree: $($_.Exception.Message)"
            try { $process.Kill() } catch {}
        }
        try { $process.WaitForExit() } catch {}
        $stdout = $stdoutTask.GetAwaiter().GetResult()
        $stderr = $stderrTask.GetAwaiter().GetResult()
        [System.IO.File]::WriteAllText($log, ($stdout + $stderr), $utf8)
        $executionStatus = 'interrupted'
    }
    $process.WaitForExit()
    $stopwatch.Stop()
    $exitCode = $process.ExitCode
    $completedAt = [DateTime]::UtcNow

    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    [System.IO.File]::WriteAllText($log, ($stdout + $stderr), $utf8)

    if ($ReceiptPath) {
        $fingerprintText = & python $fingerprintScript $root
        if ($LASTEXITCODE -ne 0) { throw "Workspace fingerprint failed with exit code $LASTEXITCODE" }
        $fingerprint = ($fingerprintText -join [Environment]::NewLine) | ConvertFrom-Json
        if ($executionStatus -eq 'completed' -and $beforeFingerprint.digest -ne $fingerprint.digest) { $executionStatus = 'workspace-changed' }
        if ($CoverageJson) {
            $coverage = @($CoverageJson | ConvertFrom-Json)
        } else {
            $coverage = @()
            foreach ($id in @($AcceptanceScenarioIds) + @($QualityGateIds)) {
                $coverage += [ordered]@{ obligationId = $id; surfaces = @() }
            }
        }
        Write-Receipt -Path $ReceiptPath -ExitCode $exitCode -CompletedAt $completedAt `
            -DurationSeconds $stopwatch.Elapsed.TotalSeconds -Argv (@($wrapper) + $Tasks) `
            -WorkspaceFingerprint $fingerprint -StartedAt $startedAt -CoveredObligations $coverage `
            -StartWorkspaceFingerprint $beforeFingerprint -ExecutionStatus $executionStatus
    }
} finally {
    if ($stopwatch.IsRunning) { $stopwatch.Stop() }
    if ($lockAcquired) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
    if ($process) { $process.Dispose() }
}

if ($exitCode -eq 0 -and $executionStatus -eq 'completed') {
    Write-Host "Gradle succeeded (exit 0): $($Tasks -join ', ')"
    exit 0
}
[Console]::Error.WriteLine("Gradle failed (exit $exitCode): $($Tasks -join ', ')")
Get-Content -LiteralPath $log -Encoding UTF8 -Tail 200
Select-String -LiteralPath $log -Encoding UTF8 -Pattern 'FAILED|Exception|error|Task .* failed' -Context 2,4 | Select-Object -First 40
if ($executionStatus -ne 'completed' -and $exitCode -eq 0) { exit 1 }
exit $exitCode
