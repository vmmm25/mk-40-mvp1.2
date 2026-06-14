---
name: openclaw-messaging
version: 1.0.0
description: Integración de mensajería multiplataforma — Google Messages, Lark, Slack, Discord, Microsoft Teams. Envío, lectura, gestión de hilos, notificaciones, templates, webhooks, bots, canales, archivos, reacciones y mensajes programados.
tags: [openclaw, messaging, slack, discord, teams, lark, google-messages, webhooks, bots, notifications, cross-platform]
author: garri333
license: MIT
source: VoltAgent/awesome-openclaw-skills
---

# OpenClaw Messaging Skill

> Integración de mensajería cross-platform para agentes autónomos. Soporte para Google Messages, Lark, Slack, Discord y Microsoft Teams con API unificada.

## Cuándo activar

- Cuando el agente necesita **enviar notificaciones** sobre eventos del proyecto
- Cuando se requiere **integración con canales de comunicación** del equipo
- Cuando hay que **monitorizar mensajes** y responder automáticamente
- Cuando se necesita **routing de notificaciones** a diferentes plataformas según contexto
- Cuando se crean **bots** para automatización de comunicación
- Cuando hay que gestionar **hilos de conversación** desde el agente
- Cuando se requieren **mensajes programados** o template-based
- Cuando el agente debe **compartir archivos o reportes** en canales de equipo

## Instrucciones paso a paso

### 1. Configuración de plataformas

```yaml
# .openclaw/messaging/config.yaml
messaging:
  platforms:
    slack:
      enabled: true
      bot_token: "${SLACK_BOT_TOKEN}"
      app_token: "${SLACK_APP_TOKEN}"
      signing_secret: "${SLACK_SIGNING_SECRET}"
      default_channel: "#dev-notifications"
      
    discord:
      enabled: true
      bot_token: "${DISCORD_BOT_TOKEN}"
      guild_id: "${DISCORD_GUILD_ID}"
      default_channel: "dev-updates"
      
    teams:
      enabled: true
      tenant_id: "${TEAMS_TENANT_ID}"
      client_id: "${TEAMS_CLIENT_ID}"
      client_secret: "${TEAMS_CLIENT_SECRET}"
      default_channel: "General"
      
    lark:
      enabled: false
      app_id: "${LARK_APP_ID}"
      app_secret: "${LARK_APP_SECRET}"
      
    google_messages:
      enabled: false
      service_account: "${GOOGLE_SA_PATH}"
      agent_id: "${GOOGLE_AGENT_ID}"

  # Routing: qué notificaciones van a qué plataforma
  routing:
    - event: "deploy_success"
      platforms: ["slack", "discord"]
      channel_override: "#deployments"
    - event: "build_failure"
      platforms: ["slack", "teams"]
      channel_override: "#alerts"
      priority: "urgent"
    - event: "daily_report"
      platforms: ["slack"]
      scheduled: "09:00 UTC"
    - event: "pr_review_request"
      platforms: ["slack", "discord"]
```

### 2. API unificada de mensajería

