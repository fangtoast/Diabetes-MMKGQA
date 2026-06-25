param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 8000,

    [string]$RepoRoot = '.',

    [switch]$SkipData,
    [switch]$SkipKg,
    [switch]$SkipLoad,

    [switch]$NoBrowser,
    [switch]$NoVerify,

    [int]$HealthTimeoutSec = 30
)

$ErrorActionPreference = 'Stop'

function Write-Section {
    param([string]$Text)
    Write-Host ("`n=== {0} ===" -f $Text) -ForegroundColor Cyan
}

function Get-ProjectPython {
    $venvPython = Join-Path (Resolve-Path $RepoRoot) '.venv\Scripts\python.exe'
    if (Test-Path $venvPython) {
        return $venvPython
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return $pythonCommand.Source
    }

    return $null
}

function Invoke-Cli {
    param([string[]]$Arguments)
    if ($Arguments.Count -lt 1) {
        throw "Invoke-Cli: empty argument list."
    }

    $module = $Arguments[0]
    $moduleArgs = @()
    if ($Arguments.Count -gt 1) {
        $moduleArgs = $Arguments[1..($Arguments.Count - 1)]
    }

    $oldPythonPath = $env:PYTHONPATH
    $pythonExe = Get-ProjectPython
    if (-not $pythonExe) {
        throw "Python is not available in PATH."
    }
    try {
        $env:PYTHONPATH = (Join-Path (Resolve-Path $RepoRoot) 'src')
        & $pythonExe -m $module @moduleArgs
        if ($LASTEXITCODE -ne 0) {
            throw ("Command failed with exit code {0}: python -m {1} {2}" -f $LASTEXITCODE, $module, ($moduleArgs -join ' '))
        }
    }
    finally {
        $env:PYTHONPATH = $oldPythonPath
    }
}

function Wait-Health {
    param([string]$BaseUrl)
    $deadline = (Get-Date).AddSeconds($HealthTimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-RestMethod -Method Get -Uri "$BaseUrl/health" -TimeoutSec 2
            if ($resp -and $resp.backend_ready) {
                Write-Host "[start.ps1] health check passed." -ForegroundColor Green
                return
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    throw "Health check timed out after $HealthTimeoutSec seconds. Please check the startup log."
}

$repoRoot = (Resolve-Path $RepoRoot).Path
Set-Location $repoRoot

Write-Section "Repository root"
Write-Host "RepoRoot: $repoRoot"
Write-Host "Port: $Port"

$projectPython = Get-ProjectPython
if (-not $projectPython) {
    throw "Python is not available in PATH."
}

if (-not (Test-Path 'data/processed')) {
    New-Item -ItemType Directory -Path 'data/processed' | Out-Null
}

if (-not $SkipData) {
    Write-Section "Data"
    Invoke-Cli @('diabetes_mmkgqa_starter.cli', 'data', '--repo-root', $repoRoot)
}

if (-not $SkipKg) {
    Write-Section "KG build"
    Invoke-Cli @('diabetes_mmkgqa_starter.graph_builder')
}

if (-not $SkipLoad) {
    Write-Section "Load (portable backend)"
    Invoke-Cli @(
        'diabetes_mmkgqa_starter.cli',
        'load',
        '--backend', 'portable',
        '--repo-root', $repoRoot,
        '--output-dir', 'data/processed',
        '--ontology-path', 'configs/ontology.yaml'
    )
}

Write-Section "Start API"
$pythonExe = $projectPython
$pythonPath = (Join-Path $repoRoot 'src')
$baseUrl = "http://127.0.0.1:$Port"
$args = @(
    '-m', 'uvicorn',
    'diabetes_mmkgqa_starter.api.app:app',
    '--app-dir', $pythonPath,
    '--host', '0.0.0.0',
    '--port', "$Port"
)

$oldPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = $pythonPath
$apiProc = Start-Process -FilePath $pythonExe -ArgumentList $args -PassThru -WindowStyle Hidden
$env:PYTHONPATH = $oldPythonPath

if (-not $apiProc -or $apiProc.HasExited) {
    throw "Failed to start API process."
}

Write-Host ("[start.ps1] API started (PID={0})." -f $apiProc.Id) -ForegroundColor Green
Write-Host "Health: $baseUrl/health"
Write-Host "UI: $baseUrl/ui"

if (-not $NoVerify) {
    Wait-Health -BaseUrl $baseUrl
}

if (-not $NoBrowser) {
    Start-Process $baseUrl/ui | Out-Null
}

Write-Host "To stop service manually: Stop-Process -Id $($apiProc.Id)"
Write-Host "PID has been saved to console output only."
