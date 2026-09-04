[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$packageRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$caseRoot = Join-Path $packageRoot 'vibe-developer\assets\behavioral-evals'
$schema = Join-Path $packageRoot 'vibe-developer\assets\agent-eval-result.schema.json'
$outputRoot = Join-Path $packageRoot '.tooling\agent-evals'
$failures = [System.Collections.Generic.List[string]]::new()
$codex = Get-Command codex -ErrorAction Stop
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
$tempBase = Join-Path ([System.IO.Path]::GetTempPath()) 'vibe-agent-evals'
New-Item -ItemType Directory -Path $tempBase -Force | Out-Null

foreach ($case in Get-ChildItem -LiteralPath $caseRoot -Directory | Sort-Object Name) {
    $request = Join-Path $case.FullName 'request.md'
    $oracle = Join-Path $case.FullName 'expected.json'
    if (-not (Test-Path -LiteralPath $request -PathType Leaf) -or -not (Test-Path -LiteralPath $oracle -PathType Leaf)) {
        $failures.Add("$($case.Name): request or oracle missing")
        continue
    }
    $caseOutput = Join-Path $outputRoot $case.Name
    New-Item -ItemType Directory -Path $caseOutput -Force | Out-Null
    $jsonl = Join-Path $caseOutput 'events.jsonl'
    $final = Join-Path $caseOutput 'result.json'
    $grader = Join-Path $caseOutput 'grader-report.json'
    $workspace = Join-Path $tempBase ([Guid]::NewGuid().ToString('N'))
    $archive = "$workspace.zip"
    & git -C $packageRoot archive --format=zip --output=$archive HEAD
    if ($LASTEXITCODE -ne 0) { $failures.Add("$($case.Name): git archive failed"); continue }
    New-Item -ItemType Directory -Path $workspace | Out-Null
    Expand-Archive -LiteralPath $archive -DestinationPath $workspace
    $prompt = Get-Content -LiteralPath $request -Raw -Encoding UTF8
    $prompt += "`n`nUse `$vibe-developer from .\vibe-developer\SKILL.md. Return only the requested structured result."

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $codex.Source
    $startInfo.Arguments = 'exec --ephemeral --json --output-schema "' + $schema + '" --output-last-message "' + $final + '" -C "' + $workspace + '" -'
    $startInfo.WorkingDirectory = $workspace
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new(); $process.StartInfo = $startInfo
    if (-not $process.Start()) { $failures.Add("$($case.Name): codex did not start"); continue }
    $process.StandardInput.Write($prompt); $process.StandardInput.Close()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync(); $stderrTask = $process.StandardError.ReadToEndAsync(); $process.WaitForExit()
    [System.IO.File]::WriteAllText($jsonl, $stdoutTask.GetAwaiter().GetResult(), [System.Text.UTF8Encoding]::new($false))
    $stderr = $stderrTask.GetAwaiter().GetResult()
    if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $final)) {
        $failures.Add("$($case.Name): codex exit $($process.ExitCode): $stderr")
        continue
    }
    $actual = Get-Content -LiteralPath $final -Raw -Encoding UTF8 | ConvertFrom-Json
    $expected = Get-Content -LiteralPath $oracle -Raw -Encoding UTF8 | ConvertFrom-Json
    $issues = @()
    if ($actual.verdict -ne $expected.verdict) { $issues += "verdict expected $($expected.verdict), found $($actual.verdict)" }
    if ($actual.completionClaim -ne $expected.completionClaim) { $issues += "completionClaim mismatch" }
    foreach ($term in @($expected.requiredActionTerms)) {
        if ((@($actual.actions) -join ' ') -notmatch [regex]::Escape($term)) { $issues += "actions missing term: $term" }
    }
    $report = [ordered]@{ case = $case.Name; passed = ($issues.Count -eq 0); issues = $issues; result = $actual }
    [System.IO.File]::WriteAllText($grader, (($report | ConvertTo-Json -Depth 20) + "`n"), [System.Text.UTF8Encoding]::new($false))
    if ($issues) { $failures.Add("$($case.Name): $($issues -join '; ')") }
    $resolvedTemp = [System.IO.Path]::GetFullPath($tempBase).TrimEnd('\') + '\'
    $resolvedWorkspace = [System.IO.Path]::GetFullPath($workspace)
    if ($resolvedWorkspace.StartsWith($resolvedTemp) -and (Test-Path -LiteralPath $resolvedWorkspace)) { Remove-Item -LiteralPath $resolvedWorkspace -Recurse -Force }
    if (Test-Path -LiteralPath $archive) { Remove-Item -LiteralPath $archive -Force }
}

if ($failures) {
    foreach ($failure in $failures) { Write-Host "ERROR: $failure" -ForegroundColor Red }
    Write-Host "AGENT EVALS FAILED: $($failures.Count)" -ForegroundColor Red
    exit 1
}
Write-Host 'AGENT EVALS PASSED' -ForegroundColor Green
exit 0
