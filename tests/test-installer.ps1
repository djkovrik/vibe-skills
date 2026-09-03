[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$installer = Join-Path $root 'install-vibe-skills.ps1'
$manifest = Get-Content -LiteralPath (Join-Path $root 'vibe-skills-manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$scratchBase = Join-Path $root '.tooling\installer-tests'
$scratch = Join-Path $scratchBase ([Guid]::NewGuid().ToString('N'))
$destination = Join-Path $scratch 'skills'

function Assert-Installed {
    param([string]$ExpectedKind)
    foreach ($skill in @($manifest.skillDirectories)) {
        $target = Join-Path $destination $skill
        if (-not (Test-Path -LiteralPath (Join-Path $target 'SKILL.md') -PathType Leaf)) {
            throw "Missing installed SKILL.md for $skill"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $target 'agents\openai.yaml') -PathType Leaf)) {
            throw "Missing installed openai.yaml for $skill"
        }
        $item = Get-Item -LiteralPath $target -Force
        $actualKind = if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $item.LinkType } else { 'Directory' }
        if ($actualKind -ne $ExpectedKind) { throw "$skill installed as $actualKind instead of $ExpectedKind" }
    }
}

New-Item -ItemType Directory -Path $scratch -Force | Out-Null
try {
    & $installer -Mode Copy -Destination $destination -SkipValidation
    Assert-Installed -ExpectedKind 'Directory'
    Remove-Item -LiteralPath $destination -Recurse -Force

    & $installer -Mode Junction -Destination $destination -SkipValidation
    Assert-Installed -ExpectedKind 'Junction'
    Write-Host "installer Copy/Junction tests passed for $(@($manifest.skillDirectories).Count) manifest skills"
} finally {
    $resolvedBase = [System.IO.Path]::GetFullPath($scratchBase)
    $resolvedScratch = [System.IO.Path]::GetFullPath($scratch)
    if ($resolvedScratch.StartsWith($resolvedBase + [System.IO.Path]::DirectorySeparatorChar) -and (Test-Path -LiteralPath $resolvedScratch)) {
        foreach ($skill in @($manifest.skillDirectories)) {
            $target = Join-Path $destination $skill
            if (Test-Path -LiteralPath $target) {
                $item = Get-Item -LiteralPath $target -Force
                if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    [System.IO.Directory]::Delete($target)
                }
            }
        }
        Remove-Item -LiteralPath $resolvedScratch -Recurse -Force
    }
}
