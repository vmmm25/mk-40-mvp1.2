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

class CalendarCreateEventTool(BaseTool):
    name = "calendar_create_event"
    description = """Create a new event in your Google Calendar."""
    parameters = {'type': 'OBJECT', 'properties': {'summary': {'type': 'STRING', 'description': 'Event title'}, 'description': {'type': 'STRING', 'description': 'Event description'}, 'date': {'type': 'STRING', 'description': 'Date YYYY-MM-DD'}, 'time': {'type': 'STRING', 'description': 'Time HH:MM (24h format, default: 12:00)'}, 'duration_minutes': {'type': 'INTEGER', 'description': 'Duration in minutes (default: 60)'}, 'attendees': {'type': 'ARRAY', 'items': {'type': 'STRING'}, 'description': 'Email addresses of attendees'}}, 'required': ['summary', 'date']}

    def execute(self, args: dict, ui: Any) -> str:
        summary = args.get('summary', '')
        date = args.get('date', '')
        time = args.get('time', '12:00')
        duration = args.get('duration_minutes', 60)
        description = args.get('description', '')
        attendees = args.get('attendees', None)
        if not summary or not date:
            return 'Missing required parameters: summary and date.'
        try:
            from services.calendar.gcal_client import GoogleCalendarClient
            client = GoogleCalendarClient()
            result = client.create_event(summary=summary, date=date, time=time, duration_minutes=duration, description=description, attendees=attendees)
            if result:
                return f"Event created: {result['summary']} (link: {result.get('htmlLink', 'N/A')})"
            return 'Failed to create calendar event.'
        except Exception as e:
            return f'Error creating calendar event: {e}'
