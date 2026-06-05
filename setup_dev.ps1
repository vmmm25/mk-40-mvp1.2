Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    J.A.R.V.I.S. - MARK 40 Dev Setup (Windows)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

if (-Not (Test-Path ".venv")) {
    Write-Host "[*] Creando entorno virtual (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "[*] Entorno virtual ya existe." -ForegroundColor Yellow
}

Write-Host "[*] Instalando y actualizando dependencias base..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe setup.py

Write-Host "[*] Instalando dependencias de desarrollo..." -ForegroundColor Yellow
& .\.venv\Scripts\pip.exe install -r requirements-dev.txt

Write-Host "[*] Configurando hooks de Git (pre-commit)..." -ForegroundColor Yellow
& .\.venv\Scripts\pre-commit.exe install

Write-Host ""
Write-Host "[OK] Entorno de desarrollo para Windows configurado exitosamente." -ForegroundColor Green
Write-Host "[!] Para activar tu entorno manualmente usa: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
