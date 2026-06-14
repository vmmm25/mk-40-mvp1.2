---
name: discord
version: 1.0.0
description: Integración con Discord para enviar mensajes, leer canales, gestionar servidores y automatizar notificaciones. Usa cuando necesites que el agente interactúe con servidores Discord.
tags: [discord, messaging, bots, automation, notifications, gaming, community]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Discord Skill

## Configuración

```bash
# pip install discord.py
# Variables de entorno
DISCORD_BOT_TOKEN=...          # Bot Token desde Discord Developer Portal
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...  # Para mensajes simples
```

## Opción 1: Webhook (enviar mensajes sin bot)

```python
import requests
import os

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_message(
    content: str = None,
    username: str = None,         # Override del nombre del webhook
    avatar_url: str = None,       # Override del avatar
    embeds: list = None,          # Rich embeds
) -> bool:
    payload = {}
    if content:
        payload["content"] = content
    if username:
        payload["username"] = username
    if avatar_url:
        payload["avatar_url"] = avatar_url
    if embeds:
        payload["embeds"] = embeds

    response = requests.post(WEBHOOK_URL, json=payload)
    return response.status_code in (200, 204)

# Mensaje simple
send_discord_message("✅ Build pasado correctamente")

# Con embed rico
send_discord_message(embeds=[{
    "title": "🚨 Alerta de Seguridad",
    "description": "Intento de acceso sospechoso detectado",
    "color": 15158332,  # Rojo
    "fields": [
        {"name": "IP", "value": "1.2.3.4", "inline": True},
        {"name": "País", "value": "RU", "inline": True},
        {"name": "Intentos", "value": "47 en 5 min", "inline": True},
    ],
    "timestamp": "2025-01-01T12:00:00.000Z",
    "footer": {"text": "Security Monitor"}
}])
```

## Opción 2: discord.py (bot completo)

```python
import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ── EVENTOS ───────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignorar mensajes propios
    
    if "hola" in message.content.lower():
        await message.channel.send(f"¡Hola {message.author.mention}!")
    
    await bot.process_commands(message)  # Procesar comandos también


# ── COMANDOS ──────────────────────────────────────────────────────────────
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latencia: {round(bot.latency * 1000)}ms")

@bot.command(name="resumen")
async def resumen(ctx, *, tema: str):
    await ctx.send(f"📝 Generando resumen sobre: **{tema}**...")
    # Aquí llamarías a tu LLM...
    summary = f"Resumen de {tema}: ..."
    await ctx.send(summary)

@bot.command(name="ayuda")
async def ayuda(ctx):
    embed = discord.Embed(
        title="Comandos disponibles",
        color=discord.Color.blue()
    )
    embed.add_field(name="!ping", value="Verificar latencia del bot")
    embed.add_field(name="!resumen [tema]", value="Generar resumen de un tema")
    await ctx.send(embed=embed)


# ── ENVIAR MENSAJES PROGRAMÁTICAMENTE ─────────────────────────────────────
async def send_to_channel(channel_id: int, message: str):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)

async def send_to_user(user_id: int, message: str):
    user = await bot.fetch_user(user_id)
    if user:
        await user.send(message)  # DM


# ── LEER HISTORIAL ────────────────────────────────────────────────────────
async def get_channel_history(channel_id: int, limit: int = 50) -> list:
    channel = bot.get_channel(channel_id)
    messages = []
    async for msg in channel.history(limit=limit):
        messages.append({
            "author": str(msg.author),
            "content": msg.content,
            "timestamp": msg.created_at.isoformat(),
        })
    return messages


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
```

## discord.py sin bot (solo leer/enviar con token de usuario — user self-bot)

```python
# IMPORTANTE: Los self-bots pueden violar los ToS de Discord.
# Usar solo para bots propios con token de bot, no de usuario.

# Para enviar desde un script sin bot corriendo, usa webhooks
# o crea un async context:

import asyncio
import discord

async def send_once(channel_id: int, message: str):
    """Enviar un mensaje y desconectar (útil para scripts)"""
    client = discord.Client(intents=discord.Intents.default())
    
    @client.event
    async def on_ready():
        channel = client.get_channel(channel_id)
        await channel.send(message)
        await client.close()
    
    await client.start(os.getenv("DISCORD_BOT_TOKEN"))

# Ejecutar desde script síncrono:
asyncio.run(send_once(CHANNEL_ID, "Mensaje enviado!"))
```

## Slash commands (Discord moderno)

```python
import discord
from discord import app_commands

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        await self.tree.sync()  # Registrar slash commands

bot = MyBot()

@bot.tree.command(name="estado", description="Ver estado del sistema")
async def estado(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=discord.Embed(
            title="Estado del sistema",
            description="✅ Todos los servicios operativos",
            color=discord.Color.green()
        )
    )
```

## Referencias
- [discord.py docs](https://discordpy.readthedocs.io/) — Librería principal
- [Discord Developer Portal](https://discord.com/developers/applications) — Crear bots
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook) — Webhooks API
- [Block Kit equivalente (Embeds)](https://discordpy.readthedocs.io/en/stable/api.html#discord.Embed) — Rich embeds
