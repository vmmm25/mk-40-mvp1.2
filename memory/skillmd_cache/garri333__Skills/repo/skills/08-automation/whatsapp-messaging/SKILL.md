---
name: whatsapp-messaging
version: 1.0.0
description: Enviar mensajes de WhatsApp desde un agente usando Wacli o la WhatsApp Business API. Usa cuando necesites enviar notificaciones, alertas, o mensajes programáticos por WhatsApp.
tags: [whatsapp, messaging, automation, notifications, wacli, business-api]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# WhatsApp Messaging Skill

## Cuándo usar esta skill
- Enviar notificaciones o alertas por WhatsApp desde un agente
- Automatizar mensajes recurrentes
- Enviar reportes o resúmenes por WhatsApp
- Integraciones de WhatsApp en flujos de trabajo

## Opciones disponibles

| Opción | Tipo | Ideal para |
|--------|------|-----------|
| WhatsApp Business API (Meta) | Oficial | Empresas, alta escala |
| wacli (CLI unofficial) | Librería unofficial | Personal, desarrollo, testing |
| Twilio WhatsApp | Oficial (tercero) | Desarrollo rápido, escala media |
| wa-web.js | Unofficial web | Automatización personal |

## Opción 1: wacli (WhatsApp CLI)

```bash
# Instalar wacli
npm install -g wacli

# Primera configuración — escanear QR
wacli auth
# Abre el QR para escanear con WhatsApp en el móvil

# Enviar mensaje
wacli send --to "34612345678" --message "Hola! Mensaje enviado con wacli"

# Enviar a grupo (usar el JID del grupo)
wacli send --to "123456789@g.us" --message "Hola grupo!"

# Enviar archivo
wacli send --to "34612345678" --file "/ruta/al/reporte.pdf" --caption "Aquí tu reporte"

# Listar conversaciones
wacli list chats

# Listar grupos
wacli list groups
```

## Opción 2: WhatsApp Business API (oficial)

### Setup
```bash
# Necesitas:
# 1. Cuenta Meta Business
# 2. App en Meta Developers (https://developers.facebook.com/)
# 3. WhatsApp Business Account
# 4. Número de teléfono verificado

export WHATSAPP_TOKEN="tu-access-token"
export WHATSAPP_PHONE_ID="tu-phone-number-id"
```

### Enviar mensaje de texto
```python
import requests
import os

def send_whatsapp_message(to_number: str, message: str) -> dict:
    """
    Enviar mensaje de texto por WhatsApp Business API
    
    Args:
        to_number: Número en formato internacional sin + (ej: "34612345678")
        message: Texto del mensaje
    """
    token = os.environ["WHATSAPP_TOKEN"]
    phone_id = os.environ["WHATSAPP_PHONE_ID"]
    
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    response.raise_for_status()
    return response.json()
```

### Enviar plantilla (template message)
```python
def send_template_message(
    to_number: str, 
    template_name: str,
    language: str = "es",
    components: list = None
) -> dict:
    """
    Enviar un template pre-aprobado por Meta
    Los templates son obligatorios para iniciar conversaciones
    """
    token = os.environ["WHATSAPP_TOKEN"]
    phone_id = os.environ["WHATSAPP_PHONE_ID"]
    
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        }
    }
    
    if components:
        payload["template"]["components"] = components
    
    response = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()


# Ejemplo con variables en el template
# Template: "Hola {{1}}, tu pedido {{2}} está listo."
send_template_message(
    to_number="34612345678",
    template_name="pedido_listo",
    components=[
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": "María"},
                {"type": "text", "text": "#12345"}
            ]
        }
    ]
)
```

### Enviar imagen
```python
def send_image(to_number: str, image_url: str, caption: str = "") -> dict:
    token = os.environ["WHATSAPP_TOKEN"]
    phone_id = os.environ["WHATSAPP_PHONE_ID"]
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    
    response = requests.post(
        f"https://graph.facebook.com/v18.0/{phone_id}/messages",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()
```

## Opción 3: Twilio WhatsApp

```python
from twilio.rest import Client

client = Client(
    os.environ["TWILIO_ACCOUNT_SID"],
    os.environ["TWILIO_AUTH_TOKEN"]
)

def send_via_twilio(to_number: str, message: str) -> str:
    """
    Enviar mensaje de WhatsApp con Twilio
    Sandbox gratuito disponible para testing
    """
    msg = client.messages.create(
        from_=f"whatsapp:+14155238886",  # Número de Twilio sandbox
        to=f"whatsapp:+{to_number}",
        body=message
    )
    return msg.sid
```

## Casos de uso comunes

### Alertas de sistema
```python
import functools

def alert_on_error(whatsapp_number: str):
    """Decorator para enviar alerta si una función falla"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                send_whatsapp_message(
                    whatsapp_number,
                    f"⚠️ ERROR en {func.__name__}:\n{str(e)[:500]}"
                )
                raise
        return wrapper
    return decorator

# Uso:
@alert_on_error("34612345678")
def proceso_critico():
    # Si esta función falla, recibes WhatsApp
    ...
```

### Reporte diario
```python
from datetime import date
import schedule
import time

def send_daily_report():
    today = date.today().strftime("%d/%m/%Y")
    
    # Recopilar datos del día
    stats = get_daily_stats()
    
    message = f"""📊 *Reporte diario — {today}*

👥 Usuarios nuevos: {stats['new_users']}
💰 Ventas: {stats['sales']}€
🔄 Conversiones: {stats['conversion_rate']:.1%}

{'✅ Todo bien' if stats['errors'] == 0 else f'⚠️ {stats["errors"]} errores detectados'}"""
    
    send_whatsapp_message("34612345678", message)

# Programar
schedule.every().day.at("09:00").do(send_daily_report)
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Limitaciones y consideraciones

```
⚠️  WhatsApp Business API: Solo se pueden iniciar conversaciones con templates pre-aprobados
⚠️  wacli: Es unofficial — puede dejar de funcionar con updates de WhatsApp
⚠️  Límites: WhatsApp limita el número de mensajes por día según el tier
⚠️  Política: No usar para spam. Los usuarios pueden reportar y tu número se baneará
⚠️  GDPR: En Europa, necesitas consentimiento explícito antes de enviar mensajes

Buenas prácticas:
✅ Solo enviar a usuarios que hayan dado consentimiento explícito
✅ Siempre incluir opción de cancelar suscripción
✅ No enviar más de 1-2 mensajes por semana si no es urgente
✅ Usar templates para mensajes de marketing
```

## Referencias
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Twilio WhatsApp](https://www.twilio.com/whatsapp)
- [wacli GitHub](https://github.com/nicholasgasior/wacli)
