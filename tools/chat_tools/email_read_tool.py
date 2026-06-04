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

class EmailReadTool(BaseTool):
    name = "email_read"
    description = """Reads emails from the user's Gmail account."""
    parameters = {'type': 'OBJECT', 'properties': {'max_results': {'type': 'INTEGER', 'description': 'Maximum number of emails to read (default: 5)'}, 'query': {'type': 'STRING', 'description': "Search query for filtering emails (e.g. 'is:unread', 'from:boss@company.com')"}}, 'required': []}

    def execute(self, args: dict, ui: Any) -> str:
        max_results = args.get('max_results', 5)
        query = args.get('query', '')
        try:
            from services.email.gmail_client import GmailClient
            client = GmailClient()
            emails = client.read_emails(max_results=max_results, query=query)
            if not emails:
                return 'No emails found.'
            formatted = []
            for e in emails:
                formatted.append(f"From: {e['sender']}\nSubject: {e['subject']}\nSnippet: {e['snippet']}\n---")
            return '\n'.join(formatted)
        except Exception as e:
            return f'Error reading emails: {e}'
