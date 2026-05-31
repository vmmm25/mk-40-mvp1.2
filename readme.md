# 🤖 MARK XL (40) — J.A.R.V.I.S Series
## El Asistente Personal de Inteligencia Artificial Definitivo

**Desarrollado por:** lolpl 🚀

---

## 📚 Índice
- [Descripción del Proyecto](# descripción-del-proyecto)
- [Características Principales](# características-principales)
- [Requisitos de Hardware y Sistema](# requisitos-de-hardware-y-sistema)
- [Instalación y Configuración](# instalación-y-configuración)
  - [1. Clonar el Repositorio](# 1-clonar-el-repositorio)
  - [2. Instalar Dependencias de Python](# 2-instalar-dependencias-de-python)
  - [3. Instalar Controladores de Playwright](# 3-instalar-controladores-de-playwright)
  - [4. Configurar Claves de API](# 4-configurar-claves-de-api)
  - [5. Instalar Motores de Voz Locales](# 5-instalar-motores-de-voz-locales)
- [Uso del Asistente](# uso-del-asistente)
- [Contribuir](# contribuir)
- [Licencia](# licencia)

---

## 📝 Descripción del Proyecto
> **MARK XL** es un asistente de IA personal, multiplataforma y en tiempo real. Funciona localmente sin suscripciones, proporcionando diálogo de voz natural, análisis avanzado de documentos, visión por computadora y automatización de flujos de trabajo mediante una interfaz HUD cyberpunk interactiva.

---

## ✨ Características Principales
| Característica | Descripción |
| :--- | :--- |
| 🎙️ **Voz en Tiempo Real** | Conversación ultra-baja latencia con soporte híbrido (Local y Nube). |
| 🖥️ **Control del Sistema** | Abrir aplicaciones, administrar archivos y ejecutar comandos en la terminal. |
| 🧩 **Tareas Autónomas** | Planificación inteligente y ejecución paso a paso. |
| 👁️ **Visión de Pantalla** | Procesamiento en tiempo real de la pantalla y cámara web. |
| 🧠 **Memoria Persistente** | Recuerda preferencias y proyectos entre sesiones. |
| 🎨 **Interfaz Cyberpunk HUD** | Panel de control personalizable y dinámico. |
| 📂 **Carga de Archivos** | Arrastrar y soltar PDFs, imágenes o código para análisis. |

---

## ⚡ Instalación y Configuración
Sigue estos pasos para poner tu MARK XL en marcha en Windows 10/11.

### 1. Clonar el repositorio
```bash
git clone <ENLACE_DE_GITHUB>
cd update-mk40
```

### 2. Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

### 3. Instalar controladores de Playwright
```bash
playwright install
```

### 4. Configurar claves de API
1. Copia `config/api_keys.json.example` a `config/api_keys.json`.
2. Introduce tus claves en el archivo.

```json
{
  "gemini_api_key": "TU_API_KEY_AQUÍ",
  "openrouter_api_key": "OPCIONAL_TU_OPENROUTER_KEY"
}
```

### 5. Instalar motores de voz locales (Whisper & Piper)
```bash
python download_engines.py
```

---

## 🚀 Uso del Asistente
```bash
python main.py
```

---

## 🤝 Contribuir
1. Haz fork del repositorio.  
2. Crea una rama para tu característica o corrección.  
3. Ejecuta `python main.py` y verifica los cambios.  
4. Abre un Pull Request describiendo tu aporte.

---

## 📜 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---