```python
class UnifiedMessenger:
    """
    API unificada para enviar mensajes a cualquier plataforma.
    Abstrae las diferencias entre Slack, Discord, Teams, etc.
    """
    
    def __init__(self, config_path: str = ".openclaw/messaging/config.yaml"):
        self.config = load_config(config_path)
        self.adapters = self._init_adapters()
    
    def _init_adapters(self) -> dict[str, PlatformAdapter]:
        adapters = {}
        if self.config["slack"]["enabled"]:
            adapters["slack"] = SlackAdapter(self.config["slack"])
        if self.config["discord"]["enabled"]:
            adapters["discord"] = DiscordAdapter(self.config["discord"])
        if self.config["teams"]["enabled"]:
            adapters["teams"] = TeamsAdapter(self.config["teams"])
        if self.config["lark"]["enabled"]:
            adapters["lark"] = LarkAdapter(self.config["lark"])
        if self.config["google_messages"]["enabled"]:
            adapters["google_messages"] = GoogleMessagesAdapter(
                self.config["google_messages"]
            )
        return adapters
    
    # ── Envío de mensajes ──────────────────────────────────
    
    def send_message(
        self,
        text: str,
        platform: str = None,
        channel: str = None,
        thread_id: str = None,
        attachments: list = None,
        format: str = "markdown"
    ) -> MessageResult:
        """
        Envía mensaje a una o todas las plataformas configuradas.
        
        Args:
            text: Contenido del mensaje (markdown o plain)
            platform: Plataforma específica o None para todas
            channel: Canal/grupo. None = default
            thread_id: ID de hilo para respuesta en thread
            attachments: Lista de archivos adjuntos
            format: 'markdown' | 'plain' | 'rich'
        """
        targets = [platform] if platform else list(self.adapters.keys())
        results = []
        
        for target in targets:
            adapter = self.adapters[target]
            
            # Convertir formato según plataforma
            formatted_text = self.format_for_platform(text, target, format)
            
            # Resolver canal
            resolved_channel = channel or self.config[target].get("default_channel")
            
            result = adapter.send(
                text=formatted_text,
                channel=resolved_channel,
                thread_id=thread_id,
                attachments=attachments
            )
            results.append(result)
        
        return MessageResult(
            success=all(r.success for r in results),
            platform_results=results,
            message_ids={r.platform: r.message_id for r in results}
        )
    
    # ── Lectura de mensajes ────────────────────────────────
    
    def read_messages(
        self,
        platform: str,
        channel: str,
        limit: int = 50,
        since: datetime = None,
        thread_id: str = None
    ) -> list[Message]:
        """Lee mensajes de un canal o hilo."""
        adapter = self.adapters[platform]
        
        messages = adapter.fetch_messages(
            channel=channel,
            limit=limit,
            since=since,
            thread_id=thread_id
        )
        
        # Normalizar a formato unificado
        return [
            Message(
                id=msg.id,
                platform=platform,
                channel=channel,
                author=msg.author,
                content=msg.content,
                timestamp=msg.timestamp,
                thread_id=msg.thread_id,
                reactions=msg.reactions,
                attachments=msg.attachments,
                is_bot=msg.is_bot
            )
            for msg in messages
        ]
    
    # ── Gestión de hilos ───────────────────────────────────
    
    def create_thread(
        self,
        platform: str,
        channel: str,
        title: str,
        initial_message: str
    ) -> Thread:
        """Crea un nuevo hilo de conversación."""
        adapter = self.adapters[platform]
        
        # Enviar mensaje inicial (que se convierte en parent del thread)
        result = adapter.send(
            text=f"**{title}**\n\n{initial_message}",
            channel=channel
        )
        
        return Thread(
            id=result.message_id,
            platform=platform,
            channel=channel,
            title=title,
            created_at=datetime.utcnow()
        )
    
    def reply_to_thread(
        self,
        platform: str,
        channel: str,
        thread_id: str,
        text: str
    ) -> MessageResult:
        """Responde dentro de un hilo existente."""
        return self.send_message(
            text=text,
            platform=platform,
            channel=channel,
            thread_id=thread_id
        )
```

### 3. Adaptadores por plataforma

