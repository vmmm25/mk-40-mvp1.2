@echo off
title J.A.R.V.I.S. (MARK-40) Launcher
color 0a

echo ===================================================
echo     J.A.R.V.I.S. - MARK 40 (Click ^& Play)
echo ===================================================
echo.

:: Comprobar si existe el entorno virtual
IF NOT EXIST ".venv" (
    echo [*] Primera ejecucion detectada. Configurando entorno...
    echo [*] Creando entorno virtual en .venv...
    python -m venv .venv
    
    echo [*] Activando entorno e instalando dependencias...
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    echo.
    echo [OK] Entorno configurado correctamente.
) ELSE (
    echo [*] Iniciando entorno virtual...
    call .venv\Scripts\activate.bat
)

echo.
echo [*] Conectando Sistemas... Iniciando Nucleo MARK-40...
echo ===================================================
echo.

python main.py

echo.
echo [!] La aplicacion se ha cerrado.
pause
