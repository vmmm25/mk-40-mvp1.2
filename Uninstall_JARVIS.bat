@echo off
title J.A.R.V.I.S. (MARK-40) Uninstaller
color 0c

echo ===================================================
echo     J.A.R.V.I.S. - MARK 40 (Limpieza Total)
echo ===================================================
echo.
echo ADVERTENCIA: Esto eliminara todo rastro local de JARVIS en esta computadora.
echo Se borraran configuraciones, el entorno virtual (.venv), perfiles de navegacion
echo creados por la IA y la memoria almacenada.
echo.
echo Presiona CTRL+C para cancelar, o cualquier tecla para proceder.
pause >nul

echo.
echo [*] Cerrando procesos de Python si estan activos...
taskkill /F /IM python.exe >nul 2>&1

echo [*] Eliminando entorno virtual (.venv)...
if exist ".venv" rmdir /s /q ".venv"

echo [*] Eliminando cache y compilados de Python (__pycache__)...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"

echo [*] Eliminando memoria y configuracion (memory/)...
if exist "memory\config.json" del /q "memory\config.json"
if exist "memory\memory.json" del /q "memory\memory.json"

echo [*] Eliminando perfiles de navegador de la IA (.jarvis_profiles)...
if exist "%USERPROFILE%\.jarvis_profiles" rmdir /s /q "%USERPROFILE%\.jarvis_profiles"

echo.
echo ===================================================
echo [OK] Limpieza completada con exito.
echo El agente J.A.R.V.I.S. ha sido erradicado de la maquina.
echo Puedes borrar esta carpeta manualmente ahora si lo deseas.
echo ===================================================
echo.
pause
