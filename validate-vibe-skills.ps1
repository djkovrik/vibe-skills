[CmdletBinding()]
param(
    [switch]$SkipInstallerWhatIf
)

$ErrorActionPreference = 'Continue'
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
$root = [System.IO.Path]::GetFullPath($PSScriptRoot)
$failures = [System.Collections.Generic.List[string]]::new()

function Add-Failure {
    param([string]$Message)
    $script:failures.Add($Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
}

$manifestPath = Join-Path $root 'vibe-skills-manifest.json'
try {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Add-Failure "Invalid manifest: $($_.Exception.Message)"
    exit 1
}

$expected = @($manifest.skillDirectories)
$actual = @(Get-ChildItem -LiteralPath $root -Directory -Force |
    Where-Object Name -Like 'vibe-*' |
    Select-Object -ExpandProperty Name)
if ($expected.Count -ne 13) {
    Add-Failure "Manifest lists $($expected.Count) skills instead of 13"
}
$missing = @($expected | Where-Object { $_ -notin $actual })
$extra = @($actual | Where-Object { $_ -notin $expected })
if ($missing) { Add-Failure "Missing skill directories: $($missing -join ', ')" }
if ($extra) { Add-Failure "Unexpected skill directories: $($extra -join ', ')" }

$privacyContractFiles = Get-ChildItem -LiteralPath $root -File -Recurse -Force |
    Where-Object {
        $_.Extension -in @('.md', '.json', '.py', '.ps1', '.yaml', '.yml') -and
        $_.FullName -notlike "$root\.git\*" -and
        $_.FullName -notlike "$root\.tooling\*"
    }
foreach ($privacyContractFile in $privacyContractFiles) {
    $privacyContractText = Get-Content -LiteralPath $privacyContractFile.FullName -Raw -Encoding UTF8
    if ($privacyContractText -match ('(?i)\bU' + 'MP\b')) {
        Add-Failure "Unsupported consent SDK reference in $($privacyContractFile.FullName)"
    }
}

$quickValidate = 'C:\Users\Sergey\.codex\skills\.system\skill-creator\scripts\quick_validate.py'
$localPython = Join-Path $root '.tooling\venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $localPython -PathType Leaf)) {
    Add-Failure "Local validation Python is missing: $localPython"
}
if (-not (Test-Path -LiteralPath $quickValidate -PathType Leaf)) {
    Add-Failure "Official quick_validate.py is missing: $quickValidate"
}

foreach ($skill in $expected) {
    $skillRoot = Join-Path $root $skill
    $skillMd = Join-Path $skillRoot 'SKILL.md'
    $openai = Join-Path $skillRoot 'agents\openai.yaml'
    if (-not (Test-Path -LiteralPath $skillMd -PathType Leaf)) {
        Add-Failure "${skill}: SKILL.md missing"
        continue
    }
    if (-not (Test-Path -LiteralPath $openai -PathType Leaf)) {
        Add-Failure "${skill}: agents/openai.yaml missing"
    }

    $content = Get-Content -LiteralPath $skillMd -Raw -Encoding UTF8
    $textFiles = Get-ChildItem -LiteralPath $skillRoot -File -Recurse |
        Where-Object Extension -In @('.md', '.json', '.py', '.ps1', '.yaml', '.yml')
    foreach ($textFile in $textFiles) {
        $text = Get-Content -LiteralPath $textFile.FullName -Raw -Encoding UTF8
        if ($text -match '(?im)\bTODO\b|\bTBD\b|\[TODO') {
            Add-Failure "${skill}: unfilled placeholder in $($textFile.FullName)"
        }
    }
    if ($content -notmatch '(?s)^---\r?\nname:\s*([a-z0-9-]+)\r?\ndescription:\s*(.+?)\r?\n---') {
        Add-Failure "${skill}: invalid or non-minimal frontmatter"
    } else {
        if ($Matches[1] -ne $skill) { Add-Failure "${skill}: name does not match directory" }
        if ($Matches[2].Trim().Length -lt 80) { Add-Failure "${skill}: description is not meaningful" }
    }

    foreach ($markdownFile in ($textFiles | Where-Object Extension -EQ '.md')) {
        $markdown = Get-Content -LiteralPath $markdownFile.FullName -Raw -Encoding UTF8
        foreach ($match in [regex]::Matches($markdown, '\]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)')) {
            $relative = [Uri]::UnescapeDataString($match.Groups[1].Value)
            $linked = [System.IO.Path]::GetFullPath((Join-Path $markdownFile.DirectoryName $relative))
            if (-not (Test-Path -LiteralPath $linked)) {
                Add-Failure "${skill}: broken relative link $relative in $($markdownFile.FullName)"
            }
        }
    }

    if (Test-Path -LiteralPath $openai -PathType Leaf) {
        $yaml = Get-Content -LiteralPath $openai -Raw -Encoding UTF8
        foreach ($field in @('display_name:', 'short_description:', 'default_prompt:')) {
            if ($yaml -notmatch [regex]::Escape($field)) { Add-Failure "${skill}: openai.yaml missing $field" }
        }
        if ($yaml -notmatch [regex]::Escape("`$$skill")) {
            Add-Failure "${skill}: default_prompt must mention `$$skill"
        }
    }

    $registry = [System.IO.Path]::GetFullPath((Join-Path $skillRoot $manifest.sharedRegistryRelativePath))
    if (-not (Test-Path -LiteralPath $registry -PathType Leaf)) {
        Add-Failure "${skill}: sibling source-registry link invariant failed"
    }

    if ((Test-Path -LiteralPath $localPython) -and (Test-Path -LiteralPath $quickValidate)) {
        & $localPython $quickValidate $skillRoot
        if ($LASTEXITCODE -ne 0) {
            Add-Failure "${skill}: official quick_validate.py failed with $LASTEXITCODE"
        }
    }
}

$appValidator = Join-Path $root 'vibe-developer\scripts\validate-app-spec.py'
$validFixture = Join-Path $root 'vibe-developer\assets\app-spec-template\app-spec'
$invalidMajor = Join-Path $root 'vibe-developer\assets\app-spec-fixtures\invalid-major'
$invalidLinks = Join-Path $root 'vibe-developer\assets\app-spec-fixtures\invalid-links'
$invalidUiContract = Join-Path $root 'vibe-developer\assets\app-spec-fixtures\invalid-ui-contract'
if ((Test-Path -LiteralPath $localPython) -and (Test-Path -LiteralPath $appValidator)) {
    & $localPython $appValidator $validFixture
    if ($LASTEXITCODE -ne 0) { Add-Failure 'Bundled valid AppSpec was rejected' }
    foreach ($invalid in @($invalidMajor, $invalidLinks, $invalidUiContract)) {
        & $localPython $appValidator $invalid
        if ($LASTEXITCODE -eq 0) { Add-Failure "Bundled invalid AppSpec was accepted: $invalid" }
    }
}

if (-not $SkipInstallerWhatIf) {
    $installer = Join-Path $root 'install-vibe-skills.ps1'
    $whatIfDestination = Join-Path $root '.tooling\whatif-skills'
    & $installer -Mode Copy -Destination $whatIfDestination -WhatIf -SkipValidation
    if (-not $?) { Add-Failure 'Installer -WhatIf failed' }
}

if ($failures.Count) {
    Write-Host "VALIDATION FAILED: $($failures.Count) issue(s)" -ForegroundColor Red
    exit 1
}
Write-Host "VALIDATION PASSED: $($expected.Count) skills" -ForegroundColor Green
exit 0
