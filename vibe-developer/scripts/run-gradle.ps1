[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ProjectRoot,

    [Parameter(Mandatory)]
    [string[]]$Tasks,

    [Parameter(Mandatory)]
    [string]$LogPath
)

$ErrorActionPreference = 'Stop'
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

$root = [System.IO.Path]::GetFullPath($ProjectRoot)
if (-not [System.IO.Path]::IsPathRooted($root) -or -not (Test-Path -LiteralPath $root -PathType Container)) {
    throw "ProjectRoot must be an existing absolute directory: $root"
}

$wrapper = Join-Path $root 'gradlew.bat'
if (-not (Test-Path -LiteralPath $wrapper -PathType Leaf)) {
    throw "Gradle wrapper not found: $wrapper"
}

$log = [System.IO.Path]::GetFullPath($LogPath)
$logParent = Split-Path -Parent $log
if (-not (Test-Path -LiteralPath $logParent -PathType Container)) {
    throw "Log directory does not exist: $logParent"
}

Push-Location -LiteralPath $root
try {
    & $wrapper -q @Tasks *> $log
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($exitCode -eq 0) {
    Write-Host "Gradle succeeded (exit 0): $($Tasks -join ', ')"
    exit 0
}

Write-Error "Gradle failed (exit $exitCode): $($Tasks -join ', ')"
Get-Content -LiteralPath $log -Encoding UTF8 -Tail 200
Select-String -LiteralPath $log -Encoding UTF8 -Pattern 'FAILED|Exception|error|Task .* failed' -Context 2,4 |
    Select-Object -First 40
exit $exitCode

