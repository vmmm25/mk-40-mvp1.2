---
name: remind-me
version: 1.0.0
description: Crear y gestionar recordatorios con lenguaje natural usando cron jobs o herramientas del sistema. Usa cuando necesites programar recordatorios, alertas o tareas periódicas.
tags: [reminders, cron, scheduling, automation, notifications, tasks]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Remind Me Skill

## Cuándo usar esta skill
- El usuario dice "recuérdame hacer X en 30 minutos"
- Programar tareas periódicas o recordatorios
- Crear alertas basadas en tiempo
- Automatizar notificaciones recurrentes

## Parsear lenguaje natural a tiempo

```python
from datetime import datetime, timedelta
import re

def parse_time_expression(expression: str) -> datetime:
    """
    Convierte expresiones naturales a datetime
    
    Ejemplos:
    - "en 30 minutos"
    - "en 2 horas"
    - "mañana a las 9"
    - "el viernes"
    - "en 3 días"
    """
    now = datetime.now()
    expression = expression.lower().strip()
    
    # Patrones de tiempo relativo
    patterns = [
        # "en X minutos/horas/días"
        (r'en (\d+) minutos?', lambda m: now + timedelta(minutes=int(m.group(1)))),
        (r'en (\d+) horas?', lambda m: now + timedelta(hours=int(m.group(1)))),
        (r'en (\d+) días?', lambda m: now + timedelta(days=int(m.group(1)))),
        (r'en (\d+) semanas?', lambda m: now + timedelta(weeks=int(m.group(1)))),
        
        # "mañana"
        (r'mañana(?: a las? (\d+)(?::(\d+))?)?', lambda m: (
            (now + timedelta(days=1)).replace(
                hour=int(m.group(1) or 9),
                minute=int(m.group(2) or 0),
                second=0, microsecond=0
            )
        )),
        
        # "a las X"
        (r'a las? (\d+)(?::(\d+))?', lambda m: (
            now.replace(hour=int(m.group(1)), minute=int(m.group(2) or 0), second=0)
            + (timedelta(days=1) if int(m.group(1)) <= now.hour else timedelta(0))
        )),
    ]
    
    for pattern, handler in patterns:
        match = re.search(pattern, expression)
        if match:
            return handler(match)
    
    raise ValueError(f"No puedo interpretar '{expression}' como una expresión de tiempo")


# Ejemplos de uso:
print(parse_time_expression("en 30 minutos"))
print(parse_time_expression("mañana a las 9"))
print(parse_time_expression("en 2 horas"))
```

## Crear recordatorio en Linux/Mac (cron)

```python
import subprocess
import tempfile
import os

def create_cron_reminder(message: str, run_at: datetime) -> str:
    """
    Crear un recordatorio usando cron (Linux/Mac)
    """
    # Determinar método de notificación
    if os.name == 'posix':  # Linux/Mac
        if os.path.exists('/usr/bin/notify-send'):
            notify_cmd = f'notify-send "Recordatorio" "{message}"'
        else:
            notify_cmd = f'echo "{message}" | wall'
    
    # Expresión cron
    cron_expr = f"{run_at.minute} {run_at.hour} {run_at.day} {run_at.month} *"
    
    # Crear trabajo cron de un solo uso (se borra solo)
    cron_job = f'{cron_expr} {notify_cmd} && crontab -l | grep -v "{message[:20]}" | crontab -'
    
    # Añadir a crontab
    try:
        # Obtener crontab actual
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout if result.returncode == 0 else ""
        
        # Añadir nuevo job
        new_crontab = current_crontab + f"\n{cron_job}\n"
        
        # Escribir nuevo crontab
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(new_crontab)
            tmp_file = f.name
        
        subprocess.run(['crontab', tmp_file], check=True)
        os.unlink(tmp_file)
        
        return f"✅ Recordatorio programado para {run_at.strftime('%d/%m/%Y a las %H:%M')}"
    
    except Exception as e:
        return f"❌ Error creando recordatorio: {e}"
```

## Crear recordatorio en Windows (Task Scheduler)

