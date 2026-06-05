#!/bin/bash
# J.A.R.V.I.S. (MARK-40) Launcher for Linux (Ubuntu/Debian)

echo "==================================================="
echo "    J.A.R.V.I.S. - MARK 40 Launcher (Linux)"
echo "==================================================="
echo ""

# Verificar dependencias del sistema recomendadas
missing_deps=()
for cmd in xdg-open pactl nmcli wmctrl ffmpeg; do
    if ! command -v $cmd &> /dev/null; then
        missing_deps+=($cmd)
    fi
done

# Verificar si portaudio2 está presente (requerido por sounddevice)
if ! ldconfig -p | grep -q libportaudio.so 2>/dev/null; then
    missing_deps+=("libportaudio2")
fi

if [ ${#missing_deps[@]} -ne 0 ]; then
    echo "[!] Advertencia: Faltan dependencias del sistema recomendadas: ${missing_deps[*]}"
    echo "[*] Para un funcionamiento óptimo de audio y control, instálalas usando:"
    echo "    sudo apt update && sudo apt install -y xdg-utils pulseaudio-utils network-manager wmctrl libportaudio2 build-essential ffmpeg"
    echo ""
fi

# Comprobar si existe el entorno virtual
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
    echo "[*] Primera ejecución detectada. Configurando entorno..."
    echo "[*] Creando entorno virtual en .venv..."
    python3 -m venv .venv
    
    echo "[*] Activando entorno e instalando dependencias..."
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    python -m playwright install
    python -m playwright install-deps
    
    echo ""
    echo "[OK] Entorno configurado correctamente."
else
    echo "[*] Iniciando entorno virtual..."
    source .venv/bin/activate
fi

echo ""
echo "[*] Conectando Sistemas... Iniciando Núcleo MARK-40..."
echo "==================================================="
echo ""

python main.py

echo ""
echo "[!] La aplicación se ha cerrado."
read -p "Presiona Enter para salir..."
