[CmdletBinding()]
param(
    [string]$RepositoryPath = 'D:\Sources\Android\DishReady',
    [string]$OutputRoot,
    [string]$AuditResultsRoot
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $RepositoryPath -PathType Container)) {
    throw "DishReady repository does not exist: $RepositoryPath"
}

$resolvedRepository = (Resolve-Path -LiteralPath $RepositoryPath).Path
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("vibe-dishready-regression-" + [guid]::NewGuid().ToString('N'))
}

$resolvedOutputParent = Split-Path -Parent ([System.IO.Path]::GetFullPath($OutputRoot))
if (-not (Test-Path -LiteralPath $resolvedOutputParent -PathType Container)) {
    New-Item -ItemType Directory -Path $resolvedOutputParent | Out-Null
}
New-Item -ItemType Directory -Path $OutputRoot -ErrorAction Stop | Out-Null
$resolvedOutput = (Resolve-Path -LiteralPath $OutputRoot).Path

$cases = @(
    [ordered]@{
        commit = 'f073da6'
        expectedVerdict = 'GAPS'
        extractPath = $null
        requiredGapPatterns = @(
            'preset[^\r\n]*rename|rename[^\r\n]*preset',
            'preset[^\r\n]*update|update[^\r\n]*preset',
            'history[^\r\n]*reuse|reuse[^\r\n]*history',
            'history[^\r\n]*delete|delete[^\r\n]*history',
            'draft[^\r\n]*resume|resume[^\r\n]*draft',
            'draft[^\r\n]*discard|discard[^\r\n]*draft',
            'direct[^\r\n]*quantity|quantity[^\r\n]*direct',
            'direct[^\r\n]*remove|remove[^\r\n]*direct',
            'granular[^\r\n]*draft[^\r\n]*delet|draft[^\r\n]*granular[^\r\n]*delet'
        )
    },
    [ordered]@{
        commit = 'ae94900'
        expectedVerdict = 'INDEPENDENT'
        extractPath = $null
        requiredGapPatterns = @()
    }
)

foreach ($case in $cases) {
    & git -C $resolvedRepository cat-file -e ($case.commit + '^{commit}')
    if ($LASTEXITCODE -ne 0) {
        throw "Commit $($case.commit) is unavailable in $resolvedRepository"
    }

    $archivePath = Join-Path $resolvedOutput ($case.commit + '.zip')
    $extractPath = Join-Path $resolvedOutput $case.commit
    & git -C $resolvedRepository archive --format=zip --output=$archivePath $case.commit
    if ($LASTEXITCODE -ne 0) {
        throw "git archive failed for $($case.commit)"
    }
    Expand-Archive -LiteralPath $archivePath -DestinationPath $extractPath
    $case.extractPath = $extractPath
}

$expectationsPath = Join-Path $resolvedOutput 'regression-expectations.json'
$cases | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $expectationsPath -Encoding utf8

if (-not [string]::IsNullOrWhiteSpace($AuditResultsRoot)) {
    $resolvedResults = (Resolve-Path -LiteralPath $AuditResultsRoot).Path
    foreach ($case in $cases) {
        $auditPath = Join-Path $resolvedResults (Join-Path $case.commit '.vibe\closure-audit.json')
        if (-not (Test-Path -LiteralPath $auditPath -PathType Leaf)) {
            throw "Missing fresh audit result for $($case.commit): $auditPath"
        }
        $auditText = Get-Content -Raw -LiteralPath $auditPath
        $audit = $auditText | ConvertFrom-Json
        if ($case.expectedVerdict -eq 'GAPS' -and $audit.verdict -ne 'GAPS') {
            throw "$($case.commit) must produce GAPS, got $($audit.verdict)"
        }
        if ($case.expectedVerdict -eq 'INDEPENDENT' -and $audit.verdict -notin @('PASS', 'GAPS', 'BLOCKED')) {
            throw "$($case.commit) has invalid independent verdict: $($audit.verdict)"
        }
        if ([string]::IsNullOrWhiteSpace([string]$audit.appSpecFingerprint.digest) -or [string]::IsNullOrWhiteSpace([string]$audit.workspaceFingerprint.digest)) {
            throw "$($case.commit) audit is missing fingerprints"
        }
        if ($audit.schemaVersion -ne '2.0' -or $audit.auditorContext.implementationContextAvailable -ne $false -or [string]::IsNullOrWhiteSpace([string]$audit.auditRequest.sha256)) {
            throw "$($case.commit) audit is not request-bound Protocol 2.0 fresh-context evidence"
        }
        $searchableAudit = $auditText -replace '\s+', ' '
        foreach ($pattern in $case.requiredGapPatterns) {
            if ($searchableAudit -notmatch $pattern) {
                throw "$($case.commit) audit did not identify required gap pattern: $pattern"
            }
        }
    }
    Write-Output "Verified DishReady regression audits under $resolvedResults"
}

[pscustomobject]@{
    outputRoot = $resolvedOutput
    expectations = $expectationsPath
    f073da6 = (Join-Path $resolvedOutput 'f073da6')
    ae94900 = (Join-Path $resolvedOutput 'ae94900')
} | ConvertTo-Json
