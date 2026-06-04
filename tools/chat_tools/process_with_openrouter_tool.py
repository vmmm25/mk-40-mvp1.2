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

class ProcessWithOpenrouterTool(BaseTool):
    name = "process_with_openrouter"
    description = """Routes the user's request through an OpenRouter model for intelligent processing. Use when the current provider is OpenRouter or when the user specifically requests an OpenRouter model. Provides access to Llama, Gemma, Qwen, DeepSeek, and other models. The response will be spoken back to the user."""
    parameters = {'type': 'OBJECT', 'properties': {'prompt': {'type': 'STRING', 'description': "The user's complete request or question to send to OpenRouter"}}, 'required': ['prompt']}

    def execute(self, args: dict, ui: Any) -> str:
        try:
            from or_client import client
            prompt = args.get('prompt', '').strip()
            if not prompt:
                return 'No prompt provided.'
            result = client.chat(prompt, model=None)
            return result if result else 'OpenRouter returned an empty response.'
        except Exception as e:
            return f'OpenRouter error: {e}'
