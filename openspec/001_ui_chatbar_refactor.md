# SDD: Refactorización de UI/UX (Chat Bar y Controles)

**Estado:** PLANIFICACIÓN (Esperando respuestas)
**Modo de Ejecución:** Interactivo (A1)
**Límite de Revisión:** 400 líneas (D1)

## Contexto
El objetivo es transformar la UI actual de JARVIS para llevarla a un nivel "end-user ready", eliminando el `FileDropZone` invasivo y las filas masivas de selectores de modelos, consolidándolos en una barra de chat (Chat Bar) inteligente y auto-expandible.

## Preguntas Abiertas (Esperando al usuario)
1. **Auto-expandible**: ¿Tope de altura (ej: 150px) con scroll vertical a partir de ahí, o crecimiento infinito?
2. **Selectores (Agente, Modelo, Pensamiento)**: ¿Flotando adentro de la caja de texto o como una mini-barra arriba?
3. **Panel de Permisos**: ¿Botón en el chat bar que abre un popover flotante, o un dock lateral?

## Plan de Implementación
### 1. `ui/components/chat_bar.py` (NUEVO)
Extracción de toda la lógica de entrada de comandos y texto para no sobrecargar `main_window.py`.
- `AutoExpandingTextEdit`: Reemplaza a `QLineEdit`.
- `AttachmentMenu`: Reemplaza al cuadrado gigante de DropZone por un menú flotante con ícono de clip.
- Controles agrupados y limpios.

### 2. `ui/main_window.py` (MODIFICAR)
- Limpieza masiva de la columna derecha (`chat_col`).
- Eliminación de la fila dedicada a `_provider_lbl` y `_right_model_combo`.
- Eliminación del `_drop_zone` y reestructuración del layout inferior.
- Inyección del nuevo `ChatBarWidget`.
