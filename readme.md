# 🧠 MARK-40 (JARVIS) - Asistente IA Multimodal Cyberpunk

MARK-40 es un asistente virtual multimodal diseñado con una interfaz **Cyberpunk HUD**. Integra soporte para modelos locales (Ollama, LM Studio, Piper, Whisper.cpp) y modelos en la nube (Gemini, OpenRouter) para ofrecer capacidades avanzadas de visión, transcripción y síntesis de voz.

![HUD Interface](https://via.placeholder.com/800x400.png?text=HUD+Interface+Preview)

## ✨ Características Principales

*   **Multi-Motor de Lenguaje (LLM):** Soporta ejecución local mediante Ollama y LM Studio, o a través de la nube usando la API de Gemini y OpenRouter.
*   **Visión Computacional:** Capacidad de leer la pantalla actual o ventanas específicas para entender el contexto visual.
*   **Voz Modular (STT & TTS):** 
    *   *Oído (STT):* Compatible con Whisper.cpp (Local) o Gemini (Nube).
    *   *Boca (TTS):* Compatible con Piper (Local) o Gemini (Nube).
*   **Interfaz Cyberpunk Reactiva:** Un diseño tipo HUD semitransparente construido en PyQt6 con animaciones e indicadores de estado.
*   **Gestión Integrada de Modelos:** Accesos directos para cambiar rápidamente entre modelos, recargarlos "en caliente" y administrar los archivos de modelos locales directamente desde la UI.

## 🛠 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/MARK-40.git
   cd MARK-40
   ```

2. Crea un entorno virtual (Recomendado):
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Uso

Inicia el asistente ejecutando el archivo principal:

```bash
python main.py
```

Al iniciar por primera vez, verás el panel de configuración (engranaje inferior derecho). Desde allí podrás:
- Conectar tu API Key de Gemini u OpenRouter.
- Configurar tus motores locales y descargar los modelos (Ollama/LM Studio).
- Especificar la ruta a los ejecutables locales de Whisper y Piper si deseas Voz Offline.

## 📦 Motores Locales Soportados

Para utilizar a JARVIS sin conexión a internet, necesitas descargar al menos uno de los siguientes motores e indicarle a JARVIS su ruta en la configuración:

- [Ollama](https://ollama.com/) (Para modelos de texto locales).
- [LM Studio](https://lmstudio.ai/) (Para cargar GGUFs locales como servidor).
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) (Para transcripción STT local).
- [Piper](https://github.com/rhasspy/piper) (Para síntesis de voz TTS local).

## 📄 Licencia

Este proyecto se distribuye bajo la Licencia MIT. Eres libre de usarlo, modificarlo y distribuirlo de forma gratuita o comercial.

---
*Si este proyecto te parece interesante, no dudes en dejar una estrella ⭐.*