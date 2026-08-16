param(
    [Parameter(Mandatory=$true)][string]$RunDir,
    [Parameter(Mandatory=$true)][string]$Manifest,
    [string]$PythonExe,
    [switch]$Background,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$skillRoot = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $PSScriptRoot "run_pyscf_job.py"
$resolvedRunDir = [IO.Path]::GetFullPath($RunDir)
New-Item -ItemType Directory -Force -Path $resolvedRunDir | Out-Null
$manifestPath = [IO.Path]::GetFullPath($Manifest)
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "Manifest not found: $manifestPath" }
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) { throw "PySCF runner not found: $runner" }
if (-not $PythonExe) { $PythonExe = $env:PYSCF_PYTHON }
if (-not $PythonExe) {
    $pythonCommand = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($pythonCommand) { $PythonExe = $pythonCommand.Source }
}
if (-not $PythonExe -or -not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python not found. Pass -PythonExe or set PYSCF_PYTHON."
}
$record = [ordered]@{
    engine = "pyscf"; python = [IO.Path]::GetFullPath($PythonExe); runner = $runner
    run_dir = $resolvedRunDir; manifest = $manifestPath; background = [bool]$Background
    status = $(if ($DryRun) { "dry-run" } else { "starting" }); started_at = (Get-Date).ToString("o")
}
$statePath = Join-Path $resolvedRunDir "pyscf_launch_state.json"
$record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8
if ($DryRun) { $record | ConvertTo-Json -Depth 4; exit 0 }
$arguments = @(
    ('"' + $runner + '"'),
    "--manifest", ('"' + $manifestPath + '"'),
    "--run-dir", ('"' + $resolvedRunDir + '"')
)
$stdout = Join-Path $resolvedRunDir "pyscf.stdout.log"
$stderr = Join-Path $resolvedRunDir "pyscf.stderr.log"
$processArgs = @{
    FilePath = $PythonExe; ArgumentList = $arguments; WorkingDirectory = $resolvedRunDir
    RedirectStandardOutput = $stdout; RedirectStandardError = $stderr; WindowStyle = "Hidden"; PassThru = $true
}
if ($Background) {
    $process = Start-Process @processArgs
    $record.pid = $process.Id; $record.status = "running"
} else {
    $processArgs.Wait = $true
    $process = Start-Process @processArgs
    $record.pid = $process.Id; $record.exit_code = $process.ExitCode
    $record.status = $(if ($process.ExitCode -eq 0) { "process-exited" } else { "failed" })
}
$record.updated_at = (Get-Date).ToString("o")
$record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8
$record | ConvertTo-Json -Depth 4
