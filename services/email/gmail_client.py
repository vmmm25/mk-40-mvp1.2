import os.path
import base64
import logging
from email.message import EmailMessage

logger = logging.getLogger(__name__)

# Scopes for reading and sending email
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailClient:
    def __init__(self, credentials_path: str = "config/credentials.json", token_path: str = "config/token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()

    def _authenticate(self):
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError:
            logger.error("Google API client libraries are not installed.")
            return

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    logger.warning(f"Credentials file not found at {self.credentials_path}. Gmail disabled.")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def send_email(self, to: str, subject: str, body: str) -> bool:
        if not self.service:
            logger.error("Gmail service not initialized.")
            return False
            
        try:
            message = EmailMessage()
            message.set_content(body)
            message['To'] = to
            message['From'] = "me"
            message['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}

            send_message = (self.service.users().messages().send(userId="me", body=create_message).execute())
            logger.info(f"Message Id: {send_message['id']} sent successfully.")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def read_emails(self, max_results: int = 5, query: str = "") -> list:
        if not self.service:
            logger.error("Gmail service not initialized.")
            return []
            
        try:
            results = self.service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
            messages = results.get('messages', [])
            
            emails = []
            for msg in messages:
                txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                payload = txt.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                
                # Get snippet
                snippet = txt.get('snippet', '')
                
                emails.append({
                    "id": msg['id'],
                    "sender": sender,
                    "subject": subject,
                    "snippet": snippet
                })
            return emails
        except Exception as e:
            logger.error(f"Error reading emails: {e}")
            return []