```python
class SlackAdapter(PlatformAdapter):
    """Adaptador para Slack Web API."""
    
    def __init__(self, config: dict):
        self.client = WebClient(token=config["bot_token"])
    
    def send(self, text: str, channel: str, thread_id: str = None,
             attachments: list = None) -> PlatformResult:
        try:
            payload = {
                "channel": channel,
                "text": text,
                "mrkdwn": True,
            }
            if thread_id:
                payload["thread_ts"] = thread_id
            if attachments:
                payload["attachments"] = self._format_attachments(attachments)
            
            response = self.client.chat_postMessage(**payload)
            
            return PlatformResult(
                success=True,
                platform="slack",
                message_id=response["ts"],
                channel=channel
            )
        except SlackApiError as e:
            return PlatformResult(
                success=False,
                platform="slack",
                error=str(e)
            )
    
    def add_reaction(self, channel: str, message_ts: str, emoji: str):
        self.client.reactions_add(
            channel=channel,
            timestamp=message_ts,
            name=emoji  # e.g., "white_check_mark"
        )
    
    def upload_file(self, channel: str, file_path: str, title: str = None):
        self.client.files_upload_v2(
            channel=channel,
            file=file_path,
            title=title or os.path.basename(file_path)
        )


class DiscordAdapter(PlatformAdapter):
    """Adaptador para Discord Bot API."""
    
    def __init__(self, config: dict):
        self.token = config["bot_token"]
        self.guild_id = config["guild_id"]
        self.base_url = "https://discord.com/api/v10"
        self.headers = {"Authorization": f"Bot {self.token}"}
    
    def send(self, text: str, channel: str, thread_id: str = None,
             attachments: list = None) -> PlatformResult:
        channel_id = self._resolve_channel(channel)
        target = thread_id or channel_id
        
        payload = {"content": self._markdown_to_discord(text)}
        
        if attachments:
            return self._send_with_files(target, payload, attachments)
        
        response = requests.post(
            f"{self.base_url}/channels/{target}/messages",
            headers=self.headers,
            json=payload
        )
        
        if response.ok:
            data = response.json()
            return PlatformResult(
                success=True,
                platform="discord",
                message_id=data["id"],
                channel=channel
            )
        return PlatformResult(success=False, platform="discord", error=response.text)
    
    def create_thread(self, channel: str, name: str, message_id: str = None):
        channel_id = self._resolve_channel(channel)
        
        if message_id:
            # Thread desde mensaje existente
            response = requests.post(
                f"{self.base_url}/channels/{channel_id}/messages/{message_id}/threads",
                headers=self.headers,
                json={"name": name, "auto_archive_duration": 1440}
            )
        else:
            # Thread standalone
            response = requests.post(
                f"{self.base_url}/channels/{channel_id}/threads",
                headers=self.headers,
                json={"name": name, "type": 11, "auto_archive_duration": 1440}
            )
        
        return response.json()


class TeamsAdapter(PlatformAdapter):
    """Adaptador para Microsoft Teams via Graph API."""
    
    def __init__(self, config: dict):
        self.tenant_id = config["tenant_id"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.token = self._get_token()
    
    def send(self, text: str, channel: str, thread_id: str = None,
             attachments: list = None) -> PlatformResult:
        team_id, channel_id = self._resolve_channel(channel)
        
        url = (
            f"https://graph.microsoft.com/v1.0/teams/{team_id}"
            f"/channels/{channel_id}/messages"
        )
        
        if thread_id:
            url += f"/{thread_id}/replies"
        
        payload = {
            "body": {
                "contentType": "html",
                "content": self._markdown_to_html(text)
            }
        }
        
        response = requests.post(
            url, 
            headers={"Authorization": f"Bearer {self.token}"},
            json=payload
        )
        
        if response.ok:
            data = response.json()
            return PlatformResult(
                success=True,
                platform="teams",
                message_id=data["id"],
                channel=channel
            )
        return PlatformResult(success=False, platform="teams", error=response.text)
```

### 4. Notificación routing

```python
class NotificationRouter:
    """Enruta notificaciones a las plataformas correctas según reglas."""
    
    def __init__(self, messenger: UnifiedMessenger, config: dict):
        self.messenger = messenger
        self.rules = config.get("routing", [])
    
    def route_notification(
        self, 
        event: str, 
        data: dict, 
        template: str = None
    ):
        """
        Enruta una notificación basándose en las reglas configuradas.
        
        Args:
            event: Tipo de evento (deploy_success, build_failure, etc.)
            data: Datos del evento para templates
            template: Template de mensaje a usar
        """
        matching_rules = [r for r in self.rules if r["event"] == event]
        
        if not matching_rules:
            # Default: enviar al canal default de todas las plataformas
            self.messenger.send_message(
                text=self.format_notification(event, data, template)
            )
            return
        
        for rule in matching_rules:
            message = self.format_notification(event, data, template)
            
            for platform in rule["platforms"]:
                self.messenger.send_message(
                    text=message,
                    platform=platform,
                    channel=rule.get("channel_override")
                )
    
    def format_notification(
        self, event: str, data: dict, template: str = None
    ) -> str:
        if template:
            return self.render_template(template, data)
        
        # Templates por defecto
        default_templates = {
            "deploy_success": (
                "✅ **Deploy exitoso**\n"
                "- Entorno: {environment}\n"
                "- Versión: {version}\n"
                "- Commit: `{commit_sha}`\n"
                "- Duración: {duration}s"
            ),
            "build_failure": (
                "❌ **Build fallido**\n"
                "- Branch: {branch}\n"
                "- Error: ```{error_message}```\n"
                "- Pipeline: {pipeline_url}"
            ),
            "pr_review_request": (
                "👀 **PR pendiente de review**\n"
                "- [{pr_title}]({pr_url})\n"
                "- Autor: {author}\n"
                "- Files changed: {files_changed}"
            ),
        }
        
        tmpl = default_templates.get(event, "📌 **{event}**: {summary}")
        return tmpl.format(event=event, **data)
```

