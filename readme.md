# 🧠 J.A.R.V.I.S. (MARK-40) - Asistente IA Multimodal Cyberpunk

MARK-40 es un asistente virtual multimodal diseñado con una interfaz **Cyberpunk HUD**. Integra soporte para modelos locales (Ollama, LM Studio, Piper, Whisper.cpp) y modelos en la nube (Gemini, OpenRouter) para ofrecer capacidades avanzadas de visión, transcripción y síntesis de voz totalmente personalizables.

![HUD Interface](https://via.placeholder.com/800x400.png?text=HUD+Interface+Preview)

## ✨ Características Principales

*   **Multi-Motor de Lenguaje (LLM):** Soporta ejecución local mediante Ollama y LM Studio, o a través de la nube usando la API de Gemini y OpenRouter.
*   **Visión Computacional (Ojos):** Capacidad de leer la pantalla actual o ventanas específicas para entender el contexto visual e interactuar contigo sobre lo que estás viendo.
*   **Voz Modular (Oído & Boca):** 
    *   *STT (Transcripción):* Compatible con Whisper.cpp (Local offline) o Gemini (Nube ultrarrápida).
    *   *TTS (Síntesis):* Compatible con Piper (Local offline) o Gemini (Nube).
*   **Interfaz Cyberpunk Reactiva:** Un diseño tipo HUD semitransparente construido en PyQt6 con animaciones e indicadores de estado interactivos.
*   **Gestión Integrada:** Accesos directos nativos a tus carpetas de modelos, cambio rápido de configuración sin reiniciar y panel centralizado.

## 🛠 Instalación Rápida (Click & Play)

MARK-40 incluye un instalador automático para Windows.

1. **Clona o descarga este repositorio:**
   ```bash
   git clone https://github.com/vmmm25/mk-40-mvp1.2.git
   ```

2. **Abre la carpeta del proyecto y ejecuta:**
   Haz doble clic sobre el archivo **`Run_JARVIS.bat`**. 
   
   *(El script detectará si es tu primera vez, instalará el entorno virtual Python, descargará las librerías necesarias y abrirá el Asistente automáticamente).*

## 🚀 Uso Avanzado

Al iniciar por primera vez, verás el panel de configuración (engranaje inferior derecho). Desde allí podrás:
- Conectar tu API Key de Gemini u OpenRouter.
- Configurar tus motores locales y enlazar tu servidor (Ollama/LM Studio).
- Especificar la ruta a los ejecutables locales de Whisper y Piper si deseas tener control total por Voz Offline.

## 📦 Motores Locales Soportados

Para utilizar a JARVIS sin conexión a internet (100% privado), te recomendamos descargar e integrar los siguientes motores:

- [Ollama](https://ollama.com/) (Ejecución de modelos de lenguaje).
- [LM Studio](https://lmstudio.ai/) (Servidor OpenAI-compatible).
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) (Transcripción de voz).
- [Piper](https://github.com/rhasspy/piper) (Síntesis de voz).

## 📝 Changelog

* **[v1.2.1] - Fix Instalación:** Se ha corregido la creación del entorno virtual y se han añadido dependencias faltantes (`playwright`, `psutil`, `requests`) para que el programa inicie correctamente en máquinas nuevas sin errores de módulos. Ahora `Run_JARVIS.bat` instala automáticamente los navegadores necesarios de Playwright.

## 📄 Licencia

Este proyecto se distribuye bajo la Licencia MIT. Eres libre de usarlo, modificarlo y distribuirlo de forma gratuita o comercial.

---
*Si este proyecto te parece útil o interesante, no dudes en dejar una estrella ⭐ en el repositorio.*