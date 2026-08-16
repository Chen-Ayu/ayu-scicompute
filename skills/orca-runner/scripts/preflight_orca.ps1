param(
    [string]$OrcaExe,
    [string]$OutputJson
)

$ErrorActionPreference = "Stop"
if (-not $OrcaExe) { $OrcaExe = $env:ORCA_EXE }
if (-not $OrcaExe) {
    $command = Get-Command "orca.exe" -ErrorAction SilentlyContinue
    if ($command) { $OrcaExe = $command.Source }
}
if (-not $OrcaExe) {
    throw "ORCA executable not found. Pass -OrcaExe or set ORCA_EXE."
}
$OrcaExe = [IO.Path]::GetFullPath($OrcaExe)
$orcaDir = Split-Path -Parent $OrcaExe
$helpers = @("orca_plot.exe", "orca_2mkl.exe", "orca_chelpg.exe", "orca_vpot.exe")
$helperStatus = @()
foreach ($helper in $helpers) {
    $path = Join-Path $orcaDir $helper
    $helperStatus += [ordered]@{
        name = $helper
        path = $path
        exists = Test-Path -LiteralPath $path
    }
}
$packages = @()
if (Test-Path -LiteralPath $orcaDir) {
    $packages = @(
        Get-ChildItem -LiteralPath $orcaDir -Filter "Orca.*" -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty Name
    )
}
$mpi = Get-Command "mpiexec.exe" -ErrorAction SilentlyContinue
$record = [ordered]@{
    checked_at = (Get-Date).ToString("o")
    orca_exe = $OrcaExe
    orca_exists = Test-Path -LiteralPath $OrcaExe
    orca_directory = $orcaDir
    package_evidence = $packages
    expected_local_version = $null
    helpers = $helperStatus
    mpiexec = $(if ($mpi) { $mpi.Source } else { $null })
    ready_for_serial_smoke = Test-Path -LiteralPath $OrcaExe
    ready_for_parallel_smoke = ((Test-Path -LiteralPath $OrcaExe) -and [bool]$mpi)
}
$json = $record | ConvertTo-Json -Depth 6
if ($OutputJson) {
    $parent = Split-Path -Parent $OutputJson
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    Set-Content -LiteralPath $OutputJson -Value $json -Encoding UTF8
}
$json