### 5. Template-based messaging

```yaml
# .openclaw/messaging/templates.yaml
templates:
  daily_standup:
    format: markdown
    content: |
      🌅 **Daily Standup — {date}**
      
      **Completado ayer:**
      {completed_items}
      
      **Plan para hoy:**
      {planned_items}
      
      **Blockers:**
      {blockers}
  
  release_notes:
    format: markdown
    content: |
      🚀 **Release {version}** — {date}
      
      **Nuevas features:**
      {features}
      
      **Bug fixes:**
      {fixes}
      
      **Breaking changes:**
      {breaking_changes}
  
  incident_alert:
    format: markdown
    priority: urgent
    content: |
      🚨 **INCIDENCIA — Severidad: {severity}**
      
      **Servicio afectado:** {service}
      **Inicio:** {start_time}
      **Impacto:** {impact}
      **Estado:** {status}
      
      **Acciones tomadas:**
      {actions}
```

```python
class TemplateRenderer:
    """Renderiza templates para mensajería."""
    
    def render(self, template_name: str, data: dict) -> str:
        templates = load_yaml(".openclaw/messaging/templates.yaml")
        template = templates["templates"][template_name]
        
        content = template["content"]
        
        # Renderizar listas
        for key, value in data.items():
            if isinstance(value, list):
                formatted_list = "\n".join(f"  - {item}" for item in value)
                data[key] = formatted_list if formatted_list else "  _Ninguno_"
        
        return content.format(**data)
```

### 6. Webhooks y bots

```python
class WebhookManager:
    """Gestiona webhooks entrantes y salientes."""
    
    def register_webhook(
        self,
        platform: str,
        event: str,
        callback_url: str,
        filters: dict = None
    ):
        """Registra un webhook para eventos de una plataforma."""
        webhook = {
            "id": generate_id(),
            "platform": platform,
            "event": event,
            "callback_url": callback_url,
            "filters": filters or {},
            "created_at": datetime.utcnow().isoformat(),
            "active": True
        }
        save_webhook(webhook)
        return webhook
    
    def handle_incoming_webhook(self, platform: str, payload: dict):
        """Procesa webhook entrante de una plataforma."""
        # Verificar firma/autenticación
        if not self.verify_signature(platform, payload):
            raise SecurityError("Invalid webhook signature")
        
        # Parsear evento
        event = self.parse_event(platform, payload)
        
        # Ejecutar handlers registrados
        handlers = get_handlers(platform, event.type)
        for handler in handlers:
            handler(event)


class BotBuilder:
    """Creación de bots para plataformas de mensajería."""
    
    def create_slash_command(
        self,
        platform: str,
        command: str,
        description: str,
        handler: Callable
    ):
        """Registra un slash command en la plataforma."""
        adapter = self.adapters[platform]
        
        adapter.register_command(
            name=command,
            description=description,
        )
        
        self.command_handlers[f"/{command}"] = handler
    
    def handle_command(self, platform: str, command_data: dict):
        """Procesa un slash command recibido."""
        command = command_data["command"]
        args = command_data.get("text", "")
        user = command_data["user"]
        
        handler = self.command_handlers.get(command)
        if handler:
            response = handler(args=args, user=user, platform=platform)
            return response
        
        return "Comando no reconocido"
```

### 7. Mensajes programados

