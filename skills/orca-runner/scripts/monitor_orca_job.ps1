param(
    [Parameter(Mandatory=$true)][string]$RunDir,
    [string]$OutputFile,
    [string]$OutputJson
)

$ErrorActionPreference = "Stop"
$resolvedRunDir = (Resolve-Path -LiteralPath $RunDir).Path
$statePath = Join-Path $resolvedRunDir "orca_job_state.json"
$state = $null
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
}
if (-not $OutputFile) {
    if ($state -and $state.output) {
        $OutputFile = $state.output
    } else {
        $candidate = Get-ChildItem -LiteralPath $resolvedRunDir -Filter "*.out" |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($candidate) { $OutputFile = $candidate.FullName }
    }
}
$text = ""
if ($OutputFile -and (Test-Path -LiteralPath $OutputFile)) {
    $text = Get-Content -LiteralPath $OutputFile -Raw -ErrorAction SilentlyContinue
}
$normal = $text -match "ORCA TERMINATED NORMALLY"
$errors = @()
foreach ($pattern in @("ORCA finished by error termination", "SCF NOT CONVERGED", "aborting the run")) {
    if ($text -match [regex]::Escape($pattern)) { $errors += $pattern }
}
$active = $false
if ($state -and $state.pid) {
    $active = [bool](Get-Process -Id $state.pid -ErrorAction SilentlyContinue)
}
$status = if ($normal -and $errors.Count -eq 0) {
    "completed"
} elseif ($active) {
    "running"
} elseif ($text) {
    "incomplete-or-failed"
} else {
    "not-started"
}
$record = [ordered]@{
    checked_at = (Get-Date).ToString("o")
    run_dir = $resolvedRunDir
    output = $OutputFile
    status = $status
    process_active = $active
    normal_termination = $normal
    error_hits = $errors
}
$json = $record | ConvertTo-Json -Depth 5
if ($OutputJson) { Set-Content -LiteralPath $OutputJson -Value $json -Encoding UTF8 }
$json
