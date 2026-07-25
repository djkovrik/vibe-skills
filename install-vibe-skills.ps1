[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('Junction', 'Copy')]
    [string]$Mode = 'Junction',

    [string]$Destination,

    [switch]$Force,

    [switch]$SkipValidation
)

$ErrorActionPreference = 'Stop'
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

$packageRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$manifestPath = Join-Path $packageRoot 'vibe-skills-manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Manifest not found: $manifestPath"
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$skills = @($manifest.skillDirectories)
if ($skills.Count -ne 13 -or ($skills | Where-Object { $_ -notmatch '^vibe-[a-z0-9-]+$' })) {
    throw 'Manifest must contain the exact validated list of 13 vibe-* directories.'
}

if (-not $Destination) {
    if ($env:CODEX_HOME) {
        $Destination = Join-Path $env:CODEX_HOME 'skills'
    } else {
        $Destination = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\skills'
    }
}

$destinationRoot = [System.IO.Path]::GetFullPath($Destination)
if (-not [System.IO.Path]::IsPathRooted($destinationRoot)) {
    throw "Destination must resolve to an absolute path: $destinationRoot"
}
if ($destinationRoot -eq $packageRoot -or $destinationRoot.Length -le 3) {
    throw "Unsafe destination: $destinationRoot"
}

foreach ($skill in $skills) {
    $source = [System.IO.Path]::GetFullPath((Join-Path $packageRoot $skill))
    if ((Split-Path -Parent $source) -ne $packageRoot -or -not (Test-Path -LiteralPath $source -PathType Container)) {
        throw "Invalid source skill directory: $source"
    }
}

if (-not $SkipValidation) {
    $validator = Join-Path $packageRoot 'validate-vibe-skills.ps1'
    & $validator -SkipInstallerWhatIf
    if ($LASTEXITCODE -ne 0) {
        throw "Package validation failed with exit code $LASTEXITCODE"
    }
}

function Get-EntryKind {
    param([Parameter(Mandatory)][string]$LiteralPath)
    if (-not (Test-Path -LiteralPath $LiteralPath)) {
        return 'Missing'
    }
    $item = Get-Item -LiteralPath $LiteralPath -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        if ($item.LinkType -eq 'Junction') { return 'Junction' }
        if ($item.LinkType -eq 'SymbolicLink') { return 'Symlink' }
        return 'ReparsePoint'
    }
    if ($item.PSIsContainer) { return 'Directory' }
    return 'File'
}

function Assert-NoNestedReparsePoint {
    param([Parameter(Mandatory)][string]$LiteralPath)
    $pending = [System.Collections.Generic.Stack[string]]::new()
    $pending.Push([System.IO.Path]::GetFullPath($LiteralPath))
    while ($pending.Count -gt 0) {
        $current = $pending.Pop()
        foreach ($entry in Get-ChildItem -LiteralPath $current -Force) {
            if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Refusing recursive copy through reparse point: $($entry.FullName)"
            }
            if ($entry.PSIsContainer) {
                $pending.Push($entry.FullName)
            }
        }
    }
}

$backups = [System.Collections.Generic.List[string]]::new()
$installed = [System.Collections.Generic.List[string]]::new()
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'

if (-not (Test-Path -LiteralPath $destinationRoot -PathType Container)) {
    if ($PSCmdlet.ShouldProcess($destinationRoot, 'Create skills destination')) {
        New-Item -ItemType Directory -Path $destinationRoot | Out-Null
    }
}

foreach ($skill in $skills) {
    $source = Join-Path $packageRoot $skill
    $target = Join-Path $destinationRoot $skill
    $kind = Get-EntryKind -LiteralPath $target

    if ($Mode -eq 'Junction' -and $kind -eq 'Junction') {
        $resolvedTarget = [System.IO.Path]::GetFullPath((Get-Item -LiteralPath $target -Force).Target)
        if ($resolvedTarget -eq [System.IO.Path]::GetFullPath($source)) {
            $installed.Add("$skill (existing junction)")
            continue
        }
    }

    if ($kind -in @('Directory', 'File')) {
        if ($Mode -eq 'Copy' -and -not $Force) {
            throw "Real target exists for $skill. Use -Force to back it up and resynchronize."
        }
        $backup = Join-Path $destinationRoot "$skill.backup-$timestamp"
        if (Test-Path -LiteralPath $backup) {
            throw "Backup path already exists: $backup"
        }
        if ($PSCmdlet.ShouldProcess($target, "Move existing $kind to $backup")) {
            Move-Item -LiteralPath $target -Destination $backup
            $backups.Add($backup)
        }
    } elseif ($kind -in @('Junction', 'Symlink', 'ReparsePoint')) {
        if ($PSCmdlet.ShouldProcess($target, "Remove existing $kind link")) {
            Remove-Item -LiteralPath $target -Force
        }
    } elseif ($kind -ne 'Missing') {
        throw "Unsupported target type for ${target}: $kind"
    }

    if ($Mode -eq 'Junction') {
        if ($PSCmdlet.ShouldProcess($target, "Create junction to $source")) {
            New-Item -ItemType Junction -Path $target -Target $source | Out-Null
            $installed.Add("$skill (junction)")
        }
    } else {
        Assert-NoNestedReparsePoint -LiteralPath $source
        if ($PSCmdlet.ShouldProcess($target, "Copy exact manifest skill from $source")) {
            Copy-Item -LiteralPath $source -Destination $target -Recurse
            $installed.Add("$skill (copy)")
        }
    }
}

if (-not $WhatIfPreference) {
    foreach ($skill in $skills) {
        $target = Join-Path $destinationRoot $skill
        foreach ($relative in @('SKILL.md', 'agents\openai.yaml')) {
            $required = Join-Path $target $relative
            if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
                throw "Post-install check failed: $required"
            }
        }
        $registry = [System.IO.Path]::GetFullPath((Join-Path $target $manifest.sharedRegistryRelativePath))
        if (-not (Test-Path -LiteralPath $registry -PathType Leaf)) {
            throw "Sibling source-registry invariant failed for ${skill}: $registry"
        }
    }

    Write-Host "Confirmed installation mode: $Mode"
    Write-Host "Destination: $destinationRoot"
    $installed | ForEach-Object { Write-Host "  $_" }
    if ($backups.Count) {
        Write-Host 'Backups:'
        $backups | ForEach-Object { Write-Host "  $_" }
    }
} else {
    Write-Host "WhatIf completed for $Mode -> $destinationRoot"
}
