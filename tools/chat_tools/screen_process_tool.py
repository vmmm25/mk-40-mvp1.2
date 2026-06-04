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

class ScreenProcessTool(BaseTool):
    name = "screen_process"
    description = """Captures and analyzes the screen or webcam image. MUST be called when user asks what is on screen, what you see, analyze my screen, look at camera, etc. You have NO visual ability without this tool. After calling this tool, stay SILENT — the vision module speaks directly."""
    parameters = {'type': 'OBJECT', 'properties': {'angle': {'type': 'STRING', 'description': "'screen' to capture display, 'camera' for webcam. Default: 'screen'"}, 'text': {'type': 'STRING', 'description': 'The question or instruction about the captured image'}}, 'required': ['text']}

    def execute(self, args: dict, ui: Any) -> str:
        threading.Thread(target=screen_process, kwargs={'parameters': args, 'response': None, 'player': ui, 'session_memory': None}, daemon=True).start()
        return 'Screen processing started.'
