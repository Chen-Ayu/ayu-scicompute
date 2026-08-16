param(
    [Parameter(Mandatory=$true)][string]$RunDir,
    [Parameter(Mandatory=$true)][string]$InputFile,
    [string]$OrcaExe,
    [switch]$Background,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$requestedOrcaExe = $OrcaExe
if (-not $requestedOrcaExe) { $requestedOrcaExe = $env:ORCA_EXE }
if (-not $requestedOrcaExe) {
    $command = Get-Command "orca.exe" -ErrorAction SilentlyContinue
    if ($command) { $requestedOrcaExe = $command.Source }
}
if (-not $requestedOrcaExe) {
    throw "ORCA executable not found. Pass -OrcaExe or set ORCA_EXE."
}
$OrcaExe = [IO.Path]::GetFullPath($requestedOrcaExe)
$resolvedRunDir = (Resolve-Path -LiteralPath $RunDir).Path
if (-not (Test-Path -LiteralPath $OrcaExe)) { throw "ORCA executable not found: $OrcaExe" }
if ($InputFile -ne [IO.Path]::GetFileName($InputFile) -or $InputFile -notmatch '^[A-Za-z0-9][A-Za-z0-9._ -]*\.inp$') {
    throw "InputFile must be a safe .inp leaf filename inside RunDir."
}
$inputPath = Join-Path $resolvedRunDir $InputFile
if (-not (Test-Path -LiteralPath $inputPath -PathType Leaf)) { throw "ORCA input not found: $inputPath" }
$baseName = [IO.Path]::GetFileNameWithoutExtension($InputFile)
$outputPath = Join-Path $resolvedRunDir ($baseName + ".out")
$errorPath = Join-Path $resolvedRunDir ($baseName + ".stderr.log")
$statePath = Join-Path $resolvedRunDir "orca_job_state.json"
$record = [ordered]@{
    engine = "orca"
    executable = $OrcaExe
    run_dir = $resolvedRunDir
    input = $InputFile
    output = $outputPath
    background = [bool]$Background
    status = $(if ($DryRun) { "dry-run" } else { "starting" })
    started_at = (Get-Date).ToString("o")
}
$record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8
if ($DryRun) {
    $record | ConvertTo-Json -Depth 4
    exit 0
}

$orcaDir = Split-Path -Parent $OrcaExe
$previousPath = $env:PATH
$env:PATH = $orcaDir + ";" + $env:PATH
try {
    if ($Background) {
        $process = Start-Process -FilePath $OrcaExe `
            -ArgumentList @('"' + $InputFile + '"') `
            -WorkingDirectory $resolvedRunDir `
            -RedirectStandardOutput $outputPath `
            -RedirectStandardError $errorPath `
            -WindowStyle Hidden `
            -PassThru
        $record.pid = $process.Id
        $record.status = "running"
    } else {
        $process = Start-Process -FilePath $OrcaExe `
            -ArgumentList @('"' + $InputFile + '"') `
            -WorkingDirectory $resolvedRunDir `
            -RedirectStandardOutput $outputPath `
            -RedirectStandardError $errorPath `
            -WindowStyle Hidden `
            -Wait `
            -PassThru
        $record.pid = $process.Id
        $record.exit_code = $process.ExitCode
        $record.status = $(if ($process.ExitCode -eq 0) { "process-exited" } else { "failed" })
    }
} finally {
    $env:PATH = $previousPath
    $record.updated_at = (Get-Date).ToString("o")
    $record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8
}
$record | ConvertTo-Json -Depth 4