```python
import subprocess
from datetime import datetime

def create_windows_reminder(message: str, run_at: datetime, task_name: str = None) -> str:
    """Crear recordatorio en Windows usando Task Scheduler"""
    
    if not task_name:
        task_name = f"Reminder_{run_at.strftime('%Y%m%d%H%M%S')}"
    
    time_str = run_at.strftime("%H:%M")
    date_str = run_at.strftime("%d/%m/%Y")
    
    # Comando PowerShell para mostrar notificación
    ps_cmd = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText01)
    $template.SelectSingleNode('//text[@id="1"]').InnerText = '{message}'
    $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Reminder').Show($toast)
    """
    
    # Crear tarea
    cmd = [
        'schtasks', '/create', '/tn', task_name,
        '/tr', f'powershell -WindowStyle Hidden -Command "{ps_cmd}"',
        '/sc', 'once',
        '/st', time_str,
        '/sd', date_str,
        '/f',  # Force (overwrite if exists)
        '/v1', '/z'  # Delete after running
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return f"✅ Recordatorio programado para {run_at.strftime('%d/%m/%Y a las %H:%M')}"
    else:
        return f"❌ Error: {result.stderr}"
```

## Sistema completo de recordatorios (agnóstico de plataforma)

```python
import json
import threading
import time
from pathlib import Path

REMINDERS_FILE = Path.home() / ".reminders.json"

def load_reminders() -> list:
    if REMINDERS_FILE.exists():
        return json.loads(REMINDERS_FILE.read_text())
    return []

def save_reminders(reminders: list):
    REMINDERS_FILE.write_text(json.dumps(reminders, default=str, indent=2))

def add_reminder(message: str, remind_at: datetime) -> str:
    reminders = load_reminders()
    reminder = {
        "id": len(reminders) + 1,
        "message": message,
        "remind_at": remind_at.isoformat(),
        "created_at": datetime.now().isoformat(),
        "completed": False
    }
    reminders.append(reminder)
    save_reminders(reminders)
    
    # Programar en un hilo
    delay = (remind_at - datetime.now()).total_seconds()
    if delay > 0:
        timer = threading.Timer(delay, trigger_reminder, args=[reminder])
        timer.daemon = True
        timer.start()
    
    return f"✅ Recordatorio #{reminder['id']}: '{message}' para {remind_at.strftime('%d/%m %H:%M')}"

def trigger_reminder(reminder: dict):
    print(f"\n🔔 RECORDATORIO: {reminder['message']}")
    
    # Notificación del sistema si está disponible
    try:
        import subprocess
        if os.name == 'nt':  # Windows
            subprocess.run(['msg', '*', f"RECORDATORIO: {reminder['message']}"], 
                         capture_output=True)
        else:  # Linux/Mac
            subprocess.run(['notify-send', 'Recordatorio', reminder['message']],
                         capture_output=True)
    except Exception:
        pass

def list_reminders() -> str:
    reminders = [r for r in load_reminders() if not r['completed']]
    if not reminders:
        return "No tienes recordatorios pendientes"
    
    output = "📋 Recordatorios pendientes:\n"
    for r in reminders:
        dt = datetime.fromisoformat(r['remind_at'])
        output += f"#{r['id']} — {dt.strftime('%d/%m %H:%M')} — {r['message']}\n"
    
    return output


# Flujo completo de uso:
# 1. Usuario dice: "recuérdame enviar el informe semanal mañana a las 9"
time_expr = "mañana a las 9"
message = "Enviar el informe semanal"

remind_at = parse_time_expression(time_expr)
result = add_reminder(message, remind_at)
print(result)  # ✅ Recordatorio #1: 'Enviar el informe semanal' para 15/01 09:00
```

## Integración con agentes de IA

```python
def process_reminder_request(user_message: str) -> str:
    """
    Interpretar un mensaje natural y crear un recordatorio
    
    El agente extrae:
    1. La tarea a recordar
    2. El tiempo para el recordatorio
    """
    
    # Ejemplos de frases que esta función manejaría:
    # "Recuérdame llamar al dentista en 2 horas"
    # "Pon un recordatorio para revisar el PR mañana a las 10"
    # "Avísame en 30 minutos para tomar el café"
    
    # Patrones para extraer la tarea y el tiempo
    reminder_patterns = [
        r'recuérdame (.+?) (en \d+.+|mañana.+|a las.+)',
        r'pon (?:un )?recordatorio para (.+?) (en \d+.+|mañana.+)',
        r'avísame en (.+?) para (.+)',
    ]
    
    for pattern in reminder_patterns:
        match = re.search(pattern, user_message.lower())
        if match:
            if 'avísame en' in pattern:
                time_expr = match.group(1)
                task = match.group(2)
            else:
                task = match.group(1)
                time_expr = match.group(2)
            
            try:
                remind_at = parse_time_expression(time_expr)
                return add_reminder(task.strip(), remind_at)
            except ValueError as e:
                return f"No entendí el tiempo: {e}"
    
    return "No pude interpretar el recordatorio. Prueba: 'Recuérdame [tarea] en [tiempo]'"
```
