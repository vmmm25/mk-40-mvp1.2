---
name: google-workspace
version: 1.0.0
description: CLI para automatizar Gmail, Google Calendar, Drive y Contacts con comandos de línea de comandos. Usa cuando necesites enviar emails, crear eventos, subir archivos o buscar en Google Workspace desde un agente.
tags: [google, gmail, calendar, drive, automation, cli, workspace, gcloud]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Google Workspace CLI Skill

## Cuándo usar esta skill
- Enviar emails programáticamente desde un agente
- Crear o actualizar eventos en Google Calendar
- Subir, descargar, buscar archivos en Google Drive
- Automatizar flujos de trabajo con Google Workspace
- Integrar Google Workspace en pipelines de automatización

## Setup inicial

### Option A: gam (CLI oficial para Workspace)
```bash
# Instalar gam (Google Apps Manager)
# https://github.com/GAM-team/GAM

# Windows
winget install GAM-team.GAM
# O descargar desde: https://github.com/GAM-team/GAM/releases

# Configurar
gam create project
gam oauth create
gam version  # Verificar instalación
```

### Option B: Google APIs con Python
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Gmail

### Enviar email
```python
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def send_email(to: str, subject: str, body: str, body_html: str = None):
    """Enviar email via Gmail API"""
    creds = Credentials.from_authorized_user_file('token.json', [
        'https://www.googleapis.com/auth/gmail.send'
    ])
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    
    if body_html:
        message.attach(MIMEText(body_html, 'html'))
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId='me', 
        body={'raw': raw}
    ).execute()
    
    print(f"Email enviado a {to}")
```

### Buscar emails
```python
def search_emails(query: str, max_results: int = 10) -> list:
    """
    Buscar emails. Query supporta Gmail search operators:
    - from:email@domain.com
    - subject:palabra
    - after:2024/01/01
    - has:attachment
    - is:unread
    """
    creds = Credentials.from_authorized_user_file('token.json', [
        'https://www.googleapis.com/auth/gmail.readonly'
    ])
    service = build('gmail', 'v1', credentials=creds)
    
    results = service.users().messages().list(
        userId='me', 
        q=query, 
        maxResults=max_results
    ).execute()
    
    messages = []
    for msg in results.get('messages', []):
        full_msg = service.users().messages().get(
            userId='me', 
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
        messages.append({
            'id': msg['id'],
            'from': headers.get('From'),
            'subject': headers.get('Subject'),
            'date': headers.get('Date'),
            'snippet': full_msg.get('snippet')
        })
    
    return messages
```

## Google Calendar

### Crear evento
```python
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def create_event(
    title: str,
    start: datetime,
    duration_minutes: int = 60,
    attendees: list = None,
    description: str = "",
    location: str = "",
    meet_link: bool = False
):
    """Crear evento en Google Calendar"""
    creds = Credentials.from_authorized_user_file('token.json', [
        'https://www.googleapis.com/auth/calendar'
    ])
    service = build('calendar', 'v3', credentials=creds)
    
    end = start + timedelta(minutes=duration_minutes)
    
    event = {
        'summary': title,
        'description': description,
        'location': location,
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'Europe/Madrid',
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'Europe/Madrid',
        },
    }
    
    if attendees:
        event['attendees'] = [{'email': a} for a in attendees]
    
    if meet_link:
        event['conferenceData'] = {
            'createRequest': {
                'requestId': f'meet-{int(start.timestamp())}',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    
    result = service.events().insert(
        calendarId='primary', 
        body=event,
        conferenceDataVersion=1 if meet_link else 0,
        sendNotifications=True if attendees else False
    ).execute()
    
    return {
        'event_id': result['id'],
        'html_link': result.get('htmlLink'),
        'meet_link': result.get('hangoutLink'),
    }
```

### Listar próximos eventos
```python
def list_upcoming_events(days: int = 7, max_events: int = 20) -> list:
    """Listar próximos eventos del calendario"""
    creds = Credentials.from_authorized_user_file('token.json', [
        'https://www.googleapis.com/auth/calendar.readonly'
    ])
    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=end,
        maxResults=max_events,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return [{
        'title': event.get('summary', '(Sin título)'),
        'start': event['start'].get('dateTime', event['start'].get('date')),
        'attendees': [a['email'] for a in event.get('attendees', [])],
        'meet_link': event.get('hangoutLink', ''),
    } for event in events_result.get('items', [])]
```

## Google Drive

### Subir archivo
```python
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path: str, folder_id: str = None, file_name: str = None) -> dict:
    """Subir archivo a Google Drive"""
    creds = Credentials.from_authorized_user_file('token.json', [
        'https://www.googleapis.com/auth/drive'
    ])
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': file_name or file_path.split('/')[-1],
    }
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()
    
    return {
        'file_id': file['id'],
        'name': file['name'],
        'view_link': file['webViewLink'],
    }
```

### Buscar archivos
```python
def search_drive(query: str, max_results: int = 10) -> list:
    """
    Buscar archivos en Drive
    Query examples:
    - "name contains 'report'"
    - "mimeType='application/pdf'"
    - "modifiedTime > '2024-01-01'"
    - "'folder_id' in parents"
    """
    creds = Credentials.from_authorized_user_file('token.json', [
        'https://www.googleapis.com/auth/drive.readonly'
    ])
    service = build('drive', 'v3', credentials=creds)
    
    results = service.files().list(
        q=query,
        pageSize=max_results,
        fields='files(id, name, mimeType, modifiedTime, webViewLink)'
    ).execute()
    
    return results.get('files', [])
```

## Usando gam (CLI)

```bash
# Enviar email
gam sendemail to user@example.com subject "Asunto" message "Cuerpo del email"

# Listar eventos de calendar
gam user admin@domain.com show events primary after 2024-01-01

# Listar archivos en Drive
gam user admin@domain.com show filelist query "name contains 'report'"

# Crear usuario
gam create user nuevo@domain.com firstname "Nombre" lastname "Apellido" password "SecurePass123!"

# Ver info de usuario
gam info user user@domain.com
```

## Referencias
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Calendar API Reference](https://developers.google.com/calendar/api/v3/reference)
- [Drive API Reference](https://developers.google.com/drive/api/reference/rest/v3)
- [GAM GitHub](https://github.com/GAM-team/GAM)
