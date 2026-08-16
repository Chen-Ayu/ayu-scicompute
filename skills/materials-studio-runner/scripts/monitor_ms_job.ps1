param(
    [Parameter(Mandatory=$true)][string]$RunDir,
    [string]$ExpectedMarker = "MS_TASK_ALL_DONE",
    [string]$OutputJson
)

$ErrorActionPreference = "Stop"
$projectRunDir = (Resolve-Path -LiteralPath $RunDir).Path
$statePath = Join-Path $projectRunDir "ms_job_state.json"
$state = $null
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
}
$executionRunDir = $projectRunDir
if ($state -and $state.execution_run_dir -and (Test-Path -LiteralPath $state.execution_run_dir)) {
    $candidateLogs = Get-ChildItem -LiteralPath $state.execution_run_dir -Filter "*.pl.out" -ErrorAction SilentlyContinue
    $candidateResults = Join-Path $state.execution_run_dir "ms_results.csv"
    if ($candidateLogs -or (Test-Path -LiteralPath $candidateResults)) {
        $executionRunDir = $state.execution_run_dir
    }
}
$logs = Get-ChildItem -LiteralPath $executionRunDir -Filter "*.pl.out" -ErrorAction SilentlyContinue
$combined = ""
foreach ($log in $logs) {
    $combined += "`n" + (Get-Content -LiteralPath $log.FullName -Raw -ErrorAction SilentlyContinue)
}
$errorPatterns = @(
    "error condition",
    "failed",
    "cannot load",
    "license",
    "not converged"
)
$hits = @()
foreach ($pattern in $errorPatterns) {
    if ($combined -match [regex]::Escape($pattern)) { $hits += $pattern }
}
$markerFound = $combined -match [regex]::Escape($ExpectedMarker)
$processes = Get-Process -Name "MatServer","xmsengine" -ErrorAction SilentlyContinue |
    Select-Object ProcessName,Id,StartTime
$status = if ($markerFound -and $hits.Count -eq 0) {
    "completed"
} elseif ($processes) {
    "running-or-shared-engine-active"
} elseif ($logs.Count -eq 0) {
    "not-started"
} else {
    "incomplete-or-failed"
}
$record = [ordered]@{
    checked_at = (Get-Date).ToString("o")
    run_dir = $projectRunDir
    execution_run_dir = $executionRunDir
    status = $status
    expected_marker = $ExpectedMarker
    marker_found = $markerFound
    error_hits = $hits
    logs = @($logs.FullName)
    active_processes = @($processes)
}
if ($executionRunDir -ne $projectRunDir -and $status -ne "running-or-shared-engine-active") {
    Get-ChildItem -LiteralPath $executionRunDir -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $projectRunDir -Recurse -Force
    }
    $record.collected_to_project = $true
}
$json = $record | ConvertTo-Json -Depth 6
if ($OutputJson) { Set-Content -LiteralPath $OutputJson -Value $json -Encoding UTF8 }
$json
