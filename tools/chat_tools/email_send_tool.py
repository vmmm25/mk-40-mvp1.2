from typing import Any, Callable
from tools.base import BaseTool
import json
import os
import subprocess
import threading
import time

import os
import time
import threading
from typing import Callable, Any
from actions.file_processor import file_processor
from actions.flight_finder import flight_finder
from actions.open_app import open_app
from actions.weather_report import weather_action
from actions.send_message import send_message
from actions.reminder import reminder
from actions.computer_settings import computer_settings
from actions.screen_processor import screen_process
from actions.youtube_video import youtube_video
from actions.desktop import desktop_control
from actions.browser_control import browser_control
from actions.file_controller import file_controller
from actions.code_helper import code_helper
from actions.dev_agent import dev_agent
from actions.web_search import web_search as web_search_action
from actions.computer_control import computer_control
from actions.game_updater import game_updater
from actions.terminal_control import terminal_control
from agent.task_queue import get_queue, TaskPriority
from memory.memory_manager import update_memory
from memory.config_manager import get_os_system
import asyncio
import os
from pathlib import Path

class EmailSendTool(BaseTool):
    name = "email_send"
    description = """Sends an email using the user's Gmail account."""
    parameters = {'type': 'OBJECT', 'properties': {'to': {'type': 'STRING', 'description': 'Recipient email address'}, 'subject': {'type': 'STRING', 'description': 'Subject of the email'}, 'body': {'type': 'STRING', 'description': 'Body content of the email'}}, 'required': ['to', 'subject', 'body']}

    def execute(self, args: dict, ui: Any) -> str:
        to = args.get('to')
        subject = args.get('subject')
        body = args.get('body')
        if not to or not subject or (not body):
            return 'Missing required parameters for email_send.'
        try:
            from services.email.gmail_client import GmailClient
            client = GmailClient()
            success = client.send_email(to=to, subject=subject, body=body)
            return 'Email sent successfully.' if success else 'Failed to send email.'
        except Exception as e:
            return f'Error sending email: {e}'
