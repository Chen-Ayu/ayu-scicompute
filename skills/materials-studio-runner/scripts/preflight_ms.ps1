param(
    [string]$MaterialsStudioRoot,
    [string]$RunMatScript,
    [string]$GatewayHost = "localhost",
    [int]$GatewayPort = 18888,
    [string]$OutputJson
)

$ErrorActionPreference = "Stop"
if (-not $MaterialsStudioRoot) { $MaterialsStudioRoot = $env:MATERIALS_STUDIO_SERVER_ROOT }
if (-not $RunMatScript) { $RunMatScript = $env:MATERIALS_STUDIO_RUNNER }
if (-not $RunMatScript -and $MaterialsStudioRoot) {
    $RunMatScript = Join-Path $MaterialsStudioRoot "etc\Scripting\bin\RunMatScript.bat"
}
$runner = $RunMatScript
$gatewayStart = $(if ($MaterialsStudioRoot) { Join-Path $MaterialsStudioRoot "etc\Gateway\gwstartservice.bat" } else { $null })
$rootExists = [bool]($MaterialsStudioRoot -and (Test-Path -LiteralPath $MaterialsStudioRoot))
$runnerExists = [bool]($runner -and (Test-Path -LiteralPath $runner))
$gatewayStartExists = [bool]($gatewayStart -and (Test-Path -LiteralPath $gatewayStart))
$processNames = @("MatStudio", "MatServer", "xmsengine")
$processes = Get-Process -Name $processNames -ErrorAction SilentlyContinue |
    Select-Object ProcessName, Id, StartTime
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

$record = [ordered]@{
    checked_at = (Get-Date).ToString("o")
    materials_studio_root = $MaterialsStudioRoot
    root_exists = $rootExists
    run_mat_script = $runner
    run_mat_script_exists = $runnerExists
    gateway_start_script = $gatewayStart
    gateway_start_script_exists = $gatewayStartExists
    gateway_host = $GatewayHost
    gateway_port = $GatewayPort
    gateway_reachable = $gatewayReachable
    active_processes = @($processes)
    ready_for_script_launch = ($runnerExists -and $gatewayReachable)
    note = "Runner and Gateway connectivity do not prove license availability; verify with a smoke job."
}

$json = $record | ConvertTo-Json -Depth 6
if ($OutputJson) {
    $parent = Split-Path -Parent $OutputJson
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    Set-Content -LiteralPath $OutputJson -Value $json -Encoding UTF8
}
$json
