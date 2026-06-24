[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet(
        'help',
        'bootstrap',
        'data',
        'kg',
        'up',
        'load',
        'test',
        'verify',
        'demo',
        'report',
        'package'
    )]
    [string]$Command = 'help',

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..'))
Set-Location $repoRoot

function Invoke-MakeOrFallback {
    param(
        [string]$Target,
        [ScriptBlock]$Fallback,
        [string]$FallbackMessage
    )

    if (Get-Command make -ErrorAction SilentlyContinue) {
        Write-Host "[run.ps1] Running: make $Target" -ForegroundColor Cyan
        & make $Target
        if ($LASTEXITCODE -ne 0) {
            Write-Error "make $Target failed with code $LASTEXITCODE"
            exit $LASTEXITCODE
        }
        return
    }

    Write-Warning "make is not available; using PowerShell fallback for '$Target'."
    Write-Host $FallbackMessage -ForegroundColor Yellow
    if ($Fallback) {
        & $Fallback
    }
}

function Write-Placeholder {
    param([string]$Message)
    Write-Host "[run.ps1] $Message" -ForegroundColor Yellow
}

function Invoke-Bootstrap {
    param([switch]$SkipInstall)
    Write-Host '=== bootstrap ===' -ForegroundColor Cyan
    if (-not (Test-Path requirements-lock.txt)) {
        Write-Error 'requirements-lock.txt not found. Please run BOOT-002 first.'
        exit 1
    }

    if ($SkipInstall) {
        Write-Placeholder 'skip-install mode: dependency install skipped.'
        return
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host 'Installing pinned requirements from requirements-lock.txt ...'
        python -m pip install --disable-pip-version-check -r requirements-lock.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Error 'python -m pip install failed.'
            exit $LASTEXITCODE
        }
    }
    else {
        Write-Error 'Python not available on this environment.'
        exit 1
    }

    New-Item -ItemType Directory -Force -Path data/interim, data/processed, deliverables | Out-Null
    Write-Host 'Created runtime/data directories (if not existing): data/interim, data/processed, deliverables'
}

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
}

function Invoke-Demo {
    Write-Host '=== demo ==='
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error 'Python is required to run demo cases.'
        exit 1
    }

    $args = @(
        '--processed-dir', 'data/processed',
        '--demo-output-dir', 'docs/cases',
        '--demo-output-json', 'demo_cases.json'
    )
    if ($Rest -and $Rest.Count -gt 0) {
        $args = $Rest
    }

    $prevPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = (Join-Path (Get-Location) 'src')
        & python -m diabetes_mmkgqa_starter.cli @args demo
        if ($LASTEXITCODE -ne 0) {
            Write-Error "demo command failed with code $LASTEXITCODE"
            exit $LASTEXITCODE
        }
    }
    finally {
        $env:PYTHONPATH = $prevPythonPath
    }
}

function Invoke-Report {
    Write-Host '=== report ==='
    Ensure-Dir docs/cases
    Ensure-Dir docs/screenshots
    Write-Placeholder 'Report command is scaffolded. Will collect stats/docs/screenshots in docs/cases and docs/screenshots.'
}

function Invoke-Package {
    Write-Host '=== package ==='
    Ensure-Dir deliverables
    Write-Placeholder 'Package command is scaffolded. deliverables package assembly should exclude unauthorized raw datasets.'
}

function Show-Help {
    @'
Run helper for project bootstrap/build tasks.

Usage:
  ./scripts/run.ps1 <command>

Commands:
  help      - Show this help
  bootstrap - Install pinned dependencies and prepare runtime dirs
  data      - Run data pipeline equivalent
  kg        - Run graph build pipeline equivalent
  up        - Start API/UI services
  load      - Load graph into backend
  test      - Run tests
  verify    - Run lint/tests/quality smoke checks
  demo      - Run fixed demo cases
  report    - Assemble report inputs
  package   - Create deliverable package

All commands are course-demo oriented and non-clinical.
'@ | Write-Host
}