```python
class ScheduledMessages:
    """Gestión de mensajes programados."""
    
    def schedule_message(
        self,
        text: str,
        platform: str,
        channel: str,
        send_at: datetime,
        recurrence: str = None,  # "daily", "weekly", "cron:0 9 * * 1-5"
        template: str = None,
        data_source: Callable = None  # Función que genera data dinámica
    ) -> ScheduledMessage:
        scheduled = ScheduledMessage(
            id=generate_id(),
            text=text,
            platform=platform,
            channel=channel,
            send_at=send_at,
            recurrence=recurrence,
            template=template,
            data_source=data_source.__name__ if data_source else None,
            status="scheduled"
        )
        save_scheduled(scheduled)
        return scheduled
    
    def process_due_messages(self):
        """Ejecuta mensajes cuyo tiempo ha llegado."""
        due = get_due_messages(datetime.utcnow())
        
        for msg in due:
            # Si tiene data_source dinámica, generar datos frescos
            if msg.data_source:
                data = invoke_data_source(msg.data_source)
                text = TemplateRenderer().render(msg.template, data)
            else:
                text = msg.text
            
            # Enviar
            result = self.messenger.send_message(
                text=text,
                platform=msg.platform,
                channel=msg.channel
            )
            
            msg.last_sent = datetime.utcnow()
            msg.status = "sent" if result.success else "failed"
            
            # Programar siguiente ejecución si es recurrente
            if msg.recurrence:
                msg.send_at = calculate_next_run(msg.recurrence, msg.send_at)
                msg.status = "scheduled"
            
            save_scheduled(msg)
```

## Mejores prácticas

1. **Usar routing de notificaciones**: No enviar todo a todas las plataformas; enrutar según tipo de evento
2. **Templates para consistencia**: Usar templates para mensajes recurrentes (standups, releases, alertas)
3. **Rate limiting**: Implementar rate limiting por plataforma para evitar spam y bans
4. **Verificar firmas de webhooks**: Siempre validar la autenticidad de webhooks entrantes
5. **Fallback entre plataformas**: Si Slack falla, intentar enviar por Discord automáticamente
6. **No exponer tokens**: Usar variables de entorno, nunca hardcodear tokens en config
7. **Mensajes concisos**: Los mensajes de notificación deben ser breves y accionables
8. **Threading para contexto**: Usar hilos para conversaciones largas, no saturar canales principales
9. **Archivos vía upload, no inline**: Para contenido largo, subir como archivo en lugar de pegar
10. **Audit trail de mensajes**: Registrar todos los mensajes enviados por el agente para auditoría

## Ejemplos

### Ejemplo 1: Notificación de deploy exitoso

```
→ NotificationRouter.route_notification(
    event="deploy_success",
    data={
        "environment": "production",
        "version": "2.3.1",
        "commit_sha": "abc123f",
        "duration": 45
    }
  )

→ Slack #deployments: "✅ Deploy exitoso — production v2.3.1"
→ Discord #dev-updates: "✅ Deploy exitoso — production v2.3.1"
```

### Ejemplo 2: Standup diario automatizado

```
→ ScheduledMessages.schedule_message(
    text=None,
    platform="slack",
    channel="#standup",
    send_at=parse("09:00 UTC"),
    recurrence="cron:0 9 * * 1-5",
    template="daily_standup",
    data_source=gather_standup_data
  )

Cada día laboral a las 09:00 UTC:
→ Genera datos de tareas completadas/planificadas
→ Renderiza template daily_standup
→ Publica en Slack #standup
```

### Ejemplo 3: Bot con slash commands

```
/openclaw status
→ "📊 Sprint 3: 75% completado | 2 blockers | ETA: Feb 24"

/openclaw deploy staging
→ "🚀 Iniciando deploy a staging... (se notificará al completarse)"
→ [Ejecuta pipeline]
→ "✅ Deploy a staging completado en 32s — https://staging.app.com"
```

### Ejemplo 4: Alerta de incidencia multi-plataforma

```
→ route_notification(
    event="incident",
    data={
        "severity": "P1",
        "service": "API Gateway",
        "impact": "50% de requests con error 500",
        "status": "Investigating"
    }
  )

→ Slack #alerts: 🚨 INCIDENCIA P1 — API Gateway
→ Teams #Incidents: 🚨 INCIDENCIA P1 — API Gateway
→ Discord @here en #alerts: 🚨 INCIDENCIA P1 — API Gateway
```

### Ejemplo 5: Compartir reporte en hilo

```
→ thread = messenger.create_thread(
    platform="slack",
    channel="#dev",
    title="Sprint 3 Retrospective",
    initial_message="Resumen del sprint y puntos de discusión"
  )

→ messenger.reply_to_thread(
    platform="slack",
    channel="#dev",
    thread_id=thread.id,
    text="📈 Velocity: 24 pts (↑ 20%)\n📊 Completion rate: 83%"
  )

→ messenger.upload_file_to_thread(
    platform="slack",
    channel="#dev",
    thread_id=thread.id,
    file_path="reports/sprint3_burndown.png"
  )
```
