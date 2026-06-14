---
name: bird
version: 1.0.0
description: X/Twitter CLI para leer, buscar y publicar tweets via cookies de sesión o Sweetistics API. Usa cuando necesites automatizar acciones en X/Twitter desde el agente.
tags: [twitter, x, social-media, cli, automation, bird]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Bird — X/Twitter CLI

## Instalación

```bash
npm install -g @sweetistics/bird
# O con Clawdbot
clawdhub install bird
```

## Autenticación

```bash
# Opción 1: Con cookies de sesión (no requiere API key)
bird auth --cookies "auth_token=...; ct0=..."

# Opción 2: Con API key de Sweetistics
bird auth --api-key YOUR_SWEETISTICS_KEY

# Verificar autenticación
bird whoami
```

## Comandos principales

```bash
# Timeline
bird timeline              # Tu home timeline
bird timeline --limit 20   # Últimos 20 tweets

# Buscar
bird search "prompt engineering AI 2025"
bird search "@garri333" --type user
bird search "#claude" --limit 50 --media

# Ver perfil
bird profile @username
bird profile me

# Publicar
bird tweet "Texto del tweet"
bird tweet "Tweet con imagen" --media /ruta/imagen.jpg
bird tweet --reply TWEET_ID "Respuesta"
bird retweet TWEET_ID
bird like TWEET_ID

# DMs
bird dm list                        # Lista de conversaciones
bird dm read USERNAME                # Ver mensajes con usuario
bird dm send USERNAME "Mensaje"      # Enviar DM

# Notificaciones
bird notifications               # Menciones, likes, RTs
bird notifications --type mentions  # Solo menciones
```

## Búsqueda avanzada

```bash
# Operadores de búsqueda
bird search "from:elonmusk since:2025-01-01"
bird search "python AI -filter:retweets min_faves:100"
bird search "site:github.com agent skills"

# Exportar resultados
bird search "llm agents" --format json --output tweets.json
bird search "llm agents" --format csv --output tweets.csv
```

## Automatización con Python

```python
import subprocess
import json

def search_twitter(query: str, limit: int = 20) -> list:
    result = subprocess.run(
        ["bird", "search", query, "--limit", str(limit), "--format", "json"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def post_tweet(text: str, media_path: str = None) -> dict:
    cmd = ["bird", "tweet", text]
    if media_path:
        cmd.extend(["--media", media_path])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

# Monitorizar menciones cada 5 minutos
import time

def monitor_mentions(callback, interval_seconds=300):
    seen = set()
    while True:
        result = subprocess.run(
            ["bird", "notifications", "--type", "mentions", "--format", "json"],
            capture_output=True, text=True
        )
        mentions = json.loads(result.stdout)
        for mention in mentions:
            if mention["id"] not in seen:
                seen.add(mention["id"])
                callback(mention)
        time.sleep(interval_seconds)
```

## Casos de uso

```bash
# Publicar resumen diario automático
bird tweet "$(cat daily-summary.md | head -5)"

# Monitorizar hashtag y guardar
bird search "#cybersecurity" --since yesterday --format json >> security-mentions.jsonl

# Programar tweet (con at/cron)
echo 'bird tweet "Buenos días!"' | at 09:00

# Cross-posting desde LinkedIn content
bird tweet "$(cat linkedin-post.md | head -2)... 🧵"
```

## Referencias
- [Sweetistics Bird CLI](https://sweetistics.com/) — CLI oficial
- [X/Twitter API v2](https://developer.twitter.com/en/docs/twitter-api) — Para uso con API key
