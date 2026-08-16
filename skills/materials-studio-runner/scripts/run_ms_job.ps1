param(
    [Parameter(Mandatory=$true)][string]$RunDir,
    [Parameter(Mandatory=$true)][string]$ScriptName,
    [string]$RunMatScript,
    [string]$GatewayHost = "localhost",
    [int]$GatewayPort = 18888,
    [string]$StagingRoot = (Join-Path $env:TEMP "codex_ms_jobs"),
    [switch]$DisableAutoStaging,
    [switch]$SkipGatewayCheck,
    [switch]$Background,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
if (-not $RunMatScript) { $RunMatScript = $env:MATERIALS_STUDIO_RUNNER }
if (-not $RunMatScript) { throw "RunMatScript not configured. Pass -RunMatScript or set MATERIALS_STUDIO_RUNNER." }
$RunMatScript = [IO.Path]::GetFullPath($RunMatScript)
$projectRunDir = (Resolve-Path -LiteralPath $RunDir).Path
if ($ScriptName -ne [IO.Path]::GetFileName($ScriptName) -or $ScriptName -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*(?:\.pl)?$') {
    throw "ScriptName must be a safe MaterialsScript leaf filename."
}
$scriptLeaf = [IO.Path]::GetFileNameWithoutExtension($ScriptName)
if (-not (Test-Path -LiteralPath $RunMatScript)) { throw "RunMatScript not found: $RunMatScript" }
if (-not $SkipGatewayCheck) {
    $gatewayReachable = $false
    $tcp = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $tcp.BeginConnect($GatewayHost, $GatewayPort, $null, $null)
        if ($async.AsyncWaitHandle.WaitOne(1500, $false)) {
            $tcp.EndConnect($async)
            $gatewayReachable = $tcp.Connected
        }
    } catch {
        $gatewayReachable = $false
    } finally {
        $tcp.Close()
    }
    if (-not $gatewayReachable) {
        throw "Materials Studio Gateway is not reachable at ${GatewayHost}:${GatewayPort}"
    }
}

$executionRunDir = $projectRunDir
$stagingUsed = $false
if ((-not $DisableAutoStaging) -and ($projectRunDir -match '[^\x00-\x7F]')) {
    New-Item -ItemType Directory -Force -Path $StagingRoot | Out-Null
    $stageName = $scriptLeaf + "_" + (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + [guid]::NewGuid().ToString("N").Substring(0,8)
    $executionRunDir = Join-Path $StagingRoot $stageName
    New-Item -ItemType Directory -Force -Path $executionRunDir | Out-Null
    Get-ChildItem -LiteralPath $projectRunDir -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $executionRunDir -Recurse -Force
    }
    $stagingUsed = $true
}
$scriptPath = Join-Path $executionRunDir ($scriptLeaf + ".pl")
if (-not (Test-Path -LiteralPath $scriptPath)) { throw "MaterialsScript file not found: $scriptPath" }

$statePath = Join-Path $projectRunDir "ms_job_state.json"
$commandRecord = [ordered]@{
    engine = "materials-studio"
    runner = $RunMatScript
    run_dir = $projectRunDir
    execution_run_dir = $executionRunDir
    staging_used = $stagingUsed
    staging_preserved = $stagingUsed
    gateway = "${GatewayHost}:${GatewayPort}"
    script = $scriptLeaf
    background = [bool]$Background
    status = $(if ($DryRun) { "dry-run" } else { "starting" })
    started_at = (Get-Date).ToString("o")
}
$commandRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8
if ($DryRun) {
    $commandRecord | ConvertTo-Json -Depth 4
    exit 0
}

$previousLocale = @{
    LC_ALL = $env:LC_ALL
    LC_CTYPE = $env:LC_CTYPE
    LANG = $env:LANG
}
$env:LC_ALL = ""
$env:LC_CTYPE = ""
$env:LANG = ""

try {
    if ($Background) {
        $process = Start-Process -FilePath $RunMatScript `
            -ArgumentList @("-flat", $scriptLeaf) `
            -WorkingDirectory $executionRunDir `
            -WindowStyle Hidden `
            -PassThru
        $commandRecord.status = "running"
        $commandRecord.pid = $process.Id
    } else {
        Push-Location $executionRunDir
        try {
            & $RunMatScript -flat $scriptLeaf
            $commandRecord.exit_code = $LASTEXITCODE
            $commandRecord.status = $(if ($LASTEXITCODE -eq 0) { "process-exited" } else { "failed" })
        } finally {
            Pop-Location
        }
    }
} finally {
    $env:LC_ALL = $previousLocale.LC_ALL
    $env:LC_CTYPE = $previousLocale.LC_CTYPE
    $env:LANG = $previousLocale.LANG
    $commandRecord.updated_at = (Get-Date).ToString("o")
    if ($stagingUsed -and (-not $Background)) {
        Get-ChildItem -LiteralPath $executionRunDir -Force | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $projectRunDir -Recurse -Force
        }
        $commandRecord.collected_to_project = $true
    }
    $commandRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8
}
$commandRecord | ConvertTo-Json -Depth 4