switch ($Command) {
    'help' {
        Show-Help
    }

    'bootstrap' {
        Invoke-MakeOrFallback -Target 'bootstrap' -FallbackMessage 'make bootstrap unavailable; using script bootstrap path.' -Fallback {
            Invoke-Bootstrap
        }
    }

    'data' {
        Invoke-MakeOrFallback -Target 'data' -FallbackMessage 'make data unavailable; placeholder for source validation and root/interim setup.' -Fallback {
            if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
                Write-Error 'python is not available; cannot run MedMNIST data workflow.'
                exit 1
            }
            $args = @('--dataset', 'all', '--dry-run')
            if ($Rest -and $Rest.Count -gt 0) {
                $args = $Rest
            }
            & python scripts/fetch_medmnist.py @args
            if ($LASTEXITCODE -ne 0) {
                Write-Error "data workflow failed with code $LASTEXITCODE"
                exit $LASTEXITCODE
            }

            Write-Host '---' 
            & python scripts/fetch_diakg.py --dry-run
            if ($LASTEXITCODE -ne 0) {
                Write-Error "DiaKG workflow check failed with code $LASTEXITCODE"
                exit $LASTEXITCODE
            }
        }
    }

    'kg' {
        Invoke-MakeOrFallback -Target 'kg' -FallbackMessage 'make kg unavailable; placeholder for graph build pipeline.' -Fallback {
            if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
                Write-Error 'python is not available; cannot run graph build.'
                exit 1
            }
            $args = @()
            if ($Rest -and $Rest.Count -gt 0) {
                $args = $Rest
            }
            $prevPythonPath = $env:PYTHONPATH
            try {
                $env:PYTHONPATH = (Join-Path (Get-Location) 'src')
                & python -m diabetes_mmkgqa_starter.graph_builder @args
            }
            finally {
                $env:PYTHONPATH = $prevPythonPath
            }
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Graph build failed with code $LASTEXITCODE"
                exit $LASTEXITCODE
            }
        }
    }

    'up' {
        Invoke-MakeOrFallback -Target 'up' -FallbackMessage 'make up unavailable; backend service launcher is not implemented yet.' -Fallback {
            if (Get-Command uvicorn -ErrorAction SilentlyContinue) {
                $args = @(
                    'diabetes_mmkgqa_starter.api.app:app',
                    '--app-dir', (Join-Path (Get-Location) 'src'),
                    '--host', '0.0.0.0',
                    '--port', '8000'
                )
                if ($Rest -and $Rest.Count -gt 0) {
                    $args = $args + $Rest
                }
                & uvicorn @args
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "up failed with code $LASTEXITCODE"
                    exit $LASTEXITCODE
                }
            }
            elseif (Get-Command python -ErrorAction SilentlyContinue) {
                $args = @(
                    '-m', 'uvicorn',
                    'diabetes_mmkgqa_starter.api.app:app',
                    '--app-dir', (Join-Path (Get-Location) 'src'),
                    '--host', '0.0.0.0',
                    '--port', '8000'
                )
                if ($Rest -and $Rest.Count -gt 0) {
                    $args = $args + $Rest
                }
                $prevPythonPath = $env:PYTHONPATH
                try {
                    $env:PYTHONPATH = (Join-Path (Get-Location) 'src')
                    & python @args
                    if ($LASTEXITCODE -ne 0) {
                        Write-Error "up failed with code $LASTEXITCODE"
                        exit $LASTEXITCODE
                    }
                }
                finally {
                    $env:PYTHONPATH = $prevPythonPath
                }
            }
            else {
                Write-Error 'Python or uvicorn is not available. Cannot start API server.'
                exit 1
            }
        }
    }

    'load' {
        Invoke-MakeOrFallback -Target 'load' -FallbackMessage 'make load unavailable; load helper uses portable backend if Neo4j password absent.' -Fallback {
            if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
                Write-Error 'python is not available; cannot run load fallback.'
                exit 1
            }
            $args = @(
                'load'
                '--backend', 'portable'
                '--repo-root', (Get-Location).Path
            )
            if ($Rest -and $Rest.Count -gt 0) {
                $args = $Rest
            }
            else {
                $args += '--output-dir', 'data/processed'
            }
            $prevPythonPath = $env:PYTHONPATH
            try {
                $env:PYTHONPATH = (Join-Path (Get-Location) 'src')
                & python -m diabetes_mmkgqa_starter.cli @args
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "load failed with code $LASTEXITCODE"
                    exit $LASTEXITCODE
                }
            }
            finally {
                $env:PYTHONPATH = $prevPythonPath
            }
        }
    }

    'test' {
        Invoke-MakeOrFallback -Target 'test' -FallbackMessage 'make test unavailable; falling back to pytest if installed.' -Fallback {
            if (Get-Command pytest -ErrorAction SilentlyContinue) {
                pytest
            }
            else {
                Write-Placeholder 'pytest not installed yet; bootstrap should install test dependencies first.'
            }
        }
    }

    'verify' {
        Invoke-MakeOrFallback -Target 'verify' -FallbackMessage 'make verify unavailable; fallback smoke checks if possible.' -Fallback {
            if (Get-Command python -ErrorAction SilentlyContinue) {
                Write-Placeholder 'Running lightweight verification smoke checks (scripted path).'
                python --version
            }
            else {
                Write-Placeholder 'python not available for verification smoke check.'
            }
        }
    }

    'demo' {
        Invoke-Demo
    }

    'report' {
        Invoke-Report
    }

    'package' {
        Invoke-Package
    }
}
