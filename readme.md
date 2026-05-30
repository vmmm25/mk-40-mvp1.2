# 🤖 MARK XL (40) — J.A.R.V.I.S Series
### El Asistente Personal de Inteligencia Artificial Definitivo
**Desarrollado por: lolpl** 🚀

---

## 📝 Descripción del Proyecto
> [!NOTE]
> **MARK XL es un potente asistente de IA personal, multiplataforma y en tiempo real. Funciona localmente sin suscripciones, utilizando diálogo de voz natural, análisis avanzado de documentos y visión por computadora para comprender la pantalla y ejecutar flujos de automatización complejos de forma autónoma con una interfaz HUD interactiva cyberpunk.**

---

## ✨ Características Principales

| Característica | Descripción |
| :--- | :--- |
| 🎙️ **Voz en Tiempo Real** | Conversación fluida de ultra-baja latencia con soporte híbrido (Local y Nube). |
| 🖥️ **Control del Sistema** | Abre aplicaciones, administra archivos y ejecuta comandos en la terminal de forma nativa. |
| 🧩 **Tareas Autónomas** | Planificación inteligente y ejecución paso a paso para resolver objetivos complejos. |
| 👁️ **Consciencia Visual** | Procesamiento en tiempo real de tu pantalla y cámara web para dar soporte contextual. |
| 🧠 **Memoria Persistente** | Recuerda detalles clave, preferencias personales y proyectos pasados entre sesiones. |
| 🎨 **Interfaz Cyberpunk HUD** | Panel de control futurista de alta tecnología con controles de transparencia, redimensionable y dinámico. |
| 📂 **Carga de Archivos** | Soporte directo para arrastrar y soltar PDFs, imágenes o código fuente para análisis instantáneo. |

---

## ⚡ Guía de Instalación y Configuración

Sigue estos sencillos pasos para tener tu **MARK XL** listo y funcionando en cualquier PC con Windows 10 u 11.

### 1. Clonar el Repositorio
Abre tu consola de comandos (Terminal, Git CMD o PowerShell) y clona el proyecto:
```bash
git clone <tu-enlace-de-github>
cd update-mk40
```

### 2. Instalar Dependencias de Python
> [!IMPORTANT]
> Se requiere **Python 3.11** o **3.12** instalado en el sistema. Asegúrate de marcar la opción *"Add Python to PATH"* durante la instalación.

Instala todas las librerías necesarias con el siguiente comando:
```bash
pip install -r requirements.txt
```

### 3. Instalar Controladores de Playwright
El asistente utiliza Playwright para navegar y analizar páginas web. Instala los componentes internos ejecutando:
```bash
playwright install
```

### 4. Configurar tus Claves de API (API Keys)
Para proteger tus datos personales, las claves de acceso reales no se suben al servidor remoto. Configura tu entorno así:
1. Dirígete a la carpeta `config/`.
2. Duplica o renombra el archivo `api_keys.json.example` como `api_keys.json`.
3. Abre `api_keys.json` con tu editor preferido e introduce tus claves de API:
   - **`gemini_api_key`**: Consigue una clave gratuita en [Google AI Studio](https://aistudio.google.com/).
   - **`openrouter_api_key`** (Opcional): Si deseas utilizar modelos alternativos en la nube.

```json
{
  "gemini_api_key": "TU_API_KEY_AQUÍ",
  "openrouter_api_key": "OPCIONAL_TU_OPENROUTER_KEY"
}
```

### 5. Instalar Motores de Voz Locales (Whisper & Piper) 🎙️
> [!TIP]
> **¡No necesitas descargar nada manualmente!** Hemos diseñado un instalador táctico automatizado que descarga los motores locales de transcripción (Whisper.cpp) y síntesis de voz (Piper), descarga las voces en español de calidad media y configura de forma automática todas las rutas en tu archivo `api_keys.json`.

Simplemente ejecuta el script en tu terminal:
```bash
python download_engines.py
```

Una vez finalizado, verás un mensaje de éxito indicando que los motores locales de voz están listos para ser usados de manera inmediata.

---

## 🚀 Cómo Iniciar el Asistente

Para encender a tu asistente y desplegar la consola HUD interactiva cyberpunk, ejecuta el siguiente comando:
```bash
python main.py
```

---

## 📋 Requisitos de Hardware y Sistema

* **Sistema Operativo:** Windows 10/11 (Totalmente soportado), macOS o Linux.
* **Procesador:** CPU multinúcleo moderna (Intel i5/Ryzen 5 o superior).
* **Micrófono y Parlantes:** Requeridos para habilitar las conversaciones de voz interactivas.
* **Conexión a Internet:** Requerida solo para las llamadas a la API de Gemini (el procesamiento de audio y comandos se ejecuta 100% de forma local).

---

> [!TIP]
> **¿Quieres cambiar de motor de voz?** Una vez abierta la aplicación, dirígete a la pestaña **🎙 VOZ** para alternar con total libertad entre la voz integrada en la nube de Google Gemini y los motores offline ultrarrápidos de Whisper y Piper.
