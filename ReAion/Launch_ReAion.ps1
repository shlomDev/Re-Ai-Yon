$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $python) { throw 'Python 3 is required. Install it from https://www.python.org/downloads/windows/ and run this launcher again.' }

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    & $python.Source -m venv .venv
}
$vpy = Join-Path $PWD '.venv\Scripts\python.exe'

if (-not (Test-Path '.venv\.dependencies-ready')) {
    & $vpy -m pip install --upgrade pip
    & $vpy -m pip install -r requirements.txt
    & $vpy -m playwright install chromium
    New-Item '.venv\.dependencies-ready' -ItemType File -Force | Out-Null
}

& $vpy setup_private_profile.py
& $vpy quick_start.py
