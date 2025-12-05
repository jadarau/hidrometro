Param(
    [string]$HostIP = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$NoReload
)

# Ensure we're in the back-end folder
Push-Location $PSScriptRoot

# Create venv if missing (Python 3.11 recommended)
if (!(Test-Path ".venv")) {
    Write-Host "[setup] Creating Python 3.11 venv..."
    try {
        py -3.11 -m venv .venv
    } catch {
        Write-Host "[setup] Fallback to default python for venv..."
        python -m venv .venv
    }
}

# Activate venv
Write-Host "[setup] Activating venv..."
& ".\.venv\Scripts\Activate.ps1"

# Upgrade basic tooling
Write-Host "[setup] Upgrading pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel | Out-Null

# Install requirements if not already satisfied
Write-Host "[setup] Installing requirements..."
pip install -r requirements.txt | Out-Null

# Set PYTHONPATH to include this back-end folder for reliable imports
$env:PYTHONPATH = $PSScriptRoot
Write-Host "[env] PYTHONPATH set to $($env:PYTHONPATH)"

# Load uvicorn with optional reload
$reloadArg = $NoReload.IsPresent ? "" : "--reload"
Write-Host "[run] Starting uvicorn on $HostIP:$Port $reloadArg"
python -m uvicorn app.main:app --host $HostIP --port $Port $reloadArg

# Restore location
Pop-Location