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

class ComputerSettingsTool(BaseTool):
    name = "computer_settings"
    description = """Controls the computer: volume, brightness, window management, keyboard shortcuts, typing text on screen, closing apps, fullscreen, dark mode, WiFi, restart, shutdown, scrolling, tab management, zoom, screenshots, lock screen, refresh/reload page. Use for ANY single computer control command. NEVER route to agent_task."""
    parameters = {'type': 'OBJECT', 'properties': {'action': {'type': 'STRING', 'description': 'The action to perform'}, 'description': {'type': 'STRING', 'description': 'Natural language description of what to do'}, 'value': {'type': 'STRING', 'description': 'Optional value: volume level, text to type, etc.'}}, 'required': []}

    def execute(self, args: dict, ui: Any) -> str:
        return computer_settings(parameters=args, response=None, player=ui) or 'Done.'
