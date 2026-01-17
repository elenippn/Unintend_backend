$ErrorActionPreference = 'Stop'

# Runs the backend with a local SQLite database + seed data.
# Safe to re-run; it will create the venv/db if missing.

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "[1/4] Creating venv (if missing)..."
if (-not (Test-Path -Path ".venv")) {
  py -m venv .venv
}

Write-Host "[2/4] Activating venv..."
. .\.venv\Scripts\Activate.ps1

Write-Host "[3/4] Installing requirements..."
pip install -r requirements.txt

Write-Host "[4/4] Seeding DB (first run) and starting server..."
# Seed is idempotent enough for demo purposes.
py -m app.seed

# For emulator use: base URL is http://10.0.2.2:8000
# For physical device (same Wi-Fi): use --host 0.0.0.0 and set API_BASE_URL to your PC IP.
uvicorn app.main:app --host 127.0.0.1 --port 8000
