$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
py -m venv .build-venv
$python = Join-Path $PWD '.build-venv\Scripts\python.exe'
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt pyinstaller
& $python -m playwright install chromium
& $python -m PyInstaller --noconfirm --clean ReAion.spec
Write-Host "Build complete: dist\ReAion"
