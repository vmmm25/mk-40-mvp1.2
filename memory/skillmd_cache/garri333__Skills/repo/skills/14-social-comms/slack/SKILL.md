---
name: slack
version: 1.0.0
description: Integración con Slack para enviar mensajes, leer canales y automatizar notificaciones desde el agente. Usa cuando necesites que el agente interactúe con tu workspace de Slack.
tags: [slack, messaging, automation, webhooks, api, notifications, team]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Slack Skill

## Configuración

```bash
# Variables de entorno necesarias
SLACK_BOT_TOKEN=xoxb-...           # Bot Token (para Slack API)
SLACK_WEBHOOK_URL=https://hooks... # Webhook (para notificaciones simples)
SLACK_SIGNING_SECRET=...           # Para verificar eventos
```

## Opción 1: Webhook simple (enviar mensajes)

```python
import requests
import os

WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_message(
    text: str = None,
    blocks: list = None,
    channel: str = None,  # Solo si el webhook lo permite
) -> bool:
    payload = {}
    if text:
        payload["text"] = text
    if blocks:
        payload["blocks"] = blocks
    if channel:
        payload["channel"] = channel

    response = requests.post(WEBHOOK_URL, json=payload)
    return response.status_code == 200

# Uso simple
send_slack_message("✅ Deploy completado en producción")

# Con formato rico (Block Kit)
send_slack_message(blocks=[
    {
        "type": "header",
        "text": {"type": "plain_text", "text": "🚨 Alerta de Seguridad"}
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Anomalía detectada* en el servidor `web-01`\n• IP sospechosa: `1.2.3.4`\n• Intentos: 47 en 5 min"
        }
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Ver logs"},
                "url": "https://my-logs.com/web-01"
            }
        ]
    }
])
```

## Opción 2: Slack SDK (lectura + escritura completa)

```python
# pip install slack_sdk
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))


# ── ENVIAR ────────────────────────────────────────────────────────────────
def send_message(channel: str, text: str, thread_ts: str = None) -> dict:
    return client.chat_postMessage(
        channel=channel,
        text=text,
        thread_ts=thread_ts  # Para responder en hilo
    )

# Enviar con archivo adjunto
def send_file(channel: str, file_path: str, title: str = "") -> dict:
    return client.files_upload_v2(
        channel=channel,
        file=file_path,
        title=title
    )


# ── LEER ──────────────────────────────────────────────────────────────────
def get_channel_history(channel: str, limit: int = 20) -> list:
    """Obtener mensajes recientes de un canal"""
    result = client.conversations_history(channel=channel, limit=limit)
    return result["messages"]

def get_thread_replies(channel: str, thread_ts: str) -> list:
    result = client.conversations_replies(channel=channel, ts=thread_ts)
    return result["messages"]

def search_messages(query: str, count: int = 10) -> list:
    result = client.search_messages(query=query, count=count)
    return result["messages"]["matches"]


# ── CANALES ───────────────────────────────────────────────────────────────
def list_channels() -> list:
    result = client.conversations_list(types="public_channel,private_channel")
    return [{"name": c["name"], "id": c["id"]} for c in result["channels"]]

def get_channel_id(name: str) -> str | None:
    channels = list_channels()
    for c in channels:
        if c["name"] == name:
            return c["id"]
    return None


# ── USUARIOS ──────────────────────────────────────────────────────────────
def get_user_info(user_id: str) -> dict:
    result = client.users_info(user=user_id)
    return result["user"]

def list_members(channel: str) -> list:
    result = client.conversations_members(channel=channel)
    return result["members"]
```

## Notificaciones automáticas comunes

```python
def notify_deploy(env: str, version: str, status: str, author: str):
    emoji = "✅" if status == "success" else "❌"
    send_message(
        channel="#deployments",
        text=f"{emoji} Deploy *{version}* en `{env}` por {author}: *{status}*"
    )

def notify_error(error_msg: str, file: str, line: int):
    send_message(
        channel="#alerts",
        text=f"🔴 Error en `{file}:{line}`\n```{error_msg}```"
    )

def daily_summary(metrics: dict):
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "📊 Resumen diario"}},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*Usuarios:* {metrics.get('users', 0)}"},
            {"type": "mrkdwn", "text": f"*Conversiones:* {metrics.get('conversions', 0)}"},
            {"type": "mrkdwn", "text": f"*Revenue:* ${metrics.get('revenue', 0):,.2f}"},
            {"type": "mrkdwn", "text": f"*Errores:* {metrics.get('errors', 0)}"},
        ]}
    ]
    send_slack_message(blocks=blocks)
```

## Escuchar eventos (Bot receptor)

```python
# pip install slack_bolt
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@app.message("hola")
def handle_hello(message, say):
    say(f"¡Hola <@{message['user']}>!")

@app.command("/resume")
def handle_resume(ack, body, say):
    ack()
    say(f"*Resumen generado para:* {body['text']}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
```

## Referencias
- [Slack SDK Python](https://slack.dev/python-slack-sdk/) — SDK oficial
- [Slack Block Kit Builder](https://app.slack.com/block-kit-builder) — UI visual para bloques
- [Slack API docs](https://api.slack.com/methods) — Referencia completa de métodos
