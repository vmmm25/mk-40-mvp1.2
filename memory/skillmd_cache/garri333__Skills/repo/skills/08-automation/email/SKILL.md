---
name: email
version: 1.0.0
description: Send, read, search, and organize emails using IMAP/SMTP and Gmail API. Supports attachments, threading, labels, and multi-provider setup (Gmail, Outlook, Fastmail, any IMAP).
tags: [email, imap, smtp, gmail, outlook, automation, notifications, attachments]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Email Skill

## Setup and Dependencies

```bash
pip install imapclient smtplib secure-smtplib google-auth google-auth-oauthlib google-api-python-client python-dotenv
```

`.env`:
```
GMAIL_USER=you@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx   # App Password (2FA required)
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## Send Email (SMTP)

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(
    to: str | list[str],
    subject: str,
    body: str,
    html: bool = False,
    attachments: list[str] = None,
    cc: str | list[str] = None
):
    """Send an email via SMTP."""
    msg = MIMEMultipart()
    msg["From"] = os.getenv("GMAIL_USER")
    msg["To"] = to if isinstance(to, str) else ", ".join(to)
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = cc if isinstance(cc, str) else ", ".join(cc)

    # Body
    mime_type = "html" if html else "plain"
    msg.attach(MIMEText(body, mime_type))

    # Attachments
    for filepath in (attachments or []):
        with open(filepath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(filepath)}")
        msg.attach(part)

    with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
        recipients = [to] if isinstance(to, str) else to
        if cc:
            recipients += [cc] if isinstance(cc, str) else cc
        server.sendmail(os.getenv("GMAIL_USER"), recipients, msg.as_string())

    return {"status": "sent", "to": to, "subject": subject}

# Quick usage:
send_email(
    to="client@example.com",
    subject="Report ready",
    body="<h1>Your weekly report is attached.</h1>",
    html=True,
    attachments=["report.pdf"]
)
```

## Read Emails (IMAP)

```python
import imapclient
import email
from email.header import decode_header

def read_emails(folder="INBOX", limit=10, unseen_only=False):
    """Fetch and decode emails from IMAP."""
    with imapclient.IMAPClient(os.getenv("IMAP_SERVER"), ssl=True) as client:
        client.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
        client.select_folder(folder, readonly=True)

        criteria = ["UNSEEN"] if unseen_only else ["ALL"]
        messages = client.search(criteria)
        messages = messages[-limit:]  # most recent

        results = []
        for msg_id, data in client.fetch(messages, ["RFC822"]).items():
            raw = data[b"RFC822"]
            msg = email.message_from_bytes(raw)

            subject, enc = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(enc or "utf-8")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="replace")

            results.append({
                "id": msg_id,
                "from": msg["From"],
                "subject": subject,
                "date": msg["Date"],
                "body": body[:500]  # preview
            })

        return results

# Usage:
emails = read_emails(limit=5, unseen_only=True)
for e in emails:
    print(f"[{e['date']}] {e['from']} — {e['subject']}")
```

## Search Emails

```python
def search_emails(query: str, folder="INBOX", limit=20):
    """Search emails by subject or sender using IMAP SEARCH."""
    with imapclient.IMAPClient(os.getenv("IMAP_SERVER"), ssl=True) as client:
        client.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
        client.select_folder(folder, readonly=True)

        # IMAP search criteria
        criteria = [f'SUBJECT "{query}"']
        # To search sender: [f'FROM "{query}"']
        # To search body: [f'BODY "{query}"']

        messages = client.search(criteria)
        messages = messages[-limit:]

        if not messages:
            return []

        results = []
        for msg_id, data in client.fetch(messages, ["ENVELOPE"]).items():
            env = data[b"ENVELOPE"]
            subject = env.subject.decode() if env.subject else ""
            sender = env.from_[0] if env.from_ else None
            from_addr = f"{sender.mailbox.decode()}@{sender.host.decode()}" if sender else ""
            results.append({"id": msg_id, "subject": subject, "from": from_addr, "date": str(env.date)})

        return results
```

## Gmail API (OAuth2) — Full Access

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def get_gmail_service():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("gmail", "v1", credentials=creds)

def list_labels(service):
    """List Gmail labels."""
    results = service.users().labels().list(userId="me").execute()
    return [{l["id"]: l["name"]} for l in results.get("labels", [])]

def send_via_gmail_api(service, to: str, subject: str, body: str):
    """Send email using Gmail API."""
    msg = MIMEText(body)
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()

def move_to_label(service, msg_id: str, label_id: str):
    """Add a label to an email."""
    service.users().messages().modify(
        userId="me", id=msg_id,
        body={"addLabelIds": [label_id]}
    ).execute()
```

## Email Templates

```python
TEMPLATES = {
    "follow_up": """
Hi {name},

Following up on my previous email about {topic}.

Would you have 15 minutes this week for a quick call?

Best,
{sender}
    """.strip(),

    "delivery": """
Hi {name},

Your {product} is ready! Here's what we've prepared:

{summary}

Let me know if you have any questions.

Best regards,
{sender}
    """.strip(),

    "invoice": """
Hi {name},

Please find attached invoice #{invoice_number} for {amount}.

Payment due: {due_date}

Thank you for your business!
    """.strip()
}

def send_template(template_name: str, to: str, **kwargs):
    body = TEMPLATES[template_name].format(**kwargs)
    subject = kwargs.get("subject", f"Re: {template_name}")
    return send_email(to=to, subject=subject, body=body)
```

## Bulk Email with Rate Limiting

```python
import time

def send_bulk(recipients: list[dict], subject: str, body_template: str, delay_seconds=2):
    """
    Send personalized emails in bulk with rate limiting.
    recipients: [{"email": "...", "name": "...", ...}]
    """
    results = []
    for r in recipients:
        body = body_template.format(**r)
        try:
            result = send_email(to=r["email"], subject=subject, body=body)
            results.append({"email": r["email"], "status": "sent"})
        except Exception as e:
            results.append({"email": r["email"], "status": "error", "error": str(e)})
        time.sleep(delay_seconds)  # Respect rate limits

    return results
```

## References
- [Google Gmail API](https://developers.google.com/gmail/api) — OAuth2 full access
- [imapclient](https://imapclient.readthedocs.io/) — IMAP library
- [Python email docs](https://docs.python.org/3/library/email.html)
- [App Passwords (Gmail)](https://myaccount.google.com/apppasswords)
