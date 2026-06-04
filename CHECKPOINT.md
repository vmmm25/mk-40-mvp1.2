# 🧠 MARK XL — Checkpoint de Sesión

> **Actualizado:** 2026-06-04  
> **Estado:** Completo / Limpieza de Repositorio realizada  

---

## 🎯 Objetivo General
Revisar, corregir problemas críticos y mejorar el asistente virtual MARK XL (J.A.R.V.I.S. Mark-40) con:
- Barra de herramientas superior con iconos de "cerebro" para proveedores de LLM.
- Panel de configuración centralizado estilo Google (con pestañas).
- Integración local completa con Ollama y LM Studio (vía CLI `lms` oficial).
- Gestión de API Keys para Gemini y OpenRouter desde la interfaz gráfica.
- Configuración de dispositivos de audio (micrófono, altavoces, volumen) y seguridad.

---

## 📋 Progreso

### ✅ Completado

#### 🖥️ Integración de Motores Locales y Nube
- **LM Studio (`lms` CLI):** Integración completa para levantar/detener el servidor daemon de LM Studio y cargar/descargar modelos de memoria RAM en Windows automáticamente de forma asíncrona.
- **Ollama CLI:** Integración con `ollama serve` y `ollama pull <modelo>` mediante terminales visibles para el usuario.
- **Auto-Inicio Inteligente:** Al seleccionar y activar un motor local (Ollama / LM Studio), la aplicación levanta el servidor y precarga el modelo configurado en segundo plano de manera automática.
- **Gemini & OpenRouter:** Gestión segura de API keys escritas y leídas desde `config/api_keys.json`, evitando keys hardcodeadas.

#### 🎨 Interfaz de Usuario (UI) & UX Cyberpunk
- **Pestaña de Ajustes Centralizada (Google Style):** Organización clara en tres subventanas:
  1. **Ajustes de Motor y Voz:** Dispositivos de audio, volumen del sistema, contraseña de seguridad y selección de motores STT (Whisper) y TTS (Piper).
  2. **Configuración de Modelos (LLM):** Pestañas independientes para Gemini (GEM), OpenRouter (OR), Ollama (OLL) y LM Studio (LM).
  3. **Seguridad / API Keys:** Gestión centralizada de credenciales.
- **Auto-Guardado Inteligente:** Eliminación de botones redundantes de guardado individual. Los cambios en comboboxes, sliders y rutas de ejecutables se guardan y aplican automáticamente en tiempo real.
- **Optimización de Logs:** Se optimizó el polling en segundo plano del estado de los servidores de 3 s a 30 s para evitar la saturación de logs cuando los servicios no están activos.
- **Iconos de Cerebro Interactivos:** Icono dibujado en QPainter con colores según proveedor (Gemini = celeste, Ollama = blanco, OpenRouter = color dinámico de la compañía del modelo).

#### 🔊 Audio & Voz Modular
- **Dispositivos de Entrada/Salida:** Menús desplegables que obtienen dinámicamente el hardware mediante `sounddevice.query_devices()`.
- **Control de Volumen:** Barra deslizadora funcional que aplica escalado de samples de audio en tiempo real sin dependencias externas pesadas.
- **Motores STT/TTS:** Enrutamiento modular para Whisper (local/nube) y Piper (local/nube).

#### 🚀 Limpieza y Estructura del Proyecto
- **Eliminación de Obsoletos:** Se eliminaron los borradores de planificación antiguos (`PLAN_IMPLEMENTACION.md` y `PLAN_REFACTOR.md`) para mantener limpio el directorio raíz.
- **Documentación Visual:** Actualización de `readme.md` con capturas de pantalla reales del HUD y de los paneles de configuración y voz.
- **Instalación Directa:** `Run_JARVIS.bat` automatiza la creación del entorno virtual `.venv` y la instalación de dependencias requeridas (`playwright`, `psutil`, `requests`, `sounddevice`, etc.).

---

## 🛠️ Archivos Relevantes

| Archivo | Descripción |
|---|---|
| [ui.py](file:///c:/Users/lolpl/Desktop/02_Proyectos_Dev/MARK-39_AI/update-mk40/ui.py) | Componentes principales de la UI, barra de herramientas de cerebros y pestañas de configuración. |
| [main.py](file:///c:/Users/lolpl/Desktop/02_Proyectos_Dev/MARK-39_AI/update-mk40/main.py) | Punto de entrada del asistente, procesamiento y escalado de volumen de audio. |
| [lmstudio_control.py](file:///c:/Users/lolpl/Desktop/02_Proyectos_Dev/MARK-39_AI/update-mk40/lmstudio_control.py) | Controlador asíncrono para la CLI oficial de LM Studio (`lms`). |
| [readme.md](file:///c:/Users/lolpl/Desktop/02_Proyectos_Dev/MARK-39_AI/update-mk40/readme.md) | Documentación oficial del proyecto con la nueva guía visual y changelog. |
| [MAINTENANCE_GUIDE.md](file:///c:/Users/lolpl/Desktop/02_Proyectos_Dev/MARK-39_AI/update-mk40/MAINTENANCE_GUIDE.md) | Guía de mantenimiento y reglas de desarrollo para colaboradores. |

---

## 🔒 Decisiones de Diseño Clave
1. **Asincronía Total en CLI:** Todos los comandos de CLI (`ollama`, `lms`) se ejecutan asíncronamente en subprocesos para no congelar la UI de PyQt6.
2. **Auto-Guardado Activo:** Todo cambio de configuración se persiste automáticamente al perder el foco o cambiar el valor, mejorando la UX cyberpunk.
3. **Escalado de Volumen Seguro:** Multiplicación de samples de audio directa en arrays `int16` para evitar el uso obligatorio de `numpy` en entornos ligeros.
